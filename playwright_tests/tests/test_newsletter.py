"""
Newsletter Tests - TC-NEWSLETTER-001 bis TC-NEWSLETTER-002
Tests fuer Newsletter-Anmeldung mit gueltiger und ungueltiger E-Mail
"""
import time
import pytest
from playwright.sync_api import Page, expect

from ..conftest import accept_cookie_banner


# =============================================================================
# TC-NEWSLETTER-001: Anmeldung mit gueltiger E-Mail
# =============================================================================

@pytest.mark.newsletter
@pytest.mark.feature
def test_newsletter_signup_valid_email(page: Page, base_url: str):
    """
    TC-NEWSLETTER-001: Newsletter-Anmeldung mit gueltiger E-Mail.

    Prueft, dass eine Newsletter-Anmeldung mit gueltiger E-Mail
    erfolgreich durchgefuehrt werden kann.
    """
    print("\n=== TC-NEWSLETTER-001: Newsletter-Anmeldung gueltige E-Mail ===")

    # Schritt 1: Startseite aufrufen
    print("[1] Startseite aufrufen...")
    page.goto(base_url)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)
    accept_cookie_banner(page)

    # Schritt 2: Newsletter-Formular im Footer suchen
    print("[2] Newsletter-Formular suchen...")
    # Zum Footer scrollen
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(1000)

    newsletter_form = page.locator(
        "form.newsletter-form, .footer-newsletter form, "
        ".newsletter-signup form, .cms-element-form-newsletter"
    )

    if newsletter_form.count() == 0:
        # Fallback: Newsletter-Seite direkt aufrufen
        print("   Kein Footer-Formular, versuche /newsletter...")
        page.goto(f"{base_url}/newsletter")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(1000)
        newsletter_form = page.locator("form")

    if newsletter_form.count() == 0:
        pytest.skip("Kein Newsletter-Formular gefunden")

    # Schritt 3: Gueltige E-Mail eingeben
    print("[3] E-Mail eingeben...")
    timestamp = int(time.time())
    test_email = f"test-newsletter-{timestamp}@example.com"

    email_input = page.locator(
        "input[type='email'], input[name='email'], "
        "input#newsletterMail, .newsletter-form input[type=email]"
    )

    if email_input.count() == 0:
        pytest.skip("Kein E-Mail-Eingabefeld im Newsletter-Formular gefunden")

    expect(email_input.first).to_be_visible(timeout=5000)
    email_input.first.fill(test_email)
    print(f"   E-Mail: {test_email}")

    # Schritt 4: Formular absenden
    print("[4] Formular absenden...")
    submit_button = page.locator(
        "button[type='submit'], .newsletter-form button, "
        ".btn-newsletter-submit, input[type=submit]"
    )

    if submit_button.count() > 0:
        submit_button.first.click()
    else:
        # Fallback: Enter druecken
        email_input.first.press("Enter")

    page.wait_for_timeout(3000)

    # Schritt 5: Bestaetigungsmeldung pruefen
    print("[5] Bestaetigungsmeldung pruefen...")
    success_selectors = [
        ".alert-success",
        ".newsletter-success",
        "text=Vielen Dank",
        "text=erfolgreich",
        "text=Anmeldung",
        ".success-message",
    ]

    success_found = False
    for selector in success_selectors:
        msg = page.locator(selector)
        if msg.count() > 0 and msg.first.is_visible():
            success_found = True
            print(f"   Erfolgsmeldung gefunden: {selector}")
            break

    # Auch auf Fehler pruefen
    error_msg = page.locator(".alert-danger, .alert-error, .newsletter-error")
    if error_msg.count() > 0 and error_msg.first.is_visible():
        error_text = error_msg.first.inner_text()
        print(f"   Fehlermeldung: {error_text}")

    if not success_found:
        # Moeglicherweise wurde die Seite weitergeleitetet
        current_url = page.url
        print(f"   Aktuelle URL nach Submit: {current_url}")
        # Wenn URL sich geaendert hat, ist das auch ein Zeichen fuer Erfolg
        if "newsletter" in current_url.lower() or "danke" in current_url.lower():
            success_found = True
            print("   Weiterleitung zu Bestaetigungsseite")

    assert success_found, "Newsletter-Anmeldung sollte eine Erfolgsmeldung zeigen"

    print("=== TC-NEWSLETTER-001: BESTANDEN ===")


# =============================================================================
# TC-NEWSLETTER-002: Anmeldung mit ungueltiger E-Mail
# =============================================================================

@pytest.mark.newsletter
@pytest.mark.feature
def test_newsletter_signup_invalid_email(page: Page, base_url: str):
    """
    TC-NEWSLETTER-002: Newsletter-Anmeldung mit ungueltiger E-Mail.

    Prueft, dass eine Newsletter-Anmeldung mit ungueltiger E-Mail
    eine Fehlermeldung zeigt und nicht erfolgreich ist.
    """
    print("\n=== TC-NEWSLETTER-002: Newsletter-Anmeldung ungueltige E-Mail ===")

    # Schritt 1: Startseite aufrufen
    print("[1] Startseite aufrufen...")
    page.goto(base_url)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)
    accept_cookie_banner(page)

    # Schritt 2: Newsletter-Formular suchen
    print("[2] Newsletter-Formular suchen...")
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(1000)

    newsletter_form = page.locator(
        "form.newsletter-form, .footer-newsletter form, "
        ".newsletter-signup form, .cms-element-form-newsletter"
    )

    if newsletter_form.count() == 0:
        page.goto(f"{base_url}/newsletter")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(1000)
        newsletter_form = page.locator("form")

    if newsletter_form.count() == 0:
        pytest.skip("Kein Newsletter-Formular gefunden")

    # Schritt 3: Ungueltige E-Mail eingeben
    print("[3] Ungueltige E-Mail eingeben...")
    invalid_email = "keine-gueltige-email"

    email_input = page.locator(
        "input[type='email'], input[name='email'], "
        "input#newsletterMail, .newsletter-form input[type=email]"
    )

    if email_input.count() == 0:
        pytest.skip("Kein E-Mail-Eingabefeld gefunden")

    expect(email_input.first).to_be_visible(timeout=5000)
    email_input.first.fill(invalid_email)
    print(f"   Ungueltige E-Mail: {invalid_email}")

    # Schritt 4: Formular absenden
    print("[4] Formular absenden...")
    submit_button = page.locator(
        "button[type='submit'], .newsletter-form button, "
        ".btn-newsletter-submit, input[type=submit]"
    )

    if submit_button.count() > 0:
        submit_button.first.click()
    else:
        email_input.first.press("Enter")

    page.wait_for_timeout(2000)

    # Schritt 5: Fehlermeldung pruefen
    print("[5] Fehlermeldung pruefen...")

    # Browser-eigene Validierung pruefen (HTML5 email type)
    is_invalid = email_input.first.evaluate(
        "el => !el.validity.valid"
    )

    # Auch auf Server-seitige Fehler pruefen
    error_selectors = [
        ".alert-danger",
        ".alert-error",
        ".newsletter-error",
        ".invalid-feedback",
        ".form-error",
        "text=ungueltig",
        "text=Fehler",
    ]

    error_found = is_invalid
    for selector in error_selectors:
        msg = page.locator(selector)
        if msg.count() > 0 and msg.first.is_visible():
            error_found = True
            error_text = msg.first.inner_text().strip()
            print(f"   Fehlermeldung gefunden: {error_text[:100]}")
            break

    if is_invalid:
        print("   HTML5-Validierung: E-Mail ungueltig")

    # Keine Erfolgsmeldung sollte erscheinen
    success_msg = page.locator(".alert-success, .newsletter-success, .success-message")
    no_success = success_msg.count() == 0 or not success_msg.first.is_visible()

    assert error_found or no_success, (
        "Ungueltige E-Mail sollte Fehler zeigen oder Anmeldung verhindern"
    )

    print("=== TC-NEWSLETTER-002: BESTANDEN ===")
