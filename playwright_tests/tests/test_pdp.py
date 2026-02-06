"""
PDP (Product Detail Page) Tests - TC-PDP-001 bis TC-PDP-007
Tests fuer Produktbilder-Galerie, Varianten, Beschreibung, Lagerbestand, Hotspots, Bewertungen

Ausfuehrung:
    pytest playwright_tests/tests/test_pdp.py -v
    pytest -m pdp -v
"""
import re
import pytest
from playwright.sync_api import Page, expect

from ..conftest import accept_cookie_banner


# =============================================================================
# Testdaten
# =============================================================================

TEST_PRODUCT = {
    "id": "49415",
    "path": "p/duftkissen-lavendel/ge-p-49415",
    "name": "Duftkissen Lavendel",
}

VARIANT_PRODUCT = {
    "id": "862990",
    "path": "p/kurzarmshirt-aus-bio-baumwolle/ge-p-862990",
    "name": "Kurzarmshirt aus Bio-Baumwolle",
}


# =============================================================================
# Hilfsfunktionen
# =============================================================================

def take_error_screenshot(page: Page, test_name: str):
    """Erstellt einen Screenshot bei Testfehler."""
    try:
        page.screenshot(path=f"error_pdp_{test_name}.png", full_page=False)
        print(f"    [Screenshot] error_pdp_{test_name}.png gespeichert")
    except Exception as e:
        print(f"    [Screenshot] Fehler beim Speichern: {e}")


def extract_price(text: str) -> float | None:
    """Extrahiert Preis aus Text."""
    if not text:
        return None
    cleaned = re.sub(r"[^\d,.]", "", text)
    if "," in cleaned and "." in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    elif "," in cleaned:
        cleaned = cleaned.replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None

# =============================================================================
# TC-PDP-001: Produktbilder-Galerie und Zoom
# =============================================================================

@pytest.mark.pdp
@pytest.mark.feature
def test_product_image_gallery(page: Page, base_url: str):
    """
    TC-PDP-001: Prueft Produktbilder-Galerie, Thumbnails und Zoom.
    """
    print(f"\n[PDP] TC-PDP-001: Produktbilder-Galerie und Zoom")

    try:
        print(f"    Step 1: Produktseite aufrufen")
        page.goto(f"{base_url}/{TEST_PRODUCT['path']}")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(1500)

        print(f"    Step 2: Cookie-Banner akzeptieren")
        accept_cookie_banner(page)
        page.wait_for_timeout(500)

        print(f"    Step 3: Hauptbild pruefen")
        image_selectors = [
            ".gallery-slider-image",
            ".product-detail-media img",
            ".gallery-slider-single-image",
            ".gallery-slider img",
            ".product-image img",
            "img[src*='media']",
        ]

        main_image = None
        for sel in image_selectors:
            img = page.locator(sel)
            if img.count() > 0 and img.first.is_visible():
                main_image = img.first
                print(f"    [OK] Hauptbild gefunden: {sel}")
                break

        assert main_image is not None, "Kein Hauptbild auf der Produktseite gefunden"

        src = main_image.get_attribute("src")
        if not src or src.startswith("data:"):
            src = main_image.get_attribute("data-src")
        if not src:
            src = main_image.get_attribute("srcset")
        has_image_source = src is not None and len(str(src)) > 10
        print(f"    Bild-Quelle: {str(src)[:80] if src else 'None'}")
        assert has_image_source, "Hauptbild hat keine gueltige Quelle"

        print(f"    Step 4: Thumbnails pruefen")
        thumbnail_selectors = [
            ".gallery-slider-thumbnails-item",
            ".gallery-slider-thumbnails img",
            ".gallery-slider-thumbnails-container img",
        ]

        thumbnails = None
        thumb_count = 0
        for sel in thumbnail_selectors:
            thumbs = page.locator(sel)
            if thumbs.count() > 0:
                thumbnails = thumbs
                thumb_count = thumbs.count()
                print(f"    [OK] {thumb_count} Thumbnails gefunden: {sel}")
                break

        if thumb_count > 1:
            print(f"    Step 5: Thumbnail anklicken")
            second_thumb = thumbnails.nth(1) if thumb_count > 1 else thumbnails.first
            if second_thumb.is_visible():
                second_thumb.click()
                page.wait_for_timeout(1000)
                print(f"    [OK] Thumbnail angeklickt")
        else:
            print(f"    [INFO] Weniger als 2 Thumbnails, Klick-Test uebersprungen")

        print(f"    Step 6: Zoom/Vergroesserung testen")
        if main_image and main_image.is_visible():
            main_image.click()
            page.wait_for_timeout(1500)

            zoom_selectors = [
                ".image-zoom-container",
                ".gallery-slider-modal",
                ".modal.show",
                ".lightbox",
                "[role='dialog']",
            ]
            zoom_found = False
            for sel in zoom_selectors:
                zoom = page.locator(sel)
                if zoom.count() > 0:
                    zoom_found = True
                    print(f"    [OK] Zoom/Lightbox geoeffnet: {sel}")
                    break

            if not zoom_found:
                print(f"    [INFO] Kein Zoom-Overlay erkannt (evtl. CSS-basierter Zoom)")

        print(f"    [OK] Produktbilder-Galerie Test abgeschlossen")

    except Exception as e:
        take_error_screenshot(page, "TC-PDP-001")
        raise

# =============================================================================
# TC-PDP-002: Varianten-Auswahl
# =============================================================================

@pytest.mark.pdp
@pytest.mark.feature
def test_variant_selection(page: Page, base_url: str):
    """
    TC-PDP-002: Prueft Varianten-Auswahl, Preisaktualisierung und Warenkorb.
    """
    print(f"\n[PDP] TC-PDP-002: Varianten-Auswahl")

    try:
        print(f"    Step 1: Produktseite mit Varianten aufrufen")
        page.goto(f"{base_url}/{VARIANT_PRODUCT['path']}")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(1500)

        print(f"    Step 2: Cookie-Banner akzeptieren")
        accept_cookie_banner(page)
        page.wait_for_timeout(500)

        print(f"    Step 3: Varianten-Auswahl pruefen")
        variant_selectors = [
            ".product-detail-configurator-option",
            ".product-detail-configurator select",
            ".product-detail-configurator",
            "[data-product-configurator]",
            ".product-detail-form select",
        ]

        variant_found = False
        variant_element = None
        for sel in variant_selectors:
            elem = page.locator(sel)
            if elem.count() > 0:
                variant_found = True
                variant_element = elem
                print(f"    [OK] Varianten-Auswahl gefunden: {sel} ({elem.count()} Optionen)")
                break

        if not variant_found:
            print(f"    [SKIP] Keine Varianten-Auswahl - evtl. kein Variantenprodukt")
            return

        print(f"    Step 4: Andere Variante auswaehlen")
        # Preis vor Variantenwechsel merken
        price_before = ""
        price_elem = page.locator(".product-detail-price")
        if price_elem.count() > 0:
            price_before = price_elem.first.inner_text().strip()
            print(f"    Preis vor Wechsel: {price_before}")

        # Variante wechseln
        if "select" in (variant_selectors[variant_selectors.index(sel)] if variant_found else ""):
            # Dropdown-Variante
            select_elem = page.locator(".product-detail-configurator select").first
            options = select_elem.locator("option")
            if options.count() > 1:
                option_val = options.nth(1).get_attribute("value")
                if option_val:
                    select_elem.select_option(value=option_val)
                    print(f"    Variante gewaehlt via Dropdown: {option_val}")
        else:
            # Button/Radio-Variante
            options = page.locator(".product-detail-configurator-option")
            if options.count() > 1:
                # Nicht bereits ausgewaehlte Option klicken
                for i in range(options.count()):
                    opt = options.nth(i)
                    is_active = "is-active" in (opt.get_attribute("class") or "")
                    is_selected = opt.get_attribute("aria-checked") == "true"
                    if not is_active and not is_selected and opt.is_visible():
                        opt_text = opt.inner_text().strip()
                        print(f"    Variante gewaehlt: {opt_text}")
                        opt.click()
                        break

        page.wait_for_timeout(2000)

        print(f"    Step 5: Preis nach Variantenwechsel pruefen")
        price_after = ""
        if price_elem.count() > 0:
            price_after = price_elem.first.inner_text().strip()
            print(f"    Preis nach Wechsel: {price_after}")

        price_value = extract_price(price_after)
        if price_value and price_value > 0:
            print(f"    [OK] Preis ist gueltig: {price_value}")
        else:
            print(f"    [WARN] Preis konnte nicht extrahiert werden")

        print(f"    Step 6: Variante in den Warenkorb legen")
        buy_btn = page.locator("button.btn-buy, [data-add-to-cart]")
        if buy_btn.count() > 0 and buy_btn.first.is_visible():
            is_disabled = buy_btn.first.get_attribute("disabled") is not None
            if not is_disabled:
                buy_btn.first.click()
                page.wait_for_timeout(2000)
                print(f"    [OK] Variante zum Warenkorb hinzugefuegt")
            else:
                print(f"    [INFO] Warenkorb-Button deaktiviert (Variante evtl. nicht vorreetig)")
        else:
            print(f"    [WARN] Kein Warenkorb-Button gefunden")

        print(f"    [OK] Varianten-Auswahl Test abgeschlossen")

    except Exception as e:
        take_error_screenshot(page, "TC-PDP-002")
        raise

# =============================================================================
# TC-PDP-003: Beschreibung und Details sichtbar
# =============================================================================

@pytest.mark.pdp
@pytest.mark.feature
def test_product_description_visible(page: Page, base_url: str):
    """
    TC-PDP-003: Prueft Produktbeschreibung, Material- und Pflegehinweise.
    """
    print(f"\n[PDP] TC-PDP-003: Beschreibung und Details sichtbar")

    try:
        print(f"    Step 1: Produktseite aufrufen")
        page.goto(f"{base_url}/{TEST_PRODUCT['path']}")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(1500)

        print(f"    Step 2: Cookie-Banner akzeptieren")
        accept_cookie_banner(page)
        page.wait_for_timeout(500)

        print(f"    Step 3: Produktbeschreibung pruefen")
        desc_selectors = [
            ".product-detail-description",
            ".product-detail-tabs",
            ".product-detail-description-text",
            "[data-product-description]",
        ]

        desc_found = False
        desc_text = ""
        for sel in desc_selectors:
            desc = page.locator(sel)
            if desc.count() > 0:
                desc_found = True
                desc_text = desc.first.inner_text().strip()
                print(f"    [OK] Beschreibung gefunden: {sel}")
                print(f"    Beschreibungslaenge: {len(desc_text)} Zeichen")
                break

        assert desc_found, "Produktbeschreibung nicht gefunden"
        assert len(desc_text) > 10, f"Beschreibung zu kurz ({len(desc_text)} Zeichen)"

        print(f"    Step 4: Material-/Pflegehinweise pruefen")
        body_text = page.locator("body").inner_text().lower()
        material_keywords = ["material", "pflege", "zusammensetzung", "bio", "baumwolle", "lavendel"]
        found_keywords = [kw for kw in material_keywords if kw in body_text]
        print(f"    Material/Pflege-Keywords gefunden: {found_keywords}")

        if found_keywords:
            print(f"    [OK] Material-/Pflegeinformationen vorhanden")
        else:
            print(f"    [INFO] Keine spezifischen Material-Keywords gefunden")

        print(f"    Step 5: Produktname als h1 pruefen")
        name_elem = page.locator("h1.product-detail-name, .product-detail-name, h1")
        assert name_elem.count() > 0, "Kein Produktname (h1) gefunden"
        name_text = name_elem.first.inner_text().strip()
        assert len(name_text) > 0, "Produktname ist leer"
        print(f"    [OK] Produktname: {name_text}")

        print(f"    [OK] Beschreibung und Details Test abgeschlossen")

    except Exception as e:
        take_error_screenshot(page, "TC-PDP-003")
        raise

# =============================================================================
# TC-PDP-004: Nicht-auf-Lager-Verhalten
# =============================================================================

@pytest.mark.pdp
@pytest.mark.feature
def test_out_of_stock_behavior(page: Page, base_url: str):
    """
    TC-PDP-004: Prueft Verhalten bei nicht vorraetigem Produkt/Variante.
    """
    print(f"\n[PDP] TC-PDP-004: Nicht-auf-Lager-Verhalten")

    try:
        print(f"    Step 1: Produktseite aufrufen")
        page.goto(f"{base_url}/{VARIANT_PRODUCT['path']}")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(1500)

        print(f"    Step 2: Cookie-Banner akzeptieren")
        accept_cookie_banner(page)
        page.wait_for_timeout(500)

        print(f"    Step 3: Nicht vorreetige Variante suchen")
        options = page.locator(".product-detail-configurator-option")

        oos_variant_found = False
        if options.count() > 0:
            for i in range(options.count()):
                opt = options.nth(i)
                opt_classes = opt.get_attribute("class") or ""
                is_oos = ("is-combinable" not in opt_classes and 
                          "is-active" not in opt_classes)
                if is_oos and opt.is_visible():
                    opt_text = opt.inner_text().strip()
                    print(f"    Nicht vorreetige Variante gefunden: {opt_text}")
                    opt.click()
                    page.wait_for_timeout(1500)
                    oos_variant_found = True
                    break

        if not oos_variant_found:
            print(f"    [INFO] Keine nicht vorreetige Variante identifiziert")
            print(f"    Pruefe allgemeines Verfuegbarkeitsverhalten")

        print(f"    Step 4: Warenkorb-Button pruefen")
        buy_btn = page.locator("button.btn-buy, [data-add-to-cart]")

        if buy_btn.count() > 0:
            is_disabled = buy_btn.first.get_attribute("disabled") is not None
            is_visible = buy_btn.first.is_visible()
            print(f"    Warenkorb-Button sichtbar: {is_visible}, deaktiviert: {is_disabled}")

            if oos_variant_found:
                if is_disabled or not is_visible:
                    print(f"    [OK] Button korrekt deaktiviert/versteckt")
                else:
                    print(f"    [WARN] Button noch aktiv trotz OOS-Variante")
            else:
                print(f"    [INFO] Button-Status: sichtbar={is_visible}, disabled={is_disabled}")
        else:
            print(f"    [INFO] Kein Warenkorb-Button gefunden")

        print(f"    Step 5: Verfuegbarkeitsmeldung pruefen")
        delivery_selectors = [
            ".delivery-information",
            ".delivery-status",
            ".product-detail-delivery",
            "[data-delivery-information]",
        ]

        delivery_found = False
        for sel in delivery_selectors:
            delivery = page.locator(sel)
            if delivery.count() > 0:
                delivery_text = delivery.first.inner_text().strip()
                delivery_found = True
                print(f"    Lieferinfo: {delivery_text}")
                break

        if delivery_found:
            print(f"    [OK] Verfuegbarkeitsinformation vorhanden")
        else:
            print(f"    [INFO] Keine explizite Verfuegbarkeitsmeldung")

        print(f"    [OK] Nicht-auf-Lager Test abgeschlossen")

    except Exception as e:
        take_error_screenshot(page, "TC-PDP-004")
        raise

# =============================================================================
# TC-PDP-005: Hotspot-Elemente auf Bildern
# =============================================================================

@pytest.mark.pdp
@pytest.mark.feature
def test_hotspot_elements(page: Page, base_url: str):
    """
    TC-PDP-005: Prueft Hotspot-Elemente auf Bildern (Inspirationsseiten).
    """
    print(f"\n[PDP] TC-PDP-005: Hotspot-Elemente auf Bildern")

    try:
        print(f"    Step 1: Seite mit Hotspot-Bildern aufrufen")
        page.goto(f"{base_url}/")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)

        print(f"    Step 2: Cookie-Banner akzeptieren")
        accept_cookie_banner(page)
        page.wait_for_timeout(500)

        print(f"    Step 3: Hotspot-Bilder suchen")
        # Auf der Seite nach unten scrollen, um lazy-loaded Inhalte zu laden
        page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
        page.wait_for_timeout(2000)

        hotspot_selectors = [
            ".cms-element-image-slider .hotspot",
            ".image-hotspot",
            "[data-hotspot]",
            ".hotspot-container",
            ".cms-element-image-hotspot",
        ]

        hotspot_found = False
        hotspot_elements = None
        for sel in hotspot_selectors:
            elems = page.locator(sel)
            if elems.count() > 0:
                hotspot_found = True
                hotspot_elements = elems
                print(f"    [OK] {elems.count()} Hotspot-Elemente gefunden: {sel}")
                break

        if not hotspot_found:
            # Scroll weiter und erneut suchen
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000)
            for sel in hotspot_selectors:
                elems = page.locator(sel)
                if elems.count() > 0:
                    hotspot_found = True
                    hotspot_elements = elems
                    print(f"    [OK] {elems.count()} Hotspot-Elemente nach Scroll gefunden")
                    break

        if not hotspot_found:
            print(f"    [SKIP] Keine Hotspot-Elemente auf dieser Seite gefunden")
            print(f"    [INFO] Hotspots sind moeglicherweise nur auf bestimmten CMS-Seiten verfuegbar")
            return

        print(f"    Step 4: Hotspot-Marker auf Sichtbarkeit pruefen")
        visible_count = 0
        for i in range(min(hotspot_elements.count(), 5)):
            if hotspot_elements.nth(i).is_visible():
                visible_count += 1
        print(f"    Sichtbare Hotspots: {visible_count}")
        assert visible_count > 0, "Keine sichtbaren Hotspot-Marker"

        print(f"    Step 5: Hotspot anklicken")
        first_hotspot = hotspot_elements.first
        if first_hotspot.is_visible():
            first_hotspot.click()
            page.wait_for_timeout(1500)

            print(f"    Step 6: Hotspot-Produktinfo pruefen")
            # Pruefen ob Overlay/Tooltip mit Produktinfo erscheint
            overlay_selectors = [
                ".hotspot-overlay",
                ".hotspot-tooltip",
                ".hotspot-product",
                ".popover",
                ".tooltip.show",
                "[data-hotspot-overlay]",
            ]

            overlay_found = False
            for sel in overlay_selectors:
                overlay = page.locator(sel)
                if overlay.count() > 0 and overlay.first.is_visible():
                    overlay_text = overlay.first.inner_text().strip()
                    print(f"    [OK] Hotspot-Overlay: {overlay_text[:100]}")
                    overlay_found = True
                    break

            if not overlay_found:
                print(f"    [INFO] Kein Hotspot-Overlay erkannt (evtl. direkter Link)")
                # Pruefen ob sich die URL geaendert hat (direkter Link)
                if page.url != f"{base_url}/":
                    print(f"    [OK] Hotspot fuehrt zu: {page.url[:80]}")

        print(f"    [OK] Hotspot-Elemente Test abgeschlossen")

    except Exception as e:
        take_error_screenshot(page, "TC-PDP-005")
        raise

# =============================================================================
# TC-PDP-006: Produktbewertung abgeben [Staging only]
# =============================================================================

# Shopware 6 Review-Selektoren
REVIEW_TAB_LINK = "a[href='#review-tab-pane'], .product-detail-tabs .nav-link:has-text('Bewertungen')"
REVIEW_TAB_PANE = "#review-tab-pane"
REVIEW_FORM = ".product-detail-review-form"
REVIEW_RATING_SELECT = "#reviewRating"
REVIEW_TITLE_INPUT = "#reviewTitle"
REVIEW_CONTENT_TEXTAREA = "#reviewContent"
REVIEW_SUBMIT_BUTTON = ".product-detail-review-form button[type='submit']"
REVIEW_LIST = ".product-detail-review-list"
REVIEW_ITEM_CONTENT = ".product-detail-review-list .product-review-content"
REVIEW_LOGIN_HINT = ".product-detail-review-login"


@pytest.mark.pdp
@pytest.mark.feature
def test_product_review(page: Page, base_url: str, config):
    """
    TC-PDP-006: Produktbewertung abgeben und im Bewertungs-Tab verifizieren.

    NUR auf Staging ausfuehren - schreibt echte Daten (Bewertung).

    1. Staging-Check
    2. Login als AT-Kunde
    3. Produktseite aufrufen
    4. Bewertungs-Tab oeffnen
    5. Bewertung abgeben (5 Sterne, Text)
    6. Pruefen: Bewertung erscheint in der Liste
    """
    print(f"\n[PDP] TC-PDP-006: Produktbewertung abgeben [Staging]")

    # Staging-Only Guard
    if config.test_profile != "staging":
        pytest.skip("TC-PDP-006 darf nur auf Staging ausgefuehrt werden")

    review_text = "Ich liebe Grüne Erde Produkte"

    # Login-Daten holen
    customer = config.get_customer_by_country("AT")
    if not customer:
        pytest.skip("Kein AT-Kunde in config.yaml konfiguriert")
    email = customer.email
    password = config.get_customer_password(customer)
    if not password:
        pytest.skip("Kein Passwort fuer AT-Kunde konfiguriert")

    try:
        # [1] Login
        print(f"    Step 1: Login als AT-Kunde ({email})")
        page.goto(f"{base_url}/account/login")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(1000)
        accept_cookie_banner(page)

        page.fill("#loginMail", email)
        page.fill("#loginPassword", password)
        page.locator("button:has-text('Anmelden')").first.click()
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(1500)

        assert "account/login" not in page.url, "Login fehlgeschlagen"
        print(f"    [OK] Login erfolgreich")

        # [2] Produktseite aufrufen
        print(f"    Step 2: Produktseite aufrufen")
        page.goto(f"{base_url}/{TEST_PRODUCT['path']}")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(1500)

        # [3] Bewertungs-Tab oeffnen
        print(f"    Step 3: Bewertungs-Tab oeffnen")
        review_tab = page.locator(REVIEW_TAB_LINK)
        if review_tab.count() > 0 and review_tab.first.is_visible():
            review_tab.first.click()
            page.wait_for_timeout(1000)
            print(f"    [OK] Bewertungs-Tab geoeffnet")
        else:
            # Zum Tab-Bereich scrollen und erneut versuchen
            page.evaluate("document.querySelector('.product-detail-tabs')?.scrollIntoView()")
            page.wait_for_timeout(1000)
            review_tab = page.locator(REVIEW_TAB_LINK)
            assert review_tab.count() > 0, "Bewertungs-Tab nicht gefunden"
            review_tab.first.click()
            page.wait_for_timeout(1000)

        # [4] Bewertungsformular ausfuellen
        print(f"    Step 4: Bewertungsformular ausfuellen")

        # Sternbewertung (5 Sterne)
        rating_select = page.locator(REVIEW_RATING_SELECT)
        if rating_select.count() > 0 and rating_select.is_visible():
            rating_select.select_option("5")
            print(f"    Bewertung: 5 Sterne")
        else:
            print(f"    [WARN] Rating-Select nicht gefunden, versuche alternatives Rating")
            # Fallback: Klick auf letzten Stern
            stars = page.locator(".product-detail-review-form .product-review-point")
            if stars.count() > 0:
                stars.last.click()
                print(f"    Bewertung via Stern-Klick gesetzt")

        # Titel (optional, aber ausfuellen wenn vorhanden)
        title_input = page.locator(REVIEW_TITLE_INPUT)
        if title_input.count() > 0 and title_input.is_visible():
            title_input.fill("Tolles Produkt")
            print(f"    Titel: 'Tolles Produkt'")

        # Bewertungstext
        content_textarea = page.locator(REVIEW_CONTENT_TEXTAREA)
        assert content_textarea.count() > 0, "Bewertungs-Textfeld nicht gefunden"
        content_textarea.fill(review_text)
        print(f"    Text: '{review_text}'")

        # [5] Bewertung absenden
        print(f"    Step 5: Bewertung absenden")
        submit_btn = page.locator(REVIEW_SUBMIT_BUTTON)
        assert submit_btn.count() > 0, "Absenden-Button nicht gefunden"
        submit_btn.first.click()
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)

        # [6] Bewertung verifizieren
        print(f"    Step 6: Bewertung in der Liste verifizieren")

        # Erfolgs-Meldung pruefen (manche Shops zeigen "Bewertung gespeichert")
        success_alert = page.locator(".alert-success")
        if success_alert.count() > 0 and success_alert.first.is_visible():
            print(f"    [OK] Erfolgsmeldung: {success_alert.first.inner_text().strip()[:80]}")

        # Bewertungs-Tab sicherstellen (Seite koennte neu geladen haben)
        review_tab = page.locator(REVIEW_TAB_LINK)
        if review_tab.count() > 0 and review_tab.first.is_visible():
            review_tab.first.click()
            page.wait_for_timeout(1000)

        # Bewertungstext in der Liste suchen
        review_items = page.locator(REVIEW_ITEM_CONTENT)
        found = False
        if review_items.count() > 0:
            for i in range(review_items.count()):
                item_text = review_items.nth(i).inner_text().strip()
                if review_text in item_text:
                    found = True
                    print(f"    [OK] Bewertung gefunden in Liste: '{item_text[:80]}'")
                    break

        if not found:
            # Fallback: Im gesamten Tab-Pane suchen
            tab_pane = page.locator(REVIEW_TAB_PANE)
            if tab_pane.count() > 0:
                pane_text = tab_pane.first.inner_text()
                if review_text in pane_text:
                    found = True
                    print(f"    [OK] Bewertung im Tab-Bereich gefunden")

        if not found:
            # Bewertung evtl. noch nicht freigegeben (Admin-Moderation)
            print(f"    [INFO] Bewertung nicht sofort sichtbar - evtl. Admin-Freigabe noetig")
            # Trotzdem als bestanden werten wenn Erfolgsmeldung kam
            if success_alert.count() > 0:
                print(f"    [OK] Bewertung wurde erfolgreich eingereicht (Moderation aktiv)")
            else:
                page.screenshot(path="error_pdp_TC-PDP-006.png")
                assert False, (
                    f"Bewertung '{review_text}' nicht gefunden und keine Erfolgsmeldung"
                )

        print(f"    [OK] Produktbewertung Test abgeschlossen")

    except Exception as e:
        take_error_screenshot(page, "TC-PDP-006")
        raise

# =============================================================================
# TC-PDP-007: Varianten aendern Preis und Lagerbestand
# =============================================================================

# Selektoren fuer Varianten-Preis-/Verfuegbarkeitstest
VARIANT_OPTION = ".product-detail-configurator-option"
VARIANT_OPTION_LABEL = ".product-detail-configurator-option-label"
VARIANT_CONFIGURATOR_SELECT = ".product-detail-configurator select"
VARIANT_PRICE = ".product-detail-price"
VARIANT_DELIVERY_INFO = ".delivery-information, .delivery-status, .product-detail-delivery"
VARIANT_BUY_BUTTON = "button.btn-buy, [data-add-to-cart]"


@pytest.mark.pdp
@pytest.mark.feature
def test_variant_changes_price_and_stock(page: Page, base_url: str):
    """
    TC-PDP-007: Produktvarianten-Auswahl (Groesse, Farbe) aendert Preis/Verfuegbarkeit.

    Prueft systematisch fuer jede Variante:
    - Preis wird korrekt angezeigt (> 0)
    - Verfuegbarkeitsstatus / Lieferinformation ist sichtbar
    - Warenkorb-Button reagiert auf Lagerbestand (aktiv/deaktiviert)

    1. Produktseite mit Varianten aufrufen
    2. Alle verfuegbaren Varianten-Optionen ermitteln
    3. Jede Variante anklicken und Preis + Verfuegbarkeit erfassen
    4. Assert: Preis ist bei jeder Variante gueltig
    5. Assert: Verfuegbarkeitsstatus wird bei jeder Variante angezeigt
    6. Log: Unterschiede zwischen Varianten dokumentieren
    """
    print(f"\n[PDP] TC-PDP-007: Varianten aendern Preis und Lagerbestand")

    try:
        # [1] Produktseite aufrufen
        print(f"    Step 1: Produktseite mit Varianten aufrufen")
        page.goto(f"{base_url}/{VARIANT_PRODUCT['path']}")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(1500)

        print(f"    Step 2: Cookie-Banner akzeptieren")
        accept_cookie_banner(page)
        page.wait_for_timeout(500)

        # [2] Varianten-Typ ermitteln (Buttons vs. Dropdown)
        print(f"    Step 3: Varianten-Optionen ermitteln")
        variant_results = []  # Liste von {name, price, delivery, buy_enabled}

        button_options = page.locator(VARIANT_OPTION)
        select_options = page.locator(VARIANT_CONFIGURATOR_SELECT)
        is_dropdown = select_options.count() > 0 and button_options.count() == 0

        if is_dropdown:
            # Dropdown-Varianten
            select_elem = select_options.first
            options = select_elem.locator("option")
            option_count = options.count()
            print(f"    [OK] {option_count} Varianten via Dropdown gefunden")

            for i in range(option_count):
                opt = options.nth(i)
                opt_val = opt.get_attribute("value")
                opt_text = opt.inner_text().strip()

                # Leere/Platzhalter-Optionen ueberspringen
                if not opt_val or opt_val == "" or opt_text.startswith("Bitte"):
                    continue

                print(f"\n    --- Variante: {opt_text} ---")
                select_elem.select_option(value=opt_val)
                page.wait_for_timeout(2000)

                result = _capture_variant_state(page, opt_text)
                variant_results.append(result)

        else:
            # Button-Varianten
            option_count = button_options.count()
            if option_count == 0:
                pytest.skip("Keine Varianten-Optionen auf dieser Produktseite gefunden")

            print(f"    [OK] {option_count} Varianten via Buttons gefunden")

            for i in range(option_count):
                opt = button_options.nth(i)
                if not opt.is_visible():
                    continue

                opt_text = opt.inner_text().strip()
                opt_classes = opt.get_attribute("class") or ""

                print(f"\n    --- Variante: {opt_text} ---")
                opt.click()
                page.wait_for_timeout(2000)

                result = _capture_variant_state(page, opt_text)
                result["combinable"] = "is-combinable" in opt_classes or "is-active" in opt_classes
                variant_results.append(result)

        # [3] Ergebnisse auswerten
        print(f"\n    Step 4: Ergebnisse auswerten ({len(variant_results)} Varianten)")
        assert len(variant_results) >= 2, (
            f"Mindestens 2 Varianten erwartet, aber nur {len(variant_results)} gefunden"
        )

        # Zusammenfassung drucken
        print(f"\n    {'Variante':<25} {'Preis':>10} {'Verfuegbar':<15} {'Warenkorb':<12}")
        print(f"    {'-'*62}")

        valid_prices = 0
        delivery_shown = 0
        prices_seen = set()

        for r in variant_results:
            price_str = f"{r['price']:.2f} EUR" if r["price"] else "N/A"
            delivery_str = r["delivery_text"][:15] if r["delivery_text"] else "-"
            buy_str = "aktiv" if r["buy_enabled"] else "deaktiviert"
            print(f"    {r['name']:<25} {price_str:>10} {delivery_str:<15} {buy_str:<12}")

            if r["price"] and r["price"] > 0:
                valid_prices += 1
                prices_seen.add(r["price"])
            if r["delivery_text"]:
                delivery_shown += 1

        # [4] Assertions
        print(f"\n    Step 5: Validierung")

        # Jede Variante muss einen gueltigen Preis haben
        assert valid_prices == len(variant_results), (
            f"Nicht alle Varianten haben gueltigen Preis: {valid_prices}/{len(variant_results)}"
        )
        print(f"    [OK] Alle {valid_prices} Varianten haben gueltigen Preis")

        # Verfuegbarkeitsstatus muss bei jeder Variante angezeigt werden
        assert delivery_shown == len(variant_results), (
            f"Nicht alle Varianten zeigen Verfuegbarkeit: {delivery_shown}/{len(variant_results)}"
        )
        print(f"    [OK] Alle {delivery_shown} Varianten zeigen Verfuegbarkeitsstatus")

        # Preis- oder Verfuegbarkeitsunterschiede dokumentieren
        if len(prices_seen) > 1:
            print(f"    [OK] Preise variieren zwischen Varianten: {sorted(prices_seen)}")
        else:
            print(f"    [INFO] Alle Varianten haben denselben Preis: {prices_seen}")

        # Pruefen ob nicht-kombinierbare Varianten den Warenkorb deaktivieren
        non_combinable = [r for r in variant_results if not r.get("combinable", True)]
        if non_combinable:
            disabled_buy = [r for r in non_combinable if not r["buy_enabled"]]
            print(f"    [INFO] {len(non_combinable)} nicht-kombinierbare Varianten, "
                  f"davon {len(disabled_buy)} mit deaktiviertem Warenkorb")

        print(f"\n    [OK] Varianten-Preis-/Lagerbestand-Test abgeschlossen")

    except Exception as e:
        take_error_screenshot(page, "TC-PDP-007")
        raise


def _capture_variant_state(page: Page, variant_name: str) -> dict:
    """Erfasst Preis, Verfuegbarkeit und Warenkorb-Status der aktuellen Variante."""
    result = {
        "name": variant_name,
        "price": None,
        "price_text": "",
        "delivery_text": "",
        "buy_enabled": False,
    }

    # Preis auslesen
    price_elem = page.locator(VARIANT_PRICE)
    if price_elem.count() > 0:
        price_text = price_elem.first.inner_text().strip()
        result["price_text"] = price_text
        result["price"] = extract_price(price_text)
        print(f"    Preis: {price_text} (parsed: {result['price']})")

    # Verfuegbarkeit / Lieferinfo
    delivery_selectors = [
        ".delivery-information",
        ".delivery-status",
        ".product-detail-delivery",
        "[data-delivery-information]",
    ]
    for sel in delivery_selectors:
        delivery = page.locator(sel)
        if delivery.count() > 0:
            text = delivery.first.inner_text().strip()
            if text:
                result["delivery_text"] = text
                print(f"    Verfuegbarkeit: {text[:60]}")
                break

    # Warenkorb-Button
    buy_btn = page.locator(VARIANT_BUY_BUTTON)
    if buy_btn.count() > 0 and buy_btn.first.is_visible():
        is_disabled = buy_btn.first.get_attribute("disabled") is not None
        result["buy_enabled"] = not is_disabled
        print(f"    Warenkorb: {'aktiv' if result['buy_enabled'] else 'deaktiviert'}")
    else:
        print(f"    Warenkorb: nicht sichtbar")

    return result
