"""
Content Extended Tests - TC-CONTENT-003 bis TC-CONTENT-007
Tests fuer Footer-Links, Kontaktinfo, Trust-Siegel, Beratungs-Tools, Online-Katalog
"""
import pytest
from playwright.sync_api import Page, expect

from ..conftest import accept_cookie_banner


# =============================================================================
# Helper Functions
# =============================================================================

def scroll_to_footer(page: Page) -> None:
    """Scrollt zum Footer der Seite."""
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(1000)  # Scroll-Animation und Lazy-Loading abwarten


def verify_link_loads(page: Page, link_text: str, url_fragment: str) -> None:
    """
    Prueft ob ein Link sichtbar ist, klickt ihn und verifiziert dass die Seite laedt.

    Args:
        page: Playwright Page-Instanz
        link_text: Text des Links (fuer has-text Selektor)
        url_fragment: Erwartetes URL-Fragment nach Navigation
    """
    # Link im Footer suchen (mehrere Selektor-Strategien)
    link = page.locator(
        f"footer a:has-text('{link_text}'), "
        f".footer-main a:has-text('{link_text}'), "
        f".footer a:has-text('{link_text}'), "
        f"a:has-text('{link_text}')"
    ).first

    expect(link).to_be_visible(timeout=5000)
    print(f"  Link '{link_text}' ist sichtbar")

    link.click()
    page.wait_for_load_state("domcontentloaded")

    current_url = page.url.lower()
    assert url_fragment.lower() in current_url,             f"URL '{page.url}' enthaelt nicht '{url_fragment}' nach Klick auf '{link_text}'"

    # Pruefen, dass kein Server-Fehler vorliegt
    error_elements = page.locator(".alert-danger, .error-500, .error-404")
    assert error_elements.count() == 0,             f"Fehler auf der Seite nach Klick auf '{link_text}'"

    # Seiteninhalt muss vorhanden sein (nicht leer)
    body_text = page.locator("body").inner_text()
    assert len(body_text.strip()) > 50,             f"Seite nach Klick auf '{link_text}' hat zu wenig Inhalt"

    print(f"  Seite '{link_text}' erfolgreich geladen: {page.url}")


# =============================================================================
# TC-CONTENT-003: Footer-Links erreichbar
# =============================================================================

@pytest.mark.regression
def test_footer_links_accessible(page: Page, base_url: str):
    """TC-CONTENT-003: Footer-Links (Impressum, Datenschutz, AGB) sind erreichbar."""
    print("\nTC-CONTENT-003: Footer-Links erreichbar")

    try:
        # Step 1: Startseite aufrufen
        print("Step 1: Startseite aufrufen")
        page.goto(base_url)
        page.wait_for_load_state("domcontentloaded")

        # Step 2: Cookie-Banner akzeptieren
        print("Step 2: Cookie-Banner akzeptieren")
        accept_cookie_banner(page)

        # Step 3: Zum Footer scrollen
        print("Step 3: Zum Footer scrollen")
        scroll_to_footer(page)

        # Step 4: Impressum-Link pruefen
        print("Step 4: Impressum-Link pruefen und klicken")
        verify_link_loads(page, "Impressum", "impressum")

        # Step 5: Zurueck und Datenschutz-Link pruefen
        print("Step 5: Zurueck navigieren, Datenschutz-Link pruefen")
        page.go_back()
        page.wait_for_load_state("domcontentloaded")
        scroll_to_footer(page)
        verify_link_loads(page, "Datenschutz", "datenschutz")

        # Step 6: Zurueck und AGB-Link pruefen
        print("Step 6: Zurueck navigieren, AGB-Link pruefen")
        page.go_back()
        page.wait_for_load_state("domcontentloaded")
        scroll_to_footer(page)
        verify_link_loads(page, "AGB", "agb")

        print("TC-CONTENT-003: BESTANDEN - Alle Footer-Links erreichbar")

    except Exception as e:
        print(f"TC-CONTENT-003: FEHLGESCHLAGEN - {e}")
        try:
            page.screenshot(path="error_TC-CONTENT-003_footer-links.png")
            print("  Screenshot gespeichert: error_TC-CONTENT-003_footer-links.png")
        except Exception:
            pass
        raise


# =============================================================================
# TC-CONTENT-004: Kontaktinformationen im Footer
# =============================================================================

@pytest.mark.regression
def test_footer_contact_info(page: Page, base_url: str):
    """TC-CONTENT-004: Kontaktinformationen sind im Footer sichtbar."""
    print("\nTC-CONTENT-004: Kontaktinformationen im Footer")

    try:
        # Step 1: Startseite aufrufen
        print("Step 1: Startseite aufrufen")
        page.goto(base_url)
        page.wait_for_load_state("domcontentloaded")

        # Step 2: Cookie-Banner akzeptieren
        print("Step 2: Cookie-Banner akzeptieren")
        accept_cookie_banner(page)

        # Step 3: Zum Footer scrollen
        print("Step 3: Zum Footer scrollen")
        scroll_to_footer(page)

        # Step 4: Kontaktbereich pruefen
        print("Step 4: Kontaktbereich im Footer pruefen")
        footer = page.locator("footer, .footer-main, .footer").first
        expect(footer).to_be_visible(timeout=5000)

        contact_selectors = [
            ".footer-contact",
            ".footer-service-hotline",
            ".service-menu",
            "footer .contact",
            "footer [class*='contact']",
            "footer [class*='service']",
            "footer [class*='hotline']",
        ]

        contact_found = False
        for selector in contact_selectors:
            contact_section = page.locator(selector)
            if contact_section.count() > 0 and contact_section.first.is_visible():
                contact_found = True
                print(f"  Kontaktbereich gefunden mit Selektor: {selector}")
                break

        if not contact_found:
            # Fallback: Pruefen ob Footer Kontakt-relevanten Text enthaelt
            footer_text = footer.inner_text().lower()
            contact_keywords = [
                "kontakt", "service", "telefon", "tel",
                "hotline", "email", "e-mail", "@"
            ]
            for keyword in contact_keywords:
                if keyword in footer_text:
                    contact_found = True
                    print(f"  Kontakt-Keyword gefunden im Footer: '{keyword}'")
                    break

        assert contact_found,             "Kein Kontaktbereich oder Kontakt-Informationen im Footer gefunden"

        # Step 5: Kontakt oder Service-Info pruefen
        print("Step 5: Kontakt oder Service-Info pruefen")
        footer_text = footer.inner_text().lower()
        service_keywords = [
            "kontakt", "service", "telefon", "tel",
            "hotline", "beratung"
        ]
        keyword_found = any(kw in footer_text for kw in service_keywords)

        assert keyword_found,             f"Footer enthaelt keine Kontakt-/Service-Keywords. Footer-Text: {footer_text[:200]}"

        print("TC-CONTENT-004: BESTANDEN - Kontaktinformationen im Footer vorhanden")

    except Exception as e:
        print(f"TC-CONTENT-004: FEHLGESCHLAGEN - {e}")
        try:
            page.screenshot(path="error_TC-CONTENT-004_kontaktinfo.png")
            print("  Screenshot gespeichert: error_TC-CONTENT-004_kontaktinfo.png")
        except Exception:
            pass
        raise


# =============================================================================
# TC-CONTENT-005: Trust-Siegel angezeigt
# =============================================================================

@pytest.mark.regression
def test_trust_seals_displayed(page: Page, base_url: str):
    """TC-CONTENT-005: Trust-Siegel/Zertifizierungen werden im Footer angezeigt."""
    print("\nTC-CONTENT-005: Trust-Siegel angezeigt")

    try:
        # Step 1: Startseite aufrufen
        print("Step 1: Startseite aufrufen")
        page.goto(base_url)
        page.wait_for_load_state("domcontentloaded")

        # Step 2: Cookie-Banner akzeptieren
        print("Step 2: Cookie-Banner akzeptieren")
        accept_cookie_banner(page)

        # Step 3: Zum Footer scrollen
        print("Step 3: Zum Footer scrollen")
        scroll_to_footer(page)

        # Step 4: Trust-Siegel Bereich pruefen
        print("Step 4: Trust-Siegel/Zertifizierungen Bereich pruefen")
        trust_selectors = [
            ".footer-trust",
            ".trust-badges",
            ".footer-logos",
            "footer [class*='trust']",
            "footer [class*='badge']",
            "footer [class*='siegel']",
            "footer [class*='certificate']",
            "footer [class*='zertifikat']",
            "footer [class*='logo']",
        ]

        trust_section_found = False
        matched_selector = None
        for selector in trust_selectors:
            section = page.locator(selector)
            if section.count() > 0 and section.first.is_visible():
                trust_section_found = True
                matched_selector = selector
                print(f"  Trust-Bereich gefunden mit Selektor: {selector}")
                break

        assert trust_section_found,             "Kein Trust-Siegel/Zertifizierungsbereich im Footer gefunden"

        # Step 5: Mindestens ein Trust-Badge/Siegel-Bild pruefen
        print("Step 5: Trust-Badge/Siegel-Bild pruefen")
        image_selectors = [
            ".footer-trust img",
            ".trust-badges img",
            ".footer-logos img",
            "footer [class*='trust'] img",
            "footer [class*='badge'] img",
            "footer [class*='siegel'] img",
            "footer [class*='logo'] img",
        ]

        image_found = False
        for selector in image_selectors:
            images = page.locator(selector)
            if images.count() > 0:
                # Pruefen ob mindestens ein Bild sichtbar ist
                for i in range(images.count()):
                    if images.nth(i).is_visible():
                        image_found = True
                        print(f"  Trust-Siegel-Bild gefunden mit Selektor: {selector} (Index {i})")
                        break
            if image_found:
                break

        if not image_found:
            # Fallback: SVG-Elemente pruefen
            svg_selectors = [
                "footer [class*='trust'] svg",
                "footer [class*='badge'] svg",
                "footer [class*='logo'] svg",
            ]
            for selector in svg_selectors:
                svgs = page.locator(selector)
                if svgs.count() > 0:
                    image_found = True
                    print(f"  Trust-Siegel als SVG gefunden mit Selektor: {selector}")
                    break

        assert image_found,             "Kein Trust-Siegel-Bild (img oder svg) im Footer gefunden"

        print("TC-CONTENT-005: BESTANDEN - Trust-Siegel werden angezeigt")

    except Exception as e:
        print(f"TC-CONTENT-005: FEHLGESCHLAGEN - {e}")
        try:
            page.screenshot(path="error_TC-CONTENT-005_trust-siegel.png")
            print("  Screenshot gespeichert: error_TC-CONTENT-005_trust-siegel.png")
        except Exception:
            pass
        raise


# =============================================================================
# TC-CONTENT-006: Matratzen-Berater erreichbar
# =============================================================================

@pytest.mark.regression
def test_mattress_advisor_accessible(page: Page, base_url: str):
    """TC-CONTENT-006: Matratzen-Berater ist erreichbar und interaktiv."""
    print("\nTC-CONTENT-006: Matratzen-Berater erreichbar")

    try:
        # Step 1: Schlafen-Kategorie aufrufen
        print("Step 1: Schlafen-Kategorie aufrufen")
        page.goto(f"{base_url}/schlafen/")
        page.wait_for_load_state("domcontentloaded")

        # Step 2: Cookie-Banner akzeptieren
        print("Step 2: Cookie-Banner akzeptieren")
        accept_cookie_banner(page)

        # Step 3: Link zum Matratzen-Berater finden
        print("Step 3: Link zum Matratzen-Berater finden")
        advisor_selectors = [
            "a[href*='matratzen-berater']",
            "a:has-text('Matratzen-Berater')",
            "a:has-text('Matratzenberater')",
            "a[href*='berater']",
            "a:has-text('Berater')",
        ]

        advisor_link = None
        for selector in advisor_selectors:
            link = page.locator(selector)
            if link.count() > 0 and link.first.is_visible():
                advisor_link = link.first
                print(f"  Matratzen-Berater Link gefunden mit Selektor: {selector}")
                break

        if advisor_link is None:
            # Fallback: Suche verwenden
            print("  Kein direkter Link gefunden - Suche verwenden")
            page.goto(f"{base_url}/search?search=Matratzen-Berater")
            page.wait_for_load_state("domcontentloaded")

            for selector in advisor_selectors:
                link = page.locator(selector)
                if link.count() > 0 and link.first.is_visible():
                    advisor_link = link.first
                    print(f"  Matratzen-Berater Link in Suchergebnissen gefunden: {selector}")
                    break

        assert advisor_link is not None,             "Kein Link zum Matratzen-Berater gefunden (weder in Schlafen-Kategorie noch via Suche)"

        # Step 4: Matratzen-Berater Link klicken
        print("Step 4: Matratzen-Berater Link klicken")
        advisor_link.click()
        page.wait_for_load_state("domcontentloaded")

        current_url = page.url.lower()
        assert "berater" in current_url or "advisor" in current_url or "matratzen" in current_url,             f"URL '{page.url}' scheint nicht zur Berater-Seite zu fuehren"

        print(f"  Berater-Seite geladen: {page.url}")

        # Pruefen auf Server-Fehler
        error_elements = page.locator(".alert-danger, .error-500, .error-404")
        assert error_elements.count() == 0,             "Fehler auf der Matratzen-Berater Seite"

        # Step 5: Interaktive Elemente pruefen
        print("Step 5: Interaktive Elemente pruefen")
        interactive_selectors = [
            ".advisor-step button",
            ".berater-step button",
            "button[class*='advisor']",
            "button[class*='berater']",
            "form button",
            "form select",
            "form input",
            ".cms-section button",
            "button",
        ]

        interactive_found = False
        for selector in interactive_selectors:
            elements = page.locator(selector)
            if elements.count() > 0:
                interactive_found = True
                print(f"  Interaktive Elemente gefunden: {selector} ({elements.count()} Elemente)")
                break

        assert interactive_found,             "Keine interaktiven Elemente auf der Matratzen-Berater Seite gefunden"

        print("TC-CONTENT-006: BESTANDEN - Matratzen-Berater erreichbar und interaktiv")

    except Exception as e:
        print(f"TC-CONTENT-006: FEHLGESCHLAGEN - {e}")
        try:
            page.screenshot(path="error_TC-CONTENT-006_matratzen-berater.png")
            print("  Screenshot gespeichert: error_TC-CONTENT-006_matratzen-berater.png")
        except Exception:
            pass
        raise


# =============================================================================
# TC-CONTENT-007: Online-Katalog aufrufbar
# =============================================================================

@pytest.mark.regression
def test_online_catalog_accessible(page: Page, base_url: str):
    """TC-CONTENT-007: Online-Katalog ist aufrufbar (Seite oder PDF)."""
    print("\nTC-CONTENT-007: Online-Katalog aufrufbar")

    try:
        # Step 1: Startseite aufrufen
        print("Step 1: Startseite aufrufen")
        page.goto(base_url)
        page.wait_for_load_state("domcontentloaded")

        # Step 2: Cookie-Banner akzeptieren
        print("Step 2: Cookie-Banner akzeptieren")
        accept_cookie_banner(page)

        # Step 3: Katalog-Link finden (Footer oder Navigation)
        print("Step 3: Katalog-Link finden")

        # Erst zum Footer scrollen um alle Links sichtbar zu machen
        scroll_to_footer(page)

        catalog_selectors = [
            "a:has-text('Katalog')",
            "a[href*='katalog']",
            "a:has-text('Online-Katalog')",
            "a:has-text('Onlinekatalog')",
            "footer a:has-text('Katalog')",
            "footer a[href*='katalog']",
        ]

        catalog_link = None
        for selector in catalog_selectors:
            link = page.locator(selector)
            if link.count() > 0 and link.first.is_visible():
                catalog_link = link.first
                print(f"  Katalog-Link gefunden mit Selektor: {selector}")
                break

        if catalog_link is None:
            # Fallback: Zurueck nach oben scrollen und in Navigation suchen
            print("  Kein Katalog-Link im Footer - Navigation pruefen")
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(500)

            nav_selectors = [
                "nav a:has-text('Katalog')",
                "nav a[href*='katalog']",
                ".main-navigation a:has-text('Katalog')",
                "header a:has-text('Katalog')",
            ]

            for selector in nav_selectors:
                link = page.locator(selector)
                if link.count() > 0 and link.first.is_visible():
                    catalog_link = link.first
                    print(f"  Katalog-Link in Navigation gefunden: {selector}")
                    break

        assert catalog_link is not None,             "Kein Katalog-Link gefunden (weder im Footer noch in der Navigation)"

        # Step 4: Katalog-Link klicken
        print("Step 4: Katalog-Link klicken")

        # Pruefen ob der Link ein PDF oeffnet oder eine Seite
        href = catalog_link.get_attribute("href") or ""
        target = catalog_link.get_attribute("target") or ""

        if ".pdf" in href.lower():
            print(f"  Katalog ist ein PDF-Link: {href}")
            # Bei PDF-Links pruefen wir nur dass der href gesetzt ist
            assert len(href) > 5, "PDF-Link URL ist zu kurz"
            print(f"  PDF-Katalog URL: {href}")
        elif target == "_blank":
            print(f"  Katalog oeffnet in neuem Tab: {href}")
            # Bei externen Links: Neues Tab abfangen
            with page.expect_popup() as popup_info:
                catalog_link.click()
            popup_page = popup_info.value
            popup_page.wait_for_load_state("domcontentloaded")
            popup_url = popup_page.url
            print(f"  Katalog-Seite geladen (neues Tab): {popup_url}")
            assert len(popup_url) > 10, "Katalog-Seite URL ist leer"
            popup_page.close()
        else:
            catalog_link.click()
            page.wait_for_load_state("domcontentloaded")
            current_url = page.url
            print(f"  Katalog-Seite geladen: {current_url}")

            # Pruefen auf Server-Fehler
            error_elements = page.locator(".alert-danger, .error-500, .error-404")
            assert error_elements.count() == 0,                 "Fehler auf der Katalog-Seite"

            # Seiteninhalt muss vorhanden sein
            body_text = page.locator("body").inner_text()
            assert len(body_text.strip()) > 20,                 "Katalog-Seite hat zu wenig Inhalt"

        print("TC-CONTENT-007: BESTANDEN - Online-Katalog ist aufrufbar")

    except Exception as e:
        print(f"TC-CONTENT-007: FEHLGESCHLAGEN - {e}")
        try:
            page.screenshot(path="error_TC-CONTENT-007_online-katalog.png")
            print("  Screenshot gespeichert: error_TC-CONTENT-007_online-katalog.png")
        except Exception:
            pass
        raise
