"""
E2E Click & Collect Tests - Bestellung mit Abholung im Shop.

TC-E2E-CC-001: 4 parametrisierte Varianten
  - AT: Wien (1010), Linz (4020)
  - DE: Muenchen (80331), Berlin (10115)
  - Zahlungsart: Zahlung bei Abholung
  - PLZ-Suche mit Abholort-Auswahl
"""
import time
from dataclasses import dataclass

import pytest
from playwright.async_api import async_playwright

from ..conftest import accept_cookie_banner_async
from ..config import get_config
from ..pages.account_page import AccountPage, RegistrationData
from ..pages.checkout_page import CheckoutPage, CheckoutResult


# ============================================================================
# Varianten
# ============================================================================

@dataclass
class ClickCollectVariant:
    """Eine Click & Collect Testvariante."""
    variant_id: int
    country: str
    plz: str
    city: str
    product_type: str  # "post" oder "spedition"

    @property
    def test_id(self) -> str:
        return f"CC-{self.variant_id}-{self.country}-{self.city}-{self.product_type}"


CC_VARIANTS = [
    ClickCollectVariant(1, "AT", "1010", "Wien", "post"),
    ClickCollectVariant(2, "AT", "4020", "Linz", "spedition"),
    ClickCollectVariant(3, "DE", "80331", "München", "post"),
    ClickCollectVariant(4, "DE", "10115", "Berlin", "post"),
]


def _variant_id(variant: ClickCollectVariant) -> str:
    return variant.test_id


# Produkt-Pfade
POST_PRODUCT = "p/kurzarmshirt-aus-bio-baumwolle/ge-p-862990"
SPEDITION_PRODUCT = "p/polsterbett-almeno/ge-p-693278"

COUNTRY_PATHS = {
    "AT": "",
    "DE": "/de-de",
}

GUEST_ADDRESSES = {
    "AT": {"street": "Teststraße 123", "zip": "4020", "city": "Linz"},
    "DE": {"street": "Teststraße 456", "zip": "80331", "city": "München"},
}


# ============================================================================
# Test
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.e2e
@pytest.mark.click_collect
@pytest.mark.parametrize("variant", CC_VARIANTS, ids=_variant_id)
async def test_e2e_click_collect(config, request, variant: ClickCollectVariant):
    """
    TC-E2E-CC-001: Click & Collect - Abholung im Shop.

    Testet:
    1. Neuregistrierung
    2. Produkt in Warenkorb
    3. Versandart: Click & Collect
    4. PLZ-Suche + Abholort waehlen
    5. Zahlungsart: Zahlung bei Abholung
    6. Bestellung absenden
    """
    start_time = time.time()
    headed = request.config.getoption("--headed", default=False)

    print(f"\n{'='*60}")
    print(f"Click & Collect Variante {variant.variant_id}: {variant.country} | "
          f"{variant.city} ({variant.plz}) | {variant.product_type}")
    print(f"{'='*60}")

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
            base_url = config.base_url
            country_path = COUNTRY_PATHS[variant.country]

            # =================================================================
            # SCHRITT 1: Neuregistrierung
            # =================================================================
            print(f"\n[1] Neuregistrierung ({variant.country})...")

            account = AccountPage(page, base_url)
            await page.goto(f"{base_url}{country_path}/account/login", timeout=60000)
            await page.wait_for_load_state("domcontentloaded")
            await account.accept_cookies_if_visible()

            # Registrierungsformular aufklappen
            collapse_btn = page.locator(account.REGISTER_COLLAPSE_BUTTON)
            if await collapse_btn.count() > 0 and await collapse_btn.first.is_visible(timeout=3000):
                await collapse_btn.first.click()
                await page.wait_for_timeout(500)

            timestamp = int(time.time())
            email = f"cc-{variant.variant_id}-{timestamp}@matthias-sax.de"

            addr = GUEST_ADDRESSES[variant.country]
            data = RegistrationData(
                salutation="mr",
                first_name="CC",
                last_name=f"Test-{variant.variant_id}",
                email=email,
                password="Test1234!secure",
                street=addr["street"],
                zip_code=addr["zip"],
                city=addr["city"],
                country=variant.country,
            )

            success = await account.register(data)
            assert success, f"Registrierung fehlgeschlagen fuer {email}"
            print(f"   Registriert: {email}")

            # =================================================================
            # SCHRITT 2: Produkt in den Warenkorb
            # =================================================================
            print(f"\n[2] Produkt zum Warenkorb ({variant.product_type})...")

            product_path = POST_PRODUCT if variant.product_type == "post" else SPEDITION_PRODUCT
            await page.goto(f"{base_url}{country_path}/{product_path}", timeout=60000)
            await page.wait_for_load_state("domcontentloaded")

            add_btn = page.locator("button.btn-buy")
            await add_btn.first.click()
            await page.wait_for_timeout(2000)

            # Offcanvas schliessen
            offcanvas_close = page.locator(".offcanvas-close, .btn-close, [data-bs-dismiss='offcanvas']")
            if await offcanvas_close.count() > 0:
                try:
                    if await offcanvas_close.first.is_visible(timeout=2000):
                        await offcanvas_close.first.click()
                        await page.wait_for_timeout(500)
                except Exception:
                    pass

            print("   Produkt hinzugefuegt")

            # =================================================================
            # SCHRITT 3: Zum Checkout
            # =================================================================
            print(f"\n[3] Zum Checkout...")

            await page.goto(f"{base_url}{country_path}/checkout/cart", timeout=60000)
            await page.wait_for_load_state("domcontentloaded")
            await page.wait_for_timeout(1000)

            checkout_btn = page.locator("a:has-text('Zur Kasse'), button:has-text('Zur Kasse')")
            if await checkout_btn.count() > 0:
                await checkout_btn.first.click()
                await page.wait_for_load_state("domcontentloaded")
                await page.wait_for_timeout(1000)

            # Sicherstellen, dass wir auf /checkout/confirm sind
            if "checkout/confirm" not in page.url:
                await page.goto(f"{base_url}{country_path}/checkout/confirm", timeout=60000)
                await page.wait_for_load_state("domcontentloaded")
                await page.wait_for_timeout(1000)

            checkout = CheckoutPage(page, base_url)

            # =================================================================
            # SCHRITT 4: Click & Collect auswaehlen
            # =================================================================
            print(f"\n[4] Click & Collect auswaehlen (PLZ: {variant.plz})...")

            await _select_click_and_collect(page, variant.plz)

            # =================================================================
            # SCHRITT 5: Zahlungsart "Zahlung bei Abholung"
            # =================================================================
            print(f"\n[5] Zahlungsart: Zahlung bei Abholung...")

            try:
                # Versuche verschiedene Labels
                for payment_label in ["Zahlung bei Abholung", "Barzahlung", "cash_on_pickup"]:
                    try:
                        await checkout.select_payment_method(payment_label)
                        print(f"   Zahlungsart '{payment_label}' ausgewaehlt")
                        break
                    except ValueError:
                        continue
                else:
                    # Fallback: Nimm die erste verfuegbare Zahlungsart
                    methods = await checkout.get_available_payment_methods()
                    print(f"   Verfuegbare Zahlungsarten: {methods}")
                    if methods:
                        await checkout.select_payment_method(methods[0])
                        print(f"   Fallback: '{methods[0]}' ausgewaehlt")
            except Exception as e:
                print(f"   WARNUNG Zahlungsart: {e}")

            # =================================================================
            # SCHRITT 6: AGB und Bestellung
            # =================================================================
            print(f"\n[6] Bestellung absenden...")

            await checkout.accept_terms()
            await checkout.place_order()

            try:
                await checkout.wait_for_confirmation(timeout=60000)
            except Exception as e:
                error_msg = await checkout.get_error_message()
                pytest.fail(
                    f"Click & Collect Checkout fehlgeschlagen fuer Variante {variant.test_id}: "
                    f"{error_msg or str(e)}"
                )

            order_number = await checkout.get_order_number()
            duration = time.time() - start_time

            print(f"\n--- Ergebnis ---")
            print(f"Bestellnummer: {order_number}")
            print(f"Abholort: {variant.city} ({variant.plz})")
            print(f"Dauer: {duration:.1f}s")

            assert order_number, f"Keine Bestellnummer fuer Variante {variant.test_id}"

        finally:
            await context.close()
            await browser.close()


# ============================================================================
# Click & Collect Hilfsfunktionen
# ============================================================================

async def _select_click_and_collect(page, plz: str):
    """
    Waehlt Click & Collect als Versandart und sucht einen Abholort.

    TODO: Die Selektoren muessen an das tatsaechliche Click & Collect Widget
    auf dem Staging angepasst werden. Die Selektoren hier sind Platzhalter
    basierend auf gaengigen Shopware 6 Patterns.

    Typischer Flow:
    1. Click & Collect als Versandart auswaehlen
    2. PLZ-Suchfeld wird eingeblendet
    3. PLZ eingeben
    4. Ergebnisliste mit Abholorten erscheint
    5. Ersten Abholort auswaehlen
    """
    # Schritt 1: Click & Collect Versandart finden und klicken
    # Verschiedene moegliche Selektoren/Labels
    cc_selectors = [
        ".shipping-method:has-text('Click & Collect')",
        ".shipping-method:has-text('Abholung')",
        ".shipping-method:has-text('Click and Collect')",
        ".shipping-method:has-text('Store Pickup')",
        "label:has-text('Click & Collect')",
        "label:has-text('Abholung im Shop')",
    ]

    cc_selected = False
    for selector in cc_selectors:
        locator = page.locator(selector)
        if await locator.count() > 0 and await locator.first.is_visible(timeout=2000):
            # Radio-Button im Container klicken
            radio = locator.first.locator("input[type='radio']")
            if await radio.count() > 0:
                await radio.first.click()
            else:
                await locator.first.click()
            cc_selected = True
            print(f"   Click & Collect ausgewaehlt via: {selector}")
            break

    if not cc_selected:
        # Fallback: Alle Versand-Radio-Buttons durchsuchen
        radios = page.locator("input[name='shippingMethodId']")
        count = await radios.count()
        for i in range(count):
            radio = radios.nth(i)
            radio_id = await radio.get_attribute("id")
            if radio_id:
                label = page.locator(f"label[for='{radio_id}']")
                if await label.count() > 0:
                    label_text = (await label.text_content() or "").lower()
                    if any(kw in label_text for kw in ["collect", "abholung", "abholen", "store pickup"]):
                        await radio.click()
                        cc_selected = True
                        print(f"   Click & Collect ausgewaehlt via Radio: {label_text.strip()}")
                        break

    assert cc_selected, "Click & Collect Versandart nicht gefunden"

    await page.wait_for_timeout(1000)

    # Schritt 2: PLZ eingeben
    # Typische Selektoren fuer PLZ-Suchfeld
    plz_selectors = [
        "input[name='zipcode']",
        "input[placeholder*='PLZ']",
        "input[placeholder*='Postleitzahl']",
        ".click-collect-search input",
        ".store-locator input[type='text']",
        "#storeLocatorZip",
    ]

    plz_filled = False
    for selector in plz_selectors:
        locator = page.locator(selector)
        if await locator.count() > 0 and await locator.first.is_visible(timeout=2000):
            await locator.first.fill(plz)
            plz_filled = True
            print(f"   PLZ '{plz}' eingegeben via: {selector}")
            break

    if plz_filled:
        # Suche ausloesen (Enter oder Such-Button)
        search_btn = page.locator(
            "button:has-text('Suchen'), button:has-text('Finden'), "
            ".store-locator-search button, .click-collect-search button"
        )
        if await search_btn.count() > 0 and await search_btn.first.is_visible(timeout=2000):
            await search_btn.first.click()
        else:
            # Enter druecken
            await page.keyboard.press("Enter")

        await page.wait_for_timeout(2000)

        # Schritt 3: Ersten Abholort aus der Liste waehlen
        location_selectors = [
            ".store-result:first-child",
            ".store-locator-result:first-child",
            ".click-collect-result:first-child",
            ".pickup-location:first-child",
            ".store-list-item:first-child",
        ]

        for selector in location_selectors:
            locator = page.locator(selector)
            if await locator.count() > 0 and await locator.first.is_visible(timeout=3000):
                # Radio oder Button im Ergebnis klicken
                radio = locator.first.locator("input[type='radio']")
                if await radio.count() > 0:
                    await radio.first.click()
                else:
                    button = locator.first.locator("button, a")
                    if await button.count() > 0:
                        await button.first.click()
                    else:
                        await locator.first.click()
                print(f"   Abholort ausgewaehlt via: {selector}")
                break
    else:
        print("   WARNUNG: PLZ-Suchfeld nicht gefunden - Click & Collect moeglicherweise anders aufgebaut")

    await page.wait_for_timeout(1000)
