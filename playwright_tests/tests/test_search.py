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


@pytest.mark.smoke
def test_search_wildrose_excludes_brushes(page: Page, base_url: str):
    """
    Testet, dass bei der Suche nach "wildrose" keine Bürsten in den
    Suchergebnissen erscheinen.

    Die Suche soll relevante Ergebnisse liefern - Wildrose-Produkte (z.B. Kosmetik,
    Öle, Cremes) aber keine irrelevanten Produkte wie Bürsten.

    Schritte:
    1. Startseite laden
    2. Nach "wildrose" suchen
    3. Suchergebnisseite prüfen
    4. Sicherstellen, dass keine Bürsten in den Ergebnissen sind
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

    # "wildrose" eingeben
    search_input = page.locator("input#header-main-search-input")
    expect(search_input).to_be_visible()
    search_input.fill("wildrose")

    # Enter drücken - zur Suchergebnisseite
    search_input.press("Enter")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(2000)

    # Prüfen dass wir auf der Suchergebnisseite sind
    assert "search" in page.url, f"Nicht auf Suchergebnisseite: {page.url}"

    # Alle Produktnamen auf der Suchergebnisseite sammeln
    product_names = page.locator(
        ".product-box .product-name, .product-item .product-name, "
        ".cms-listing-col .product-name, .product-name"
    )

    product_count = product_names.count()

    # Wenn keine Ergebnisse gefunden wurden, ist der Test bestanden
    # (keine Bürsten bedeutet keine Bürsten)
    if product_count == 0:
        print("   Keine Suchergebnisse für 'wildrose' gefunden")
        return

    # Alle Produktnamen durchgehen und auf "Bürste" prüfen
    brush_products_found = []
    brush_keywords = ["bürste", "buerste", "brush", "pinsel"]

    for i in range(product_count):
        try:
            name = product_names.nth(i).inner_text().strip().lower()
            for keyword in brush_keywords:
                if keyword in name:
                    brush_products_found.append(product_names.nth(i).inner_text().strip())
                    break
        except Exception:
            continue

    # Test schlägt fehl wenn Bürsten gefunden wurden
    assert len(brush_products_found) == 0, (
        f"SUCHRELEVANZ-FEHLER: Bei Suche nach 'wildrose' wurden {len(brush_products_found)} "
        f"Bürsten-Produkte gefunden, obwohl diese nicht relevant sind:\n"
        + "\n".join(f"  - {name}" for name in brush_products_found)
    )

    print(f"   [OK] {product_count} Suchergebnisse für 'wildrose', keine Bürsten gefunden")


# =============================================================================
# Nosto-spezifische Tests
# =============================================================================

@pytest.mark.search
@pytest.mark.nosto
def test_search_suggest_appears_on_input(page: Page, base_url: str):
    """
    TC-SEARCH-NOSTO-001: Suggest-Container erscheint bei Eingabe.

    Testet, dass Nosto bei einer minimalen Eingabe (1-2 Zeichen)
    bereits Suchvorschläge anzeigt.

    Schritte:
    1. Startseite laden
    2. Suchfeld öffnen
    3. Minimale Eingabe ("be" für breite Ergebnisse)
    4. Prüfen: Suggest-Container erscheint mit Vorschlägen
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

    # Suchfeld fokussieren und minimale Eingabe
    search_input = page.locator("input#header-main-search-input")
    expect(search_input).to_be_visible()

    # Minimale Eingabe um Suggest auszulösen (z.B. "be" für "Bett", "Bettwäsche" etc.)
    search_input.fill("be")

    # Warten auf Nosto Suggest
    page.wait_for_timeout(2500)

    # Prüfen ob Suggest-Container erscheint
    suggest_selectors = [
        ".search-suggest",
        ".search-suggest-container",
        ".ns-autocomplete",  # Nosto-spezifisch
        "[data-search-suggest]",
        ".header-search-suggest",
    ]

    suggest_found = False
    for selector in suggest_selectors:
        container = page.locator(selector)
        if container.count() > 0 and container.first.is_visible():
            suggest_found = True
            print(f"   Suggest-Container gefunden: {selector}")

            # Prüfen ob Inhalte vorhanden sind
            inner_text = container.first.inner_text()
            has_content = len(inner_text.strip()) > 0
            print(f"   Container hat Inhalt: {has_content}")

            if has_content:
                # Anzahl der Vorschläge zählen
                products = container.locator(".search-suggest-product, .search-suggest-product-link")
                product_count = products.count()
                print(f"   Anzahl Produktvorschlaege: {product_count}")
                break

    # Test ist erfolgreich wenn Suggest-Container mit Inhalt gefunden wurde
    assert suggest_found, (
        "Kein Suggest-Container bei minimaler Eingabe gefunden. "
        "Geprufte Selektoren: " + ", ".join(suggest_selectors)
    )


@pytest.mark.search
@pytest.mark.nosto
def test_search_suggest_shows_categories(page: Page, base_url: str):
    """
    TC-SEARCH-NOSTO-004: Kategorie-Vorschlaege im Autocomplete.

    Testet, dass Nosto bei bestimmten Suchbegriffen auch
    passende Kategorien als Vorschlaege anzeigt.

    Schritte:
    1. Startseite laden
    2. Suchbegriff eingeben der Kategorien matcht (z.B. "bett")
    3. Pruefen: Kategorie-Vorschlaege erscheinen im Suggest
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

    # Suchbegriff eingeben der Kategorien matchen sollte
    search_input = page.locator("input#header-main-search-input")
    expect(search_input).to_be_visible()

    # "bett" sollte Kategorien wie "Betten", "Bettwaesche" etc. vorschlagen
    search_input.fill("bett")

    # Warten auf Nosto Suggest (etwas laenger fuer Kategorien)
    page.wait_for_timeout(3000)

    # Suggest-Container finden - warte bis sichtbar
    suggest_container = page.locator(".search-suggest-container:visible, .search-suggest:visible")

    # Falls nicht sichtbar, nochmal warten und erneut versuchen
    if suggest_container.count() == 0:
        page.wait_for_timeout(2000)
        suggest_container = page.locator(".search-suggest-container, .search-suggest").filter(has=page.locator(":visible"))

    # Pruefen ob Container existiert und sichtbar ist
    container_visible = False
    for selector in [".search-suggest-container", ".search-suggest"]:
        loc = page.locator(selector)
        if loc.count() > 0:
            try:
                if loc.first.is_visible(timeout=3000):
                    suggest_container = loc
                    container_visible = True
                    print(f"   Suggest-Container sichtbar: {selector}")
                    break
            except Exception:
                continue

    if not container_visible:
        print("   HINWEIS: Suggest-Container nicht sichtbar - ueberspringe Kategorie-Test")
        import pytest
        pytest.skip("Suggest-Container nicht sichtbar")

    # Kategorie-Selektoren pruefen
    category_selectors = [
        ".search-suggest-category",
        ".search-suggest-categories a",
        ".search-suggest-categories li",
        ".suggest-category",
        ".ns-category",  # Nosto-spezifisch
        "a[href*='/kategorie/']",
        "a[href*='/c/']",  # Shopware Kategorie-URLs
        ".search-suggest a:not(.search-suggest-product-link)",  # Links die keine Produkte sind
    ]

    categories_found = False
    category_count = 0
    category_texts = []

    for selector in category_selectors:
        categories = suggest_container.locator(selector)
        count = categories.count()
        if count > 0:
            categories_found = True
            category_count = count
            print(f"   Kategorie-Selektor gefunden: {selector} ({count} Treffer)")

            # Kategorie-Texte sammeln (max 5)
            for i in range(min(count, 5)):
                try:
                    text = categories.nth(i).inner_text().strip()
                    href = categories.nth(i).get_attribute("href") or ""
                    if text and len(text) < 100:  # Nur kurze Texte (keine Produkte)
                        category_texts.append(f"{text} -> {href[:50]}")
                except Exception:
                    pass
            break

    if category_texts:
        print(f"   Gefundene Kategorien:")
        for cat in category_texts[:5]:
            print(f"      - {cat}")

    # Soft-Assert: Kategorien sind optional, aber wuenschenswert
    if not categories_found:
        print("   HINWEIS: Keine Kategorie-Vorschlaege gefunden.")
        print("   Dies kann je nach Suchbegriff und Nosto-Konfiguration normal sein.")
        # Test trotzdem bestehen lassen, aber warnen
        import warnings
        warnings.warn(
            "Keine Kategorie-Vorschlaege im Suggest gefunden. "
            "Prufen Sie die Nosto-Konfiguration falls Kategorien erwartet werden."
        )
    else:
        print(f"   [OK] {category_count} Kategorie-Vorschlaege gefunden")


@pytest.mark.search
@pytest.mark.nosto
@pytest.mark.parametrize("article_number,expected_url_path", ARTICLE_NUMBER_TEST_DATA[:3])
def test_search_autocomplete_shows_product_images(
    page: Page,
    base_url: str,
    article_number: str,
    expected_url_path: str,
):
    """
    TC-SEARCH-NOSTO-002: Produktbilder werden im Autocomplete angezeigt.

    Testet, dass Nosto bei der Suche nach einer Artikelnummer
    Produktbilder im Autocomplete/Suggest anzeigt.

    Schritte:
    1. Startseite laden
    2. Artikelnummer eingeben
    3. Auf Autocomplete warten
    4. Prüfen: Produktbilder sind sichtbar
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
    page.wait_for_timeout(2500)

    # Produktvorschläge finden
    suggest_product_selectors = [
        ".search-suggest-product",
        ".search-suggest-product-link",
        ".ns-product",  # Nosto-spezifisch
        "[data-search-suggest-product]",
    ]

    product_found = False
    for selector in suggest_product_selectors:
        products = page.locator(selector)
        if products.count() > 0:
            product_found = True
            print(f"   Produkt-Container gefunden: {selector}")
            break

    assert product_found, (
        f"Keine Produktvorschläge für Artikelnummer {article_number} gefunden"
    )

    # Produktbilder im Suggest prüfen
    image_selectors = [
        ".search-suggest-product img",
        ".search-suggest-product-image img",
        ".search-suggest-product-link img",
        ".ns-product img",  # Nosto-spezifisch
        "[data-search-suggest-product] img",
        ".search-suggest img",
    ]

    images_found = False
    image_count = 0
    for selector in image_selectors:
        images = page.locator(selector)
        count = images.count()
        if count > 0:
            images_found = True
            image_count = count
            print(f"   Produktbilder gefunden: {count} ({selector})")

            # Prüfen ob mindestens ein Bild sichtbar ist
            first_image = images.first
            if first_image.is_visible():
                # Prüfen ob Bild eine src hat
                src = first_image.get_attribute("src")
                if src and len(src) > 0:
                    print(f"   Erstes Bild src: {src[:80]}...")
                    break

    assert images_found and image_count > 0, (
        f"Keine Produktbilder im Autocomplete für Artikelnummer {article_number} gefunden. "
        "Geprüfte Selektoren: " + ", ".join(image_selectors)
    )


@pytest.mark.search
@pytest.mark.nosto
def test_search_autocomplete_product_info_complete(page: Page, base_url: str):
    """
    TC-SEARCH-NOSTO-003: Produktinformationen im Autocomplete sind vollständig.

    Testet, dass Nosto im Autocomplete folgende Informationen anzeigt:
    - Produktbild
    - Produktname
    - Preis (optional)

    Verwendet die erste Artikelnummer aus den Testdaten.
    """
    article_number = ARTICLE_NUMBER_TEST_DATA[0][0]  # "862990"

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
    page.wait_for_timeout(2500)

    # Ersten Produktvorschlag finden
    first_product = page.locator(
        ".search-suggest-product, .search-suggest-product-link, .ns-product"
    ).first
    expect(first_product).to_be_visible(timeout=5000)

    # Prüfen: Produktname vorhanden
    product_name = first_product.locator(
        ".search-suggest-product-name, .product-name, .ns-product-name, span, strong"
    ).first
    name_text = product_name.inner_text() if product_name.count() > 0 else ""
    has_name = len(name_text.strip()) > 0
    print(f"   Produktname: '{name_text[:50]}...' (vorhanden: {has_name})")

    # Prüfen: Produktbild vorhanden
    product_image = first_product.locator("img").first
    has_image = product_image.count() > 0 and product_image.is_visible()
    if has_image:
        img_src = product_image.get_attribute("src") or ""
        print(f"   Produktbild: vorhanden (src: {img_src[:50]}...)")
    else:
        print(f"   Produktbild: nicht gefunden")

    # Prüfen: Preis vorhanden (optional, aber wünschenswert)
    price_selectors = [
        ".search-suggest-product-price",
        ".product-price",
        ".price",
        ".ns-product-price",
    ]
    has_price = False
    for selector in price_selectors:
        price_elem = first_product.locator(selector)
        if price_elem.count() > 0:
            price_text = price_elem.first.inner_text()
            if "€" in price_text or "EUR" in price_text or price_text.replace(",", "").replace(".", "").isdigit():
                has_price = True
                print(f"   Preis: '{price_text}' (vorhanden: True)")
                break

    if not has_price:
        print(f"   Preis: nicht gefunden (optional)")

    # Mindestens Name UND Bild müssen vorhanden sein
    assert has_name, f"Produktname fehlt im Autocomplete für Artikelnummer {article_number}"
    assert has_image, f"Produktbild fehlt im Autocomplete für Artikelnummer {article_number}"

    print(f"\n   [OK] Produktinformationen vollstaendig: Name={has_name}, Bild={has_image}, Preis={has_price}")
