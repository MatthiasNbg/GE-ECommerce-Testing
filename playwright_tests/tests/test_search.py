"""
Such-Tests für den Shopware Shop.

Testet die Suche nach Artikelnummern:
1. Autocomplete (Live-Suggest) - zeigt Vorschläge während der Eingabe
2. Suchergebnisseite (nach Enter) - zeigt vollständige Ergebnisliste

Beide Varianten müssen das korrekte Produkt als erstes Ergebnis zeigen.
"""
import pytest
from playwright.sync_api import Page, expect

from ..conftest import accept_cookie_banner


# Testdaten: Artikelnummer -> erwartete Produkt-URL
ARTICLE_NUMBER_TEST_DATA = [
    ("862990", "p/kurzarmshirt-aus-bio-baumwolle/ge-p-862990"),
    ("863190", "p/blusenshirt-aus-bio-leinen/ge-p-863190"),
    ("693645", "p/kleiderstaender-jukai-pur/ge-p-693645"),
    ("693278", "p/polsterbett-almeno/ge-p-693278"),
    ("49415", "p/duftkissen-lavendel/ge-p-49415"),
    ("74157", "p/augen-entspannungskissen-mit-amaranth/ge-p-74157"),
    ("410933", "p/bademantel-raute-fuer-damen-und-herren/ge-p-410933"),
]


# =============================================================================
# Autocomplete-Tests (Live-Suggest während der Eingabe)
# =============================================================================

@pytest.mark.smoke
@pytest.mark.parametrize("article_number,expected_url_path", ARTICLE_NUMBER_TEST_DATA)
def test_search_autocomplete_shows_correct_product(
    page: Page,
    base_url: str,
    article_number: str,
    expected_url_path: str,
):
    """
    Testet das Autocomplete (Live-Suggest): Bei Eingabe einer Artikelnummer
    muss das korrekte Produkt als erster Vorschlag erscheinen.

    Schritte:
    1. Startseite laden
    2. Suche öffnen
    3. Artikelnummer eingeben
    4. Auf Autocomplete-Vorschläge warten
    5. Prüfen: Erster Vorschlag ist das erwartete Produkt
    """
    # Startseite laden
    page.goto(base_url)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)

    # Cookie-Banner akzeptieren
    accept_cookie_banner(page)

    # Such-Toggle klicken
    search_toggle = page.locator("button.search-toggle-btn.js-search-toggle-btn")
    search_toggle.click()
    page.wait_for_timeout(500)

    # Artikelnummer eingeben
    search_input = page.locator("input#header-main-search-input")
    expect(search_input).to_be_visible()
    search_input.fill(article_number)

    # Auf Autocomplete warten (2 Sekunden für AJAX)
    page.wait_for_timeout(2000)

    # Ersten Autocomplete-Produktvorschlag prüfen
    # Der erste Vorschlag sollte ein Produktlink sein
    first_suggest = page.locator(".search-suggest-product-link, .search-suggest-product a").first
    expect(first_suggest).to_be_visible(timeout=5000)

    # URL des ersten Vorschlags prüfen
    first_suggest_href = first_suggest.get_attribute("href")

    # Erwartete Produkt-ID muss in der URL enthalten sein
    expected_product_id = expected_url_path.split("/")[-1]  # z.B. "ge-p-862990"

    assert expected_product_id in first_suggest_href, (
        f"AUTOCOMPLETE-FEHLER für Artikelnummer {article_number}: "
        f"Erwartetes Produkt '{expected_product_id}' nicht im ersten Vorschlag. "
        f"Gefunden: {first_suggest_href}"
    )


@pytest.mark.smoke
@pytest.mark.parametrize("article_number,expected_url_path", ARTICLE_NUMBER_TEST_DATA)
def test_search_autocomplete_click_navigates_to_product(
    page: Page,
    base_url: str,
    article_number: str,
    expected_url_path: str,
):
    """
    Testet den vollständigen Autocomplete-Flow: Artikelnummer eingeben,
    auf ersten Vorschlag klicken, Produktseite wird geladen.
    """
    # Startseite laden
    page.goto(base_url)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)

    # Cookie-Banner akzeptieren
    accept_cookie_banner(page)

    # Such-Toggle klicken
    search_toggle = page.locator("button.search-toggle-btn.js-search-toggle-btn")
    search_toggle.click()
    page.wait_for_timeout(500)

    # Artikelnummer eingeben
    search_input = page.locator("input#header-main-search-input")
    expect(search_input).to_be_visible()
    search_input.fill(article_number)

    # Auf Autocomplete warten
    page.wait_for_timeout(2000)

    # Ersten Vorschlag anklicken
    first_suggest = page.locator(".search-suggest-product-link, .search-suggest-product a").first
    expect(first_suggest).to_be_visible(timeout=5000)
    first_suggest.click()

    # Auf Produktseite warten
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)

    # URL prüfen
    current_url = page.url
    expected_product_id = expected_url_path.split("/")[-1]

    assert expected_product_id in current_url, (
        f"AUTOCOMPLETE-NAVIGATION für Artikelnummer {article_number}: "
        f"Nach Klick nicht auf erwarteter Produktseite. "
        f"Erwartet: {expected_product_id}, Aktuell: {current_url}"
    )

    # Produktseite-Elemente prüfen
    product_title = page.locator("h1.product-detail-name, h1")
    expect(product_title).to_be_visible()


# =============================================================================
# Suchergebnisseite-Tests (nach Enter/Absenden)
# =============================================================================

@pytest.mark.smoke
@pytest.mark.parametrize("article_number,expected_url_path", ARTICLE_NUMBER_TEST_DATA)
def test_search_results_page_shows_correct_product(
    page: Page,
    base_url: str,
    article_number: str,
    expected_url_path: str,
):
    """
    Testet die Suchergebnisseite: Nach Eingabe einer Artikelnummer und
    Drücken von Enter muss das korrekte Produkt als erstes Ergebnis erscheinen.

    HINWEIS: Dieser Test deckt einen bekannten Bug auf - die Suchergebnisseite
    zeigt aktuell nicht immer das korrekte Produkt als erstes Ergebnis.

    Schritte:
    1. Startseite laden
    2. Suche öffnen
    3. Artikelnummer eingeben
    4. Enter drücken (zur Suchergebnisseite)
    5. Prüfen: Erstes Ergebnis ist das erwartete Produkt
    """
    # Startseite laden
    page.goto(base_url)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)

    # Cookie-Banner akzeptieren
    accept_cookie_banner(page)

    # Such-Toggle klicken
    search_toggle = page.locator("button.search-toggle-btn.js-search-toggle-btn")
    search_toggle.click()
    page.wait_for_timeout(500)

    # Artikelnummer eingeben
    search_input = page.locator("input#header-main-search-input")
    expect(search_input).to_be_visible()
    search_input.fill(article_number)

    # Enter drücken - zur Suchergebnisseite
    search_input.press("Enter")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(2000)

    # Prüfen dass wir auf der Suchergebnisseite sind
    assert "search" in page.url, f"Nicht auf Suchergebnisseite: {page.url}"

    # Erstes Suchergebnis prüfen
    first_result = page.locator(".product-box a.product-name, .product-item a, .cms-listing-col a.product-name").first
    expect(first_result).to_be_visible(timeout=5000)

    # URL des ersten Ergebnisses prüfen
    first_result_href = first_result.get_attribute("href")

    # Erwartete Produkt-ID muss in der URL enthalten sein
    expected_product_id = expected_url_path.split("/")[-1]

    assert expected_product_id in first_result_href, (
        f"SUCHERGEBNIS-FEHLER für Artikelnummer {article_number}: "
        f"Erwartetes Produkt '{expected_product_id}' nicht als erstes Ergebnis. "
        f"Gefunden: {first_result_href}"
    )


@pytest.mark.smoke
@pytest.mark.parametrize("article_number,expected_url_path", ARTICLE_NUMBER_TEST_DATA)
def test_search_results_page_click_navigates_to_product(
    page: Page,
    base_url: str,
    article_number: str,
    expected_url_path: str,
):
    """
    Testet den vollständigen Such-Flow über die Ergebnisseite:
    Artikelnummer eingeben, Enter, erstes Ergebnis klicken, Produktseite prüfen.
    """
    # Startseite laden
    page.goto(base_url)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)

    # Cookie-Banner akzeptieren
    accept_cookie_banner(page)

    # Such-Toggle klicken
    search_toggle = page.locator("button.search-toggle-btn.js-search-toggle-btn")
    search_toggle.click()
    page.wait_for_timeout(500)

    # Artikelnummer eingeben
    search_input = page.locator("input#header-main-search-input")
    expect(search_input).to_be_visible()
    search_input.fill(article_number)

    # Enter drücken
    search_input.press("Enter")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(2000)

    # Erstes Suchergebnis anklicken
    first_result = page.locator(".product-box a.product-name, .product-item a, .cms-listing-col a.product-name").first
    expect(first_result).to_be_visible(timeout=5000)
    first_result.click()

    # Auf Produktseite warten
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)

    # URL prüfen
    current_url = page.url
    expected_product_id = expected_url_path.split("/")[-1]

    assert expected_product_id in current_url, (
        f"SUCHERGEBNIS-NAVIGATION für Artikelnummer {article_number}: "
        f"Nach Klick nicht auf erwarteter Produktseite. "
        f"Erwartet: {expected_product_id}, Aktuell: {current_url}"
    )

    # Produktseite-Elemente prüfen
    product_title = page.locator("h1.product-detail-name, h1")
    expect(product_title).to_be_visible()


# =============================================================================
# Negative Tests
# =============================================================================

@pytest.mark.smoke
def test_search_no_results_for_invalid_article(page: Page, base_url: str):
    """Testet, dass bei ungültiger Artikelnummer keine/passende Ergebnisse kommen."""
    # Startseite laden
    page.goto(base_url)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)

    # Cookie-Banner akzeptieren
    accept_cookie_banner(page)

    # Such-Toggle klicken
    search_toggle = page.locator("button.search-toggle-btn.js-search-toggle-btn")
    search_toggle.click()
    page.wait_for_timeout(500)

    # Ungültige Artikelnummer eingeben
    search_input = page.locator("input#header-main-search-input")
    expect(search_input).to_be_visible()
    search_input.fill("99999999")

    # Enter drücken
    search_input.press("Enter")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(2000)

    # Entweder keine Ergebnisse oder "keine Ergebnisse" Meldung
    no_results = page.locator(".search-no-results, .cms-element-text:has-text('keine'), .alert:has-text('keine')")
    product_results = page.locator(".product-box, .product-item")

    has_no_results_message = no_results.count() > 0
    has_products = product_results.count() > 0

    # Test ist erfolgreich wenn: keine Produkte ODER "keine Ergebnisse" Meldung
    assert has_no_results_message or not has_products, (
        "Bei ungültiger Artikelnummer wurden unerwartete Ergebnisse angezeigt"
    )
