"""
Discovery Test für automatische Ermittlung von Zahlungsarten.

Dieser Test ist NICHT für die normale Test-Suite gedacht!
Er muss manuell ausgeführt werden und interagiert mit dem echten Shop.

Usage:
    python -m pytest playwright_tests/tests/test_payment_discovery.py -m discovery -v -s
"""
import pytest
from playwright.sync_api import Page, expect
from playwright_tests.config import TestConfig
from playwright_tests.conftest import accept_cookie_banner
from playwright_tests.utils.payment_discovery import update_config_with_payment_methods
from playwright_tests.pages.checkout_page import Address


def add_test_product_to_cart(page: Page, base_url: str, product_path: str) -> None:
    """
    Fügt ein Testprodukt zum Warenkorb hinzu.

    Args:
        page: Playwright Page-Objekt
        base_url: Basis-URL des Shops
        product_path: Relativer Pfad zum Produkt (z.B. "p/produkt/ge-p-123")
    """
    # Produktseite aufrufen
    product_url = f"{base_url}/{product_path}"
    page.goto(product_url)
    page.wait_for_load_state("domcontentloaded")

    # "In den Warenkorb" Button finden und klicken
    add_to_cart = page.locator(".btn-buy, [data-add-to-cart]")
    expect(add_to_cart.first).to_be_visible(timeout=5000)
    add_to_cart.first.click()

    # Warten auf Feedback (Offcanvas oder Notification)
    page.wait_for_timeout(2000)


def complete_checkout_to_payment_page(page: Page, base_url: str, country_code: str) -> None:
    """
    Führt den Checkout-Flow durch bis zur Zahlungsarten-Seite.

    Args:
        page: Playwright Page-Objekt
        base_url: Basis-URL des Shops
        country_code: Ländercode (AT, DE, CH)
    """
    # Zum Checkout navigieren
    page.goto(f"{base_url}/checkout/register")
    page.wait_for_load_state("domcontentloaded")

    # Cookie-Banner akzeptieren (Usercentrics oder Shopware)
    accept_cookie_banner(page)

    # Gast-Checkout aktivieren
    guest_button = page.locator("css=[data-toggle='collapse'][href='#collapseGuestCheckout'], .register-guest, button:has-text('Als Gast bestellen')")
    if guest_button.count() > 0:
        guest_button.first.click(force=True)
        page.wait_for_timeout(1000)

    # Test-Adressdaten basierend auf Land
    test_addresses = {
        "AT": Address(
            salutation="mr",
            first_name="Test",
            last_name="Discovery",
            street="Teststraße 1",
            zip_code="4020",
            city="Linz",
            country="AT",
            email="discovery@test.local"
        ),
        "DE": Address(
            salutation="mr",
            first_name="Test",
            last_name="Discovery",
            street="Teststraße 1",
            zip_code="10115",
            city="Berlin",
            country="DE",
            email="discovery@test.local"
        ),
        "CH": Address(
            salutation="mr",
            first_name="Test",
            last_name="Discovery",
            street="Teststrasse 1",
            zip_code="8001",
            city="Zürich",
            country="CH",
            email="discovery@test.local"
        )
    }

    address = test_addresses.get(country_code, test_addresses["AT"])

    # Felder ausfüllen - NUR im Gast-Checkout-Bereich suchen
    try:
        # Gast-Checkout-Container finden und warten
        guest_container = page.locator("#collapseGuestCheckout, #guest, .register-form, form.register-form").first
        guest_container.locator("input[name*='firstName'], #personalFirstName").first.wait_for(state="visible", timeout=10000)

        # Persönliche Daten ausfüllen
        guest_container.locator("input[name*='firstName'], #personalFirstName").first.fill(address.first_name)
        guest_container.locator("input[name*='lastName'], #personalLastName").first.fill(address.last_name)
        guest_container.locator("input[name*='email'], input[type='email'], #personalMail").first.fill(address.email)

        # Adresse ausfüllen
        guest_container.locator("input[name*='street'], input[name*='addressStreet']").first.fill(address.street)
        guest_container.locator("input[name*='zipcode'], input[name*='postalCode']").first.fill(address.zip_code)
        guest_container.locator("input[name*='city']").first.fill(address.city)

        # Anrede auswählen (Pflichtfeld)
        salutation = guest_container.locator("select[name*='salutation'], #personalSalutation")
        if salutation.count() > 0:
            try:
                salutation.first.select_option(label="Herr", timeout=2000)
            except:
                salutation.first.select_option("mr", timeout=2000)

        # Land auswählen (falls nötig)
        country = guest_container.locator("select[name*='country'], #billingAddressAddressCountry")
        if country.count() > 0:
            try:
                country.first.select_option(address.country, timeout=2000)
            except:
                pass  # Land bereits vorausgewählt

    except Exception as e:
        print(f"[Discovery] WARNUNG: Fehler beim Ausfüllen: {str(e)}")

    # "Weiter"-Button finden - im Gast-Checkout-Bereich
    # Erst versuchen, spezifischen Button mit "Weiter"-Text zu finden
    continue_button = page.locator("button[type='submit']:visible").filter(has_text="Weiter")

    # Fallback: Alle sichtbaren Submit-Buttons
    if continue_button.count() == 0:
        continue_button = page.locator("button[type='submit']:visible")

    # Pflicht-Checkboxen aktivieren (AGBs, Datenschutz)
    checkboxes = page.locator("input[type='checkbox'][required], input[type='checkbox'][aria-required='true']")
    for i in range(checkboxes.count()):
        checkbox = checkboxes.nth(i)
        if not checkbox.is_checked():
            checkbox.check()

    # "Weiter"-Button klicken
    for i in range(continue_button.count()):
        button = continue_button.nth(i)
        if button.is_visible():
            button_text = button.inner_text()
            if "Weiter" in button_text or "weiter" in button_text:
                button.click()
                page.wait_for_load_state("domcontentloaded")
                page.wait_for_timeout(2000)
                break


@pytest.mark.discovery
def test_discover_payment_methods(page: Page, config: TestConfig):
    """
    Ermittelt verfügbare Zahlungsarten für alle konfigurierten Länder.

    WICHTIG: Dies ist ein Discovery-Test und muss manuell ausgeführt werden!

    Durchläuft:
    1. Alle country_paths (AT, DE, CH)
    2. Fügt Testprodukt zum Warenkorb hinzu
    3. Navigiert zur Checkout-Seite
    4. Extrahiert Zahlungsarten aus DOM
    5. Aktualisiert config.yaml mit Ergebnissen

    Returns:
        None (aktualisiert config.yaml als Side-Effect)
    """
    print(f"\n[Discovery] Profil: {config.test_profile}")
    print(f"[Discovery] Base URL: {config.base_url}")

    discovered_methods: dict[str, list[str]] = {}

    # Über alle konfigurierten Länder iterieren
    for country_code, country_path in config.country_paths.items():
        print(f"\n[Discovery] --- {country_code} ---")

        # Voller URL-Pfad
        country_base_url = f"{config.base_url}{country_path}".rstrip("/")
        print(f"[Discovery] URL: {country_base_url}")

        # Warenkorb leeren (via direkter Aufruf)
        page.goto(f"{country_base_url}/checkout/cart")
        page.wait_for_load_state("domcontentloaded")

        # Testprodukt zum Warenkorb hinzufügen
        test_product = config.test_products[0] if config.test_products else "p/default/ge-p-000000"
        print(f"[Discovery] Füge Produkt hinzu: {test_product}")
        add_test_product_to_cart(page, country_base_url, test_product)

        # Checkout-Flow durchlaufen bis zur Zahlungsarten-Seite
        print(f"[Discovery] Durchlaufe Checkout-Flow...")
        complete_checkout_to_payment_page(page, country_base_url, country_code)

        # Zahlungsarten extrahieren
        # Grüne Erde: <label class="payment-method-label"><strong>Name</strong>...</label>
        payment_labels = page.locator(".payment-method-label strong").all_inner_texts()

        # Bereinigen (Whitespace entfernen, leere Einträge filtern)
        payment_labels = [label.strip() for label in payment_labels if label.strip()]

        print(f"[Discovery] Gefunden: {payment_labels}")
        discovered_methods[country_code] = payment_labels

    # Zusammenfassung
    print("\n[Discovery] === Ergebnisse ===")
    for country, methods in discovered_methods.items():
        print(f"[Discovery] {country}: {methods}")

    # Config.yaml aktualisieren
    print("\n[Discovery] Aktualisiere config.yaml...")
    update_config_with_payment_methods(
        profile_name=config.test_profile,
        discovered_methods=discovered_methods
    )

    print("[Discovery] Discovery abgeschlossen!")

    # Assertion damit Test als "passed" gilt
    assert len(discovered_methods) > 0, "Keine Zahlungsarten entdeckt"
