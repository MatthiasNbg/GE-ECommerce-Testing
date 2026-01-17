"""
Einzelner Checkout-Test zur Diagnose.

Führt einen kompletten Gast-Checkout mit Zahlungsart "Rechnung" durch.
"""
import pytest
from playwright.async_api import Browser

from ..conftest import accept_cookie_banner_async
from ..pages.checkout_page import CheckoutPage, Address


@pytest.mark.asyncio
async def test_single_guest_checkout(browser: Browser, config):
    """Führt einen einzelnen Gast-Checkout durch."""

    print(f"\n=== Test startet ===")
    print(f"Base URL: {config.base_url}")
    print(f"HTTP Auth: {config.htaccess_user}")

    # Neuen Context mit HTTP-Credentials erstellen
    context_args = {"viewport": {"width": 1920, "height": 1080}}
    if config.htaccess_user and config.htaccess_password:
        context_args["http_credentials"] = {
            "username": config.htaccess_user,
            "password": config.htaccess_password,
        }
        print(f"   HTTP-Credentials gesetzt: {config.htaccess_user}")

    context = await browser.new_context(**context_args)
    page = await context.new_page()

    try:
        # Schritt 1: Produkt in Warenkorb legen
        print("\n[1] Produkt laden...")
        products = config.get_all_products()
        product_path = products[0] if products else "p/kurzarmshirt-aus-bio-baumwolle/ge-p-862990"
        product_url = f"{config.base_url}/{product_path}"
        print(f"   Produkt: {product_path}")
        await page.goto(product_url, timeout=60000)
        await page.wait_for_load_state("networkidle")
        print(f"   URL: {page.url}")

        # Cookie-Banner akzeptieren (Usercentrics oder Shopware)
        if await accept_cookie_banner_async(page):
            print("   Cookie-Banner akzeptiert")
        else:
            print("   Kein Cookie-Banner")

        # Screenshot der Produktseite
        await page.screenshot(path="debug_01_product.png")
        print("   Screenshot: debug_01_product.png")

        # In den Warenkorb
        print("\n[2] In den Warenkorb...")
        add_btn = page.locator("button.btn-buy, button:has-text('In den Warenkorb'), .product-detail-buy button")
        await add_btn.first.click()
        await page.wait_for_timeout(2000)
        await page.screenshot(path="debug_02_cart.png")
        print("   Screenshot: debug_02_cart.png")

        # Schritt 2: Zum Checkout navigieren
        print("\n[3] Zum Checkout navigieren...")
        checkout = CheckoutPage(page, config.base_url)
        await checkout.goto_checkout()
        await page.screenshot(path="debug_03_checkout.png")
        print(f"   URL: {page.url}")
        print("   Screenshot: debug_03_checkout.png")

        # Schritt 3: Gast-Checkout starten
        print("\n[4] Gast-Checkout starten...")
        await checkout.start_guest_checkout()
        await page.screenshot(path="debug_04_guest.png")
        print("   Screenshot: debug_04_guest.png")

        # Schritt 4: Adresse ausfüllen
        print("\n[5] Adresse ausfüllen...")
        address = Address(
            salutation="mr",
            first_name="Test",
            last_name="Kunde",
            street="Teststraße 123",
            zip_code="4020",
            city="Linz",
            country="AT",
            email="test@example.com"
        )
        await checkout.fill_guest_address(address)
        await page.screenshot(path="debug_05_address.png")
        print("   Screenshot: debug_05_address.png")

        # Schritt 5: Datenschutz und Weiter
        print("\n[6] Datenschutz akzeptieren und weiter...")
        await checkout.accept_privacy_and_continue()
        await page.screenshot(path="debug_06_confirm.png")
        print(f"   URL: {page.url}")
        print("   Screenshot: debug_06_confirm.png")

        # Schritt 6: Zahlungsart "Rechnung" wählen (keine Kreditkartendaten nötig)
        print("\n[7] Zahlungsmethode 'Rechnung' wählen...")
        try:
            # Direkt auf Rechnung-Label klicken (robuster als select_payment_method)
            rechnung_label = page.locator(".payment-method-label:has-text('Rechnung'), label:has-text('Rechnung')")
            if await rechnung_label.count() > 0:
                await rechnung_label.first.click()
                await page.wait_for_timeout(500)
                print("   Rechnung ausgewählt (via Label)")
            else:
                # Fallback: via checkout method
                await checkout.select_payment_method("invoice")
                print("   Rechnung ausgewählt (via select_payment_method)")
        except Exception as e:
            print(f"   FEHLER: {e}")
            await page.screenshot(path="debug_07_payment_error.png")
            raise

        await page.screenshot(path="debug_08_payment.png")
        print("   Screenshot: debug_08_payment.png")

        # Schritt 7: AGB akzeptieren
        print("\n[8] AGB akzeptieren...")
        await checkout.accept_terms()

        # Schritt 8: Bestellung abschließen
        print("\n[9] Bestellung abschließen...")
        await checkout.place_order()

        # Schritt 9: Bestätigung warten
        print("\n[10] Auf Bestätigung warten...")
        await checkout.wait_for_confirmation()
        await page.screenshot(path="debug_09_confirmation.png")
        print("   Screenshot: debug_09_confirmation.png")

        order_number = await checkout.get_order_number()
        print(f"\n=== ERFOLG! Bestellnummer: {order_number} ===")

    finally:
        await context.close()
