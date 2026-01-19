"""
Critical Path Tests (Phase 1) - Kerngeschäftsprozesse.

Testet die wichtigsten Bestellprozesse:
- TC-CRITICAL-001: Gast-Checkout AT
- TC-CRITICAL-002: Gast-Checkout DE
- TC-CRITICAL-003: Gast-Checkout CH
- TC-CRITICAL-004: Registrierter User Checkout
- TC-CRITICAL-008: Warenkorb-Persistenz

Priorität: P0 - Diese Tests MÜSSEN vor jedem Deployment bestehen!
"""
import pytest
from playwright.async_api import async_playwright

from ..pages.checkout_page import CheckoutPage, Address
from ..pages.base_page import BasePage


# =============================================================================
# Testdaten pro Land
# =============================================================================

COUNTRY_TEST_DATA = {
    "AT": {
        "country_path": "/",
        "address": Address(
            salutation="mr",
            first_name="Test",
            last_name="Kunde-AT",
            street="Teststraße 123",
            zip_code="4020",
            city="Linz",
            country="AT",
            email="test-at@example.com"
        ),
        "payment_method": "invoice",  # Rechnung
    },
    "DE": {
        "country_path": "/de-de",
        "address": Address(
            salutation="mrs",
            first_name="Test",
            last_name="Kunde-DE",
            street="Teststraße 456",
            zip_code="80331",
            city="München",
            country="DE",
            email="test-de@example.com"
        ),
        "payment_method": "invoice",  # Rechnung
    },
    "CH": {
        "country_path": "/de-ch",
        "address": Address(
            salutation="mr",
            first_name="Test",
            last_name="Kunde-CH",
            street="Teststrasse 789",
            zip_code="8001",
            city="Zürich",
            country="CH",
            email="test-ch@example.com"
        ),
        "payment_method": "prepayment",  # Vorkasse (CH hat keine Rechnung)
    },
}


# =============================================================================
# Hilfsfunktionen
# =============================================================================

def get_test_customer_credentials(config, country: str = "AT"):
    """Holt Test-Kunden-Zugangsdaten für ein Land."""
    customer = config.get_customer_by_country(country)
    if not customer:
        customer = config.get_registered_customer(0)
    if not customer:
        pytest.skip("Keine Test-Kunden konfiguriert")

    password = config.get_customer_password(customer)
    if not password:
        pytest.skip("Kein Passwort konfiguriert")

    return customer.email, password


async def add_product_to_cart(page, config, base_page: BasePage):
    """Fügt ein Produkt zum Warenkorb hinzu."""
    products = config.get_all_products()
    product_path = products[0] if products else "p/kurzarmshirt-aus-bio-baumwolle/ge-p-862990"
    product_url = f"{config.base_url}/{product_path}"

    await page.goto(product_url, timeout=60000)
    await page.wait_for_load_state("networkidle")

    # Cookie-Banner akzeptieren
    await base_page.accept_cookies_if_visible()

    # In den Warenkorb
    add_btn = page.locator("button.btn-buy")
    if await add_btn.count() > 0:
        await add_btn.first.click()
        await page.wait_for_timeout(3000)

    # Offcanvas schließen falls offen
    offcanvas_close = page.locator(".offcanvas-close, .btn-close, [data-bs-dismiss='offcanvas']")
    if await offcanvas_close.count() > 0:
        try:
            if await offcanvas_close.first.is_visible(timeout=2000):
                await offcanvas_close.first.click()
                await page.wait_for_timeout(500)
        except Exception:
            pass

    return product_path


async def navigate_to_checkout(page, config):
    """Navigiert zum Checkout."""
    await page.goto(f"{config.base_url}/checkout/cart")
    await page.wait_for_load_state("domcontentloaded")
    await page.wait_for_timeout(1000)

    # Prüfen ob Warenkorb leer
    empty_cart = page.locator(".cart-empty, :has-text('Ihr Warenkorb ist leer')")
    if await empty_cart.count() > 0:
        try:
            if await empty_cart.first.is_visible(timeout=2000):
                raise Exception("Warenkorb ist leer!")
        except Exception:
            pass

    # Zur Kasse
    checkout_btn = page.locator("a:has-text('Zur Kasse'), button:has-text('Zur Kasse')")
    await checkout_btn.first.click()
    await page.wait_for_load_state("domcontentloaded")
    await page.wait_for_timeout(1000)


# =============================================================================
# TC-CRITICAL-001/002/003: Gast-Checkout (AT, DE, CH)
# =============================================================================

@pytest.mark.asyncio
@pytest.mark.critical
@pytest.mark.checkout
@pytest.mark.parametrize("country", ["AT", "DE", "CH"])
async def test_guest_checkout_complete(config, request, country):
    """
    TC-CRITICAL-001/002/003: Vollständiger Gast-Checkout pro Land.

    Testet den kompletten Bestellprozess als Gast:
    1. Produkt in Warenkorb
    2. Checkout starten
    3. Adresse eingeben
    4. Zahlungsart wählen
    5. Bestellung abschließen
    6. Bestätigung prüfen
    """
    test_data = COUNTRY_TEST_DATA[country]
    print(f"\n=== TC-CRITICAL: Gast-Checkout [{country}] ===")

    headed = request.config.getoption("--headed", default=False)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=not headed,
            slow_mo=200 if headed else 0
        )

        context_args = {"viewport": {"width": 1920, "height": 1080}}
        if config.htaccess_user and config.htaccess_password:
            context_args["http_credentials"] = {
                "username": config.htaccess_user,
                "password": config.htaccess_password,
            }

        context = await browser.new_context(**context_args)
        page = await context.new_page()

        try:
            base_page = BasePage(page, config.base_url)
            checkout = CheckoutPage(page, config.base_url)

            # Schritt 1: Produkt in Warenkorb
            print(f"[1] Produkt in Warenkorb legen...")
            product = await add_product_to_cart(page, config, base_page)
            print(f"    Produkt: {product}")

            # Schritt 2: Zum Checkout navigieren
            print(f"[2] Zum Checkout navigieren...")
            await navigate_to_checkout(page, config)

            # Schritt 3: Gast-Checkout starten
            print(f"[3] Gast-Checkout starten...")
            await checkout.start_guest_checkout()

            # Schritt 4: Adresse eingeben
            print(f"[4] Adresse eingeben ({country})...")
            await checkout.fill_guest_address(test_data["address"])

            # Schritt 5: Datenschutz akzeptieren und weiter
            print(f"[5] Datenschutz akzeptieren...")
            await checkout.accept_privacy_and_continue()

            # Schritt 6: Zahlungsart wählen
            print(f"[6] Zahlungsart wählen: {test_data['payment_method']}...")
            await checkout.select_payment_method(test_data["payment_method"])

            # Schritt 7: AGB akzeptieren
            print(f"[7] AGB akzeptieren...")
            await checkout.accept_terms()

            # Schritt 8: Bestellung abschließen
            print(f"[8] Bestellung abschließen...")
            await checkout.place_order()

            # Schritt 9: Bestätigung prüfen
            print(f"[9] Auf Bestätigung warten...")
            await checkout.wait_for_confirmation()

            order_number = await checkout.get_order_number()
            order_id = await checkout.get_order_id_from_url()

            print(f"\n=== ERFOLG [{country}] ===")
            print(f"    Bestellnummer: {order_number}")
            print(f"    Order-ID: {order_id}")

            assert order_number or order_id, "Bestellbestätigung sollte Bestellnummer enthalten"

        except Exception as e:
            await page.screenshot(path=f"error_checkout_{country}.png")
            print(f"\n=== FEHLER [{country}] ===")
            print(f"    {str(e)}")
            raise

        finally:
            await context.close()
            await browser.close()


# =============================================================================
# TC-CRITICAL-004: Registrierter User Checkout
# =============================================================================

@pytest.mark.asyncio
@pytest.mark.critical
@pytest.mark.checkout
async def test_registered_user_checkout(config, request):
    """
    TC-CRITICAL-004: Checkout als registrierter Kunde.

    Testet den Bestellprozess für eingeloggte Kunden:
    1. Produkt in Warenkorb
    2. Checkout starten
    3. Login mit bestehendem Account
    4. Zahlungsart wählen
    5. Bestellung abschließen
    """
    print(f"\n=== TC-CRITICAL-004: Registrierter User Checkout ===")

    email, password = get_test_customer_credentials(config, "AT")
    print(f"    Test-Account: {email}")

    headed = request.config.getoption("--headed", default=False)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=not headed,
            slow_mo=200 if headed else 0
        )

        context_args = {"viewport": {"width": 1920, "height": 1080}}
        if config.htaccess_user and config.htaccess_password:
            context_args["http_credentials"] = {
                "username": config.htaccess_user,
                "password": config.htaccess_password,
            }

        context = await browser.new_context(**context_args)
        page = await context.new_page()

        try:
            base_page = BasePage(page, config.base_url)
            checkout = CheckoutPage(page, config.base_url)

            # Schritt 1: Produkt in Warenkorb
            print(f"[1] Produkt in Warenkorb legen...")
            product = await add_product_to_cart(page, config, base_page)
            print(f"    Produkt: {product}")

            # Schritt 2: Zum Checkout navigieren
            print(f"[2] Zum Checkout navigieren...")
            await navigate_to_checkout(page, config)

            # Schritt 3: Login
            print(f"[3] Login als registrierter Kunde...")
            await checkout.login(email, password)

            # Warten auf Weiterleitung zur Confirm-Seite
            await page.wait_for_timeout(2000)

            # Falls nicht auf Confirm-Seite, dahin navigieren
            if "confirm" not in page.url:
                print(f"    Navigiere zur Confirm-Seite...")
                await checkout.goto_confirm()

            # Schritt 4: Zahlungsart wählen
            print(f"[4] Zahlungsart wählen: Rechnung...")
            await checkout.select_payment_method("invoice")

            # Schritt 5: AGB akzeptieren
            print(f"[5] AGB akzeptieren...")
            await checkout.accept_terms()

            # Schritt 6: Bestellung abschließen
            print(f"[6] Bestellung abschließen...")
            await checkout.place_order()

            # Schritt 7: Bestätigung prüfen
            print(f"[7] Auf Bestätigung warten...")
            await checkout.wait_for_confirmation()

            order_number = await checkout.get_order_number()

            print(f"\n=== ERFOLG ===")
            print(f"    Bestellnummer: {order_number}")

            assert order_number, "Bestellbestätigung sollte Bestellnummer enthalten"

        except Exception as e:
            await page.screenshot(path="error_registered_checkout.png")
            print(f"\n=== FEHLER ===")
            print(f"    {str(e)}")
            raise

        finally:
            await context.close()
            await browser.close()


# =============================================================================
# TC-CRITICAL-008: Warenkorb-Persistenz
# =============================================================================

@pytest.mark.asyncio
@pytest.mark.critical
@pytest.mark.cart
async def test_cart_persistence(config, request):
    """
    TC-CRITICAL-008: Warenkorb bleibt nach Seitennavigation erhalten.

    Testet:
    1. Produkt in Warenkorb
    2. Andere Seiten besuchen
    3. Zurück zum Warenkorb
    4. Produkt ist noch vorhanden
    """
    print(f"\n=== TC-CRITICAL-008: Warenkorb-Persistenz ===")

    headed = request.config.getoption("--headed", default=False)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=not headed,
            slow_mo=200 if headed else 0
        )

        context_args = {"viewport": {"width": 1920, "height": 1080}}
        if config.htaccess_user and config.htaccess_password:
            context_args["http_credentials"] = {
                "username": config.htaccess_user,
                "password": config.htaccess_password,
            }

        context = await browser.new_context(**context_args)
        page = await context.new_page()

        try:
            base_page = BasePage(page, config.base_url)

            # Schritt 1: Produkt in Warenkorb
            print(f"[1] Produkt in Warenkorb legen...")
            product = await add_product_to_cart(page, config, base_page)
            print(f"    Produkt: {product}")

            # Schritt 2: Warenkorb prüfen
            print(f"[2] Warenkorb prüfen...")
            await page.goto(f"{config.base_url}/checkout/cart")
            await page.wait_for_load_state("domcontentloaded")

            # Produkte im Warenkorb zählen
            cart_items = page.locator(".line-item, .cart-item")
            initial_count = await cart_items.count()
            print(f"    Produkte im Warenkorb: {initial_count}")
            assert initial_count > 0, "Warenkorb sollte Produkte enthalten"

            # Schritt 3: Andere Seiten besuchen
            print(f"[3] Andere Seiten besuchen...")

            # Homepage
            await page.goto(config.base_url)
            await page.wait_for_load_state("domcontentloaded")
            print(f"    Homepage besucht")

            # Kategorie-Seite (falls vorhanden)
            await page.goto(f"{config.base_url}/wohnen/")
            await page.wait_for_load_state("domcontentloaded")
            print(f"    Kategorie besucht")

            # Schritt 4: Zurück zum Warenkorb
            print(f"[4] Zurück zum Warenkorb...")
            await page.goto(f"{config.base_url}/checkout/cart")
            await page.wait_for_load_state("domcontentloaded")
            await page.wait_for_timeout(1000)

            # Schritt 5: Produkt prüfen
            print(f"[5] Produkt-Persistenz prüfen...")
            cart_items = page.locator(".line-item, .cart-item")
            final_count = await cart_items.count()
            print(f"    Produkte im Warenkorb: {final_count}")

            assert final_count == initial_count, \
                f"Warenkorb sollte {initial_count} Produkte enthalten, hat aber {final_count}"

            print(f"\n=== ERFOLG ===")
            print(f"    Warenkorb-Persistenz bestätigt")

        except Exception as e:
            await page.screenshot(path="error_cart_persistence.png")
            print(f"\n=== FEHLER ===")
            print(f"    {str(e)}")
            raise

        finally:
            await context.close()
            await browser.close()
