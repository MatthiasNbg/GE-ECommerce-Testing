"""
Smoke Tests - Schnelle Validierung der Kernfunktionalität.

Diese Tests sollten nach jedem Deployment laufen und grundlegende
Funktionalität des Shops verifizieren.
"""
import base64
import pytest
from playwright.sync_api import Page, expect

from ..conftest import accept_cookie_banner


@pytest.mark.smoke
def test_homepage_loads(page: Page, base_url: str, request):
    """Startseite ist erreichbar und lädt korrekt."""
    page.goto(base_url)
    page.wait_for_load_state("networkidle")

    # Cookie-Banner akzeptieren (falls vorhanden)
    accept_cookie_banner(page)

    # Screenshot als Base64 für Report
    screenshot_bytes = page.screenshot(full_page=True)
    screenshot_base64 = base64.b64encode(screenshot_bytes).decode()

    # Screenshot zum pytest-html Report hinzufügen
    if hasattr(request.node, "extras"):
        request.node.extras = request.node.extras or []
    else:
        request.node.extras = []

    from pytest_html import extras
    request.node.extras.append(extras.image(f"data:image/png;base64,{screenshot_base64}", "Homepage Screenshot"))

    # Prüfen, dass die Seite geladen wurde
    assert page.title(), "Seite hat keinen Titel"

    # Keine kritischen Fehler
    error_elements = page.locator("css=.alert-danger, .error-500")
    assert error_elements.count() == 0, "Fehler auf der Startseite"


@pytest.mark.smoke
def test_search_works(page: Page, base_url: str, test_search_term: str):
    """Produktsuche E2E: Toggle → Suche → Ergebnisse → Produktdetails."""
    page.goto(base_url)
    page.wait_for_load_state("domcontentloaded")

    # Cookie-Banner akzeptieren (falls vorhanden)
    accept_cookie_banner(page)

    # Schritt 1: Such-Toggle klicken
    search_toggle = page.locator("button.search-toggle-btn.js-search-toggle-btn")
    search_toggle.click()
    page.wait_for_timeout(500)  # Collapse-Animation abwarten

    # Schritt 2: Suchbegriff eingeben
    search_input = page.locator("input#header-main-search-input")
    expect(search_input).to_be_visible()
    search_input.fill(test_search_term)

    # Schritt 3: Suche abschicken mit Enter
    search_input.press("Enter")

    # Schritt 4: Auf Ergebnisseite warten
    page.wait_for_load_state("domcontentloaded")

    # Schritt 5: Verifizieren, dass wir auf der Suchergebnisseite sind
    current_url = page.url
    assert "search" in current_url.lower() or test_search_term.lower() in current_url.lower(), \
        f"Suche hat nicht zur Ergebnisseite navigiert: {current_url}"

    # Schritt 6: Erstes Produkt aus Ergebnissen auswählen
    product_link = page.locator(".product-box a.product-name, .product-item a, .cms-listing-col .product-link").first
    expect(product_link).to_be_visible(timeout=5000)
    product_link.click()

    # Schritt 7: Produktdetails verifizieren
    page.wait_for_load_state("domcontentloaded")
    product_title = page.locator("h1")
    expect(product_title).to_be_visible()


@pytest.mark.smoke
def test_product_page_accessible(page: Page, base_url: str, test_product_id: str):
    """Eine Produktseite ist erreichbar."""
    # Produktseite aufrufen (Format: /p/produktname/ge-p-NUMMER)
    page.goto(f"{base_url}/{test_product_id}")
    page.wait_for_load_state("domcontentloaded")

    # Cookie-Banner akzeptieren (falls vorhanden)
    accept_cookie_banner(page)

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

    # Cookie-Banner akzeptieren (falls vorhanden)
    accept_cookie_banner(page)

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

    # Cookie-Banner akzeptieren (falls vorhanden)
    accept_cookie_banner(page)

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

    # Cookie-Banner akzeptieren (falls vorhanden)
    accept_cookie_banner(page)

    # Bei leerem Warenkorb erfolgt Redirect oder Fehlermeldung
    # Das ist OK - wir prüfen nur, ob der Endpunkt antwortet

    current_url = page.url

    # Entweder sind wir im Checkout oder wurden zum Cart umgeleitet
    is_checkout = "checkout" in current_url.lower()
    is_cart = "cart" in current_url.lower()
    is_login = "login" in current_url.lower() or "account" in current_url.lower()

    assert is_checkout or is_cart or is_login, \
        f"Unerwartete Weiterleitung: {current_url}"
