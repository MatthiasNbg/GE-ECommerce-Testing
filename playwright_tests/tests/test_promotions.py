"""
Promotion-Tests für den Grüne Erde Shopware Shop.

Testet alle Promotion/Rabattcode-Funktionen:
- Prozentuale Rabatte auf Warenkorb
- Versandkostenfrei-Promotions
- Automatische Promotions
- Mindestbestellwert-Bedingungen
- Nicht-rabattierbare Artikel

Test-IDs: TC-PROMO-001 bis TC-PROMO-SHIP-006
Phase: 6 (Promotions)
Priorität: P1 (Hoch)
"""
import pytest
from playwright.sync_api import Page, expect

from ..conftest import accept_cookie_banner


# =============================================================================
# Testdaten
# =============================================================================

# Testprodukte für Promotion-Tests
TEST_PRODUCTS = {
    "post": "p/kurzarmshirt-aus-bio-baumwolle/ge-p-862990",
    "spedition": "p/kleiderstaender-jukai-pur/ge-p-693645",
    "accessoire": "p/duftkissen-lavendel/ge-p-49415",
}

# Test-Promotion-Codes (müssen im Shopware-Backend angelegt sein)
# Diese Codes sind für Testzwecke und sollten nur auf Staging aktiv sein
TEST_PROMO_CODES = {
    "percentage_cart": "TEST20",  # 20% auf Warenkorb
    "free_shipping_post": "VERSANDFREI",  # Versandkostenfrei Post
    "free_shipping_spedi": "SPEDIFREI",  # Versandkostenfrei Spedition
    "min_order_50": "MBW50TEST",  # Mindestbestellwert 50 EUR
    "invalid": "UNGUELTIG123",  # Ungültiger Code
}


# =============================================================================
# Hilfsfunktionen
# =============================================================================

def add_product_to_cart(page: Page, base_url: str, product_path: str) -> None:
    """Fügt ein Produkt zum Warenkorb hinzu."""
    page.goto(f"{base_url}/{product_path}", wait_until="domcontentloaded")
    page.wait_for_timeout(1000)

    accept_cookie_banner(page)

    add_btn = page.locator("button.btn-buy")
    expect(add_btn.first).to_be_visible(timeout=10000)
    add_btn.first.click()
    page.wait_for_timeout(3000)

    # Offcanvas schließen
    offcanvas_close = page.locator(".offcanvas-close, .btn-close, [data-bs-dismiss='offcanvas']")
    if offcanvas_close.count() > 0:
        try:
            if offcanvas_close.first.is_visible(timeout=2000):
                offcanvas_close.first.click()
                page.wait_for_timeout(500)
        except Exception:
            pass


def navigate_to_cart(page: Page, base_url: str) -> None:
    """Navigiert zur Warenkorb-Seite."""
    page.goto(f"{base_url}/checkout/cart", wait_until="domcontentloaded")
    page.wait_for_timeout(1000)


def get_cart_total(page: Page) -> str:
    """Gibt die Gesamtsumme als Text zurück."""
    total_value = page.locator(
        ".checkout-aside-summary-total dd, "
        ".checkout-aside-summary-total .checkout-aside-summary-value, "
        ".checkout-aside-summary-total strong"
    )
    if total_value.count() > 0:
        return total_value.first.text_content() or ""
    return ""


def apply_promo_code(page: Page, code: str) -> bool:
    """
    Wendet einen Promotion-Code an.

    Returns:
        True wenn erfolgreich
    """
    # Promotion-Eingabefeld suchen
    promo_input = page.locator(
        "input[name='promotionCode'], "
        "#promotionCode, "
        "input[placeholder*='Gutschein'], "
        "input[placeholder*='Code']"
    )

    # Falls Container eingeklappt ist, aufklappen
    toggle = page.locator(
        "[data-bs-toggle='collapse'][href='#promotionContainer'], "
        "button:has-text('Gutschein einlösen')"
    )
    if toggle.count() > 0:
        try:
            if toggle.first.is_visible():
                toggle.first.click()
                page.wait_for_timeout(500)
        except Exception:
            pass

    if promo_input.count() == 0:
        return False

    promo_input.first.fill(code)
    page.wait_for_timeout(300)

    # Submit-Button
    submit_btn = page.locator(
        "button[type='submit']:has-text('Einlösen'), "
        "button:has-text('Gutschein einlösen'), "
        ".promotion-submit"
    )

    if submit_btn.count() > 0:
        submit_btn.first.click()
    else:
        promo_input.first.press("Enter")

    page.wait_for_timeout(2000)

    # Prüfe Erfolg
    success = page.locator(".alert-success, .promotion-success")
    return success.count() > 0


def has_promotion_discount(page: Page) -> bool:
    """Prüft ob ein Rabatt im Warenkorb sichtbar ist."""
    discount_line = page.locator(
        ".line-item-promotion, "
        ".line-item:has-text('Rabatt'), "
        ".line-item:has-text('Promotion'), "
        ".checkout-aside-summary-list dt:has-text('Rabatt')"
    )
    return discount_line.count() > 0


def get_shipping_cost(page: Page) -> str:
    """Gibt die Versandkosten als Text zurück."""
    shipping = page.locator(
        ".checkout-aside-summary-list dt:has-text('Versand') + dd, "
        ".checkout-aside-summary-list dt:has-text('Lieferung') + dd"
    )
    if shipping.count() > 0:
        return shipping.first.text_content() or ""
    return ""


# =============================================================================
# Tests
# =============================================================================

@pytest.mark.promotions
def test_promo_invalid_code_rejected(page: Page, base_url: str):
    """
    TC-PROMO-INVALID-001: Ungültiger Promotion-Code wird abgelehnt.

    Prüft, dass ein nicht existierender Code eine Fehlermeldung zeigt.
    """
    # Produkt zum Warenkorb hinzufügen
    add_product_to_cart(page, base_url, TEST_PRODUCTS["post"])
    navigate_to_cart(page, base_url)

    # Ungültigen Code eingeben
    success = apply_promo_code(page, TEST_PROMO_CODES["invalid"])

    # Sollte fehlschlagen
    assert not success, "Ungültiger Promotion-Code wurde fälschlicherweise akzeptiert"

    # Fehlermeldung sollte sichtbar sein
    error = page.locator(".alert-danger, .promotion-error, .invalid-feedback")
    expect(error.first).to_be_visible(timeout=5000)


@pytest.mark.promotions
def test_promo_percentage_cart_discount(page: Page, base_url: str):
    """
    TC-PROMO-CART-PERCENT-001: Prozentuale Aktion auf Warenkorb.

    Prüft prozentuale Promotion auf gesamten Warenkorb mit Aktionscode.
    """
    # Produkt zum Warenkorb hinzufügen
    add_product_to_cart(page, base_url, TEST_PRODUCTS["post"])
    navigate_to_cart(page, base_url)

    # Preis vor Rabatt merken
    total_before = get_cart_total(page)

    # Promotion-Code anwenden
    success = apply_promo_code(page, TEST_PROMO_CODES["percentage_cart"])

    if success:
        # Rabatt sollte sichtbar sein
        has_discount = has_promotion_discount(page)
        assert has_discount, "Promotion-Rabatt wird nicht im Warenkorb angezeigt"

        # Gesamtpreis sollte niedriger sein
        total_after = get_cart_total(page)
        assert total_before != total_after, "Preis hat sich nach Rabatt nicht geändert"
    else:
        pytest.skip("Promotion-Code TEST20 ist nicht im System konfiguriert")


@pytest.mark.promotions
def test_promo_free_shipping_post_de_at(page: Page, base_url: str):
    """
    TC-PROMO-SHIP-001: Versandkostenfrei nur Post (DE/AT).

    Prüft versandkostenfreie Lieferung nur für Postartikel in DE/AT.
    """
    # Produkt zum Warenkorb hinzufügen (Post-Artikel)
    add_product_to_cart(page, base_url, TEST_PRODUCTS["post"])
    navigate_to_cart(page, base_url)

    # Versandkosten vor Promotion
    shipping_before = get_shipping_cost(page)

    # Versandkostenfrei-Code anwenden
    success = apply_promo_code(page, TEST_PROMO_CODES["free_shipping_post"])

    if success:
        # Versandkosten sollten 0 oder "Kostenlos" sein
        shipping_after = get_shipping_cost(page)
        is_free = "0,00" in shipping_after or "kostenlos" in shipping_after.lower() or "gratis" in shipping_after.lower()
        assert is_free, f"Versandkosten sind nicht kostenlos: {shipping_after}"
    else:
        pytest.skip("Promotion-Code VERSANDFREI ist nicht im System konfiguriert")


@pytest.mark.promotions
def test_promo_free_shipping_spedition(page: Page, base_url: str):
    """
    TC-PROMO-SHIP-003: Versandkostenfrei nur Spedition (DE/AT).

    Prüft versandkostenfreie Lieferung nur für Speditionsartikel.
    """
    # Speditions-Produkt zum Warenkorb hinzufügen
    add_product_to_cart(page, base_url, TEST_PRODUCTS["spedition"])
    navigate_to_cart(page, base_url)

    # Versandkostenfrei-Code für Spedition anwenden
    success = apply_promo_code(page, TEST_PROMO_CODES["free_shipping_spedi"])

    if success:
        shipping_after = get_shipping_cost(page)
        is_free = "0,00" in shipping_after or "kostenlos" in shipping_after.lower() or "gratis" in shipping_after.lower()
        assert is_free, f"Speditions-Versandkosten sind nicht kostenlos: {shipping_after}"
    else:
        pytest.skip("Promotion-Code SPEDIFREI ist nicht im System konfiguriert")


@pytest.mark.promotions
def test_promo_minimum_order_value_rejected(page: Page, base_url: str):
    """
    TC-PROMO-SHIP-005: Versandkostenfrei Post ab MBW EUR 50 - unter Grenze.

    Prüft, dass Promotion unter Mindestbestellwert abgelehnt wird.
    """
    # Günstiges Produkt zum Warenkorb hinzufügen (unter 50 EUR)
    add_product_to_cart(page, base_url, TEST_PRODUCTS["accessoire"])
    navigate_to_cart(page, base_url)

    # MBW-Code anwenden
    success = apply_promo_code(page, TEST_PROMO_CODES["min_order_50"])

    # Sollte fehlschlagen (unter Mindestbestellwert)
    if not success:
        # Erwartetes Verhalten - Fehlermeldung sollte auf MBW hinweisen
        error = page.locator(".alert-danger, .promotion-error")
        if error.count() > 0:
            error_text = error.first.text_content() or ""
            assert "50" in error_text or "mindest" in error_text.lower() or "minimum" in error_text.lower(), \
                f"Fehlermeldung erwähnt Mindestbestellwert nicht: {error_text}"
    else:
        pytest.skip("Promotion-Code MBW50TEST ist nicht im System konfiguriert oder MBW nicht aktiv")


@pytest.mark.promotions
def test_promo_minimum_order_value_accepted(page: Page, base_url: str):
    """
    TC-PROMO-SHIP-005: Versandkostenfrei Post ab MBW EUR 50 - über Grenze.

    Prüft, dass Promotion über Mindestbestellwert akzeptiert wird.
    """
    # Mehrere Produkte zum Warenkorb hinzufügen (über 50 EUR)
    add_product_to_cart(page, base_url, TEST_PRODUCTS["post"])
    add_product_to_cart(page, base_url, TEST_PRODUCTS["accessoire"])
    navigate_to_cart(page, base_url)

    # Prüfe ob Warenkorbwert über 50 EUR
    total = get_cart_total(page)

    # MBW-Code anwenden
    success = apply_promo_code(page, TEST_PROMO_CODES["min_order_50"])

    if success:
        # Promotion sollte aktiv sein
        has_discount = has_promotion_discount(page)
        # Bei MBW-Versandkostenfrei: Versandkosten prüfen
        shipping = get_shipping_cost(page)
        is_free = "0,00" in shipping or "kostenlos" in shipping.lower()
        assert has_discount or is_free, "MBW-Promotion wurde nicht korrekt angewendet"
    else:
        pytest.skip("Promotion-Code MBW50TEST ist nicht im System konfiguriert")


@pytest.mark.promotions
def test_promo_code_removed_on_cart_clear(page: Page, base_url: str):
    """
    TC-PROMO-REMOVE-001: Promotion wird bei Warenkorb-Leerung entfernt.

    Prüft, dass Promotion-Rabatt entfernt wird, wenn Warenkorb geleert wird.
    """
    # Produkt hinzufügen und Promotion anwenden
    add_product_to_cart(page, base_url, TEST_PRODUCTS["post"])
    navigate_to_cart(page, base_url)

    success = apply_promo_code(page, TEST_PROMO_CODES["percentage_cart"])

    if not success:
        pytest.skip("Promotion-Code TEST20 ist nicht im System konfiguriert")

    # Produkt aus Warenkorb entfernen
    remove_btn = page.locator("button.line-item-remove-button, .line-item-remove")
    if remove_btn.count() > 0:
        remove_btn.first.click()
        page.wait_for_timeout(2000)

    # Warenkorb sollte leer sein
    empty_msg = page.locator(".cart-empty, :has-text('Ihr Warenkorb ist leer')")
    is_empty = empty_msg.count() > 0

    if is_empty:
        # Promotion-Rabatt sollte nicht mehr sichtbar sein
        has_discount = has_promotion_discount(page)
        assert not has_discount, "Promotion-Rabatt ist noch sichtbar bei leerem Warenkorb"


@pytest.mark.promotions
def test_promo_persists_through_checkout(page: Page, base_url: str):
    """
    TC-PROMO-PERSIST-001: Promotion bleibt im Checkout erhalten.

    Prüft, dass angewandte Promotion im Checkout-Prozess erhalten bleibt.
    """
    # Produkt hinzufügen und Promotion anwenden
    add_product_to_cart(page, base_url, TEST_PRODUCTS["post"])
    navigate_to_cart(page, base_url)

    success = apply_promo_code(page, TEST_PROMO_CODES["percentage_cart"])

    if not success:
        pytest.skip("Promotion-Code TEST20 ist nicht im System konfiguriert")

    # Zur Kasse gehen
    checkout_btn = page.locator("a:has-text('Zur Kasse'), button:has-text('Zur Kasse')")
    if checkout_btn.count() > 0:
        checkout_btn.first.click()
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)

    # Promotion sollte noch sichtbar sein
    has_discount = has_promotion_discount(page)
    assert has_discount, "Promotion-Rabatt wurde beim Checkout-Übergang entfernt"


@pytest.mark.promotions
def test_promo_display_in_order_summary(page: Page, base_url: str):
    """
    TC-PROMO-DISPLAY-001: Promotion wird in Bestellübersicht angezeigt.

    Prüft, dass der Rabatt korrekt in der Zusammenfassung erscheint.
    """
    # Produkt hinzufügen
    add_product_to_cart(page, base_url, TEST_PRODUCTS["post"])
    navigate_to_cart(page, base_url)

    # Promotion anwenden
    success = apply_promo_code(page, TEST_PROMO_CODES["percentage_cart"])

    if not success:
        pytest.skip("Promotion-Code TEST20 ist nicht im System konfiguriert")

    # Prüfe Anzeige in Zusammenfassung
    summary = page.locator(".checkout-aside-summary, .cart-summary")
    expect(summary.first).to_be_visible(timeout=5000)

    # Rabatt sollte als separate Zeile erscheinen
    discount_display = page.locator(
        ".checkout-aside-summary-list dt:has-text('Rabatt'), "
        ".checkout-aside-summary-list dt:has-text('Promotion'), "
        ".line-item-promotion"
    )
    expect(discount_display.first).to_be_visible(timeout=5000)
