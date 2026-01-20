"""
PLZ-basierte Speditions-Tests.

Testet, ob fuer verschiedene PLZ-Bereiche die korrekte Spedition
im Checkout angezeigt wird.

WICHTIG: Diese Tests verwenden ein GROSSES PRODUKT (Speditionsware),
da die PLZ-Regeln nur fuer Speditionsversand gelten!

Testprodukt: Polsterbett Almeno (693278)

Ausfuehrung:
    # Alle PLZ-Tests
    pytest playwright_tests/tests/test_shipping_plz.py -v

    # Nur AT-Tests
    pytest playwright_tests/tests/test_shipping_plz.py -v -k "AT"

    # Nur DE-Tests
    pytest playwright_tests/tests/test_shipping_plz.py -v -k "DE"

    # Einzelner Test
    pytest playwright_tests/tests/test_shipping_plz.py -v -k "FINK-MIN"
"""
import pytest
from playwright.sync_api import Page, expect

from ..conftest import accept_cookie_banner
from ..data.shipping_rules import SHIPPING_TEST_CASES


# Testprodukt: Polsterbett Almeno (Speditionsware)
SPEDITION_PRODUCT = "p/polsterbett-almeno/ge-p-693278"


# =============================================================================
# Hilfsfunktionen
# =============================================================================

def add_spedition_product_to_cart(page: Page, base_url: str) -> None:
    """Fuegt das Speditionsprodukt zum Warenkorb hinzu."""
    product_url = f"{base_url}/{SPEDITION_PRODUCT}"
    page.goto(product_url)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)

    # Cookie-Banner akzeptieren
    accept_cookie_banner(page)

    # In den Warenkorb
    add_btn = page.locator("button.btn-buy")
    if add_btn.count() > 0:
        add_btn.first.click()
        page.wait_for_timeout(3000)

    # Offcanvas schliessen falls offen
    offcanvas_close = page.locator(".offcanvas-close, .btn-close, [data-bs-dismiss='offcanvas']")
    if offcanvas_close.count() > 0:
        try:
            if offcanvas_close.first.is_visible(timeout=2000):
                offcanvas_close.first.click()
                page.wait_for_timeout(500)
        except Exception:
            pass


def navigate_to_checkout(page: Page, base_url: str) -> None:
    """Navigiert zum Checkout."""
    page.goto(f"{base_url}/checkout/cart")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)

    # Zur Kasse
    checkout_btn = page.locator("a:has-text('Zur Kasse'), button:has-text('Zur Kasse')")
    checkout_btn.first.click()
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)


def start_guest_checkout(page: Page) -> None:
    """Startet den Gast-Checkout."""
    # Gast-Checkout Button suchen
    guest_btn_selectors = [
        "button:has-text('Als Gast bestellen')",
        "a:has-text('Als Gast bestellen')",
        ".checkout-guest-btn",
        "[data-action='checkout-guest']",
    ]

    for selector in guest_btn_selectors:
        btn = page.locator(selector)
        if btn.count() > 0 and btn.first.is_visible():
            btn.first.click()
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(1000)
            return

    # Fallback: Vielleicht sind wir schon im Gast-Checkout
    if "/checkout/register" in page.url or "/checkout/confirm" in page.url:
        return

    raise Exception("Konnte Gast-Checkout nicht starten")


def fill_address_with_plz(
    page: Page,
    country: str,
    plz: str,
    city: str,
) -> None:
    """
    Fuellt das Adressformular mit der Test-PLZ aus.

    Args:
        page: Playwright Page
        country: Laendercode (AT, DE, CH)
        plz: Postleitzahl
        city: Stadtname
    """
    # Anrede - NUR Rechnungsadresse (nicht Lieferadresse)
    salutation_select = page.locator("#personalSalutation")
    if salutation_select.count() > 0 and salutation_select.is_visible():
        salutation_select.select_option(label="Herr")

    # Vorname (korrekter Selektor aus CheckoutPage)
    first_name = page.locator("#billingAddress-personalFirstName")
    if first_name.count() > 0 and first_name.is_visible():
        first_name.fill("Test")

    # Nachname (korrekter Selektor aus CheckoutPage)
    last_name = page.locator("#billingAddress-personalLastName")
    if last_name.count() > 0 and last_name.is_visible():
        last_name.fill(f"Spedition-{country}-{plz}")

    # Strasse - Rechnungsadresse (korrekter Selektor aus CheckoutPage)
    street = page.locator("#billingAddress-AddressStreet")
    if street.count() > 0 and street.is_visible():
        street.fill("Teststrasse 1")

    # PLZ - DAS WICHTIGSTE! Rechnungsadresse
    zip_code = page.locator("#billingAddressAddressZipcode")
    if zip_code.count() > 0 and zip_code.is_visible():
        zip_code.fill(plz)

    # Stadt - Rechnungsadresse
    city_input = page.locator("#billingAddressAddressCity")
    if city_input.count() > 0 and city_input.is_visible():
        city_input.fill(city)

    # Land - Rechnungsadresse
    # Verschiedene Schreibweisen probieren (mit und ohne Umlaute)
    country_labels = {
        "AT": ["Österreich", "Oesterreich", "Austria"],
        "DE": ["Deutschland", "Germany"],
        "CH": ["Schweiz", "Switzerland"],
    }
    country_select = page.locator("#billingAddressAddressCountry")
    if country_select.count() > 0 and country_select.is_visible():
        labels_to_try = country_labels.get(country, [country])
        selected = False
        for label in labels_to_try:
            try:
                country_select.select_option(label=label, timeout=2000)
                selected = True
                break
            except Exception:
                continue
        if not selected:
            # Fallback: Versuche mit Value (manchmal sind es UUIDs oder ISO-Codes)
            try:
                country_select.select_option(value=country, timeout=2000)
            except Exception:
                # Letzter Fallback: Erstes passendes Land per Text-Suche
                options = country_select.locator("option")
                for i in range(options.count()):
                    opt_text = options.nth(i).inner_text().lower()
                    if any(l.lower() in opt_text for l in labels_to_try):
                        opt_value = options.nth(i).get_attribute("value")
                        if opt_value:
                            country_select.select_option(value=opt_value)
                            break

    # E-Mail
    email = page.locator("#personalMail")
    if email.count() > 0 and email.is_visible():
        email.fill(f"test-{plz}@example.com")

    page.wait_for_timeout(500)


def accept_privacy_and_continue(page: Page) -> None:
    """Akzeptiert Datenschutz und faehrt fort."""
    # Datenschutz-Checkbox (korrekter Selektor aus CheckoutPage)
    privacy_selectors = [
        "#acceptedDataProtection",  # Haupt-Selektor
        "input[name*='privacy']",
        "input[name*='datenschutz']",
        "#tos",
    ]

    for selector in privacy_selectors:
        cb = page.locator(selector)
        if cb.count() > 0 and cb.first.is_visible():
            if not cb.first.is_checked():
                cb.first.check()
            break

    page.wait_for_timeout(500)

    # Weiter-Button
    continue_btn = page.locator("button:has-text('Weiter')")
    if continue_btn.count() > 0 and continue_btn.first.is_visible():
        continue_btn.first.click()
        page.wait_for_load_state("domcontentloaded")
        # Warten auf Navigation zur Confirm-Seite
        try:
            page.wait_for_url("**/checkout/confirm**", timeout=10000)
        except Exception:
            pass
        page.wait_for_timeout(2000)


def get_displayed_shipping_method(page: Page) -> str:
    """
    Liest die angezeigte Versandart aus.

    Returns:
        Text der Versandart oder leerer String
    """
    # Verschiedene Selektoren fuer Versandart-Anzeige
    shipping_selectors = [
        ".shipping-method-label",
        ".shipping-method .method-name",
        ".shipping-method-name",
        "label[for*='shippingMethod']",
        ".checkout-aside-summary-list dt:has-text('Versand') + dd",
        ".shipping-method:checked + label",
        "input[name='shippingMethodId']:checked + label",
    ]

    for selector in shipping_selectors:
        elem = page.locator(selector)
        if elem.count() > 0:
            text = elem.first.inner_text()
            if text and len(text.strip()) > 0:
                return text.strip()

    # Fallback: Alle Versandart-Radio-Labels lesen
    radios = page.locator("input[name='shippingMethodId']")
    for i in range(radios.count()):
        radio = radios.nth(i)
        if radio.is_checked():
            # Label finden
            radio_id = radio.get_attribute("id")
            if radio_id:
                label = page.locator(f"label[for='{radio_id}']")
                if label.count() > 0:
                    return label.first.inner_text().strip()

    return ""


def get_all_shipping_methods(page: Page) -> list[str]:
    """
    Liest alle verfuegbaren Versandarten aus.

    Returns:
        Liste der Versandart-Namen
    """
    methods = []
    radios = page.locator("input[name='shippingMethodId']")

    for i in range(radios.count()):
        radio = radios.nth(i)
        radio_id = radio.get_attribute("id")
        if radio_id:
            label = page.locator(f"label[for='{radio_id}']")
            if label.count() > 0:
                text = label.first.inner_text().strip()
                if text:
                    methods.append(text)

    return methods


# =============================================================================
# Parametrisierte PLZ-Tests
# =============================================================================

@pytest.mark.shipping
@pytest.mark.parametrize(
    "test_id,country,carrier,plz,city,expected_label",
    SHIPPING_TEST_CASES,
    ids=[tc[0] for tc in SHIPPING_TEST_CASES]
)
def test_shipping_method_for_plz(
    page: Page,
    base_url: str,
    test_id: str,
    country: str,
    carrier: str,
    plz: str,
    city: str,
    expected_label: str,
):
    """
    Testet, ob fuer eine bestimmte PLZ die korrekte Spedition angezeigt wird.

    Schritte:
    1. Speditionsprodukt in Warenkorb
    2. Checkout starten
    3. Gast-Checkout waehlen
    4. Adresse mit Test-PLZ eingeben
    5. Zur Confirm-Seite navigieren
    6. Pruefen: Korrekte Spedition wird angezeigt
    """
    print(f"\n=== {test_id} ===")
    print(f"    Land: {country}, PLZ: {plz}, Stadt: {city}")
    print(f"    Erwartete Spedition: {expected_label}")

    # 1. Speditionsprodukt in Warenkorb
    print("[1] Speditionsprodukt in Warenkorb...")
    add_spedition_product_to_cart(page, base_url)

    # 2. Zum Checkout navigieren
    print("[2] Zum Checkout navigieren...")
    navigate_to_checkout(page, base_url)

    # 3. Gast-Checkout starten
    print("[3] Gast-Checkout starten...")
    start_guest_checkout(page)

    # 4. Adresse mit Test-PLZ eingeben
    print(f"[4] Adresse eingeben (PLZ: {plz})...")
    fill_address_with_plz(page, country, plz, city)

    # 5. Datenschutz akzeptieren und weiter
    print("[5] Weiter zur Confirm-Seite...")
    accept_privacy_and_continue(page)

    # Warten auf Confirm-Seite
    page.wait_for_timeout(2000)

    # 6. Versandart pruefen
    print("[6] Versandart pruefen...")

    # Alle verfuegbaren Versandarten ausgeben
    all_methods = get_all_shipping_methods(page)
    print(f"    Verfuegbare Versandarten: {all_methods}")

    # Ausgewaehlte/angezeigte Versandart
    displayed_method = get_displayed_shipping_method(page)
    print(f"    Angezeigte Versandart: '{displayed_method}'")

    # Pruefen ob erwartete Spedition enthalten ist
    # Extrahiere den Carrier-Namen aus expected_label (z.B. "Fink" aus "Spedition Fink")
    # Das Label im Shop ist z.B. "Speditionsversand (Fink AT)"
    carrier_name = expected_label.replace("Spedition ", "").strip()
    carrier_name_lower = carrier_name.lower()

    # Pruefen in angezeigter Methode
    if displayed_method:
        # Suche nach dem Carrier-Namen (z.B. "fink" in "Speditionsversand (Fink AT)")
        method_matches = carrier_name_lower in displayed_method.lower()
    else:
        method_matches = False

    # Pruefen in allen verfuegbaren Methoden
    method_in_list = any(
        carrier_name_lower in m.lower()
        for m in all_methods
    )

    if method_matches:
        print(f"\n    [OK] Korrekte Spedition '{expected_label}' ist ausgewaehlt")
    elif method_in_list:
        print(f"\n    [WARNUNG] Spedition '{expected_label}' ist verfuegbar, aber nicht ausgewaehlt")
        print(f"              Ausgewaehlt ist: '{displayed_method}'")
    else:
        # Screenshot bei Fehler
        page.screenshot(path=f"error_shipping_{test_id}.png")
        print(f"\n    [FEHLER] Spedition '{expected_label}' nicht gefunden!")

    # Assertion
    assert method_matches or method_in_list, (
        f"Spedition '{expected_label}' nicht gefunden fuer PLZ {plz} ({country}).\n"
        f"Angezeigte Versandart: '{displayed_method}'\n"
        f"Verfuegbare Versandarten: {all_methods}"
    )


# =============================================================================
# Einzelne Tests fuer schnelles Debugging
# =============================================================================

@pytest.mark.shipping
def test_shipping_single_at_fink(page: Page, base_url: str):
    """Schnelltest: AT PLZ 4020 (Linz) -> Spedition Fink."""
    test_shipping_method_for_plz(
        page, base_url,
        test_id="QUICK-AT-FINK",
        country="AT",
        carrier="Fink AT",
        plz="4020",
        city="Linz",
        expected_label="Spedition Fink",
    )


@pytest.mark.shipping
def test_shipping_single_de_logsens(page: Page, base_url: str):
    """Schnelltest: DE PLZ 80331 (Muenchen) -> Spedition Logsens."""
    test_shipping_method_for_plz(
        page, base_url,
        test_id="QUICK-DE-LOGSENS",
        country="DE",
        carrier="Logsens Sued",
        plz="80331",
        city="Muenchen",
        expected_label="Spedition Logsens",
    )
