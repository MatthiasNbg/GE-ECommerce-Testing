"""
Smoke Tests - Schnelle Validierung der Kernfunktionalität.

Diese Tests sollten nach jedem Deployment laufen und grundlegende
Funktionalität des Shops verifizieren.
"""
import pytest
from playwright.async_api import Page, expect


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_homepage_loads(page: Page, base_url: str):
    """Startseite ist erreichbar und lädt korrekt."""
    await page.goto(base_url)
    await page.wait_for_load_state("domcontentloaded")

    # Prüfen, dass die Seite geladen wurde
    assert await page.title(), "Seite hat keinen Titel"

    # Keine kritischen Fehler
    error_elements = page.locator("css=.alert-danger, .error-500")
    assert await error_elements.count() == 0, "Fehler auf der Startseite"


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_search_works(page: Page, base_url: str):
    """Produktsuche ist funktionsfähig."""
    await page.goto(base_url)
    await page.wait_for_load_state("domcontentloaded")

    # Such-Input finden (Shopware 6 Standard-Selektoren)
    search_input = page.locator(
        "css=input[type='search'], "
        "input[name='search'], "
        ".header-search-input, "
        "[data-search-input]"
    )

    # Prüfen ob Suche vorhanden
    if await search_input.count() > 0:
        await search_input.first.fill("Test")
        await search_input.first.press("Enter")

        # Warten auf Suchergebnisse
        await page.wait_for_load_state("domcontentloaded")

        # Prüfen, dass wir auf einer Suchergebnisseite sind
        current_url = page.url
        assert "search" in current_url.lower() or "suche" in current_url.lower(), \
            f"Suche hat nicht navigiert: {current_url}"


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_product_page_accessible(page: Page, base_url: str, test_product_id: str):
    """Eine Produktseite ist erreichbar."""
    # Produktseite aufrufen
    await page.goto(f"{base_url}/detail/{test_product_id}")
    await page.wait_for_load_state("domcontentloaded")

    # Prüfen auf typische Produktseiten-Elemente
    product_elements = page.locator(
        "css=.product-detail, "
        ".product-detail-name, "
        "[data-product-detail], "
        ".product-detail-buy"
    )

    # Mindestens ein Produktelement sollte vorhanden sein
    assert await product_elements.count() > 0, \
        "Keine Produktelemente gefunden - möglicherweise 404?"


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_add_to_cart(page: Page, base_url: str, test_product_id: str):
    """Produkt kann zum Warenkorb hinzugefügt werden."""
    # Produktseite aufrufen
    await page.goto(f"{base_url}/detail/{test_product_id}")
    await page.wait_for_load_state("domcontentloaded")

    # "In den Warenkorb" Button finden
    add_to_cart = page.locator(
        "css=.btn-buy, "
        "[data-add-to-cart], "
        "button[type='submit'].buy-widget-btn"
    )

    if await add_to_cart.count() > 0:
        await add_to_cart.first.click()

        # Warten auf Feedback (Offcanvas-Cart oder Notification)
        await page.wait_for_timeout(2000)  # AJAX abwarten

        # Cart-Counter sollte sich ändern oder Offcanvas öffnet sich
        cart_indicator = page.locator(
            "css=.header-cart-total, "
            ".cart-item-count, "
            "[data-cart-widget], "
            ".offcanvas-cart"
        )

        # Irgendeiner der Indikatoren sollte reagieren
        assert await cart_indicator.count() > 0, \
            "Kein Warenkorb-Feedback nach Hinzufügen"


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_cart_accessible(page: Page, base_url: str):
    """Warenkorbseite ist erreichbar."""
    await page.goto(f"{base_url}/checkout/cart")
    await page.wait_for_load_state("domcontentloaded")

    # Prüfen, dass wir auf der Warenkorb-Seite sind
    cart_elements = page.locator(
        "css=.checkout-cart, "
        ".cart-main, "
        "[data-cart-widget], "
        ".line-item-container"
    )

    # Mindestens ein Cart-Element oder "Warenkorb leer" Meldung
    empty_cart = page.locator("css=.cart-empty, .empty-cart")

    has_cart = await cart_elements.count() > 0
    has_empty = await empty_cart.count() > 0

    assert has_cart or has_empty, \
        "Weder Warenkorb noch Leer-Meldung gefunden"


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_checkout_accessible(page: Page, base_url: str):
    """Checkout-Seite ist grundsätzlich erreichbar."""
    await page.goto(f"{base_url}/checkout/confirm")
    await page.wait_for_load_state("domcontentloaded")

    # Bei leerem Warenkorb erfolgt Redirect oder Fehlermeldung
    # Das ist OK - wir prüfen nur, ob der Endpunkt antwortet

    current_url = page.url

    # Entweder sind wir im Checkout oder wurden zum Cart umgeleitet
    is_checkout = "checkout" in current_url.lower()
    is_cart = "cart" in current_url.lower()
    is_login = "login" in current_url.lower() or "account" in current_url.lower()

    assert is_checkout or is_cart or is_login, \
        f"Unerwartete Weiterleitung: {current_url}"
