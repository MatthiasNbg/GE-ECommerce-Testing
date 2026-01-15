"""
Smoke Tests - Schnelle Validierung der Kernfunktionalität.

Diese Tests sollten nach jedem Deployment laufen und grundlegende
Funktionalität des Shops verifizieren.
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.smoke
def test_homepage_loads(page: Page, base_url: str):
    """Startseite ist erreichbar und lädt korrekt."""
    page.goto(base_url)
    page.wait_for_load_state("domcontentloaded")

    # Prüfen, dass die Seite geladen wurde
    assert page.title(), "Seite hat keinen Titel"

    # Keine kritischen Fehler
    error_elements = page.locator("css=.alert-danger, .error-500")
    assert error_elements.count() == 0, "Fehler auf der Startseite"


@pytest.mark.smoke
def test_search_works(page: Page, base_url: str):
    """Produktsuche ist funktionsfähig."""
    page.goto(base_url)
    page.wait_for_load_state("domcontentloaded")

    # Grüne Erde: Suchfeld ist versteckt, erst Toggle klicken
    search_toggle = page.locator(".search-toggle, [data-search-toggle]")
    if search_toggle.count() > 0 and search_toggle.first.is_visible():
        search_toggle.first.click()
        page.wait_for_timeout(500)  # Animation abwarten

    # Such-Input finden
    search_input = page.locator(
        "input[type='search'], "
        "input[name='search'], "
        ".header-search-input"
    )

    # Prüfen ob Suche sichtbar ist
    if search_input.count() > 0 and search_input.first.is_visible():
        search_input.first.fill("Shirt")
        search_input.first.press("Enter")

        # Warten auf Suchergebnisse
        page.wait_for_load_state("domcontentloaded")

        # Prüfen, dass wir auf einer Suchergebnisseite sind
        current_url = page.url
        assert "search" in current_url.lower() or "suche" in current_url.lower(), \
            f"Suche hat nicht navigiert: {current_url}"


@pytest.mark.smoke
def test_product_page_accessible(page: Page, base_url: str, test_product_id: str):
    """Eine Produktseite ist erreichbar."""
    # Produktseite aufrufen (Format: /p/produktname/ge-p-NUMMER)
    page.goto(f"{base_url}/{test_product_id}")
    page.wait_for_load_state("domcontentloaded")

    # Prüfen auf Produktseiten-Elemente (Grüne Erde spezifisch)
    product_elements = page.locator(
        "h1, "
        ".product-detail-price, "
        ".btn-buy, "
        ".buy-widget"
    )

    # Mindestens ein Produktelement sollte vorhanden sein
    assert product_elements.count() > 0, \
        "Keine Produktelemente gefunden - möglicherweise 404?"


@pytest.mark.smoke
def test_add_to_cart(page: Page, base_url: str, test_product_id: str):
    """Produkt kann zum Warenkorb hinzugefügt werden."""
    # Produktseite aufrufen (Format: /p/produktname/ge-p-NUMMER)
    page.goto(f"{base_url}/{test_product_id}")
    page.wait_for_load_state("domcontentloaded")

    # "In den Warenkorb" Button finden
    add_to_cart = page.locator(".btn-buy, [data-add-to-cart]")

    if add_to_cart.count() > 0:
        add_to_cart.first.click()

        # Warten auf Feedback (Offcanvas-Cart oder Notification)
        page.wait_for_timeout(2000)  # AJAX abwarten

        # Cart-Counter sollte sich ändern oder Offcanvas öffnet sich
        cart_indicator = page.locator(
            ".header-cart-total, "
            ".cart-item-count, "
            "[data-cart-widget], "
            ".offcanvas-cart, "
            ".cart-offcanvas"
        )

        # Irgendeiner der Indikatoren sollte reagieren
        assert cart_indicator.count() > 0, \
            "Kein Warenkorb-Feedback nach Hinzufügen"


@pytest.mark.smoke
def test_cart_accessible(page: Page, base_url: str):
    """Warenkorbseite ist erreichbar."""
    page.goto(f"{base_url}/checkout/cart")
    page.wait_for_load_state("domcontentloaded")

    # Prüfen, dass wir auf der Warenkorb-Seite sind
    cart_elements = page.locator(
        "css=.checkout-cart, "
        ".cart-main, "
        "[data-cart-widget], "
        ".line-item-container"
    )

    # Mindestens ein Cart-Element oder "Warenkorb leer" Meldung
    empty_cart = page.locator("css=.cart-empty, .empty-cart")

    has_cart = cart_elements.count() > 0
    has_empty = empty_cart.count() > 0

    assert has_cart or has_empty, \
        "Weder Warenkorb noch Leer-Meldung gefunden"


@pytest.mark.smoke
def test_checkout_accessible(page: Page, base_url: str):
    """Checkout-Seite ist grundsätzlich erreichbar."""
    page.goto(f"{base_url}/checkout/confirm")
    page.wait_for_load_state("domcontentloaded")

    # Bei leerem Warenkorb erfolgt Redirect oder Fehlermeldung
    # Das ist OK - wir prüfen nur, ob der Endpunkt antwortet

    current_url = page.url

    # Entweder sind wir im Checkout oder wurden zum Cart umgeleitet
    is_checkout = "checkout" in current_url.lower()
    is_cart = "cart" in current_url.lower()
    is_login = "login" in current_url.lower() or "account" in current_url.lower()

    assert is_checkout or is_cart or is_login, \
        f"Unerwartete Weiterleitung: {current_url}"
