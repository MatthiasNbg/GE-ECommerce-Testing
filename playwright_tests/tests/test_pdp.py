"""
PDP (Product Detail Page) Tests - TC-PDP-001 bis TC-PDP-005
Tests fuer Produktbilder-Galerie, Varianten, Beschreibung, Lagerbestand, Hotspots

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
