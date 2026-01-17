"""
Einzelner Checkout-Test zur Diagnose.

Führt einen kompletten Gast-Checkout mit Zahlungsart "Rechnung" durch.
"""
import pytest
from playwright.async_api import async_playwright

from ..conftest import accept_cookie_banner_async
from ..pages.checkout_page import CheckoutPage, Address


@pytest.mark.asyncio
async def test_single_guest_checkout(config, request):
    """Führt einen einzelnen Gast-Checkout durch."""

    print(f"\n=== Test startet ===")
    print(f"Base URL: {config.base_url}")
    print(f"HTTP Auth: {config.htaccess_user}")

    # Prüfen ob --headed Flag gesetzt ist
    headed = request.config.getoption("--headed", default=False)

    async with async_playwright() as p:
        # Browser starten (headed wenn --headed Flag gesetzt)
        browser = await p.chromium.launch(
            headless=not headed,
            slow_mo=200 if headed else 0
        )

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
            add_btn = page.locator("button.btn-buy")
            await add_btn.first.click()
            await page.wait_for_timeout(3000)

            # Offcanvas-Cart schließen falls offen
            offcanvas_close = page.locator(".offcanvas-close, .btn-close, [data-bs-dismiss='offcanvas']")
            if await offcanvas_close.count() > 0 and await offcanvas_close.first.is_visible(timeout=2000):
                await offcanvas_close.first.click()
                await page.wait_for_timeout(500)
                print("   Offcanvas geschlossen")

            # Warenkorb-Counter prüfen
            cart_count = page.locator(".header-cart-total, .cart-quantity, [data-cart-widget] .badge")
            if await cart_count.count() > 0:
                count_text = await cart_count.first.text_content()
                print(f"   Warenkorb-Counter: {count_text}")

            await page.screenshot(path="debug_02_cart.png")
            print("   Screenshot: debug_02_cart.png")

            # Schritt 2: Zum Warenkorb und dann zur Kasse
            print("\n[3] Zum Warenkorb...")
            await page.goto(f"{config.base_url}/checkout/cart")
            await page.wait_for_load_state("domcontentloaded")
            await page.wait_for_timeout(1000)  # Kurz warten für AJAX
            await page.screenshot(path="debug_03_cart.png")
            print(f"   URL: {page.url}")

            # Prüfen ob Warenkorb leer ist
            empty_cart = page.locator(".cart-empty, :has-text('Ihr Warenkorb ist leer')")
            if await empty_cart.count() > 0 and await empty_cart.first.is_visible(timeout=2000):
                raise Exception("Warenkorb ist leer! Produkt wurde nicht hinzugefügt.")

            # "Zur Kasse" Button klicken
            print("\n[4] Zur Kasse Button klicken...")
            checkout_btn = page.locator("a:has-text('Zur Kasse'), button:has-text('Zur Kasse'), .begin-checkout-btn, .checkout-btn")
            await checkout_btn.first.click()
            await page.wait_for_load_state("domcontentloaded")
            await page.wait_for_timeout(1000)
            await page.screenshot(path="debug_04_checkout.png")
            print(f"   URL: {page.url}")

            checkout = CheckoutPage(page, config.base_url)

            # Gast-Checkout starten
            await checkout.start_guest_checkout()
            await page.screenshot(path="debug_05_guest.png")
            print("   Screenshot: debug_05_guest.png")

            # Schritt 4: Adresse ausfüllen
            print("\n[6] Adresse ausfüllen...")
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
            await page.screenshot(path="debug_06_address.png")
            print("   Screenshot: debug_06_address.png")

            # Datenschutz und Weiter
            print("\n[7] Datenschutz akzeptieren und weiter...")
            await checkout.accept_privacy_and_continue()
            await page.screenshot(path="debug_07_confirm.png")
            print(f"   URL: {page.url}")
            print("   Screenshot: debug_07_confirm.png")

            # Zahlungsart "Rechnung" wählen (keine Kreditkartendaten nötig)
            print("\n[8] Zahlungsmethode 'Rechnung' wählen...")
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
                await page.screenshot(path="debug_08_payment_error.png")
                raise

            await page.screenshot(path="debug_08_payment.png")
            print("   Screenshot: debug_08_payment.png")

            # AGB akzeptieren
            print("\n[9] AGB akzeptieren...")
            await checkout.accept_terms()

            # Bestellung abschließen
            print("\n[10] Bestellung abschließen...")
            await checkout.place_order()

            # Bestätigung warten
            print("\n[11] Auf Bestätigung warten...")
            await checkout.wait_for_confirmation()
            await page.screenshot(path="debug_09_confirmation.png")
            print("   Screenshot: debug_09_confirmation.png")

            order_number = await checkout.get_order_number()
            print(f"\n=== ERFOLG! Bestellnummer: {order_number} ===")

        finally:
            await context.close()
            await browser.close()
