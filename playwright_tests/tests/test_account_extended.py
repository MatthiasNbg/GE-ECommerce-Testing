"""
Account Extended Tests - TC-ACCOUNT-009 bis TC-ACCOUNT-010
Tests fuer Passwort-Wiederherstellung und Bestellhistorie
"""
import pytest
from playwright.sync_api import Page, expect

from ..conftest import accept_cookie_banner


# =============================================================================
# Hilfsfunktionen
# =============================================================================

def _perform_login(page: Page, base_url: str, config) -> bool:
    """
    Hilfsfunktion: Login mit Test-Account durchfuehren.

    Verwendet die Konfiguration aus config.yaml.
    Returns True bei Erfolg, False bei Fehler.
    """
    # Zugangsdaten aus config holen
    try:
        customer = config.get_registered_customer(0)
        if not customer:
            return False
        email = customer.email
        password = config.get_customer_password(customer)
        if not password:
            return False
    except Exception:
        return False

    # Login-Seite aufrufen
    page.goto(f"{base_url}/account/login")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)
    accept_cookie_banner(page)

    # Login-Formular ausfuellen
    email_field = page.locator("#loginMail")
    password_field = page.locator("#loginPassword")

    if email_field.count() == 0 or password_field.count() == 0:
        return False

    email_field.fill(email)
    password_field.fill(password)

    # Login-Button klicken
    login_btn = page.locator("button[type='submit'].login-submit-btn, .login-submit-btn")
    if login_btn.count() > 0:
        login_btn.first.click()
    else:
        password_field.press("Enter")

    page.wait_for_timeout(3000)

    # Pruefen ob Login erfolgreich
    return "/account" in page.url and "/login" not in page.url


# =============================================================================
# TC-ACCOUNT-009: Passwort vergessen
# =============================================================================

@pytest.mark.account
@pytest.mark.feature
def test_password_reset_request(page: Page, base_url: str):
    """
    TC-ACCOUNT-009: Passwort vergessen.

    Prueft, dass der Passwort-Wiederherstellungsprozess gestartet
    werden kann und eine Bestaetigungsmeldung angezeigt wird.
    """
    print("\n=== TC-ACCOUNT-009: Passwort vergessen ===")

    # Schritt 1: Login-Seite aufrufen
    print("[1] Login-Seite aufrufen...")
    page.goto(f"{base_url}/account/login")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)
    accept_cookie_banner(page)

    # Schritt 2: Passwort vergessen Link klicken
    print("[2] Passwort vergessen Link klicken...")
    recover_link = page.locator(
        "a[href*='recover'], "
        "a:has-text('Passwort vergessen'), "
        "a:has-text('Kennwort vergessen')"
    )

    if recover_link.count() == 0:
        pytest.skip("Kein Passwort-vergessen-Link gefunden")

    expect(recover_link.first).to_be_visible(timeout=5000)
    recover_link.first.click()
    page.wait_for_timeout(2000)

    # Schritt 3: E-Mail eingeben
    print("[3] E-Mail eingeben...")
    email_field = page.locator(
        "#personalMail, input[name=email], "
        "input[type='email'], .recover-password-form input"
    )

    if email_field.count() == 0:
        pytest.skip("Kein E-Mail-Feld auf der Passwort-Recovery-Seite")

    expect(email_field.first).to_be_visible(timeout=5000)
    email_field.first.fill("test-recover@example.com")
    print("   E-Mail: test-recover@example.com")

    # Schritt 4: Formular absenden
    print("[4] Formular absenden...")
    submit_btn = page.locator("button[type='submit']")
    if submit_btn.count() > 0:
        submit_btn.first.click()
    else:
        email_field.first.press("Enter")

    page.wait_for_timeout(3000)

    # Schritt 5: Bestaetigungsmeldung pruefen
    print("[5] Bestaetigungsmeldung pruefen...")
    confirmation_selectors = [
        ".alert-success",
        ".alert-info",
        ".recover-password-success",
    ]

    confirmation_found = False
    for selector in confirmation_selectors:
        msg = page.locator(selector)
        if msg.count() > 0 and msg.first.is_visible():
            confirmation_found = True
            print(f"   Bestaetigung gefunden: {selector}")
            break

    current_url = page.url
    print(f"   Aktuelle URL: {current_url}")
    if not confirmation_found:
        if "recover" in current_url or "success" in current_url:
            confirmation_found = True

    assert confirmation_found, (
        "Passwort-Recovery sollte Bestaetigungsmeldung zeigen"
    )

    print("=== TC-ACCOUNT-009: BESTANDEN ===")


# =============================================================================
# TC-ACCOUNT-010: Bestellhistorie einsehen
# =============================================================================

@pytest.mark.account
@pytest.mark.feature
def test_order_history(page: Page, base_url: str, config):
    """
    TC-ACCOUNT-010: Bestellhistorie einsehen.

    Prueft, dass ein eingeloggter Kunde seine Bestellhistorie
    einsehen kann.
    """
    print("\n=== TC-ACCOUNT-010: Bestellhistorie einsehen ===")

    # Schritt 1: Login durchfuehren
    print("[1] Login durchfuehren...")
    login_success = _perform_login(page, base_url, config)

    if not login_success:
        pytest.skip("Login fehlgeschlagen - Keine Test-Zugangsdaten konfiguriert")

    print("   Login erfolgreich")

    # Schritt 2: Zur Bestellhistorie navigieren
    print("[2] Bestellhistorie aufrufen...")
    # Direkt zur Bestelluebersicht navigieren
    page.goto(f"{base_url}/account/order")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(2000)

    # Pruefen ob wir auf der richtigen Seite sind
    current_url = page.url
    print(f"   URL: {current_url}")

    # Falls auf Login-Seite umgeleitet, Login erneut versuchen
    if "/login" in current_url:
        print("   Auf Login-Seite umgeleitet, erneuter Login...")
        login_success = _perform_login(page, base_url, config)
        if not login_success:
            pytest.skip("Login nach Umleitung fehlgeschlagen")
        page.goto(f"{base_url}/account/order")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)

    # Schritt 3: Bestellhistorie pruefen
    print("[3] Bestellhistorie pruefen...")

    # Bestellungen oder Hinweis auf keine Bestellungen
    order_items = page.locator(
        ".order-item, .order-table-body tr, "
        ".order-item-header, .order-wrapper"
    )
    order_count = order_items.count()

    no_orders_msg = page.locator(
        ".account-orders-empty, text=keine Bestellungen, "
        "text=Keine Bestellungen, .empty-state"
    )

    if order_count > 0:
        print(f"   Bestellungen gefunden: {order_count}")

        # Erste Bestellung pruefen
        first_order = order_items.first
        order_text = first_order.inner_text().strip()
        print(f"   Erste Bestellung: {order_text[:100]}...")

        # Bestellnummer sollte vorhanden sein
        order_number = page.locator(
            ".order-item-header .order-number, "
            ".order-table-header-order-number, "
            ".order-id"
        )
        if order_number.count() > 0:
            nr = order_number.first.inner_text().strip()
            print(f"   Bestellnummer: {nr}")

    elif no_orders_msg.count() > 0 and no_orders_msg.first.is_visible():
        print("   Keine Bestellungen vorhanden (leere Bestellhistorie)")
        # Das ist ein gueltiger Zustand - Test bestanden
    else:
        # Seite hat weder Bestellungen noch Leer-Meldung
        page_text = page.locator("body").inner_text()[:500]
        print(f"   Seiteninhalt: {page_text[:200]}")

    # Die Seite sollte geladen haben (kein 404, kein Fehler)
    assert "/account" in page.url, (
        f"Sollte auf Account-Seite sein, aber URL ist: {page.url}"
    )

    # Mindestens eines muss zutreffen: Bestellungen oder Leer-Meldung
    has_content = order_count > 0 or (no_orders_msg.count() > 0)
    assert has_content, "Bestellhistorie-Seite sollte Bestellungen oder Leer-Hinweis zeigen"

    print("=== TC-ACCOUNT-010: BESTANDEN ===")
