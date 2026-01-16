"""
Test zur Validierung der verfügbaren Zahlungsarten für Gast-User.

Dieser Test prüft, dass alle in der config.yaml definierten Zahlungsarten
auch tatsächlich im Shop für Gast-Checkout verfügbar sind.

Usage:
    pytest playwright_tests/tests/test_payment_methods_available.py -v
    pytest playwright_tests/tests/test_payment_methods_available.py::test_payment_methods_available[AT] -v
"""
import pytest
from playwright.sync_api import Page
from playwright_tests.config import TestConfig


def add_product_and_navigate_to_checkout(page: Page, base_url: str, product_path: str) -> None:
    """
    Hilfsfunktion: Fügt Produkt hinzu und navigiert zum Checkout.

    Args:
        page: Playwright Page-Objekt
        base_url: Basis-URL des Shops
        product_path: Produktpfad (z.B. "p/kurzarmshirt/ge-p-862990")
    """
    # Produktseite aufrufen
    page.goto(f"{base_url}/{product_path}")
    page.wait_for_load_state("domcontentloaded")

    # Zum Warenkorb hinzufügen
    add_to_cart_button = page.locator(".btn-buy, [data-add-to-cart]")
    add_to_cart_button.first.click()
    page.wait_for_timeout(2000)

    # Zur Checkout-Register-Seite navigieren
    page.goto(f"{base_url}/checkout/register")
    page.wait_for_load_state("domcontentloaded")


def complete_guest_checkout_form(page: Page, country_code: str) -> None:
    """
    Füllt Gast-Checkout-Formular aus.

    Args:
        page: Playwright Page-Objekt
        country_code: Ländercode (AT, DE, CH)
    """
    # Cookie-Banner schließen
    cookie_button = page.locator("button.cookie-notice-accept, button[data-cookie-permission-button]")
    if cookie_button.count() > 0:
        cookie_button.first.click()
        page.wait_for_timeout(500)

    # Gast-Checkout aktivieren
    guest_button = page.locator(
        "[data-toggle='collapse'][href='#collapseGuestCheckout'], "
        ".register-guest, "
        "button:has-text('Als Gast bestellen')"
    )
    if guest_button.count() > 0:
        guest_button.first.click(force=True)
        page.wait_for_timeout(1000)

    # Testdaten basierend auf Land
    test_data = {
        "AT": {
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "street": "Teststraße 1",
            "zip": "4020",
            "city": "Linz",
            "country": "AT"
        },
        "DE": {
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "street": "Teststraße 1",
            "zip": "10115",
            "city": "Berlin",
            "country": "DE"
        },
        "CH": {
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "street": "Teststrasse 1",
            "zip": "8001",
            "city": "Zürich",
            "country": "CH"
        }
    }

    data = test_data.get(country_code, test_data["AT"])

    # Gast-Container finden und Formular ausfüllen
    guest_container = page.locator("#collapseGuestCheckout, #guest, .register-form").first
    guest_container.locator("input[name*='firstName'], #personalFirstName").first.wait_for(
        state="visible", timeout=10000
    )

    # Formular ausfüllen
    guest_container.locator("input[name*='firstName'], #personalFirstName").first.fill(data["first_name"])
    guest_container.locator("input[name*='lastName'], #personalLastName").first.fill(data["last_name"])
    guest_container.locator("input[name*='email'], input[type='email']").first.fill(data["email"])
    guest_container.locator("input[name*='street'], input[name*='addressStreet']").first.fill(data["street"])
    guest_container.locator("input[name*='zipcode'], input[name*='postalCode']").first.fill(data["zip"])
    guest_container.locator("input[name*='city']").first.fill(data["city"])

    # Anrede (Pflichtfeld)
    salutation = guest_container.locator("select[name*='salutation'], #personalSalutation")
    if salutation.count() > 0:
        try:
            salutation.first.select_option(label="Herr", timeout=2000)
        except:
            salutation.first.select_option("mr", timeout=2000)

    # Land
    country_select = guest_container.locator("select[name*='country']")
    if country_select.count() > 0:
        try:
            country_select.first.select_option(data["country"], timeout=2000)
        except:
            pass  # Land bereits vorausgewählt

    # Pflicht-Checkboxen aktivieren
    checkboxes = page.locator("input[type='checkbox'][required], input[type='checkbox'][aria-required='true']")
    for i in range(checkboxes.count()):
        checkbox = checkboxes.nth(i)
        if not checkbox.is_checked():
            checkbox.check()

    # Weiter-Button klicken
    continue_button = page.locator("button[type='submit']:visible").filter(has_text="Weiter")
    if continue_button.count() == 0:
        continue_button = page.locator("button[type='submit']:visible")

    for i in range(continue_button.count()):
        button = continue_button.nth(i)
        if button.is_visible():
            button_text = button.inner_text()
            if "Weiter" in button_text or "weiter" in button_text:
                button.click()
                page.wait_for_load_state("domcontentloaded")
                page.wait_for_timeout(2000)
                break


def extract_available_payment_methods(page: Page) -> list[str]:
    """
    Extrahiert verfügbare Zahlungsarten von der Checkout-Confirm-Seite.

    Args:
        page: Playwright Page-Objekt

    Returns:
        Liste der Zahlungsarten-Labels
    """
    payment_labels = page.locator(".payment-method-label strong").all_inner_texts()
    return [label.strip() for label in payment_labels if label.strip()]


@pytest.mark.parametrize("country_code", ["AT", "DE", "CH"])
def test_payment_methods_available(page: Page, config: TestConfig, country_code: str):
    """
    Testet, dass alle konfigurierten Zahlungsarten für Gast-User verfügbar sind.

    Durchläuft für jedes Land:
    1. Produkt zum Warenkorb hinzufügen
    2. Gast-Checkout-Formular ausfüllen
    3. Zur Zahlungsarten-Seite navigieren
    4. Verfügbare Zahlungsarten extrahieren
    5. Gegen config.yaml validieren

    Args:
        page: Playwright Page-Objekt
        config: TestConfig-Objekt
        country_code: Ländercode (AT, DE, CH)
    """
    # Skip wenn keine Zahlungsarten für dieses Land konfiguriert sind
    if not config.payment_methods or country_code not in config.payment_methods:
        pytest.skip(f"Keine Zahlungsarten für {country_code} in config.yaml konfiguriert")

    expected_methods = config.payment_methods[country_code]
    if not expected_methods:
        pytest.skip(f"Keine Zahlungsarten für {country_code} definiert")

    # Country-spezifische URL
    country_path = config.country_paths.get(country_code, "/")
    base_url = f"{config.base_url}{country_path}".rstrip("/")

    print(f"\n[Test] Prüfe Zahlungsarten für {country_code}")
    print(f"[Test] URL: {base_url}")
    print(f"[Test] Erwartete Zahlungsarten: {expected_methods}")

    # Testprodukt zum Warenkorb hinzufügen
    test_product = config.test_products[0] if config.test_products else "p/kurzarmshirt-aus-bio-baumwolle/ge-p-862990"
    add_product_and_navigate_to_checkout(page, base_url, test_product)

    # Gast-Checkout durchlaufen
    complete_guest_checkout_form(page, country_code)

    # Prüfen, dass wir auf der Checkout-Confirm-Seite sind
    assert "/checkout/confirm" in page.url, f"Nicht auf Zahlungsarten-Seite gelandet: {page.url}"

    # Verfügbare Zahlungsarten extrahieren
    available_methods = extract_available_payment_methods(page)
    print(f"[Test] Gefundene Zahlungsarten: {available_methods}")

    # Validierung: Alle erwarteten Zahlungsarten müssen verfügbar sein
    missing_methods = [method for method in expected_methods if method not in available_methods]

    assert len(missing_methods) == 0, (
        f"Fehlende Zahlungsarten für {country_code}: {missing_methods}\n"
        f"Erwartet: {expected_methods}\n"
        f"Gefunden: {available_methods}"
    )

    print(f"[Test] Alle erwarteten Zahlungsarten für {country_code} verfügbar")
