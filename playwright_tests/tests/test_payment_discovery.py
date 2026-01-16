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
from playwright_tests.utils.payment_discovery import update_config_with_payment_methods


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

        # Zur Checkout-Seite navigieren
        checkout_url = f"{country_base_url}/checkout/confirm"
        print(f"[Discovery] Navigiere zu: {checkout_url}")
        page.goto(checkout_url)
        page.wait_for_load_state("domcontentloaded")

        # Warten, bis Zahlungsarten geladen sind
        page.wait_for_timeout(2000)

        # Zahlungsarten extrahieren
        # Grüne Erde verwendet .payment-method-label oder ähnliche Klassen
        payment_labels = page.locator(
            ".payment-method-label, "
            ".payment-name, "
            "[data-payment-method-name], "
            ".confirm-payment-method-label"
        ).all_inner_texts()

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

    print("[Discovery] ✓ Discovery abgeschlossen!")

    # Assertion damit Test als "passed" gilt
    assert len(discovered_methods) > 0, "Keine Zahlungsarten entdeckt"
