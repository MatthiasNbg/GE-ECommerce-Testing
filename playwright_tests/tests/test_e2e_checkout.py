"""
E2E Checkout Tests - Vollstaendiger Checkout mit Neuregistrierung/Login.

TC-E2E-001: 24 parametrisierte Varianten
  - 3 Laender (AT, DE, CH)
  - 3 Zahlungsarten (Vorkasse, Rechnung, Kreditkarte) - CH ohne Rechnung
  - 3 Versandarten (Post, Spedition, Gemischt)
  - 2 Account-Typen (Neuregistrierung, bestehender Account)
"""
import time
from dataclasses import dataclass

import pytest
from playwright.async_api import async_playwright

from ..conftest import accept_cookie_banner_async
from ..config import get_config
from ..pages.account_page import AccountPage, RegistrationData
from ..pages.checkout_page import CheckoutPage, Address, CheckoutResult


# ============================================================================
# Varianten-Matrix
# ============================================================================

@dataclass
class E2EVariant:
    """Eine E2E-Testvariante."""
    variant_id: int
    country: str
    payment_method: str
    shipping_type: str  # "post", "spedition", "mixed"
    account_type: str  # "new", "existing"

    @property
    def test_id(self) -> str:
        return f"E2E-{self.variant_id:02d}-{self.country}-{self.payment_method}-{self.shipping_type}-{self.account_type}"


# Die 24 Varianten gemaess Design-Dokument
E2E_VARIANTS = [
    # AT - Vorkasse (Neu)
    E2EVariant(1, "AT", "prepayment", "post", "new"),
    E2EVariant(2, "AT", "prepayment", "spedition", "new"),
    E2EVariant(3, "AT", "prepayment", "mixed", "new"),
    # AT - Rechnung (Bestehend)
    E2EVariant(4, "AT", "invoice", "post", "existing"),
    E2EVariant(5, "AT", "invoice", "spedition", "existing"),
    E2EVariant(6, "AT", "invoice", "mixed", "existing"),
    # AT - Kreditkarte (gemischt)
    E2EVariant(7, "AT", "credit_card", "post", "new"),
    E2EVariant(8, "AT", "credit_card", "spedition", "existing"),
    E2EVariant(9, "AT", "credit_card", "mixed", "new"),
    # DE - Vorkasse (Bestehend)
    E2EVariant(10, "DE", "prepayment", "post", "existing"),
    E2EVariant(11, "DE", "prepayment", "spedition", "new"),
    E2EVariant(12, "DE", "prepayment", "mixed", "existing"),
    # DE - Rechnung (Neu)
    E2EVariant(13, "DE", "invoice", "post", "new"),
    E2EVariant(14, "DE", "invoice", "spedition", "new"),
    E2EVariant(15, "DE", "invoice", "mixed", "existing"),
    # DE - Kreditkarte (gemischt)
    E2EVariant(16, "DE", "credit_card", "post", "existing"),
    E2EVariant(17, "DE", "credit_card", "spedition", "new"),
    E2EVariant(18, "DE", "credit_card", "mixed", "new"),
    # CH - Vorkasse (gemischt) - KEINE Rechnung in CH
    E2EVariant(19, "CH", "prepayment", "post", "new"),
    E2EVariant(20, "CH", "prepayment", "spedition", "existing"),
    E2EVariant(21, "CH", "prepayment", "mixed", "new"),
    # CH - Kreditkarte (gemischt)
    E2EVariant(22, "CH", "credit_card", "post", "existing"),
    E2EVariant(23, "CH", "credit_card", "spedition", "new"),
    E2EVariant(24, "CH", "credit_card", "mixed", "existing"),
]


def _variant_id(variant: E2EVariant) -> str:
    """Erzeugt eine lesbare Test-ID fuer pytest."""
    return variant.test_id


# ============================================================================
# Produkt-Konfiguration
# ============================================================================

# Post-Produkte nach Land (relative Pfade)
POST_PRODUCTS = {
    "AT": "p/kurzarmshirt-aus-bio-baumwolle/ge-p-862990",
    "DE": "p/kurzarmshirt-aus-bio-baumwolle/ge-p-862990",
    "CH": "p/kurzarmshirt-aus-bio-baumwolle/ge-p-862990",
}

# Speditions-Produkte nach Land
SPEDITION_PRODUCTS = {
    "AT": "p/polsterbett-almeno/ge-p-693278",
    "DE": "p/polsterbett-almeno/ge-p-693278",
    "CH": "p/polsterbett-almeno/ge-p-693278",
}

# Laender-Pfade
COUNTRY_PATHS = {
    "AT": "",
    "DE": "/de-de",
    "CH": "/de-ch",
}

# Gast-Adressen pro Land
GUEST_ADDRESSES = {
    "AT": {"street": "Teststraße 123", "zip": "4020", "city": "Linz"},
    "DE": {"street": "Teststraße 456", "zip": "80331", "city": "München"},
    "CH": {"street": "Teststraße 789", "zip": "8001", "city": "Zürich"},
}


# ============================================================================
# Test
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.e2e
@pytest.mark.checkout
@pytest.mark.parametrize("variant", E2E_VARIANTS, ids=_variant_id)
async def test_e2e_checkout(config, request, variant: E2EVariant):
    """
    TC-E2E-001: Vollstaendiger E2E Checkout.

    Testet den kompletten Bestellprozess:
    1. Neuregistrierung oder Login
    2. Produkt(e) in Warenkorb (Post / Spedition / Gemischt)
    3. Checkout mit gewaehlter Zahlungsart
    4. Bestellbestaetigung pruefen
    """
    start_time = time.time()
    headed = request.config.getoption("--headed", default=False)

    print(f"\n{'='*60}")
    print(f"E2E Variante {variant.variant_id}: {variant.country} | "
          f"{variant.payment_method} | {variant.shipping_type} | {variant.account_type}")
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
            country_path = COUNTRY_PATHS.get(variant.country, "")

            # =================================================================
            # SCHRITT 1: Account vorbereiten
            # =================================================================
            if variant.account_type == "new":
                await _register_new_account(page, base_url, country_path, variant)
            else:
                await _login_existing_account(page, base_url, country_path, variant, config)

            # =================================================================
            # SCHRITT 2: Produkt(e) in den Warenkorb
            # =================================================================
            await _add_products_to_cart(page, base_url, country_path, variant)

            # =================================================================
            # SCHRITT 3: Checkout durchfuehren
            # =================================================================
            result = await _execute_checkout(page, base_url, variant, config)

            # =================================================================
            # SCHRITT 4: Ergebnis pruefen
            # =================================================================
            duration = time.time() - start_time
            print(f"\n--- Ergebnis ---")
            print(f"Erfolg: {result.success}")
            print(f"Bestellnummer: {result.order_number}")
            print(f"Dauer: {duration:.1f}s")

            assert result.success, (
                f"Checkout fehlgeschlagen fuer Variante {variant.test_id}: "
                f"{result.error_message}"
            )
            assert result.order_number, (
                f"Keine Bestellnummer fuer Variante {variant.test_id}"
            )

        finally:
            await context.close()
            await browser.close()


# ============================================================================
# Hilfsfunktionen
# ============================================================================

async def _register_new_account(page, base_url: str, country_path: str, variant: E2EVariant):
    """Registriert einen neuen Account."""
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

    # Unique E-Mail generieren
    timestamp = int(time.time())
    email = f"e2e-{variant.variant_id}-{timestamp}@matthias-sax.de"

    addr = GUEST_ADDRESSES[variant.country]
    data = RegistrationData(
        salutation="mr",
        first_name="E2E",
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


async def _login_existing_account(page, base_url: str, country_path: str, variant: E2EVariant, config):
    """Loggt sich mit einem bestehenden Testaccount ein."""
    print(f"\n[1] Login bestehender Account ({variant.country})...")

    customer = config.get_customer_by_country(variant.country)
    assert customer, f"Kein Testkunde fuer Land {variant.country} konfiguriert"

    password = config.get_customer_password(customer)
    assert password, f"Kein Passwort fuer Testkunde {customer.email}"

    account = AccountPage(page, base_url)
    await page.goto(f"{base_url}{country_path}/account/login", timeout=60000)
    await page.wait_for_load_state("domcontentloaded")
    await account.accept_cookies_if_visible()

    success = await account.login(customer.email, password)
    assert success, f"Login fehlgeschlagen fuer {customer.email}"
    print(f"   Eingeloggt: {customer.email}")


async def _add_products_to_cart(page, base_url: str, country_path: str, variant: E2EVariant):
    """Fuegt Produkte in den Warenkorb je nach Versandart."""
    print(f"\n[2] Produkte zum Warenkorb ({variant.shipping_type})...")

    products_to_add = []

    if variant.shipping_type in ("post", "mixed"):
        product_path = POST_PRODUCTS[variant.country]
        products_to_add.append(("Post", product_path))

    if variant.shipping_type in ("spedition", "mixed"):
        product_path = SPEDITION_PRODUCTS[variant.country]
        products_to_add.append(("Spedition", product_path))

    for label, product_path in products_to_add:
        product_url = f"{base_url}{country_path}/{product_path}"
        print(f"   {label}: {product_path}")
        await page.goto(product_url, timeout=60000)
        await page.wait_for_load_state("domcontentloaded")

        # In den Warenkorb
        add_btn = page.locator("button.btn-buy")
        await add_btn.first.click()
        await page.wait_for_timeout(2000)

        # Offcanvas schliessen falls offen
        offcanvas_close = page.locator(".offcanvas-close, .btn-close, [data-bs-dismiss='offcanvas']")
        if await offcanvas_close.count() > 0:
            try:
                if await offcanvas_close.first.is_visible(timeout=2000):
                    await offcanvas_close.first.click()
                    await page.wait_for_timeout(500)
            except Exception:
                pass

    print(f"   {len(products_to_add)} Produkt(e) hinzugefuegt")


async def _execute_checkout(page, base_url: str, variant: E2EVariant, config) -> CheckoutResult:
    """Fuehrt den Checkout durch."""
    print(f"\n[3] Checkout ({variant.payment_method})...")

    country_path = COUNTRY_PATHS.get(variant.country, "")

    # Zum Warenkorb navigieren
    await page.goto(f"{base_url}{country_path}/checkout/cart", timeout=60000)
    await page.wait_for_load_state("domcontentloaded")
    await page.wait_for_timeout(1000)

    # "Zur Kasse" klicken
    checkout_btn = page.locator("a:has-text('Zur Kasse'), button:has-text('Zur Kasse')")
    if await checkout_btn.count() > 0:
        await checkout_btn.first.click()
        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_timeout(1000)

    checkout = CheckoutPage(page, base_url)

    # Falls wir auf der Register-Seite landen (nicht eingeloggt), ist etwas schiefgegangen
    # Bei eingeloggten Usern sollten wir direkt auf /checkout/confirm sein
    current_url = page.url
    print(f"   Checkout-URL: {current_url}")

    if "checkout/register" in current_url:
        # Wir sind nicht eingeloggt - das sollte bei existing account nicht passieren
        if variant.account_type == "existing":
            print("   WARNUNG: Auf Register-Seite obwohl eingeloggt. Versuche Login im Checkout...")
            customer = config.get_customer_by_country(variant.country)
            password = config.get_customer_password(customer)
            await checkout.login(customer.email, password)
            await page.wait_for_timeout(1000)

    if "checkout/confirm" not in page.url:
        # Noch nicht auf Confirm-Seite - navigiere direkt
        await page.goto(f"{base_url}{country_path}/checkout/confirm", timeout=60000)
        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_timeout(1000)

    # Zahlungsart auswaehlen
    print(f"   Zahlungsart: {variant.payment_method}")
    try:
        await checkout.select_payment_method(variant.payment_method)
    except ValueError as e:
        return CheckoutResult(
            success=False,
            error_message=f"Zahlungsart '{variant.payment_method}' nicht verfuegbar: {e}"
        )

    # Bei Kreditkarte: Kartendaten eingeben (GlobalPayments iFrame)
    if variant.payment_method == "credit_card":
        print("   Kreditkartendaten eingeben (GlobalPayments)...")
        await _fill_credit_card(page, config)

    # AGB akzeptieren
    await checkout.accept_terms()

    # Bestellung absenden
    print("   Bestellung absenden...")
    await checkout.place_order()

    # Auf Bestaetigung warten
    try:
        await checkout.wait_for_confirmation(timeout=60000)
    except Exception as e:
        error_msg = await checkout.get_error_message()
        return CheckoutResult(
            success=False,
            error_message=error_msg or str(e)
        )

    order_number = await checkout.get_order_number()
    order_id = await checkout.get_order_id_from_url()

    return CheckoutResult(
        success=True,
        order_id=order_id,
        order_number=order_number,
    )


async def _fill_credit_card(page, config):
    """
    Fuellt Kreditkartendaten im GlobalPayments iFrame aus.

    TODO: Selektoren muessen an das tatsaechliche GlobalPayments-Widget
    auf dem Staging angepasst werden. Die Selektoren hier sind Platzhalter.
    """
    # GlobalPayments nutzt typischerweise iFrames fuer PCI-Compliance.
    # Die genauen Selektoren haengen vom Widget ab.
    #
    # Typisches Pattern:
    #   1. Auf iFrame warten
    #   2. In den Frame wechseln
    #   3. Kartennummer, Ablaufdatum, CVV eingeben
    #   4. Zurueck zum Hauptframe
    #
    # Platzhalter - muss nach Analyse des Staging angepasst werden:
    try:
        # Warte auf GlobalPayments Widget
        await page.wait_for_timeout(2000)

        # Versuch iFrame zu finden
        # Typische Selektoren: iframe[name*='GlobalPayments'], iframe[src*='globalpayments']
        iframe_locator = page.frame_locator("iframe[name*='GlobalPayments'], iframe[src*='globalpayments'], iframe[id*='credit-card']")

        # Kartennummer
        card_number_input = iframe_locator.locator("input[name='cardNumber'], input[id*='cardNumber'], #credit-card-number")
        if await card_number_input.count() > 0:
            await card_number_input.fill("4111111111111111")  # Standard-Testkarte

        # Ablaufdatum
        expiry_input = iframe_locator.locator("input[name='cardExpiration'], input[id*='expiry'], #credit-card-expiration")
        if await expiry_input.count() > 0:
            await expiry_input.fill("12/27")

        # CVV
        cvv_input = iframe_locator.locator("input[name='cardCvv'], input[id*='cvv'], #credit-card-cvv")
        if await cvv_input.count() > 0:
            await cvv_input.fill("123")

        # Karteninhaber (falls vorhanden)
        name_input = iframe_locator.locator("input[name='cardHolderName'], input[id*='name']")
        if await name_input.count() > 0:
            await name_input.fill("Test Kunde")

        print("   Kreditkartendaten eingegeben")

    except Exception as e:
        print(f"   WARNUNG: Kreditkarten-iFrame konnte nicht befuellt werden: {e}")
        print("   Die Kreditkarten-Selektoren muessen noch an das Staging angepasst werden.")
        # Nicht abbrechen - vielleicht ist die Karte schon vorausgewaehlt
