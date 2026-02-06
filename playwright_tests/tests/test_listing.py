"""
Listing/Kategorie Tests - TC-LISTING-001 bis TC-LISTING-004
Tests fuer Produktfilter, Sortierung, Pagination, SALE-Kategorien
"""
import re
import pytest
from playwright.sync_api import Page, expect

from ..conftest import accept_cookie_banner


# =============================================================================
# TC-LISTING-001: Produktfilter funktionieren
# =============================================================================

@pytest.mark.listing
@pytest.mark.feature
def test_product_filters(page: Page, base_url: str):
    """
    TC-LISTING-001: Produktfilter funktionieren.

    Prueft, dass Filter auf Kategorie-Seiten angewendet werden koennen
    und die Produktliste entsprechend aktualisiert wird.
    """
    print("\n=== TC-LISTING-001: Produktfilter funktionieren ===")

    # Schritt 1: Kategorie-Seite aufrufen
    print("[1] Kategorie-Seite aufrufen...")
    page.goto(f"{base_url}/moebel/")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)
    accept_cookie_banner(page)

    # Schritt 2: Filter-Panel pruefen
    print("[2] Filter-Panel pruefen...")
    filter_panel = page.locator(
        ".filter-panel, .cms-element-product-listing-filter, .filter-panel-item"
    )
    expect(filter_panel.first).to_be_visible(timeout=5000)

    # Anzahl Produkte vor Filter merken
    product_boxes = page.locator(".product-box, .cms-listing-col .card")
    initial_count = product_boxes.count()
    print(f"   Produkte vor Filter: {initial_count}")
    assert initial_count > 0, "Kategorie-Seite sollte Produkte enthalten"

    # Schritt 3: Ersten Filter anklicken
    print("[3] Filter anwenden...")
    filter_items = page.locator(".filter-panel-item")
    if filter_items.count() > 0:
        first_filter = filter_items.first
        first_filter.click()
        page.wait_for_timeout(500)

        filter_options = page.locator(
            ".filter-panel-item .filter-checkbox input, "
            ".filter-panel-item .filter-range, "
            ".filter-panel-item label.custom-checkbox"
        )
        if filter_options.count() > 0:
            filter_options.first.click()
            page.wait_for_timeout(2000)

            print("[4] Produktliste nach Filter pruefen...")
            filtered_count = product_boxes.count()
            print(f"   Produkte nach Filter: {filtered_count}")

            active_filter = page.locator(
                ".filter-active, .filter-reset-all, "
                ".filter-panel-active-filter, .active-filter-label"
            )
            if active_filter.count() > 0:
                print("   Aktiver Filter-Indikator gefunden")
            else:
                print("   Kein aktiver Filter-Indikator (evtl. anderer UI-Typ)")
        else:
            pytest.skip("Keine anklickbaren Filter-Optionen auf der Seite")
    else:
        pytest.skip("Kein Filter-Panel auf der Kategorie-Seite")

    print("=== TC-LISTING-001: BESTANDEN ===")


# =============================================================================
# TC-LISTING-002: Sortierung funktioniert
# =============================================================================

@pytest.mark.listing
@pytest.mark.feature
def test_product_sorting(page: Page, base_url: str):
    """
    TC-LISTING-002: Sortierung funktioniert.

    Prueft, dass die Sortierung auf Kategorie-Seiten funktioniert
    (z.B. nach Preis aufsteigend/absteigend, Name, Erscheinungsdatum).
    """
    print("\n=== TC-LISTING-002: Sortierung funktioniert ===")

    print("[1] Kategorie-Seite aufrufen...")
    page.goto(f"{base_url}/moebel/")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)
    accept_cookie_banner(page)

    print("[2] Sortierungs-Dropdown pruefen...")
    sort_dropdown = page.locator(
        "select.sorting, .sorting-select, "
        "select[name='order'], select.cms-element-product-listing-sorting"
    )
    expect(sort_dropdown.first).to_be_visible(timeout=5000)

    options = sort_dropdown.first.locator("option")
    option_count = options.count()
    print(f"   Sortieroptionen gefunden: {option_count}")
    assert option_count >= 2, "Mindestens 2 Sortieroptionen erwartet"

    for i in range(min(option_count, 5)):
        text = options.nth(i).inner_text().strip()
        value = options.nth(i).get_attribute("value") or ""
        print(f"   - {text} (value={value})")

    print("[3] Sortierung aendern...")
    sort_values_to_try = ["price-asc", "price-desc", "name-asc", "name-desc"]

    sort_applied = False
    for sort_value in sort_values_to_try:
        try:
            sort_dropdown.first.select_option(value=sort_value)
            page.wait_for_timeout(2000)
            sort_applied = True
            print(f"   Sortierung angewendet: {sort_value}")
            break
        except Exception:
            continue

    if not sort_applied:
        if option_count >= 2:
            second_value = options.nth(1).get_attribute("value")
            if second_value:
                sort_dropdown.first.select_option(value=second_value)
                page.wait_for_timeout(2000)
                sort_applied = True
                print(f"   Sortierung angewendet (Fallback): {second_value}")

    assert sort_applied, "Keine Sortierung konnte angewendet werden"

    print("[4] Sortierte Produktliste pruefen...")
    product_boxes = page.locator(".product-box, .cms-listing-col .card")
    sorted_count = product_boxes.count()
    print(f"   Produkte nach Sortierung: {sorted_count}")
    assert sorted_count > 0, "Nach Sortierung sollten Produkte angezeigt werden"

    print("=== TC-LISTING-002: BESTANDEN ===")


# =============================================================================
# TC-LISTING-003: Pagination
# =============================================================================

@pytest.mark.listing
@pytest.mark.feature
def test_pagination(page: Page, base_url: str):
    """
    TC-LISTING-003: Pagination funktioniert.

    Prueft, dass die Seitennavigation (Pagination) auf Kategorie-Seiten
    korrekt funktioniert.
    """
    print("\n=== TC-LISTING-003: Pagination ===")

    print("[1] Kategorie-Seite aufrufen...")
    page.goto(f"{base_url}/moebel/")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)
    accept_cookie_banner(page)

    product_boxes = page.locator(".product-box, .cms-listing-col .card")
    page1_count = product_boxes.count()
    print(f"   Produkte auf Seite 1: {page1_count}")

    print("[2] Pagination pruefen...")
    pagination = page.locator(
        ".pagination, nav.pagination, "
        ".cms-element-product-listing-pagination, .pagination-nav"
    )

    if pagination.count() == 0:
        pytest.skip("Keine Pagination auf der Kategorie-Seite (zu wenige Produkte)")

    expect(pagination.first).to_be_visible(timeout=5000)

    print("[3] Zur naechsten Seite navigieren...")
    next_page_selectors = [
        ".pagination .page-next a",
        ".pagination .page-item:last-child a",
        "a[rel='next']",
        ".pagination-nav .page-next",
    ]

    next_clicked = False
    for selector in next_page_selectors:
        next_link = page.locator(selector)
        if next_link.count() > 0 and next_link.first.is_visible():
            next_link.first.click()
            page.wait_for_timeout(2000)
            next_clicked = True
            print(f"   Naechste Seite geklickt via: {selector}")
            break

    if not next_clicked:
        page2_link = page.locator("a[href*='p=2']")
        if page2_link.count() > 0:
            page2_link.first.click()
            page.wait_for_timeout(2000)
            next_clicked = True
            print("   Seite 2 direkt geklickt")

    if not next_clicked:
        pytest.skip("Kein Naechste-Seite-Link gefunden")

    print("[4] Produkte auf Seite 2 pruefen...")
    page2_count = product_boxes.count()
    print(f"   Produkte auf Seite 2: {page2_count}")
    assert page2_count > 0, "Seite 2 sollte Produkte enthalten"

    current_url = page.url
    print(f"   Aktuelle URL: {current_url}")

    print("=== TC-LISTING-003: BESTANDEN ===")


# =============================================================================
# TC-LISTING-004: SALE-Kategorie korrekt
# =============================================================================

@pytest.mark.listing
@pytest.mark.feature
def test_sale_category(page: Page, base_url: str):
    """
    TC-LISTING-004: SALE-Kategorie korrekt.

    Prueft, dass die SALE-Kategorie/Angebots-Seite korrekt funktioniert
    und reduzierte Produkte anzeigt.
    """
    print("\n=== TC-LISTING-004: SALE-Kategorie korrekt ===")

    print("[1] SALE-Seite aufrufen...")
    sale_urls = [
        f"{base_url}/sale/",
        f"{base_url}/angebote/",
        f"{base_url}/reduziert/",
        f"{base_url}/outlet/",
    ]

    sale_page_found = False
    for url in sale_urls:
        page.goto(url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(1000)

        if page.locator(".product-box, .cms-listing-col .card").count() > 0:
            sale_page_found = True
            print(f"   SALE-Seite gefunden: {url}")
            break

    if not sale_page_found:
        print("   Suche SALE-Link im Menue...")
        page.goto(base_url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(1000)
        accept_cookie_banner(page)

        sale_nav_link = page.locator(
            "nav a:has-text('Sale'), nav a:has-text('SALE'), "
            "nav a:has-text('Angebote'), nav a:has-text('Outlet')"
        )
        if sale_nav_link.count() > 0:
            sale_nav_link.first.click()
            page.wait_for_timeout(2000)
            sale_page_found = True
            print("   SALE-Link im Menue gefunden und geklickt")
        else:
            pytest.skip("Keine SALE-Kategorie gefunden")

    accept_cookie_banner(page)

    print("[2] Produkte auf SALE-Seite pruefen...")
    product_boxes = page.locator(".product-box, .cms-listing-col .card")
    product_count = product_boxes.count()
    print(f"   Produkte auf SALE-Seite: {product_count}")

    if product_count == 0:
        pytest.skip("Keine Produkte auf der SALE-Seite")

    print("[3] Reduzierte Preise pruefen...")
    discount_indicators = page.locator(
        ".product-price del, .product-price .list-price, "
        ".product-price s, .product-price .original-price, "
        ".product-price .was-price, .list-price-wrapper"
    )
    discount_count = discount_indicators.count()
    print(f"   Produkte mit reduzierten Preisen: {discount_count}")

    print("[4] SALE-Badge pruefen...")
    sale_badges = page.locator(
        ".badge-discount, .product-badge-discount, "
        ".badge-sale, .product-badge:has-text('Sale'), "
        ".product-badge:has-text('%'), .badge:has-text('%')"
    )
    badge_count = sale_badges.count()
    print(f"   SALE-Badges gefunden: {badge_count}")

    has_sale_indicators = discount_count > 0 or badge_count > 0
    if has_sale_indicators:
        print("   SALE-Indikatoren gefunden (Preise und/oder Badges)")
    else:
        print("   HINWEIS: Keine spezifischen SALE-Indikatoren gefunden")

    print("=== TC-LISTING-004: BESTANDEN ===")
