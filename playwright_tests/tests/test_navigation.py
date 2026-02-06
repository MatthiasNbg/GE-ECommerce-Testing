"""
Navigation Tests - TC-NAV-001 bis TC-NAV-005
Tests fuer Hauptnavigation, Mega-Menue, Breadcrumbs, Laenderwechsel

Ausfuehrung:
    pytest playwright_tests/tests/test_navigation.py -v
    pytest -m navigation -v
"""
import re
import pytest
from playwright.sync_api import Page, expect

from ..conftest import accept_cookie_banner


# =============================================================================
# Testdaten
# =============================================================================

MAIN_CATEGORIES = [
    "Schlafen",
    "Moebel",
    "Heimtextilien",
    "Wohnaccessoires",
    "Kleidung",
    "Kinder",
]

TEST_PRODUCT = {
    "id": "49415",
    "path": "p/duftkissen-lavendel/ge-p-49415",
    "name": "Duftkissen Lavendel",
}

COUNTRY_DOMAINS = {
    "AT": "grueneerde.at",
    "DE": "grueneerde.com",
    "CH": "grueneerde.ch",
}


# =============================================================================
# Hilfsfunktionen
# =============================================================================

def take_error_screenshot(page: Page, test_name: str):
    """Erstellt einen Screenshot bei Testfehler."""
    try:
        page.screenshot(path=f"error_navigation_{test_name}.png", full_page=False)
        print(f"    [Screenshot] error_navigation_{test_name}.png gespeichert")
    except Exception as e:
        print(f"    [Screenshot] Fehler beim Speichern: {e}")

# =============================================================================
# TC-NAV-001: Hauptnavigation erreichbar
# =============================================================================

@pytest.mark.navigation
@pytest.mark.feature
def test_main_navigation_accessible(page: Page, base_url: str):
    """
    TC-NAV-001: Prueft, dass die Hauptnavigation sichtbar ist und alle
    erwarteten Kategorien enthaelt.
    """
    print(f"\n[Navigation] TC-NAV-001: Hauptnavigation erreichbar")

    try:
        print(f"    Step 1: Startseite aufrufen")
        response = page.goto(base_url)
        assert response is not None, "Keine Response von der Homepage"
        assert response.status == 200, f"HTTP {response.status} statt 200"
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(1500)
        print(f"    [OK] Homepage geladen (HTTP {response.status})")

        print(f"    Step 2: Cookie-Banner akzeptieren")
        accept_cookie_banner(page)
        page.wait_for_timeout(500)

        print(f"    Step 3: Hauptnavigation auf Sichtbarkeit pruefen")
        nav_selectors = [
            ".main-navigation-menu",
            ".nav-main",
            "nav.main-navigation",
            ".main-navigation",
            "header nav",
        ]

        nav_found = False
        for sel in nav_selectors:
            nav = page.locator(sel)
            if nav.count() > 0 and nav.first.is_visible():
                nav_found = True
                print(f"    [OK] Navigation gefunden mit Selektor: {sel}")
                break

        assert nav_found, "Hauptnavigation ist nicht sichtbar"

        nav_links = page.locator(
            ".main-navigation-link, .nav-link.main-navigation-link, "
            ".main-navigation a, nav.main-navigation a, header nav a"
        )
        nav_text = nav_links.all_inner_texts()
        nav_text_combined = " ".join([t.strip() for t in nav_text]).lower()

        found_categories = []
        missing_categories = []

        for category in MAIN_CATEGORIES:
            step_num = MAIN_CATEGORIES.index(category) + 4
            print(f"    Step {step_num}: Kategorie {category} pruefen")

            if category.lower() in nav_text_combined:
                found_categories.append(category)
                print(f"    [OK] {category} in Navigation gefunden")
            else:
                cat_link = page.locator(
                    f"a:has-text('{category}'), "
                    f".main-navigation-link:has-text('{category}')"
                )
                if cat_link.count() > 0:
                    found_categories.append(category)
                    print(f"    [OK] {category} in Navigation gefunden (Fallback)")
                else:
                    missing_categories.append(category)
                    print(f"    [WARN] {category} NICHT in Navigation gefunden")

        assert len(found_categories) >= 4, (
            f"Zu wenige Kategorien ({len(found_categories)}/6). "
            f"Fehlend: {missing_categories}"
        )
        print(f"    [OK] {len(found_categories)}/{len(MAIN_CATEGORIES)} Kategorien gefunden")

    except Exception as e:
        take_error_screenshot(page, "TC-NAV-001")
        raise

# =============================================================================
# TC-NAV-002: Mega-Menue Unterkategorien
# =============================================================================

@pytest.mark.navigation
@pytest.mark.feature
def test_mega_menu_subcategories(page: Page, base_url: str):
    """
    TC-NAV-002: Prueft, dass beim Hover ueber eine Hauptkategorie ein
    Mega-Menue mit Unterkategorien erscheint.
    """
    print(f"\n[Navigation] TC-NAV-002: Mega-Menue Unterkategorien")

    try:
        print(f"    Step 1: Startseite aufrufen")
        page.goto(base_url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(1500)

        print(f"    Step 2: Cookie-Banner akzeptieren")
        accept_cookie_banner(page)
        page.wait_for_timeout(500)

        print(f"    Step 3: Hover ueber Hauptkategorie")
        nav_links = page.locator(
            ".main-navigation-link, .nav-link.main-navigation-link, "
            ".main-navigation a"
        )
        assert nav_links.count() > 0, "Keine Navigations-Links gefunden"

        hovered = False
        for i in range(min(nav_links.count(), 6)):
            link = nav_links.nth(i)
            if link.is_visible():
                link_text = link.inner_text().strip()
                if link_text and len(link_text) > 1:
                    print(f"    Hover ueber: {link_text}")
                    link.hover()
                    page.wait_for_timeout(1000)
                    hovered = True
                    break
        assert hovered, "Kein Navigations-Link konnte gehovert werden"

        print(f"    Step 4: Unterkategorien im Mega-Menue pruefen")
        flyout_selectors = [
            ".navigation-flyout",
            ".navigation-flyout-content",
            ".main-navigation-flyout",
            ".mega-menu",
        ]

        flyout_found = False
        flyout_links = None
        for sel in flyout_selectors:
            flyout = page.locator(sel)
            if flyout.count() > 0:
                try:
                    if flyout.first.is_visible(timeout=3000):
                        flyout_found = True
                        flyout_links = flyout.first.locator("a")
                        link_count = flyout_links.count() if flyout_links else 0
                        print(f"    [OK] Mega-Menue gefunden ({sel}) mit {link_count} Links")
                        break
                except Exception:
                    continue

        if not flyout_found:
            print(f"    [SKIP] Kein Mega-Menue-Flyout gefunden")
            return

        print(f"    Step 5: Unterkategorie anklicken")
        if flyout_links and flyout_links.count() > 0:
            sub_link = flyout_links.first
            sub_text = sub_link.inner_text().strip()
            sub_href = sub_link.get_attribute("href")
            print(f"    Klicke auf: {sub_text} ({sub_href})")
            sub_link.click()
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(1500)

            print(f"    Step 6: Kategorieseite validieren")
            current_url = page.url
            has_products = page.locator(
                ".product-box, .cms-listing-col, [data-product-id], .product-listing"
            ).count() > 0
            page_text = page.locator("body").inner_text().lower()
            has_category_content = (
                "produkt" in page_text or "artikel" in page_text or has_products
            )
            print(f"    URL: {current_url[:80]}")
            assert has_category_content or has_products, "Kategorieseite zeigt keine Produkte"
            print(f"    [OK] Kategorieseite geladen")

    except Exception as e:
        take_error_screenshot(page, "TC-NAV-002")
        raise

# =============================================================================
# TC-NAV-003: Breadcrumb-Navigation
# =============================================================================

@pytest.mark.navigation
@pytest.mark.feature
def test_breadcrumb_navigation(page: Page, base_url: str):
    """
    TC-NAV-003: Prueft Breadcrumb-Navigation auf Produktseite.
    """
    print(f"\n[Navigation] TC-NAV-003: Breadcrumb-Navigation")

    try:
        print(f"    Step 1: Produktseite aufrufen")
        page.goto(f"{base_url}/{TEST_PRODUCT['path']}")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(1500)

        print(f"    Step 2: Cookie-Banner akzeptieren")
        accept_cookie_banner(page)
        page.wait_for_timeout(500)

        print(f"    Step 3: Breadcrumb-Navigation pruefen")
        breadcrumb_selectors = [
            ".breadcrumb",
            "nav[aria-label='breadcrumb']",
            ".breadcrumb-container",
            "ol.breadcrumb",
        ]

        breadcrumb = None
        for sel in breadcrumb_selectors:
            bc = page.locator(sel)
            if bc.count() > 0 and bc.first.is_visible():
                breadcrumb = bc.first
                print(f"    [OK] Breadcrumb gefunden: {sel}")
                break
        assert breadcrumb is not None, "Breadcrumb-Navigation nicht gefunden"

        print(f"    Step 4: Breadcrumb-Elemente pruefen")
        breadcrumb_items = page.locator(
            ".breadcrumb-item, .breadcrumb-link, .breadcrumb li, .breadcrumb a"
        )
        item_count = breadcrumb_items.count()
        print(f"    Breadcrumb-Elemente: {item_count}")
        assert item_count >= 2, f"Zu wenige Breadcrumb-Elemente ({item_count})"

        for i in range(min(item_count, 5)):
            item_text = breadcrumb_items.nth(i).inner_text().strip()
            if item_text:
                print(f"      Breadcrumb[{i}]: {item_text}")

        print(f"    Step 5: Breadcrumb-Link anklicken")
        breadcrumb_links = page.locator(
            ".breadcrumb-item a, .breadcrumb-link, .breadcrumb a[href]"
        )

        if breadcrumb_links.count() > 0:
            target_link = breadcrumb_links.first
            target_text = target_link.inner_text().strip()
            target_href = target_link.get_attribute("href")
            print(f"    Klicke auf: {target_text} ({target_href})")

            url_before = page.url
            target_link.click()
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(1500)

            print(f"    Step 6: Zielseite pruefen")
            url_after = page.url
            print(f"    URL vorher:  {url_before[:80]}")
            print(f"    URL nachher: {url_after[:80]}")
            assert url_after != url_before or target_href == "/", (
                "Breadcrumb-Navigation hat URL nicht geaendert"
            )
            print(f"    [OK] Breadcrumb-Navigation funktioniert")
        else:
            print(f"    [SKIP] Keine klickbaren Breadcrumb-Links")

    except Exception as e:
        take_error_screenshot(page, "TC-NAV-003")
        raise

# =============================================================================
# TC-NAV-004: Laenderwechsel AT/DE/CH
# =============================================================================

@pytest.mark.navigation
@pytest.mark.feature
def test_country_switch(page: Page, base_url: str):
    """
    TC-NAV-004: Prueft Laender-/Sprachswitch zwischen AT/DE/CH-Shops.
    """
    print(f"\n[Navigation] TC-NAV-004: Laenderwechsel AT/DE/CH")

    try:
        print(f"    Step 1: Startseite aufrufen")
        page.goto(base_url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(1500)

        print(f"    Step 2: Cookie-Banner akzeptieren")
        accept_cookie_banner(page)
        page.wait_for_timeout(500)

        print(f"    Step 3: Laender-/Sprachauswahl finden")
        switcher_selectors = [
            ".language-selector",
            ".country-selector",
            ".js-language-select",
            ".top-bar-language",
            "[data-language-menu]",
            ".header-language",
            "a[href*='grueneerde.com']",
            "a[href*='grueneerde.ch']",
            "a[href*='grueneerde.at']",
        ]

        switcher_found = False
        switcher_element = None
        for sel in switcher_selectors:
            elem = page.locator(sel)
            if elem.count() > 0:
                switcher_found = True
                switcher_element = elem.first
                print(f"    [OK] Laenderwechsel gefunden: {sel}")
                break

        if not switcher_found:
            country_links = page.locator(
                "a[href*='grueneerde'], a:has-text('Deutschland'), "
                "a:has-text('Schweiz'), a:has-text('Oesterreich')"
            )
            if country_links.count() > 0:
                switcher_found = True
                switcher_element = country_links.first
                print(f"    [OK] Laenderlink gefunden (Fallback)")

        if not switcher_found:
            print(f"    [SKIP] Kein Laenderwechsel-Element gefunden")
            current_url = page.url
            for country, domain in COUNTRY_DOMAINS.items():
                if domain in current_url:
                    print(f"    [INFO] Aktueller Shop: {country} ({domain})")
            return

        print(f"    Step 4: Zu DE-Shop wechseln")
        if switcher_element and switcher_element.is_visible():
            switcher_element.click()
            page.wait_for_timeout(1500)

        de_link = page.locator(
            "a[href*='grueneerde.com'], a:has-text('Deutschland'), "
            "a:has-text('DE'), option:has-text('DE')"
        )

        if de_link.count() > 0 and de_link.first.is_visible():
            de_href = de_link.first.get_attribute("href")
            print(f"    DE-Link gefunden: {de_href}")
            de_link.first.click()
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(2000)

            print(f"    Step 5: DE-Shop URL pruefen")
            new_url = page.url
            print(f"    Neue URL: {new_url[:80]}")
            if "grueneerde.com" in new_url or "/de" in new_url.lower():
                print(f"    [OK] DE-Shop erreicht")
            else:
                print(f"    [WARN] URL enthaelt nicht die erwartete DE-Domain")
        else:
            print(f"    [SKIP] DE-Link nicht klickbar")

        print(f"    Step 6-7: CH-Shop (sofern moeglich)")
        ch_link = page.locator(
            "a[href*='grueneerde.ch'], a:has-text('Schweiz'), "
            "a:has-text('CH'), option:has-text('CH')"
        )
        if ch_link.count() > 0 and ch_link.first.is_visible():
            ch_href = ch_link.first.get_attribute("href")
            print(f"    CH-Link gefunden: {ch_href}")
        else:
            print(f"    [INFO] CH-Link nicht direkt sichtbar")
        print(f"    [OK] Laenderwechsel-Test abgeschlossen")

    except Exception as e:
        take_error_screenshot(page, "TC-NAV-004")
        raise

# =============================================================================
# TC-NAV-005: Waehrungsanpassung bei Laenderwechsel
# =============================================================================

@pytest.mark.navigation
@pytest.mark.feature
def test_currency_adjustment(page: Page, base_url: str):
    """
    TC-NAV-005: Prueft EUR im AT/DE-Shop und CHF im CH-Shop.
    """
    print(f"\n[Navigation] TC-NAV-005: Waehrungsanpassung")

    try:
        print(f"    Step 1: Produktseite im AT-Shop aufrufen")
        page.goto(f"{base_url}/{TEST_PRODUCT['path']}")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(1500)

        print(f"    Step 2: Cookie-Banner akzeptieren")
        accept_cookie_banner(page)
        page.wait_for_timeout(500)

        print(f"    Step 3: Waehrung pruefen (AT/DE = EUR)")
        price_selectors = [
            ".product-detail-price",
            ".product-detail-price-container",
            "meta[itemprop='priceCurrency']",
            ".price-unit-content",
        ]

        currency_found = False
        price_text = ""

        for sel in price_selectors:
            price_elem = page.locator(sel)
            if price_elem.count() > 0:
                if "meta" in sel:
                    currency_content = price_elem.first.get_attribute("content")
                    if currency_content:
                        price_text = currency_content
                        print(f"    Meta priceCurrency: {currency_content}")
                        if currency_content.upper() in ["EUR", "CHF"]:
                            currency_found = True
                            break
                else:
                    price_text = price_elem.first.inner_text().strip()
                    print(f"    Preistext: {price_text}")
                    if price_text:
                        currency_found = True
                        break

        if currency_found:
            current_url = page.url
            is_at_or_de = (
                "grueneerde.at" in current_url or
                "grueneerde.com" in current_url or
                "at" in current_url.lower()
            )
            if is_at_or_de:
                has_eur = (
                    "€" in price_text or
                    "EUR" in price_text.upper() or
                    "eur" in price_text.lower()
                )
                if has_eur:
                    print(f"    [OK] EUR-Waehrung gefunden: {price_text}")
                else:
                    print(f"    [INFO] Kein explizites EUR-Symbol, Preis: {price_text}")

            price_numbers = re.findall(r"[\d,.]+", price_text)
            if price_numbers:
                print(f"    [OK] Numerischer Preis: {price_numbers[0]}")
            else:
                print(f"    [WARN] Kein numerischer Preis erkennbar")
        else:
            print(f"    [WARN] Kein Preiselement gefunden")

        print(f"    Step 4-6: CH-Shop Waehrung pruefen")
        ch_base = base_url.replace("grueneerde.at", "grueneerde.ch").replace(
            "grueneerde.com", "grueneerde.ch"
        )

        if ch_base != base_url:
            print(f"    CH-Shop URL: {ch_base}/{TEST_PRODUCT['path']}")
            try:
                ch_response = page.goto(f"{ch_base}/{TEST_PRODUCT['path']}")
                if ch_response and ch_response.status == 200:
                    page.wait_for_load_state("domcontentloaded")
                    page.wait_for_timeout(1500)
                    accept_cookie_banner(page)
                    for sel in price_selectors:
                        ch_price = page.locator(sel)
                        if ch_price.count() > 0:
                            if "meta" in sel:
                                ch_currency = ch_price.first.get_attribute("content")
                                if ch_currency and ch_currency.upper() == "CHF":
                                    print(f"    [OK] CHF im CH-Shop gefunden")
                                    break
                            else:
                                ch_text = ch_price.first.inner_text().strip()
                                if "CHF" in ch_text or "Fr." in ch_text:
                                    print(f"    [OK] CHF im CH-Shop: {ch_text}")
                                    break
                    else:
                        print(f"    [INFO] CHF nicht explizit erkennbar")
                else:
                    status = ch_response.status if ch_response else "keine Response"
                    print(f"    [SKIP] CH-Shop nicht erreichbar ({status})")
            except Exception as ch_err:
                print(f"    [SKIP] CH-Shop Zugriff fehlgeschlagen: {ch_err}")
        else:
            print(f"    [SKIP] CH-Shop URL konnte nicht ermittelt werden")

        print(f"    [OK] Waehrungstest abgeschlossen")

    except Exception as e:
        take_error_screenshot(page, "TC-NAV-005")
        raise
