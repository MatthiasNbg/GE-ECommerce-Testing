"""
Merkliste (Wishlist) Tests fuer den Shopware Shop.

Testet alle Merklisten-Operationen:
- Produkt zur Merkliste hinzufuegen
- Mehrere Produkte hinzufuegen
- Produkt von Merkliste entfernen
- Produkt aus Merkliste in den Warenkorb legen
- Leere Merkliste anzeigen

Test-IDs: TC-WISH-001 bis TC-WISH-005
Phase: 2 (Feature-Tests)
Prioritaet: P1 (Hoch)
Channel: Nur AT
Voraussetzung: Eingeloggter Benutzer
"""
import pytest
from playwright.sync_api import Page, expect

from ..conftest import accept_cookie_banner


# =============================================================================
# Testdaten
# =============================================================================

# AT-Testkunde
TEST_EMAIL = "ge-at-1@matthias-sax.de"
TEST_PASSWORD = "scharnsteinAT"

# Testprodukte (Post-Versand, immer auf Lager)
WISHLIST_PRODUCTS = [
    "p/kurzarmshirt-aus-bio-baumwolle/ge-p-862990",
    "p/duftkissen-lavendel/ge-p-49415",
    "p/bademantel-raute-fuer-damen-und-herren/ge-p-410933",
]


# =============================================================================
# Hilfsfunktionen
# =============================================================================

def login_customer(page: Page, base_url: str) -> None:
    """Loggt den AT-Testkunden ein."""
    page.goto(f"{base_url}/account/login", wait_until="domcontentloaded")
    page.wait_for_timeout(1000)
    accept_cookie_banner(page)

    page.fill("#loginMail", TEST_EMAIL)
    page.fill("#loginPassword", TEST_PASSWORD)
    page.locator("button:has-text('Anmelden')").first.click()
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)

    # Pruefen ob Login erfolgreich
    assert "account/login" not in page.url, "Login fehlgeschlagen"


def add_to_wishlist(page: Page, base_url: str, product_path: str) -> None:
    """Fuegt ein Produkt zur Merkliste hinzu."""
    page.goto(f"{base_url}/{product_path}", wait_until="domcontentloaded")
    page.wait_for_timeout(1000)

    # Pruefen ob bereits auf Merkliste (erster Button ist das Hauptprodukt)
    wishlist_btn = page.locator("[data-add-to-wishlist]").first
    expect(wishlist_btn).to_be_visible(timeout=10000)

    classes = wishlist_btn.get_attribute("class") or ""
    if "product-wishlist-added" in classes:
        return  # Bereits auf Merkliste

    wishlist_btn.click()
    page.wait_for_timeout(2000)


def navigate_to_wishlist(page: Page, base_url: str) -> None:
    """Navigiert zur Merklisten-Seite."""
    page.goto(f"{base_url}/wishlist", wait_until="domcontentloaded")
    page.wait_for_timeout(1000)


def get_wishlist_product_count(page: Page) -> int:
    """Gibt die Anzahl der Produkte auf der Merklisten-Seite zurueck."""
    products = page.locator(".product-box.box-wishlist")
    return products.count()


def remove_first_wishlist_product(page: Page) -> None:
    """Entfernt das erste Produkt von der Merkliste via Form-Submit."""
    page.evaluate("""() => {
        const form = document.querySelector('.product-wishlist-form');
        if (form) form.submit();
    }""")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)


def clear_wishlist(page: Page, base_url: str) -> None:
    """Leert die Merkliste komplett."""
    navigate_to_wishlist(page, base_url)
    while True:
        products = page.locator(".product-box.box-wishlist")
        if products.count() == 0:
            break
        remove_first_wishlist_product(page)


# =============================================================================
# TC-WISH-001: Produkt zur Merkliste hinzufuegen
# =============================================================================

@pytest.mark.wishlist
def test_add_product_to_wishlist(page: Page, base_url: str):
    """
    TC-WISH-001: Produkt zur Merkliste hinzufuegen.

    Schritte:
    1. Einloggen (AT-Testkunde)
    2. Produktseite aufrufen
    3. Herz-Button klicken
    4. Merklisten-Seite aufrufen
    5. Pruefen: Produkt ist auf der Merkliste sichtbar
    """
    product_path = WISHLIST_PRODUCTS[0]

    # Login
    login_customer(page, base_url)

    # Merkliste vorher leeren
    clear_wishlist(page, base_url)

    # Produkt zur Merkliste hinzufuegen
    add_to_wishlist(page, base_url, product_path)

    # Pruefen: Herz-Button ist jetzt aktiv (product-wishlist-added)
    added_indicator = page.locator(".product-wishlist-added")
    expect(added_indicator.first).to_be_visible(timeout=5000)

    # Zur Merklisten-Seite navigieren
    navigate_to_wishlist(page, base_url)

    # Pruefen: Mindestens ein Produkt auf der Merkliste
    count = get_wishlist_product_count(page)
    assert count >= 1, f"Erwartet mindestens 1 Produkt auf der Merkliste, gefunden: {count}"

    # Cleanup
    clear_wishlist(page, base_url)


# =============================================================================
# TC-WISH-002: Mehrere Produkte zur Merkliste hinzufuegen
# =============================================================================

@pytest.mark.wishlist
def test_add_multiple_products_to_wishlist(page: Page, base_url: str):
    """
    TC-WISH-002: Mehrere Produkte zur Merkliste hinzufuegen.

    Schritte:
    1. Einloggen (AT-Testkunde)
    2. 3 verschiedene Produkte zur Merkliste hinzufuegen
    3. Merklisten-Seite aufrufen
    4. Pruefen: Alle 3 Produkte sind sichtbar
    """
    # Login
    login_customer(page, base_url)

    # Merkliste vorher leeren
    clear_wishlist(page, base_url)

    # 3 Produkte hinzufuegen
    for product_path in WISHLIST_PRODUCTS:
        add_to_wishlist(page, base_url, product_path)

    # Zur Merklisten-Seite navigieren
    navigate_to_wishlist(page, base_url)

    # Pruefen: 3 Produkte auf der Merkliste
    count = get_wishlist_product_count(page)
    assert count >= 3, (
        f"Erwartet mindestens 3 Produkte auf der Merkliste, gefunden: {count}"
    )

    # Cleanup
    clear_wishlist(page, base_url)


# =============================================================================
# TC-WISH-003: Produkt von Merkliste entfernen
# =============================================================================

@pytest.mark.wishlist
def test_remove_product_from_wishlist(page: Page, base_url: str):
    """
    TC-WISH-003: Produkt von der Merkliste entfernen.

    Schritte:
    1. Einloggen (AT-Testkunde)
    2. Produkt zur Merkliste hinzufuegen
    3. Merklisten-Seite aufrufen
    4. Produkt entfernen
    5. Pruefen: Merkliste ist leer
    """
    product_path = WISHLIST_PRODUCTS[0]

    # Login
    login_customer(page, base_url)

    # Merkliste vorher leeren
    clear_wishlist(page, base_url)

    # Produkt hinzufuegen
    add_to_wishlist(page, base_url, product_path)

    # Zur Merklisten-Seite
    navigate_to_wishlist(page, base_url)

    # Pruefen: Produkt ist da
    count_before = get_wishlist_product_count(page)
    assert count_before >= 1, "Produkt sollte auf der Merkliste sein"

    # Produkt entfernen (Form-Submit)
    remove_first_wishlist_product(page)

    # Pruefen: Merkliste ist jetzt leer
    count_after = get_wishlist_product_count(page)
    assert count_after == 0, (
        f"Merkliste sollte leer sein nach Entfernen, aber enthaelt {count_after} Produkte"
    )


# =============================================================================
# TC-WISH-004: Produkt aus Merkliste in den Warenkorb legen
# =============================================================================

@pytest.mark.wishlist
def test_wishlist_add_to_cart(page: Page, base_url: str):
    """
    TC-WISH-004: Produkt aus der Merkliste in den Warenkorb legen.

    Schritte:
    1. Einloggen (AT-Testkunde)
    2. Produkt zur Merkliste hinzufuegen
    3. Merklisten-Seite aufrufen
    4. "In den Warenkorb" klicken
    5. Zur Warenkorb-Seite navigieren
    6. Pruefen: Produkt ist im Warenkorb
    """
    product_path = WISHLIST_PRODUCTS[0]

    # Login
    login_customer(page, base_url)

    # Merkliste vorher leeren
    clear_wishlist(page, base_url)

    # Produkt zur Merkliste hinzufuegen
    add_to_wishlist(page, base_url, product_path)

    # Zur Merklisten-Seite
    navigate_to_wishlist(page, base_url)

    # "In den Warenkorb" klicken
    products = page.locator(".product-box.box-wishlist")
    assert products.count() >= 1, "Mindestens ein Produkt sollte auf der Merkliste sein"

    cart_btn = products.first.locator("button.btn-buy, [data-add-to-cart]")
    expect(cart_btn.first).to_be_visible(timeout=5000)
    cart_btn.first.click()
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

    # Zur Warenkorb-Seite navigieren
    page.goto(f"{base_url}/checkout/cart", wait_until="domcontentloaded")
    page.wait_for_timeout(1000)

    # Pruefen: Mindestens ein Produkt im Warenkorb
    cart_items = page.locator(".line-item")
    assert cart_items.count() >= 1, "Produkt sollte im Warenkorb sein"

    # Cleanup: Merkliste leeren
    clear_wishlist(page, base_url)


# =============================================================================
# TC-WISH-005: Leere Merkliste anzeigen
# =============================================================================

@pytest.mark.wishlist
def test_empty_wishlist_shows_message(page: Page, base_url: str):
    """
    TC-WISH-005: Leere Merkliste zeigt entsprechende Meldung.

    Schritte:
    1. Einloggen (AT-Testkunde)
    2. Merkliste leeren (falls noetig)
    3. Merklisten-Seite aufrufen
    4. Pruefen: Leer-Hinweis wird angezeigt oder keine Produkte vorhanden
    """
    # Login
    login_customer(page, base_url)

    # Merkliste leeren
    clear_wishlist(page, base_url)

    # Zur Merklisten-Seite
    navigate_to_wishlist(page, base_url)

    # Pruefen: Keine Produkte vorhanden
    count = get_wishlist_product_count(page)
    assert count == 0, (
        f"Merkliste sollte leer sein, enthaelt aber {count} Produkte"
    )
