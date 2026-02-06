"""
Versandkosten-Validierung fuer Speditionsartikel (AT/DE).

Testet, ob die Versandkosten fuer Speditionsartikel im Gast-Checkout
korrekt berechnet werden. Die Formel lautet:
    versandkosten = max(50, min(450, warenwert * 0.03))

D.h. 3% des Warenwertes, geclampt auf 50 EUR (min) bis 450 EUR (max).

Testprodukt: Polsterbett Almeno (693278)

Ausfuehrung:
    # Alle Versandkosten-Tests
    pytest playwright_tests/tests/test_shipping_cost_spedition.py -v

    # Nur AT-Tests
    pytest playwright_tests/tests/test_shipping_cost_spedition.py -v -k "AT"

    # Nur DE-Tests
    pytest playwright_tests/tests/test_shipping_cost_spedition.py -v -k "DE"
"""
import re

import pytest
from playwright.sync_api import Page

from ..conftest import accept_cookie_banner


# Testprodukt: Polsterbett Almeno (Speditionsware)
SPEDITION_PRODUCT = "p/polsterbett-almeno/ge-p-693278"

# Versandkosten-Grenzen
MIN_SHIPPING = 50.0
MAX_SHIPPING = 450.0
SHIPPING_RATE = 0.03  # 3%

# Laender-Pfade (AT = root, DE = /de-de)
COUNTRY_PATHS = {
    "AT": "",
    "DE": "/de-de",
}


# =============================================================================
# Hilfsfunktionen (wiederverwendet aus test_shipping_plz.py)
# =============================================================================

def add_spedition_product_to_cart(page: Page, base_url: str, quantity: int = 1) -> None:
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


def set_cart_quantity(page: Page, base_url: str, quantity: int) -> None:
    """Setzt die Menge im Warenkorb auf der Cart-Seite."""
    page.goto(f"{base_url}/checkout/cart")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)

    qty_input = page.locator("input[name='quantity'], input.quantity-input")
    if qty_input.count() > 0 and qty_input.first.is_visible():
        qty_input.first.fill(str(quantity))
        # Change-Event ausloesen damit Shopware die Aenderung uebernimmt
        qty_input.first.press("Enter")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)


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

    if "/checkout/register" in page.url or "/checkout/confirm" in page.url:
        return

    raise Exception("Konnte Gast-Checkout nicht starten")


def fill_address_with_plz(page: Page, country: str, plz: str, city: str) -> None:
    """Fuellt das Adressformular mit der Test-PLZ aus."""
    # Anrede
    salutation_select = page.locator("#personalSalutation")
    if salutation_select.count() > 0 and salutation_select.is_visible():
        salutation_select.select_option(label="Herr")

    # Vorname
    first_name = page.locator("#billingAddress-personalFirstName")
    if first_name.count() > 0 and first_name.is_visible():
        first_name.fill("Test")

    # Nachname
    last_name = page.locator("#billingAddress-personalLastName")
    if last_name.count() > 0 and last_name.is_visible():
        last_name.fill(f"Versandkosten-{country}-{plz}")

    # Strasse
    street = page.locator("#billingAddress-AddressStreet")
    if street.count() > 0 and street.is_visible():
        street.fill("Teststrasse 1")

    # PLZ
    zip_code = page.locator("#billingAddressAddressZipcode")
    if zip_code.count() > 0 and zip_code.is_visible():
        zip_code.fill(plz)

    # Stadt
    city_input = page.locator("#billingAddressAddressCity")
    if city_input.count() > 0 and city_input.is_visible():
        city_input.fill(city)

    # Land
    country_labels = {
        "AT": ["Österreich", "Oesterreich", "Austria"],
        "DE": ["Deutschland", "Germany"],
    }
    country_select = page.locator("#billingAddressAddressCountry")
    if country_select.count() > 0 and country_select.is_visible():
        labels_to_try = country_labels.get(country, [country])
        for label in labels_to_try:
            try:
                country_select.select_option(label=label, timeout=2000)
                break
            except Exception:
                continue

    # E-Mail
    email = page.locator("#personalMail")
    if email.count() > 0 and email.is_visible():
        email.fill(f"test-versandkosten-{plz}@example.com")

    page.wait_for_timeout(500)


def accept_privacy_and_continue(page: Page) -> None:
    """Akzeptiert Datenschutz und faehrt fort."""
    privacy_selectors = [
        "#acceptedDataProtection",
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

    continue_btn = page.locator("button:has-text('Weiter')")
    if continue_btn.count() > 0 and continue_btn.first.is_visible():
        continue_btn.first.click()
        page.wait_for_load_state("domcontentloaded")
        try:
            page.wait_for_url("**/checkout/confirm**", timeout=10000)
        except Exception:
            pass
        page.wait_for_timeout(2000)


def parse_euro_amount(text: str) -> float:
    """
    Parst einen Euro-Betrag aus einem Text.

    Unterstuetzte Formate:
    - "123,45 EUR"
    - "1.234,56 EUR"
    - "EUR 123,45"
    - "123,45"
    - Negativ: "-123,45 EUR"

    Returns:
        Betrag als float
    """
    # Entferne Whitespace und EUR
    cleaned = text.strip().replace("EUR", "").replace("€", "").strip()
    # Entferne Tausendertrennzeichen (Punkt) und ersetze Komma durch Punkt
    cleaned = cleaned.replace(".", "").replace(",", ".")
    # Entferne Sternchen und sonstige Zeichen
    cleaned = re.sub(r"[^\d.,\-]", "", cleaned)
    return float(cleaned)


def get_shipping_cost(page: Page) -> float:
    """Liest die Versandkosten von der Checkout-Confirm-Seite."""
    shipping_elem = page.locator(
        ".checkout-aside-summary-list dt:has-text('Versandkosten') + dd"
    )
    if shipping_elem.count() > 0:
        text = shipping_elem.first.inner_text()
        print(f"    Versandkosten-Text: '{text}'")
        return parse_euro_amount(text)

    raise Exception("Versandkosten konnten nicht ausgelesen werden")


def get_subtotal(page: Page) -> float:
    """Liest den Warenwert (Zwischensumme) von der Checkout-Confirm-Seite."""
    subtotal_elem = page.locator(".checkout-aside-summary-value:first-of-type")
    if subtotal_elem.count() > 0:
        text = subtotal_elem.first.inner_text()
        print(f"    Warenwert-Text: '{text}'")
        return parse_euro_amount(text)

    raise Exception("Warenwert konnte nicht ausgelesen werden")


def calculate_expected_shipping(subtotal: float) -> float:
    """Berechnet die erwarteten Versandkosten: max(50, min(450, warenwert * 0.03))"""
    return max(MIN_SHIPPING, min(MAX_SHIPPING, subtotal * SHIPPING_RATE))


# =============================================================================
# Parametrisierte Versandkosten-Tests
# =============================================================================

SHIPPING_COST_TEST_CASES = [
    # (test_id, country, plz, city, quantity)
    ("TC-SHIP-COST-AT-001", "AT", "4020", "Linz", 1),
    ("TC-SHIP-COST-AT-002", "AT", "4020", "Linz", 5),
    ("TC-SHIP-COST-DE-001", "DE", "80331", "Muenchen", 1),
    ("TC-SHIP-COST-DE-002", "DE", "80331", "Muenchen", 5),
]


@pytest.mark.shipping
@pytest.mark.parametrize(
    "test_id,country,plz,city,quantity",
    SHIPPING_COST_TEST_CASES,
    ids=[tc[0] for tc in SHIPPING_COST_TEST_CASES],
)
def test_shipping_cost_spedition(
    page: Page,
    base_url: str,
    test_id: str,
    country: str,
    plz: str,
    city: str,
    quantity: int,
):
    """
    Testet, ob die Versandkosten fuer Speditionsartikel korrekt berechnet werden.

    Formel: versandkosten = max(50, min(450, warenwert * 0.03))

    Schritte:
    1. Speditionsprodukt in gewuenschter Menge in Warenkorb
    2. Checkout starten (Gast)
    3. Adresse eingeben
    4. Auf Confirm-Seite: Warenwert und Versandkosten auslesen
    5. Validieren: versandkosten == max(50, min(450, warenwert * 0.03))
    """
    # Laenderpfad anpassen (DE hat /de-de Prefix)
    country_path = COUNTRY_PATHS.get(country, "")
    effective_base_url = f"{base_url}{country_path}"

    print(f"\n=== {test_id} ===")
    print(f"    Land: {country}, PLZ: {plz}, Stadt: {city}, Menge: {quantity}")
    print(f"    Base-URL: {effective_base_url}")

    # 1. Speditionsprodukt in Warenkorb
    print(f"[1] Speditionsprodukt in Warenkorb (Menge: {quantity})...")
    add_spedition_product_to_cart(page, effective_base_url)

    # 1b. Menge im Warenkorb anpassen falls > 1
    if quantity > 1:
        print(f"[1b] Menge im Warenkorb auf {quantity} setzen...")
        set_cart_quantity(page, effective_base_url, quantity)

    # 2. Zum Checkout navigieren
    print("[2] Zum Checkout navigieren...")
    navigate_to_checkout(page, effective_base_url)

    # 3. Gast-Checkout starten
    print("[3] Gast-Checkout starten...")
    start_guest_checkout(page)

    # 4. Adresse eingeben
    print(f"[4] Adresse eingeben (PLZ: {plz}, Land: {country})...")
    fill_address_with_plz(page, country, plz, city)

    # 5. Datenschutz akzeptieren und weiter
    print("[5] Weiter zur Confirm-Seite...")
    accept_privacy_and_continue(page)

    # Warten auf Confirm-Seite
    page.wait_for_timeout(2000)

    # 6. Warenwert und Versandkosten auslesen
    print("[6] Warenwert und Versandkosten auslesen...")
    subtotal = get_subtotal(page)
    shipping_cost = get_shipping_cost(page)
    expected_shipping = calculate_expected_shipping(subtotal)

    print(f"    Warenwert: {subtotal:.2f} EUR")
    print(f"    Versandkosten (angezeigt): {shipping_cost:.2f} EUR")
    print(f"    Versandkosten (erwartet):  {expected_shipping:.2f} EUR")
    print(f"    Formel: max({MIN_SHIPPING}, min({MAX_SHIPPING}, {subtotal:.2f} * {SHIPPING_RATE})) = {expected_shipping:.2f}")

    # 7. Validierung
    # Toleranz von 1 Cent fuer Rundungsdifferenzen
    tolerance = 0.01
    diff = abs(shipping_cost - expected_shipping)

    if diff <= tolerance:
        print(f"\n    [OK] Versandkosten korrekt: {shipping_cost:.2f} EUR")
    else:
        page.screenshot(path=f"error_shipping_cost_{test_id}.png")
        print(f"\n    [FEHLER] Versandkosten weichen ab!")
        print(f"    Differenz: {diff:.2f} EUR")

    assert diff <= tolerance, (
        f"Versandkosten fuer {test_id} weichen ab.\n"
        f"Warenwert: {subtotal:.2f} EUR\n"
        f"Erwartet: {expected_shipping:.2f} EUR "
        f"(max({MIN_SHIPPING}, min({MAX_SHIPPING}, {subtotal:.2f} * {SHIPPING_RATE})))\n"
        f"Angezeigt: {shipping_cost:.2f} EUR\n"
        f"Differenz: {diff:.2f} EUR"
    )
