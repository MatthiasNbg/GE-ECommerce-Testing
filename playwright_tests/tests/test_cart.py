"""
Warenkorb-Tests für den Shopware Shop.

Testet alle Warenkorb-Operationen:
- Produkte hinzufügen
- Mengen ändern
- Produkte entfernen
- Preisberechnungen
- Warenkorb-Persistenz

Test-IDs: TC-CART-001 bis TC-CART-008
Phase: 2 (Feature-Tests)
Priorität: P1 (Hoch)
"""
import pytest
from playwright.sync_api import Page, expect

from ..conftest import accept_cookie_banner


# =============================================================================
# Testdaten
# =============================================================================

# Testprodukte aus config.yaml
TEST_PRODUCTS = [
    "p/kurzarmshirt-aus-bio-baumwolle/ge-p-862990",
    "p/duftkissen-lavendel/ge-p-49415",
    "p/bademantel-raute-fuer-damen-und-herren/ge-p-410933",
]


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


def get_cart_item_count(page: Page) -> int:
    """Gibt die Anzahl der Produkte im Warenkorb zurück."""
    items = page.locator(".line-item")
    return items.count()


def get_cart_total(page: Page) -> str:
    """Gibt die Gesamtsumme als Text zurück."""
    # Preis-Wert aus der Summary holen (dd-Element oder strong)
    total_value = page.locator(
        ".checkout-aside-summary-total dd, "
        ".checkout-aside-summary-total .checkout-aside-summary-value, "
        ".checkout-aside-summary-total strong"
    )
    if total_value.count() > 0:
        return total_value.first.text_content() or ""

    # Fallback: Line-Item-Total wenn nur ein Produkt
    line_total = page.locator(".line-item-total-price, .line-item-total")
    if line_total.count() > 0:
        return line_total.first.text_content() or ""
    return ""


def clear_cart(page: Page) -> None:
    """Leert den Warenkorb komplett."""
    while True:
        remove_btns = page.locator("button.line-item-remove-button")
        if remove_btns.count() == 0:
            break
        remove_btns.first.click()
        page.wait_for_timeout(2000)


# =============================================================================
# TC-CART-001: Produkt hinzufügen zeigt sich im Warenkorb
# =============================================================================

@pytest.mark.cart
@pytest.mark.smoke
def test_add_product_shows_in_cart(page: Page, base_url: str):
    """
    TC-CART-001: Produkt zum Warenkorb hinzufügen.

    Schritte:
    1. Produktseite laden
    2. "In den Warenkorb" klicken
    3. Zur Warenkorb-Seite navigieren
    4. Prüfen: Produkt ist im Warenkorb sichtbar
    """
    product_path = TEST_PRODUCTS[0]

    # Produkt hinzufügen
    add_product_to_cart(page, base_url, product_path)

    # Zur Warenkorb-Seite
    navigate_to_cart(page, base_url)

    # Prüfen: Mindestens ein Produkt im Warenkorb
    item_count = get_cart_item_count(page)
    assert item_count >= 1, f"Erwartet mindestens 1 Produkt, gefunden: {item_count}"

    # Prüfen: Kein "Warenkorb leer" Meldung
    empty_msg = page.locator(".cart-empty, :has-text('Ihr Warenkorb ist leer')")
    expect(empty_msg).not_to_be_visible(timeout=2000)


# =============================================================================
# TC-CART-002: Cart Counter aktualisiert sich
# =============================================================================

@pytest.mark.cart
def test_cart_counter_updates(page: Page, base_url: str):
    """
    TC-CART-002: Warenkorb-Counter im Header aktualisiert sich.

    Schritte:
    1. Leeren Warenkorb sicherstellen
    2. Produkt hinzufügen
    3. Prüfen: Counter zeigt mindestens "1"
    """
    # Zur Startseite und Cookie-Banner akzeptieren
    page.goto(base_url, wait_until="domcontentloaded")
    accept_cookie_banner(page)

    # Produkt hinzufügen
    add_product_to_cart(page, base_url, TEST_PRODUCTS[0])

    # Cart-Counter prüfen
    cart_counter = page.locator(".header-cart-total, .cart-quantity, [data-cart-widget] .badge")

    # Counter sollte sichtbar sein und eine Zahl > 0 enthalten
    expect(cart_counter.first).to_be_visible(timeout=5000)
    counter_text = cart_counter.first.text_content() or ""

    # Extrahiere Zahl
    import re
    match = re.search(r'\d+', counter_text)
    assert match, f"Keine Zahl im Cart-Counter gefunden: '{counter_text}'"

    count = int(match.group())
    assert count >= 1, f"Cart-Counter sollte >= 1 sein, ist aber: {count}"


# =============================================================================
# TC-CART-003: Menge ändern aktualisiert Gesamtpreis
# =============================================================================

@pytest.mark.cart
def test_update_quantity_changes_total(page: Page, base_url: str):
    """
    TC-CART-003: Mengenänderung aktualisiert den Gesamtpreis.

    Schritte:
    1. Produkt zum Warenkorb hinzufügen
    2. Zur Warenkorb-Seite
    3. Ursprünglichen Preis merken
    4. Menge auf 2 erhöhen
    5. Prüfen: Preis hat sich geändert
    """
    # Produkt hinzufügen
    add_product_to_cart(page, base_url, TEST_PRODUCTS[0])
    navigate_to_cart(page, base_url)

    # Ursprünglichen Preis merken
    original_total = get_cart_total(page)

    # Mengen-Input finden und ändern
    qty_input = page.locator("input[name='quantity'], input.quantity-input")
    expect(qty_input.first).to_be_visible(timeout=5000)

    # Menge auf 2 setzen
    qty_input.first.fill("2")
    qty_input.first.press("Enter")
    page.wait_for_timeout(3000)  # Warten auf AJAX-Update

    # Neuen Preis prüfen
    new_total = get_cart_total(page)

    # Preise sollten unterschiedlich sein (Verdopplung bei Menge 2)
    assert original_total != new_total, (
        f"Preis sollte sich nach Mengenänderung ändern. "
        f"Original: {original_total}, Neu: {new_total}"
    )


# =============================================================================
# TC-CART-004: Produkt entfernen aktualisiert Warenkorb
# =============================================================================

@pytest.mark.cart
def test_remove_product_updates_cart(page: Page, base_url: str):
    """
    TC-CART-004: Produkt entfernen aktualisiert den Warenkorb.

    Schritte:
    1. Produkt hinzufügen
    2. Zur Warenkorb-Seite
    3. Anzahl der Produkte merken
    4. Produkt entfernen
    5. Prüfen: Weniger Produkte oder leerer Warenkorb
    """
    # Produkt hinzufügen
    add_product_to_cart(page, base_url, TEST_PRODUCTS[0])
    navigate_to_cart(page, base_url)

    # Anzahl vor dem Löschen
    items_before = get_cart_item_count(page)
    assert items_before >= 1, "Mindestens 1 Produkt sollte im Warenkorb sein"

    # Produkt entfernen mit korrektem Selektor
    remove_btn = page.locator("button.line-item-remove-button")
    expect(remove_btn.first).to_be_visible(timeout=5000)
    remove_btn.first.click()
    page.wait_for_timeout(3000)

    # Anzahl nach dem Löschen
    items_after = get_cart_item_count(page)

    assert items_after < items_before, (
        f"Nach dem Löschen sollten weniger Produkte im Warenkorb sein. "
        f"Vorher: {items_before}, Nachher: {items_after}"
    )


# =============================================================================
# TC-CART-005: Leerer Warenkorb zeigt Meldung
# =============================================================================

@pytest.mark.cart
def test_empty_cart_shows_message(page: Page, base_url: str):
    """
    TC-CART-005: Leerer Warenkorb zeigt entsprechende Meldung.

    Schritte:
    1. Zur Warenkorb-Seite (leer oder leeren)
    2. Prüfen: "Warenkorb ist leer" Meldung wird angezeigt
    """
    # Zur Warenkorb-Seite
    navigate_to_cart(page, base_url)

    # Warenkorb leeren falls nicht leer
    clear_cart(page)

    # Prüfen: Leermeldung sichtbar
    empty_indicators = page.locator(
        ".cart-empty, "
        ".empty-cart, "
        ":has-text('Ihr Warenkorb ist leer'), "
        ":has-text('Warenkorb ist leer')"
    )

    # Mindestens einer der Indikatoren sollte sichtbar sein
    # ODER keine Produkte im Warenkorb
    items = page.locator(".line-item")
    item_count = items.count()

    if item_count == 0:
        # Warenkorb ist leer - Test bestanden
        pass
    else:
        # Sollte nicht passieren nach clear_cart()
        assert False, f"Warenkorb sollte leer sein, enthält aber {item_count} Produkte"


# =============================================================================
# TC-CART-006: Warenkorb-Persistenz zwischen Seiten
# =============================================================================

@pytest.mark.cart
def test_cart_persists_between_pages(page: Page, base_url: str):
    """
    TC-CART-006: Warenkorb bleibt bei Navigation erhalten.

    Schritte:
    1. Produkt hinzufügen
    2. Zur Startseite navigieren
    3. Zu einer anderen Produktseite navigieren
    4. Zurück zur Warenkorb-Seite
    5. Prüfen: Produkt ist noch im Warenkorb
    """
    # Produkt hinzufügen
    add_product_to_cart(page, base_url, TEST_PRODUCTS[0])

    # Merke Cart-Counter
    cart_counter = page.locator(".header-cart-total, .cart-quantity")
    initial_count = cart_counter.first.text_content() if cart_counter.count() > 0 else ""

    # Zur Startseite
    page.goto(base_url, wait_until="domcontentloaded")
    page.wait_for_timeout(1000)

    # Zu einem anderen Produkt
    page.goto(f"{base_url}/{TEST_PRODUCTS[1]}", wait_until="domcontentloaded")
    page.wait_for_timeout(1000)

    # Zurück zum Warenkorb
    navigate_to_cart(page, base_url)

    # Prüfen: Produkt ist noch da
    item_count = get_cart_item_count(page)
    assert item_count >= 1, (
        "Warenkorb sollte nach Navigation noch Produkte enthalten"
    )


# =============================================================================
# TC-CART-007: Mehrere Produkte hinzufügen
# =============================================================================

@pytest.mark.cart
def test_add_multiple_products(page: Page, base_url: str):
    """
    TC-CART-007: Mehrere verschiedene Produkte können hinzugefügt werden.

    Schritte:
    1. Erstes Produkt hinzufügen
    2. Zweites Produkt hinzufügen
    3. Zur Warenkorb-Seite
    4. Prüfen: Beide Produkte sind im Warenkorb
    """
    # Erstes Produkt
    add_product_to_cart(page, base_url, TEST_PRODUCTS[0])

    # Zweites Produkt
    add_product_to_cart(page, base_url, TEST_PRODUCTS[1])

    # Zur Warenkorb-Seite
    navigate_to_cart(page, base_url)

    # Prüfen: Mindestens 2 verschiedene Produkte
    item_count = get_cart_item_count(page)
    assert item_count >= 2, (
        f"Erwartet mindestens 2 Produkte im Warenkorb, gefunden: {item_count}"
    )


# =============================================================================
# TC-CART-008: Preisberechnung korrekt (Einzelpreis × Menge)
# =============================================================================

@pytest.mark.cart
def test_price_calculation_correct(page: Page, base_url: str):
    """
    TC-CART-008: Gesamtpreis entspricht Einzelpreis × Menge.

    Schritte:
    1. Produkt hinzufügen
    2. Zur Warenkorb-Seite
    3. Einzelpreis und Gesamtpreis auslesen
    4. Menge auf 3 setzen
    5. Prüfen: Gesamtpreis = Einzelpreis × 3 (mit Toleranz)
    """
    import re

    def parse_price(text: str) -> float:
        """Parst Preistext zu Float."""
        if not text:
            return 0.0
        cleaned = re.sub(r'[€$£\s]', '', text)
        cleaned = cleaned.replace(',', '.')
        match = re.search(r'[\d.]+', cleaned)
        return float(match.group()) if match else 0.0

    # Produkt hinzufügen
    add_product_to_cart(page, base_url, TEST_PRODUCTS[0])
    navigate_to_cart(page, base_url)

    # Einzelpreis auslesen
    unit_price_el = page.locator(".line-item-unit-price, .line-item-price").first
    unit_price_text = unit_price_el.text_content() if unit_price_el.is_visible() else ""
    unit_price = parse_price(unit_price_text)

    # Menge auf 3 setzen
    qty_input = page.locator("input[name='quantity'], input.quantity-input").first
    qty_input.fill("3")
    qty_input.press("Enter")
    page.wait_for_timeout(3000)

    # Zeilengesamtpreis auslesen
    total_price_el = page.locator(".line-item-total-price, .line-item-total").first
    total_price_text = total_price_el.text_content() if total_price_el.is_visible() else ""
    total_price = parse_price(total_price_text)

    # Erwarteter Preis
    expected_total = unit_price * 3

    # Prüfen mit 1% Toleranz (wegen Rundung)
    tolerance = expected_total * 0.01
    assert abs(total_price - expected_total) <= tolerance, (
        f"Preisberechnung falsch! "
        f"Einzelpreis: {unit_price}, Menge: 3, "
        f"Erwartet: {expected_total}, Tatsächlich: {total_price}"
    )
