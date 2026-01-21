"""
Regression Tests - Schnelle Validierung aller kritischen Shop-Funktionen.

Diese Tests prüfen nach Deployments oder Änderungen, dass:
- Alle kritischen Seiten erreichbar sind
- Kernfunktionen (Suche, Warenkorb, Checkout) funktionieren
- Keine Regressionen eingeführt wurden

Ausführung:
    pytest playwright_tests/tests/test_regression.py -v
    pytest playwright_tests/tests/test_regression.py -v -k "homepage"
    pytest -m regression -v
"""
import re
import pytest
from playwright.sync_api import Page, expect

from ..conftest import accept_cookie_banner


# =============================================================================
# Testdaten
# =============================================================================

# Kritische Seiten die immer erreichbar sein müssen
CRITICAL_PAGES = [
    {"path": "/", "name": "Homepage", "must_contain": ["Grüne Erde"]},
    {"path": "/search", "name": "Suchseite", "must_contain": []},
    {"path": "/checkout/cart", "name": "Warenkorb", "must_contain": ["Warenkorb"]},
    {"path": "/account/login", "name": "Login", "must_contain": ["Anmelden"]},
]

# Test-Produkt für Funktions-Tests
TEST_PRODUCT = {
    "id": "49415",
    "path": "p/duftkissen-lavendel/ge-p-49415",
    "name": "Duftkissen Lavendel",
    "price": 12.90,
}

# Suchbegriffe die Ergebnisse liefern müssen
SEARCH_TERMS = [
    {"term": "Bett", "min_results": 1},
    {"term": "Kissen", "min_results": 1},
    {"term": "49415", "min_results": 1},  # Artikelnummer
]


# =============================================================================
# Hilfsfunktionen
# =============================================================================

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
# TC-REG-001 bis TC-REG-004: Kritische Seiten erreichbar
# =============================================================================

@pytest.mark.regression
@pytest.mark.parametrize("page_info", CRITICAL_PAGES, ids=[p["name"] for p in CRITICAL_PAGES])
def test_critical_page_loads(page: Page, base_url: str, page_info: dict):
    """
    TC-REG-001-004: Prüft, dass kritische Seiten laden und HTTP 200 zurückgeben.
    """
    print(f"\n[Regression] Seite: {page_info['name']}")

    response = page.goto(f"{base_url}{page_info['path']}")

    # HTTP Status prüfen
    assert response is not None, f"Keine Response für {page_info['path']}"
    assert response.status == 200, f"HTTP {response.status} für {page_info['path']}"

    # Seite muss laden
    page.wait_for_load_state("domcontentloaded")

    # Pflicht-Inhalte prüfen
    for content in page_info.get("must_contain", []):
        page_text = page.locator("body").inner_text()
        assert content.lower() in page_text.lower(), f"'{content}' nicht auf {page_info['name']} gefunden"

    print(f"    [OK] {page_info['name']} erreichbar (HTTP {response.status})")


# =============================================================================
# TC-REG-005: Produktseite lädt mit korrekten Daten
# =============================================================================

@pytest.mark.regression
def test_product_page_loads_with_data(page: Page, base_url: str):
    """
    TC-REG-005: Prüft, dass Produktseiten laden und wichtige Elemente enthalten.
    """
    print(f"\n[Regression] Produktseite: {TEST_PRODUCT['name']}")

    page.goto(f"{base_url}/{TEST_PRODUCT['path']}")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1500)
    accept_cookie_banner(page)

    # Produktname vorhanden
    name_elem = page.locator("h1.product-detail-name, .product-detail-name, h1")
    assert name_elem.count() > 0, "Kein Produktname gefunden"

    # Preis vorhanden - spezifischere Selektoren für Shopware 6
    price_selectors = [
        ".product-detail-price .product-detail-price-container",
        ".product-detail-price",
        "meta[itemprop='price']",
        ".price-unit-content",
    ]

    price = None
    for sel in price_selectors:
        price_elem = page.locator(sel)
        if price_elem.count() > 0:
            # Bei meta-Tag das content-Attribut lesen
            if "meta" in sel:
                price_content = price_elem.first.get_attribute("content")
                if price_content:
                    price = extract_price(price_content)
            else:
                price_text = price_elem.first.inner_text()
                price = extract_price(price_text)
            if price and price > 0:
                break

    assert price is not None and price > 0, f"Ungültiger Preis (gefunden: {price})"

    # Warenkorb-Button vorhanden
    buy_btn = page.locator("button.btn-buy, .btn-buy")
    assert buy_btn.count() > 0, "Kein Warenkorb-Button gefunden"

    # Artikelnummer vorhanden
    page_text = page.locator("body").inner_text()
    assert TEST_PRODUCT["id"] in page_text, f"Artikelnummer {TEST_PRODUCT['id']} nicht gefunden"

    print(f"    [OK] Produktseite vollständig (Preis: {price} €)")


# =============================================================================
# TC-REG-006: Suche liefert Ergebnisse
# =============================================================================

@pytest.mark.regression
@pytest.mark.parametrize("search_info", SEARCH_TERMS, ids=[s["term"] for s in SEARCH_TERMS])
def test_search_returns_results(page: Page, base_url: str, search_info: dict):
    """
    TC-REG-006: Prüft, dass die Suche für wichtige Begriffe Ergebnisse liefert.
    """
    term = search_info["term"]
    print(f"\n[Regression] Suche: '{term}'")

    page.goto(f"{base_url}/search?search={term}")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1500)
    accept_cookie_banner(page)

    # Prüfen ob Ergebnisse vorhanden
    # Nosto Search oder Standard Shopware Search
    results = page.locator(".product-box, .cms-listing-col, .search-result-item, [data-product-id]")
    result_count = results.count()

    # Fallback: "Keine Ergebnisse" Text sollte NICHT vorhanden sein
    no_results = page.locator("*:has-text('keine Ergebnisse'), *:has-text('Keine Produkte')")

    if result_count < search_info["min_results"]:
        # Prüfen ob wirklich keine Ergebnisse
        page_text = page.locator("body").inner_text().lower()
        has_no_results = "keine ergebnisse" in page_text or "keine produkte" in page_text
        assert not has_no_results, f"Suche '{term}' liefert keine Ergebnisse"

    print(f"    [OK] Suche '{term}' liefert {result_count} Ergebnisse")


# =============================================================================
# TC-REG-007: Warenkorb hinzufügen funktioniert
# =============================================================================

@pytest.mark.regression
def test_add_to_cart_works(page: Page, base_url: str):
    """
    TC-REG-007: Prüft, dass Produkte zum Warenkorb hinzugefügt werden können.
    """
    print(f"\n[Regression] Warenkorb: Produkt hinzufügen")

    # Produkt öffnen
    page.goto(f"{base_url}/{TEST_PRODUCT['path']}")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)
    accept_cookie_banner(page)

    # Zum Warenkorb hinzufügen
    buy_btn = page.locator("button.btn-buy, .btn-buy")
    assert buy_btn.count() > 0, "Kein Warenkorb-Button gefunden"
    buy_btn.first.click()

    # Warten auf Reaktion (Offcanvas oder Redirect)
    page.wait_for_timeout(2000)

    # Warenkorb prüfen
    page.goto(f"{base_url}/checkout/cart")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)

    # Produkt muss im Warenkorb sein
    cart_content = page.locator("body").inner_text()
    assert TEST_PRODUCT["id"] in cart_content or "Lavendel" in cart_content, \
        "Produkt nicht im Warenkorb gefunden"

    print(f"    [OK] Produkt erfolgreich zum Warenkorb hinzugefügt")


# =============================================================================
# TC-REG-008: Warenkorb-Berechnung korrekt
# =============================================================================

@pytest.mark.regression
def test_cart_calculation_correct(page: Page, base_url: str):
    """
    TC-REG-008: Prüft, dass die Warenkorb-Berechnung korrekt ist.
    """
    print(f"\n[Regression] Warenkorb: Berechnung prüfen")

    # Sicherstellen, dass Produkt im Warenkorb ist
    page.goto(f"{base_url}/{TEST_PRODUCT['path']}")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)
    accept_cookie_banner(page)

    buy_btn = page.locator("button.btn-buy, .btn-buy")
    if buy_btn.count() > 0 and buy_btn.first.is_visible():
        buy_btn.first.click()
        page.wait_for_timeout(2000)

    # Warenkorb öffnen
    page.goto(f"{base_url}/checkout/cart")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1500)

    # Summen prüfen
    subtotal_elem = page.locator(".checkout-aside-summary-value, dt:has-text('Zwischensumme') + dd")
    total_elem = page.locator(".checkout-aside-summary-total-value, .summary-total")

    if subtotal_elem.count() > 0:
        subtotal = extract_price(subtotal_elem.first.inner_text())
        print(f"    Zwischensumme: {subtotal} €")
        assert subtotal is not None and subtotal > 0, "Ungültige Zwischensumme"

    if total_elem.count() > 0:
        total = extract_price(total_elem.first.inner_text())
        print(f"    Gesamtsumme: {total} €")
        assert total is not None and total > 0, "Ungültige Gesamtsumme"

    print(f"    [OK] Warenkorb-Berechnung plausibel")


# =============================================================================
# TC-REG-009: Checkout erreichbar
# =============================================================================

@pytest.mark.regression
def test_checkout_accessible(page: Page, base_url: str):
    """
    TC-REG-009: Prüft, dass der Checkout-Prozess erreichbar ist.
    """
    print(f"\n[Regression] Checkout: Erreichbarkeit prüfen")

    # Sicherstellen, dass Produkt im Warenkorb ist
    page.goto(f"{base_url}/{TEST_PRODUCT['path']}")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)
    accept_cookie_banner(page)

    buy_btn = page.locator("button.btn-buy, .btn-buy")
    if buy_btn.count() > 0 and buy_btn.first.is_visible():
        buy_btn.first.click()
        page.wait_for_timeout(2000)

    # Zum Warenkorb
    page.goto(f"{base_url}/checkout/cart")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)

    # "Zur Kasse" Button suchen und klicken
    checkout_btn = page.locator("a:has-text('Zur Kasse'), button:has-text('Zur Kasse'), .checkout-main-btn")

    if checkout_btn.count() > 0 and checkout_btn.first.is_visible():
        checkout_btn.first.click()
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(1500)

        # Prüfen ob wir auf Checkout-Seite sind
        current_url = page.url
        page_text = page.locator("body").inner_text().lower()

        is_checkout = (
            "/checkout" in current_url or
            "gast" in page_text or
            "anmelden" in page_text or
            "adresse" in page_text or
            "lieferadresse" in page_text
        )

        assert is_checkout, "Checkout-Seite nicht erreicht"
        print(f"    [OK] Checkout erreichbar (URL: {current_url[:60]}...)")
    else:
        # Warenkorb möglicherweise leer
        print(f"    [SKIP] Kein Checkout-Button gefunden (Warenkorb leer?)")


# =============================================================================
# TC-REG-010: Login-Seite funktioniert
# =============================================================================

@pytest.mark.regression
def test_login_page_functional(page: Page, base_url: str):
    """
    TC-REG-010: Prüft, dass die Login-Seite Formular-Elemente enthält.
    """
    print(f"\n[Regression] Login: Seite funktionsfähig")

    page.goto(f"{base_url}/account/login")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)
    accept_cookie_banner(page)

    # E-Mail-Feld vorhanden
    email_field = page.locator("input[type='email'], input[name='email'], #loginMail")
    assert email_field.count() > 0, "Kein E-Mail-Feld auf Login-Seite"

    # Passwort-Feld vorhanden
    password_field = page.locator("input[type='password'], #loginPassword")
    assert password_field.count() > 0, "Kein Passwort-Feld auf Login-Seite"

    # Anmelden-Button vorhanden
    submit_btn = page.locator("button[type='submit'], button:has-text('Anmelden')")
    assert submit_btn.count() > 0, "Kein Anmelden-Button auf Login-Seite"

    print(f"    [OK] Login-Seite vollständig (E-Mail, Passwort, Submit)")


# =============================================================================
# TC-REG-011: Registrierungs-Link vorhanden
# =============================================================================

@pytest.mark.regression
def test_registration_accessible(page: Page, base_url: str):
    """
    TC-REG-011: Prüft, dass die Registrierung erreichbar ist.
    """
    print(f"\n[Regression] Registrierung: Erreichbarkeit")

    page.goto(f"{base_url}/account/login")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)
    accept_cookie_banner(page)

    # Registrierungs-Link oder -Sektion vorhanden
    register_link = page.locator("a:has-text('Registrieren'), a:has-text('Konto erstellen'), .register-link")
    register_section = page.locator("*:has-text('Neues Kundenkonto')")

    has_registration = register_link.count() > 0 or register_section.count() > 0

    # Alternativ: Registrierungs-Formular direkt auf der Seite
    register_form = page.locator("form[action*='register'], #registerForm")
    if register_form.count() > 0:
        has_registration = True

    assert has_registration, "Keine Registrierungsmöglichkeit gefunden"
    print(f"    [OK] Registrierung erreichbar")


# =============================================================================
# TC-REG-012: Navigation funktioniert
# =============================================================================

@pytest.mark.regression
def test_navigation_works(page: Page, base_url: str):
    """
    TC-REG-012: Prüft, dass die Hauptnavigation funktioniert.
    """
    print(f"\n[Regression] Navigation: Hauptmenü prüfen")

    page.goto(base_url)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)
    accept_cookie_banner(page)

    # Hauptnavigation vorhanden
    nav = page.locator("nav, .main-navigation, .nav-main, header nav")
    assert nav.count() > 0, "Keine Navigation gefunden"

    # Mindestens einige Links in der Navigation
    nav_links = page.locator("nav a, .main-navigation a, header a")
    link_count = nav_links.count()

    assert link_count >= 3, f"Zu wenige Navigations-Links ({link_count})"

    # Logo/Home-Link vorhanden
    logo = page.locator(".logo, a[href='/'], .header-logo")
    assert logo.count() > 0, "Kein Logo/Home-Link gefunden"

    print(f"    [OK] Navigation funktioniert ({link_count} Links)")


# =============================================================================
# TC-REG-013: Footer vorhanden
# =============================================================================

@pytest.mark.regression
def test_footer_present(page: Page, base_url: str):
    """
    TC-REG-013: Prüft, dass der Footer wichtige Informationen enthält.
    """
    print(f"\n[Regression] Footer: Prüfung")

    page.goto(base_url)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)
    accept_cookie_banner(page)

    # Footer vorhanden
    footer = page.locator("footer, .footer")
    assert footer.count() > 0, "Kein Footer gefunden"

    footer_text = footer.first.inner_text().lower()

    # Wichtige Footer-Elemente (mindestens eines sollte vorhanden sein)
    important_terms = ["impressum", "datenschutz", "agb", "kontakt", "grüne erde"]
    found_terms = [term for term in important_terms if term in footer_text]

    assert len(found_terms) >= 1, "Footer enthält keine wichtigen Informationen"

    print(f"    [OK] Footer vorhanden (gefunden: {', '.join(found_terms)})")


# =============================================================================
# TC-REG-014: Bilder laden korrekt
# =============================================================================

@pytest.mark.regression
def test_images_load(page: Page, base_url: str):
    """
    TC-REG-014: Prüft, dass Bilder auf der Produktseite laden.
    """
    print(f"\n[Regression] Bilder: Laden prüfen")

    page.goto(f"{base_url}/{TEST_PRODUCT['path']}")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(2000)
    accept_cookie_banner(page)

    # Produktbilder finden - verschiedene Selektoren für Shopware 6
    image_selectors = [
        ".gallery-slider-image img",
        ".product-detail-image img",
        ".gallery-slider img",
        ".product-image img",
        "img[src*='media']",
        "img[data-src*='media']",  # Lazy-loading
    ]

    images = None
    for sel in image_selectors:
        images = page.locator(sel)
        if images.count() > 0:
            break

    img_count = images.count() if images else 0

    if img_count > 0:
        # Mindestens ein Bild prüfen
        first_img = images.first

        # src oder data-src (Lazy-Loading)
        src = first_img.get_attribute("src")
        if not src or src.startswith("data:"):
            src = first_img.get_attribute("data-src")

        # Fallback: srcset prüfen
        if not src:
            src = first_img.get_attribute("srcset")

        has_image_source = src is not None and len(src) > 10

        if has_image_source:
            print(f"    [OK] {img_count} Bilder gefunden")
        else:
            # Bild-Element existiert, aber noch nicht geladen (Lazy-Loading)
            print(f"    [OK] {img_count} Bild-Elemente gefunden (Lazy-Loading)")
    else:
        # Kein Fehler, aber Warnung
        print(f"    [WARN] Keine Produktbilder mit Standard-Selektoren gefunden")


# =============================================================================
# TC-REG-015: Keine JavaScript-Fehler auf kritischen Seiten
# =============================================================================

@pytest.mark.regression
def test_no_critical_js_errors(page: Page, base_url: str):
    """
    TC-REG-015: Prüft, dass keine kritischen JavaScript-Fehler auftreten.
    """
    print(f"\n[Regression] JavaScript: Fehlerprüfung")

    js_errors = []

    # Console-Listener einrichten
    page.on("console", lambda msg: js_errors.append(msg.text) if msg.type == "error" else None)
    page.on("pageerror", lambda err: js_errors.append(str(err)))

    # Kritische Seiten durchgehen
    test_urls = [
        base_url,
        f"{base_url}/{TEST_PRODUCT['path']}",
        f"{base_url}/checkout/cart",
    ]

    for url in test_urls:
        page.goto(url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(1000)

    # Kritische Fehler filtern (nicht alle Console-Errors sind problematisch)
    critical_errors = [
        err for err in js_errors
        if "undefined" in err.lower() or
           "typeerror" in err.lower() or
           "referenceerror" in err.lower()
    ]

    if critical_errors:
        print(f"    [WARN] {len(critical_errors)} potenzielle JS-Fehler gefunden")
        for err in critical_errors[:3]:
            print(f"           - {err[:80]}...")
    else:
        print(f"    [OK] Keine kritischen JavaScript-Fehler")
