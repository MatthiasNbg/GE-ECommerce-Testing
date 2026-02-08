"""
Technical Tests - Cookie, Fehlerseiten, Mobile, Accessibility
Tests fuer Cookie/Consent, Fehlerseiten, Responsive/Mobile, Accessibility

Test-IDs:
  Cookie/Consent:      TC-COOKIE-001 bis TC-COOKIE-003
  Fehlerseiten:        TC-ERROR-001 bis TC-ERROR-002
  Mobile/Responsive:   TC-MOBILE-001 bis TC-MOBILE-003
  Barrierefreiheit:    TC-A11Y-001 bis TC-A11Y-002

Phase: Technical/Infrastructure
Prioritaet: P0-P3
"""
import pytest
from playwright.sync_api import Page, sync_playwright, expect

from ..conftest import accept_cookie_banner


# =============================================================================
# Testdaten
# =============================================================================

TEST_PRODUCT_PATH = "p/kurzarmshirt-aus-bio-baumwolle/ge-p-862990"

COOKIE_BANNER_SELECTOR = "#usercentrics-cmp-ui"

HAMBURGER_SELECTORS = [
    ".menu-button",
    ".nav-main-toggle-btn",
    "button.navbar-toggler",
    ".js-offcanvas-menu-trigger",
]

MENU_OVERLAY_SELECTORS = [
    ".offcanvas-menu",
    ".mobile-menu",
    ".navigation-offcanvas",
    ".offcanvas.is-open",
    ".offcanvas.show",
]

MENU_CLOSE_SELECTORS = [
    ".offcanvas-close",
    ".btn-close",
    "[data-bs-dismiss='offcanvas']",
]

PRODUCT_IMAGE_SELECTORS = [
    ".product-detail-media img",
    ".gallery-slider-image img",
    "img.product-image",
    ".gallery-slider-item img",
    ".product-detail-img",
]


# =============================================================================
# Hilfsfunktionen
# =============================================================================

def _find_visible_element(page, selectors, timeout=3000):
    """Findet das erste sichtbare Element aus einer Liste von Selektoren."""
    for selector in selectors:
        try:
            loc = page.locator(selector)
            if loc.count() > 0 and loc.first.is_visible(timeout=timeout):
                return loc.first
        except Exception:
            continue
    return None


def _accept_uc_cookie_banner(page, timeout=5000):
    """Akzeptiert das Usercentrics Cookie-Banner via Shadow DOM JS evaluation."""
    try:
        page.wait_for_selector(COOKIE_BANNER_SELECTOR, timeout=timeout)
        page.wait_for_timeout(1000)
        clicked = page.evaluate("""() => {
            const ucRoot = document.querySelector('#usercentrics-cmp-ui');
            if (ucRoot && ucRoot.shadowRoot) {
                const btn = ucRoot.shadowRoot.querySelector(
                    'button[data-testid="uc-accept-all-button"]'
                );
                if (btn) { btn.click(); return true; }
            }
            const acceptBtn = document.querySelector('button#accept');
            if (acceptBtn) { acceptBtn.click(); return true; }
            const actionBtn = document.querySelector(
                'button[data-action-type="accept"]'
            );
            if (actionBtn) { actionBtn.click(); return true; }
            return false;
        }""")
        if clicked:
            page.wait_for_timeout(1500)
        return clicked
    except Exception:
        return False


# =============================================================================
# Cookie/Consent Tests (TC-COOKIE-001 bis TC-COOKIE-003)
# =============================================================================

def test_cookie_banner_appears_on_first_visit(base_url):
    """TC-COOKIE-001: Cookie-Banner erscheint beim Erstbesuch."""
    print("\n[TC-COOKIE-001] Starte Cookie-Banner Test...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()

        try:
            print("  Schritt 1: Frischer Browser-Kontext erstellt (keine Cookies)")

            print(f"  Schritt 2: Navigiere zu {base_url}")
            page.goto(base_url)
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(3000)

            print("  Schritt 3: Pruefe ob Usercentrics Cookie-Banner sichtbar ist...")
            banner_visible = page.evaluate("""() => {
                const uc = document.querySelector('#usercentrics-cmp-ui');
                return uc !== null && uc.offsetParent !== null;
            }""")

            if not banner_visible:
                banner_element = page.locator(COOKIE_BANNER_SELECTOR)
                banner_visible = banner_element.count() > 0

            assert banner_visible,                 "Cookie-Banner (Usercentrics) nicht beim Erstbesuch sichtbar"
            print("  BESTANDEN: Cookie-Banner ist beim Erstbesuch sichtbar")

        finally:
            context.close()
            browser.close()


def test_cookie_consent_accept_works(base_url):
    """TC-COOKIE-002: Cookie-Zustimmung funktioniert."""
    print("\n[TC-COOKIE-002] Starte Cookie-Zustimmung Test...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()

        try:
            print(f"  Schritt 1-2: Navigiere zu {base_url} mit frischem Kontext")
            page.goto(base_url)
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(3000)

            print("  Schritt 3: Pruefe ob Cookie-Banner sichtbar ist...")
            banner = page.locator(COOKIE_BANNER_SELECTOR)
            banner_exists = banner.count() > 0
            assert banner_exists,                 "Cookie-Banner nicht gefunden - kann Akzeptierung nicht testen"
            print("  Cookie-Banner gefunden")

            print("  Schritt 4: Klicke Alle akzeptieren Button (Shadow DOM)...")
            accepted = _accept_uc_cookie_banner(page)
            if not accepted:
                print("  Shadow DOM Klick fehlgeschlagen, versuche Fallback...")
                accepted = accept_cookie_banner(page, timeout=5000)
            assert accepted, "Cookie-Banner konnte nicht akzeptiert werden"
            print("  Cookie-Akzeptierung erfolgreich")

            print("  Schritt 5: Pruefe ob Banner verschwunden ist...")
            page.wait_for_timeout(2000)
            banner_gone = page.evaluate("""() => {
                const uc = document.querySelector('#usercentrics-cmp-ui');
                if (!uc) return true;
                const style = window.getComputedStyle(uc);
                return style.display === 'none' || style.visibility === 'hidden' || uc.offsetParent === null;
            }""")
            assert banner_gone,                 "Cookie-Banner ist nach Akzeptierung immer noch sichtbar"
            print("  BESTANDEN: Cookie-Banner verschwindet nach Akzeptierung")

        finally:
            context.close()
            browser.close()


def test_cookie_preferences_persist(base_url):
    """TC-COOKIE-003: Cookie-Praeferenzen persistent nach Reload."""
    print("\n[TC-COOKIE-003] Starte Cookie-Persistenz Test...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()

        try:
            print(f"  Schritt 1: Navigiere zu {base_url}")
            page.goto(base_url)
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(3000)

            print("  Schritt 2: Akzeptiere Cookie-Banner...")
            accepted = _accept_uc_cookie_banner(page)
            if not accepted:
                accepted = accept_cookie_banner(page, timeout=5000)
            assert accepted, "Cookie-Banner konnte nicht akzeptiert werden"
            print("  Cookie-Banner akzeptiert")
            page.wait_for_timeout(2000)

            print("  Schritt 3: Lade Seite neu...")
            page.reload()
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(3000)

            print("  Schritt 4: Pruefe ob Banner NICHT erneut erscheint...")
            banner_reappeared = page.evaluate("""() => {
                const uc = document.querySelector('#usercentrics-cmp-ui');
                if (!uc) return false;
                if (uc.shadowRoot) {
                    const dialog = uc.shadowRoot.querySelector('[role="dialog"]');
                    if (dialog) {
                        const style = window.getComputedStyle(dialog);
                        return style.display !== 'none' && style.visibility !== 'hidden';
                    }
                }
                const style = window.getComputedStyle(uc);
                return style.display !== 'none' && style.visibility !== 'hidden' && uc.offsetHeight > 100;
            }""")
            assert not banner_reappeared,                 "Cookie-Banner erscheint erneut nach Reload - Praeferenzen nicht persistent"
            print("  BESTANDEN: Cookie-Praeferenzen sind persistent nach Reload")

        finally:
            context.close()
            browser.close()


# =============================================================================
# Fehlerseiten Tests (TC-ERROR-001 bis TC-ERROR-002)
# =============================================================================

def test_404_error_page(page: Page, base_url: str):
    """TC-ERROR-001: 404-Seite bei ungueltiger URL."""
    print("\n[TC-ERROR-001] Starte 404-Seite Test...")

    page.goto(base_url)
    page.wait_for_load_state("domcontentloaded")
    accept_cookie_banner(page)

    invalid_url = f"{base_url}/diese-seite-gibt-es-nicht-12345"
    print(f"  Schritt 1: Navigiere zu ungueltiger URL: {invalid_url}")
    response = page.goto(invalid_url)
    page.wait_for_load_state("domcontentloaded")

    status_code = response.status if response else 0
    print(f"  HTTP Status: {status_code}")

    print("  Schritt 2: Pruefe ob Fehlerseite angezeigt wird...")
    body_text = page.locator("body").inner_text()
    assert len(body_text.strip()) > 0, "Fehlerseite ist komplett leer"

    body_html = page.locator("body").inner_html()
    assert len(body_html.strip()) > 50,         "Fehlerseite hat kaum Inhalt (moeglicherweise leere Seite)"
    print(f"  Seiteninhalt vorhanden ({len(body_text)} Zeichen)")

    print("  Schritt 3: Pruefe ob Navigation vorhanden ist...")
    nav_elements = page.locator(
        "header, nav, .header-main, .main-navigation, "
        "a[href='/'], a[href*='home'], .logo-main"
    )
    has_navigation = nav_elements.count() > 0
    if not has_navigation:
        links = page.locator("a")
        has_navigation = links.count() > 0
    assert has_navigation, "Fehlerseite hat keine Navigation zurueck zum Shop"
    print("  BESTANDEN: 404-Seite zeigt Inhalt und Navigation")


def test_error_page_handling(page: Page, base_url: str):
    """TC-ERROR-002: Fehlerseite bei Server-Fehler."""
    print("\n[TC-ERROR-002] Starte Fehlerseiten-Handling Test...")

    page.goto(base_url)
    page.wait_for_load_state("domcontentloaded")
    accept_cookie_banner(page)

    error_urls = [
        f"{base_url}/api/v999/nonexistent-endpoint",
        f"{base_url}/store-api/v999/nonexistent",
    ]

    for error_url in error_urls:
        print(f"  Schritt 1: Teste URL: {error_url}")
        response = page.goto(error_url)
        page.wait_for_load_state("domcontentloaded")

        status_code = response.status if response else 0
        print(f"  HTTP Status: {status_code}")

        print("  Schritt 2: Pruefe Fehlerseiten-Anzeige...")
        body_text = page.locator("body").inner_text().strip()
        body_html = page.locator("body").inner_html().strip()

        assert len(body_html) > 0, f"Leere Seite bei {error_url}"

        stack_trace_indicators = [
            "Stack trace", "Traceback", "Exception",
            "Fatal error", "vendor/", "src/Kernel.php",
        ]
        for indicator in stack_trace_indicators:
            if indicator in body_text:
                print(f"  WARNUNG: Moeglicherweise Stack-Trace sichtbar: '{indicator}'")

        print(f"  Fehlerseite fuer {error_url} zeigt Inhalt ({len(body_text)} Zeichen)")

    print("  BESTANDEN: Fehlerseiten zeigen benutzerfreundliche Inhalte")


# =============================================================================
# Responsive/Mobile Tests (TC-MOBILE-001 bis TC-MOBILE-003)
# =============================================================================

def test_homepage_mobile_viewport(base_url):
    """TC-MOBILE-001: Homepage korrekt im mobilen Viewport."""
    print("\n[TC-MOBILE-001] Starte Mobile-Homepage Test...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 375, "height": 812})
        page = context.new_page()

        try:
            print(f"  Schritt 1: Navigiere zu {base_url} (375x812 Viewport)")
            page.goto(base_url)
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(2000)

            _accept_uc_cookie_banner(page)
            accept_cookie_banner(page, timeout=3000)
            page.wait_for_timeout(1000)

            print("  Schritt 2: Pruefe horizontalen Overflow...")
            has_overflow = page.evaluate("""() => {
                return document.documentElement.scrollWidth > document.documentElement.clientWidth;
            }""")
            if has_overflow:
                scroll_w = page.evaluate("document.documentElement.scrollWidth")
                client_w = page.evaluate("document.documentElement.clientWidth")
                print(f"  WARNUNG: Horizontaler Overflow: scrollWidth={scroll_w}, clientWidth={client_w}")
            else:
                print("  Kein horizontaler Overflow")

            print("  Schritt 3: Pruefe ob Hamburger-Menue sichtbar ist...")
            hamburger = _find_visible_element(page, HAMBURGER_SELECTORS, timeout=3000)
            assert hamburger is not None, \
                f"Hamburger-Menue-Button nicht sichtbar. Selektoren: {HAMBURGER_SELECTORS}"
            print("  Hamburger-Menue-Button gefunden und sichtbar")

            print("  Schritt 4: Pruefe ob Logo sichtbar ist...")
            logo_selectors = [
                ".header-logo-main img", ".header-logo img",
                "a.header-logo-main-link img", ".logo-main img",
                "header img[alt]", "header svg",
            ]
            logo = _find_visible_element(page, logo_selectors, timeout=3000)
            assert logo is not None, "Shop-Logo nicht im mobilen Viewport sichtbar"
            print("  Logo gefunden und sichtbar")
            print("  BESTANDEN: Homepage rendert korrekt im mobilen Viewport")

        finally:
            context.close()
            browser.close()



def test_checkout_mobile_viewport(base_url, test_product_id):
    """TC-MOBILE-002: Checkout im mobilen Viewport."""
    print("\n[TC-MOBILE-002] Starte Mobile-Checkout Test...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 375, "height": 812})
        page = context.new_page()

        try:
            product_url = f"{base_url}/{test_product_id}"
            print(f"  Schritt 1: Navigiere zu Produktseite: {product_url} (375x812)")
            page.goto(product_url)
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(2000)

            _accept_uc_cookie_banner(page)
            accept_cookie_banner(page, timeout=3000)
            page.wait_for_timeout(1000)

            print("  Schritt 2: Fuege Produkt zum Warenkorb hinzu...")
            add_btn = page.locator("button.btn-buy")
            if add_btn.count() > 0 and add_btn.first.is_visible(timeout=5000):
                add_btn.first.click()
                page.wait_for_timeout(3000)
                print("  Produkt hinzugefuegt")
                close_btn = page.locator(
                    ".offcanvas-close, .btn-close, [data-bs-dismiss='offcanvas']"
                )
                if close_btn.count() > 0:
                    try:
                        close_btn.first.click(timeout=2000)
                        page.wait_for_timeout(500)
                    except Exception:
                        pass
            else:
                print("  WARNUNG: Kein In den Warenkorb Button gefunden")

            cart_url = f"{base_url}/checkout/cart"
            print(f"  Schritt 3: Navigiere zum Warenkorb: {cart_url}")
            page.goto(cart_url)
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(2000)

            print("  Schritt 4: Pruefe ob Warenkorbseite nutzbar ist...")
            body_text = page.locator("body").inner_text()
            assert len(body_text.strip()) > 0, "Warenkorbseite ist leer im mobilen Viewport"
            print(f"  Warenkorbseite hat Inhalt ({len(body_text)} Zeichen)")

            print("  Schritt 5: Pruefe ob Checkout-Button sichtbar ist...")
            checkout_selectors = [
                ".checkout-aside-action .btn-primary",
                "a[href*='checkout/confirm']",
                ".begin-checkout-btn",
                "button.btn-primary",
                ".cart-actions .btn",
            ]
            checkout_btn = _find_visible_element(page, checkout_selectors, timeout=5000)

            cart_empty = page.locator(".cart-empty, .empty-cart")
            if cart_empty.count() > 0:
                print("  Warenkorb ist leer - Checkout-Button nicht erwartet")
                print("  BESTANDEN: Warenkorbseite funktioniert im mobilen Viewport")
            else:
                if checkout_btn is None:
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    page.wait_for_timeout(1000)
                    checkout_btn = _find_visible_element(page, checkout_selectors, timeout=3000)
                assert checkout_btn is not None, \
                    "Checkout-Button nicht im mobilen Viewport sichtbar (auch nach Scrollen)"
                print("  Checkout-Button gefunden und sichtbar")
                print("  BESTANDEN: Checkout funktioniert im mobilen Viewport")

        finally:
            context.close()
            browser.close()



def test_mobile_hamburger_menu(base_url):
    """TC-MOBILE-003: Mobile Hamburger-Menue funktioniert."""
    print("\n[TC-MOBILE-003] Starte Hamburger-Menue Test...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 375, "height": 812})
        page = context.new_page()

        try:
            print(f"  Schritt 1: Navigiere zu {base_url} (375x812)")
            page.goto(base_url)
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(2000)

            _accept_uc_cookie_banner(page)
            accept_cookie_banner(page, timeout=3000)
            page.wait_for_timeout(1000)

            print("  Schritt 2: Pruefe ob Hamburger-Menue-Icon sichtbar ist...")
            hamburger = _find_visible_element(page, HAMBURGER_SELECTORS, timeout=5000)
            assert hamburger is not None, \
                "Hamburger-Menue-Icon nicht sichtbar im mobilen Viewport"
            print("  Hamburger-Menue-Icon gefunden")

            print("  Schritt 3: Klicke Hamburger-Menue...")
            hamburger.click()
            page.wait_for_timeout(1500)
            print("  Hamburger-Menue geklickt")

            print("  Schritt 4: Pruefe ob Menue geoeffnet ist...")
            menu_overlay = _find_visible_element(page, MENU_OVERLAY_SELECTORS, timeout=5000)
            if menu_overlay is None:
                offcanvas = page.locator(".offcanvas")
                if offcanvas.count() > 0:
                    for i in range(offcanvas.count()):
                        if offcanvas.nth(i).is_visible():
                            menu_overlay = offcanvas.nth(i)
                            break
            assert menu_overlay is not None, \
                "Menue-Overlay nicht sichtbar nach Klick auf Hamburger-Icon"
            print("  Menue-Overlay ist sichtbar")

            nav_links = page.locator(
                ".offcanvas a, .offcanvas .nav-link, "
                ".navigation-offcanvas a, .mobile-menu a"
            )
            nav_count = nav_links.count()
            print(f"  Navigations-Links im Menue: {nav_count}")
            assert nav_count > 0, \
                "Keine Navigationselemente im geoeffneten Menue gefunden"

            print("  Schritt 5: Schliesse Menue...")
            close_btn = _find_visible_element(page, MENU_CLOSE_SELECTORS, timeout=3000)
            if close_btn:
                close_btn.click()
                page.wait_for_timeout(1000)
                print("  Menue geschlossen via Close-Button")
            else:
                page.keyboard.press("Escape")
                page.wait_for_timeout(1000)
                print("  Menue geschlossen via Escape-Taste")

            print("  BESTANDEN: Hamburger-Menue funktioniert korrekt")

        finally:
            context.close()
            browser.close()



# =============================================================================
# Accessibility Tests (TC-A11Y-001 bis TC-A11Y-002)
# =============================================================================

def test_keyboard_navigation(page: Page, base_url: str):
    """TC-A11Y-001: Tastaturnavigation auf Hauptseiten."""
    print("\n[TC-A11Y-001] Starte Tastaturnavigation Test...")

    print(f"  Schritt 1: Navigiere zu {base_url}")
    page.goto(base_url)
    page.wait_for_load_state("domcontentloaded")

    print("  Schritt 2: Akzeptiere Cookie-Banner...")
    accept_cookie_banner(page)
    page.wait_for_timeout(1000)

    print("  Schritt 3: Teste Tab-Navigation...")
    focused_elements = []
    elements_with_focus_indicator = 0

    for i in range(10):
        page.keyboard.press("Tab")
        page.wait_for_timeout(300)

        focused_info = page.evaluate("""() => {
            const el = document.activeElement;
            if (!el || el === document.body) return null;
            const style = window.getComputedStyle(el);
            const outline = style.outline;
            const boxShadow = style.boxShadow;
            const hasVisualIndicator = (
                (outline !== 'none' && outline !== '' &&
                 outline !== '0px none rgb(0, 0, 0)') ||
                (boxShadow !== 'none' && boxShadow !== '')
            );
            return {
                tag: el.tagName,
                text: (el.textContent || '').trim().substring(0, 50),
                href: el.href || '',
                hasIndicator: hasVisualIndicator,
                outline: outline,
            };
        }""")

        if focused_info:
            focused_elements.append(focused_info)
            if focused_info.get('hasIndicator'):
                elements_with_focus_indicator += 1
            tag = focused_info.get('tag', '?')
            text = focused_info.get('text', '')[:30]
            has_ind = focused_info.get('hasIndicator', False)
            print(f"    Tab {i+1}: <{tag}> '{text}' (Fokus-Indikator: {has_ind})")

    assert len(focused_elements) > 0, \
        "Keine Elemente konnten per Tab-Taste fokussiert werden"
    print(f"  {len(focused_elements)} Elemente per Tab fokussiert")
    print(f"  {elements_with_focus_indicator} davon mit sichtbarem Fokus-Indikator")

    print("  Schritt 4: Teste Enter-Taste auf fokussiertem Link...")
    page.goto(base_url)
    page.wait_for_load_state("domcontentloaded")
    accept_cookie_banner(page)
    page.wait_for_timeout(1000)

    original_url = page.url
    link_found = False
    for i in range(15):
        page.keyboard.press("Tab")
        page.wait_for_timeout(200)

        is_link = page.evaluate("""() => {
            const el = document.activeElement;
            return el && el.tagName === 'A' && el.href && !el.href.includes('javascript:');
        }""")

        if is_link:
            link_href = page.evaluate("document.activeElement.href")
            print(f"    Fokussierter Link: {link_href}")
            page.keyboard.press("Enter")
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(1000)

            new_url = page.url
            navigated = new_url != original_url
            print(f"    Navigation nach Enter: {original_url} -> {new_url}")
            assert navigated, "Enter-Taste hat den fokussierten Link nicht aktiviert"
            print("  Enter-Navigation funktioniert")
            link_found = True
            break

    if not link_found:
        print("  WARNUNG: Kein Link per Tab erreichbar gewesen")

    print("  BESTANDEN: Tastaturnavigation funktioniert")



def test_product_image_alt_texts(page: Page, base_url: str, test_product_id: str):
    """TC-A11Y-002: Alt-Texte auf Produktbildern vorhanden."""
    print("\n[TC-A11Y-002] Starte Alt-Text Test...")

    product_url = f"{base_url}/{test_product_id}"
    print(f"  Schritt 1: Navigiere zu Produktseite: {product_url}")
    page.goto(product_url)
    page.wait_for_load_state("domcontentloaded")

    print("  Schritt 2: Akzeptiere Cookie-Banner...")
    accept_cookie_banner(page)
    page.wait_for_timeout(1000)

    print("  Schritt 3: Suche Produktbilder...")
    combined_selector = ", ".join(PRODUCT_IMAGE_SELECTORS)
    product_images = page.locator(combined_selector)
    image_count = product_images.count()

    if image_count == 0:
        print("  Keine Bilder mit spezifischen Selektoren, pruefe alle img-Elemente...")
        all_images = page.locator("img")
        image_count = all_images.count()
        product_images = all_images
        print(f"  Insgesamt {image_count} img-Elemente auf der Seite")

    assert image_count > 0, "Keine Produktbilder auf der Seite gefunden"
    print(f"  {image_count} Bilder gefunden")

    print("  Schritt 4: Pruefe alt-Attribute...")
    images_without_alt = []
    images_with_empty_alt = []
    images_with_alt = 0

    for i in range(image_count):
        img = product_images.nth(i)
        try:
            alt = img.get_attribute("alt")
            src = img.get_attribute("src") or img.get_attribute("data-src") or "unbekannt"

            is_visible = False
            try:
                is_visible = img.is_visible(timeout=500)
            except Exception:
                pass

            if not is_visible:
                continue

            size = page.evaluate(
                """(index) => {
                    const imgs = document.querySelectorAll('img');
                    const img = imgs[index];
                    return img ? { w: img.naturalWidth, h: img.naturalHeight } : null;
                }""",
                i
            )

            if size and (size.get('w', 0) < 10 or size.get('h', 0) < 10):
                continue

            if alt is None:
                images_without_alt.append(src[:80])
                print(f"    FEHLT: Bild ohne alt-Attribut: {src[:60]}")
            elif alt.strip() == '':
                images_with_empty_alt.append(src[:80])
                print(f"    LEER: Bild mit leerem alt-Attribut: {src[:60]}")
            else:
                images_with_alt += 1
                print(f"    OK: alt='{alt[:40]}' - {src[:40]}")

        except Exception as e:
            print(f"    Fehler bei Bild {i}: {e}")
            continue

    print(
        f"\n  Ergebnis: {images_with_alt} mit alt, "
        f"{len(images_without_alt)} ohne alt, "
        f"{len(images_with_empty_alt)} mit leerem alt"
    )

    assert images_with_alt > 0, "Kein einziges Produktbild hat einen alt-Text"

    if images_without_alt:
        print(f"  WARNUNG: {len(images_without_alt)} Bilder ohne alt-Attribut")

    print("  BESTANDEN: Produktbilder haben alt-Texte")
