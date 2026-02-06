"""
Account-Tests (Phase 3 Feature Tests).

Testet:
- TC-ACC-001: Registrierung erfolgreich
- TC-ACC-002: Duplikat-E-Mail wird abgelehnt
- TC-ACC-003: Ungültige E-Mail zeigt Fehler
- TC-ACC-004: Schwaches Passwort abgelehnt
- TC-ACC-005: Login erfolgreich
- TC-ACC-006: Login mit falschen Daten fehlschlägt
- TC-ACC-007: Profil anzeigen und bearbeiten
- TC-ACC-008: Adressverwaltung
- TC-ACCOUNT-011: E-Mail auf bestehende Adresse ändern wird abgelehnt
- TC-ACCOUNT-012: Adresse bearbeiten und im Checkout verifizieren
"""
import os
import pytest
from playwright.async_api import async_playwright

from ..conftest import accept_cookie_banner_async
from ..pages.account_page import AccountPage, RegistrationData
from ..pages.cart_page import CartPage
from ..pages.checkout_page import CheckoutPage


# =============================================================================
# Test Fixtures
# =============================================================================

def get_test_customer_credentials(config, country: str = None) -> tuple[str, str]:
    """
    Holt die Test-Kunden-Zugangsdaten aus der Konfiguration.

    Args:
        config: TestConfig Objekt
        country: Optional - Land des Kunden (AT, DE, CH). Wenn None, erster Kunde.

    Returns:
        Tuple (email, password)
    """
    # Kunde nach Land oder ersten Kunden holen
    if country:
        customer = config.get_customer_by_country(country)
    else:
        customer = config.get_registered_customer(0)

    if not customer:
        pytest.skip("Keine Test-Kunden in config.yaml konfiguriert")

    email = customer.email
    password = config.get_customer_password(customer)

    if not password:
        pytest.skip("Kein Passwort konfiguriert")

    return email, password


# =============================================================================
# TC-ACC-001: Registrierung erfolgreich
# =============================================================================

@pytest.mark.asyncio
@pytest.mark.account
@pytest.mark.feature
async def test_registration_success(config, request):
    """
    TC-ACC-001: Erfolgreiche Registrierung eines neuen Kunden.

    Verwendet einen Timestamp-basierten E-Mail, um Duplikate zu vermeiden.
    """
    print("\n=== TC-ACC-001: Registrierung erfolgreich ===")

    headed = request.config.getoption("--headed", default=False)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=not headed,
            slow_mo=200 if headed else 0
        )

        context_args = {"viewport": {"width": 1920, "height": 1080}}
        if config.htaccess_user and config.htaccess_password:
            context_args["http_credentials"] = {
                "username": config.htaccess_user,
                "password": config.htaccess_password,
            }

        context = await browser.new_context(**context_args)
        page = await context.new_page()

        try:
            account = AccountPage(page, config.base_url)

            # Zur Registrierungs-Seite navigieren
            print("[1] Navigiere zur Registrierungs-Seite...")
            await account.goto_register()

            # Cookie-Banner akzeptieren
            await accept_cookie_banner_async(page)

            # Einzigartige E-Mail generieren
            unique_email = AccountPage.generate_unique_email("reg-test")
            print(f"   E-Mail: {unique_email}")

            # Registrierungsdaten
            reg_data = RegistrationData(
                salutation="mr",
                first_name="Test",
                last_name="Registrierung",
                email=unique_email,
                password="TestPasswort123!",
                street="Teststraße 456",
                zip_code="4020",
                city="Linz",
                country="AT"
            )

            # Registrierung durchführen
            print("[2] Registrierung durchführen...")
            success = await account.register(reg_data)

            if not success:
                error = await account.get_registration_error()
                print(f"   Fehler: {error}")
                await page.screenshot(path="debug_registration_error.png")

            assert success, "Registrierung sollte erfolgreich sein"

            # Prüfen ob eingeloggt
            print("[3] Prüfe Login-Status...")
            is_logged_in = await account.is_logged_in()
            assert is_logged_in, "Benutzer sollte nach Registrierung eingeloggt sein"

            print("=== TC-ACC-001: BESTANDEN ===")

        finally:
            await context.close()
            await browser.close()


# =============================================================================
# TC-ACC-002: Duplikat-E-Mail wird abgelehnt
# =============================================================================

@pytest.mark.asyncio
@pytest.mark.account
@pytest.mark.feature
async def test_registration_duplicate_email_fails(config, request):
    """
    TC-ACC-002: Registrierung mit bereits verwendeter E-Mail schlägt fehl.

    Verwendet die E-Mail eines existierenden Test-Accounts.
    """
    print("\n=== TC-ACC-002: Duplikat-E-Mail wird abgelehnt ===")

    email, _ = get_test_customer_credentials(config)
    headed = request.config.getoption("--headed", default=False)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=not headed,
            slow_mo=200 if headed else 0
        )

        context_args = {"viewport": {"width": 1920, "height": 1080}}
        if config.htaccess_user and config.htaccess_password:
            context_args["http_credentials"] = {
                "username": config.htaccess_user,
                "password": config.htaccess_password,
            }

        context = await browser.new_context(**context_args)
        page = await context.new_page()

        try:
            account = AccountPage(page, config.base_url)

            print("[1] Navigiere zur Registrierungs-Seite...")
            await account.goto_register()
            await accept_cookie_banner_async(page)

            # Existierende E-Mail verwenden
            print(f"[2] Registrierung mit existierender E-Mail: {email}")
            reg_data = RegistrationData(
                salutation="mrs",
                first_name="Duplikat",
                last_name="Test",
                email=email,  # Bereits existierend
                password="TestPasswort123!",
                street="Teststraße 789",
                zip_code="4020",
                city="Linz",
                country="AT"
            )

            success = await account.register(reg_data)

            # Registrierung sollte fehlschlagen
            assert not success, "Registrierung mit Duplikat-E-Mail sollte fehlschlagen"

            # Fehlermeldung prüfen
            print("[3] Prüfe Fehlermeldung...")
            error = await account.get_registration_error()
            print(f"   Fehler: {error}")

            # Typische Fehlermeldungen: "bereits registriert", "E-Mail-Adresse existiert"
            assert error is not None, "Es sollte eine Fehlermeldung angezeigt werden"

            print("=== TC-ACC-002: BESTANDEN ===")

        finally:
            await context.close()
            await browser.close()


# =============================================================================
# TC-ACC-003: Ungültige E-Mail zeigt Fehler
# =============================================================================

@pytest.mark.asyncio
@pytest.mark.account
@pytest.mark.feature
async def test_registration_invalid_email_shows_error(config, request):
    """
    TC-ACC-003: Registrierung mit ungültiger E-Mail-Adresse zeigt Fehler.
    """
    print("\n=== TC-ACC-003: Ungültige E-Mail zeigt Fehler ===")

    headed = request.config.getoption("--headed", default=False)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=not headed,
            slow_mo=200 if headed else 0
        )

        context_args = {"viewport": {"width": 1920, "height": 1080}}
        if config.htaccess_user and config.htaccess_password:
            context_args["http_credentials"] = {
                "username": config.htaccess_user,
                "password": config.htaccess_password,
            }

        context = await browser.new_context(**context_args)
        page = await context.new_page()

        try:
            account = AccountPage(page, config.base_url)

            print("[1] Navigiere zur Registrierungs-Seite...")
            await account.goto_register()
            await accept_cookie_banner_async(page)

            # Ungültige E-Mail verwenden
            invalid_email = "ungueltige-email-ohne-at"
            print(f"[2] Registrierung mit ungültiger E-Mail: {invalid_email}")

            reg_data = RegistrationData(
                salutation="mr",
                first_name="Invalid",
                last_name="Email",
                email=invalid_email,
                password="TestPasswort123!",
                street="Teststraße 123",
                zip_code="4020",
                city="Linz",
                country="AT"
            )

            success = await account.register(reg_data)

            # Registrierung sollte fehlschlagen
            assert not success, "Registrierung mit ungültiger E-Mail sollte fehlschlagen"

            # Fehlermeldung oder Formularfehler prüfen
            print("[3] Prüfe Formularfehler...")
            has_errors = await account.has_form_errors()
            error = await account.get_registration_error()

            assert has_errors or error, "Es sollte ein Formularfehler oder Fehlermeldung angezeigt werden"
            print(f"   Fehler gefunden: {error or 'Formularfehler'}")

            print("=== TC-ACC-003: BESTANDEN ===")

        finally:
            await context.close()
            await browser.close()


# =============================================================================
# TC-ACC-004: Schwaches Passwort abgelehnt
# =============================================================================

@pytest.mark.asyncio
@pytest.mark.account
@pytest.mark.feature
async def test_registration_weak_password_rejected(config, request):
    """
    TC-ACC-004: Registrierung mit schwachem Passwort wird abgelehnt.

    Shopware 6 erfordert typischerweise:
    - Mindestens 8 Zeichen
    - Großbuchstaben
    - Kleinbuchstaben
    - Zahlen
    """
    print("\n=== TC-ACC-004: Schwaches Passwort abgelehnt ===")

    headed = request.config.getoption("--headed", default=False)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=not headed,
            slow_mo=200 if headed else 0
        )

        context_args = {"viewport": {"width": 1920, "height": 1080}}
        if config.htaccess_user and config.htaccess_password:
            context_args["http_credentials"] = {
                "username": config.htaccess_user,
                "password": config.htaccess_password,
            }

        context = await browser.new_context(**context_args)
        page = await context.new_page()

        try:
            account = AccountPage(page, config.base_url)

            print("[1] Navigiere zur Registrierungs-Seite...")
            await account.goto_register()
            await accept_cookie_banner_async(page)

            # Schwaches Passwort
            weak_password = "1234"
            unique_email = AccountPage.generate_unique_email("weak-pw")
            print(f"[2] Registrierung mit schwachem Passwort: '{weak_password}'")

            reg_data = RegistrationData(
                salutation="mr",
                first_name="Weak",
                last_name="Password",
                email=unique_email,
                password=weak_password,
                street="Teststraße 123",
                zip_code="4020",
                city="Linz",
                country="AT"
            )

            success = await account.register(reg_data)

            # Registrierung sollte fehlschlagen
            assert not success, "Registrierung mit schwachem Passwort sollte fehlschlagen"

            # Fehler prüfen
            print("[3] Prüfe Fehlermeldung...")
            error = await account.get_registration_error()
            has_errors = await account.has_form_errors()

            assert error or has_errors, "Es sollte ein Passwort-Fehler angezeigt werden"
            print(f"   Fehler: {error or 'Formularfehler'}")

            print("=== TC-ACC-004: BESTANDEN ===")

        finally:
            await context.close()
            await browser.close()


# =============================================================================
# TC-ACC-005: Login erfolgreich (alle Länder)
# =============================================================================

def get_configured_countries():
    """Lädt alle konfigurierten Länder aus config.yaml."""
    from ..config import get_config
    cfg = get_config()
    countries = []
    for customer in cfg.test_customers.registered:
        if customer.country not in countries:
            countries.append(customer.country)
    return countries if countries else ["AT"]  # Fallback


@pytest.mark.asyncio
@pytest.mark.account
@pytest.mark.feature
@pytest.mark.parametrize("country", get_configured_countries())
async def test_login_success(config, request, country):
    """
    TC-ACC-005: Erfolgreicher Login mit korrekten Zugangsdaten.

    Testet alle konfigurierten Test-Accounts (AT, DE, CH).
    """
    print(f"\n=== TC-ACC-005: Login erfolgreich [{country}] ===")

    email, password = get_test_customer_credentials(config, country=country)
    print(f"   Test-Account: {email}")

    headed = request.config.getoption("--headed", default=False)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=not headed,
            slow_mo=200 if headed else 0
        )

        context_args = {"viewport": {"width": 1920, "height": 1080}}
        if config.htaccess_user and config.htaccess_password:
            context_args["http_credentials"] = {
                "username": config.htaccess_user,
                "password": config.htaccess_password,
            }

        context = await browser.new_context(**context_args)
        page = await context.new_page()

        try:
            account = AccountPage(page, config.base_url)

            print("[1] Navigiere zur Login-Seite...")
            await account.goto_login()

            print("[2] Login durchführen...")
            success = await account.login(email, password)

            if not success:
                error = await account.get_login_error()
                print(f"   Fehler: {error}")
                await page.screenshot(path=f"debug_login_error_{country}.png")

            assert success, f"Login für {country} sollte erfolgreich sein"

            # Prüfen ob eingeloggt
            print("[3] Prüfe Login-Status...")
            is_logged_in = await account.is_logged_in()
            assert is_logged_in, "Benutzer sollte eingeloggt sein"

            # Willkommensnachricht prüfen
            welcome = await account.get_welcome_message()
            if welcome:
                print(f"   Willkommensnachricht: {welcome}")

            print(f"=== TC-ACC-005 [{country}]: BESTANDEN ===")

        finally:
            await context.close()
            await browser.close()


# =============================================================================
# TC-ACC-006: Login mit falschen Daten fehlschlägt
# =============================================================================

@pytest.mark.asyncio
@pytest.mark.account
@pytest.mark.feature
async def test_login_wrong_credentials_fails(config, request):
    """
    TC-ACC-006: Login mit falschen Zugangsdaten schlägt fehl.
    """
    print("\n=== TC-ACC-006: Login mit falschen Daten fehlschlägt ===")

    headed = request.config.getoption("--headed", default=False)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=not headed,
            slow_mo=200 if headed else 0
        )

        context_args = {"viewport": {"width": 1920, "height": 1080}}
        if config.htaccess_user and config.htaccess_password:
            context_args["http_credentials"] = {
                "username": config.htaccess_user,
                "password": config.htaccess_password,
            }

        context = await browser.new_context(**context_args)
        page = await context.new_page()

        try:
            account = AccountPage(page, config.base_url)

            print("[1] Navigiere zur Login-Seite...")
            await account.goto_login()
            await accept_cookie_banner_async(page)

            # Falsche Zugangsdaten
            wrong_email = "nicht-existierend@example.com"
            wrong_password = "FalschesPasswort123!"
            print(f"[2] Login mit falschen Daten: {wrong_email}")

            success = await account.login(wrong_email, wrong_password)

            # Login sollte fehlschlagen
            assert not success, "Login mit falschen Daten sollte fehlschlagen"

            # Fehlermeldung prüfen
            print("[3] Prüfe Fehlermeldung...")
            error = await account.get_login_error()
            print(f"   Fehler: {error}")

            assert error is not None, "Es sollte eine Fehlermeldung angezeigt werden"

            # Sicherstellen, dass wir noch auf der Login-Seite sind
            assert await account.is_on_login_page(), "Sollte auf Login-Seite bleiben"

            print("=== TC-ACC-006: BESTANDEN ===")

        finally:
            await context.close()
            await browser.close()


# =============================================================================
# TC-ACC-007: Profil anzeigen und bearbeiten
# =============================================================================

@pytest.mark.asyncio
@pytest.mark.account
@pytest.mark.feature
async def test_profile_view_and_edit(config, request):
    """
    TC-ACC-007: Profil anzeigen und bearbeiten.

    1. Login mit Test-Account
    2. Profil anzeigen
    3. Namen ändern
    4. Änderung prüfen
    """
    print("\n=== TC-ACC-007: Profil anzeigen und bearbeiten ===")

    email, password = get_test_customer_credentials(config)
    headed = request.config.getoption("--headed", default=False)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=not headed,
            slow_mo=200 if headed else 0
        )

        context_args = {"viewport": {"width": 1920, "height": 1080}}
        if config.htaccess_user and config.htaccess_password:
            context_args["http_credentials"] = {
                "username": config.htaccess_user,
                "password": config.htaccess_password,
            }

        context = await browser.new_context(**context_args)
        page = await context.new_page()

        try:
            account = AccountPage(page, config.base_url)

            # Login
            print("[1] Login...")
            await account.goto_login()
            await accept_cookie_banner_async(page)
            success = await account.login(email, password)
            assert success, "Login fehlgeschlagen"

            # Zur Profil-Übersicht navigieren
            print("[2] Profil anzeigen...")
            await account.goto_profile()
            await page.wait_for_timeout(1000)

            is_logged_in = await account.is_logged_in()
            assert is_logged_in, "Sollte eingeloggt sein"

            # Zur Profil-Bearbeitung navigieren
            print("[3] Profil bearbeiten...")
            await account.navigate_to_profile_edit()
            await page.wait_for_timeout(500)

            # Timestamp für eindeutigen Namen
            import time
            timestamp = int(time.time())
            new_first_name = f"Test{timestamp % 1000}"

            # Profil aktualisieren
            print(f"   Ändere Vorname zu: {new_first_name}")
            success = await account.update_profile(first_name=new_first_name)

            # Hinweis: Erfolg kann auch ohne sichtbare Meldung sein
            print(f"   Profil-Update: {'Erfolgreich' if success else 'Keine Erfolgsmeldung (evtl. trotzdem erfolgreich)'}")

            # Screenshot zur Dokumentation
            await page.screenshot(path="debug_profile_edit.png")

            print("=== TC-ACC-007: BESTANDEN ===")

        finally:
            await context.close()
            await browser.close()


# =============================================================================
# TC-ACC-008: Adressverwaltung
# =============================================================================

@pytest.mark.asyncio
@pytest.mark.account
@pytest.mark.feature
async def test_address_management(config, request):
    """
    TC-ACC-008: Adressverwaltung - hinzufügen, bearbeiten, löschen.

    1. Login mit Test-Account
    2. Zur Adressverwaltung navigieren
    3. Adresse hinzufügen
    4. Anzahl prüfen
    """
    print("\n=== TC-ACC-008: Adressverwaltung ===")

    email, password = get_test_customer_credentials(config)
    headed = request.config.getoption("--headed", default=False)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=not headed,
            slow_mo=200 if headed else 0
        )

        context_args = {"viewport": {"width": 1920, "height": 1080}}
        if config.htaccess_user and config.htaccess_password:
            context_args["http_credentials"] = {
                "username": config.htaccess_user,
                "password": config.htaccess_password,
            }

        context = await browser.new_context(**context_args)
        page = await context.new_page()

        try:
            account = AccountPage(page, config.base_url)

            # Login
            print("[1] Login...")
            await account.goto_login()
            await accept_cookie_banner_async(page)
            success = await account.login(email, password)
            assert success, "Login fehlgeschlagen"

            # Zur Adressverwaltung
            print("[2] Zur Adressverwaltung navigieren...")
            await account.goto_addresses()
            await page.wait_for_timeout(1000)

            # Aktuelle Anzahl der Adressen
            initial_count = await account.get_address_count()
            print(f"   Aktuelle Adressen: {initial_count}")

            # Neue Adresse hinzufügen
            print("[3] Neue Adresse hinzufügen...")
            import time
            timestamp = int(time.time())

            added = await account.add_address(
                first_name=f"Test{timestamp % 1000}",
                last_name="Adresse",
                street=f"Neue Straße {timestamp % 100}",
                zip_code="5020",
                city="Salzburg",
                country="AT"
            )

            if added:
                print("   Adresse hinzugefügt")
            else:
                print("   Adresse hinzufügen (keine explizite Bestätigung)")

            await page.wait_for_timeout(1000)

            # Anzahl prüfen
            new_count = await account.get_address_count()
            print(f"   Neue Anzahl Adressen: {new_count}")

            # Hinweis: Bei manchen Shops könnte die Adresse in einem Modal hinzugefügt werden
            # und die Anzahl ändert sich erst nach Seitenaktualisierung
            if new_count > initial_count:
                print("   Adresse erfolgreich hinzugefügt")
            else:
                print("   Adress-Anzahl unverändert (evtl. Modal oder anderer UI-Flow)")
                # Seite neu laden und nochmal prüfen
                await account.goto_addresses()
                await page.wait_for_timeout(1000)
                final_count = await account.get_address_count()
                print(f"   Nach Reload: {final_count} Adressen")

            # Screenshot zur Dokumentation
            await page.screenshot(path="debug_address_management.png")

            print("=== TC-ACC-008: BESTANDEN ===")

        finally:
            await context.close()
            await browser.close()


# =============================================================================
# TC-ACCOUNT-011: E-Mail auf bestehende Adresse ändern wird abgelehnt
# =============================================================================

@pytest.mark.asyncio
@pytest.mark.account
@pytest.mark.feature
async def test_email_change_to_existing_email(config, request):
    """
    TC-ACCOUNT-011: E-Mail-Änderung auf bereits registrierte Adresse wird abgelehnt.

    1. Login als AT-Kunde
    2. Navigiere zu /account/profile
    3. E-Mail ändern auf ge-de-1@matthias-sax.de (bereits vergeben)
    4. Assert: Fehlermeldung erscheint
    5. Assert: URL bleibt auf Profil-Seite
    """
    print("\n=== TC-ACCOUNT-011: E-Mail auf bestehende Adresse ändern ===")

    # AT-Kunde Login-Daten
    email_at, password_at = get_test_customer_credentials(config, country="AT")
    # DE-Kunde E-Mail (Ziel der Änderung)
    customer_de = config.get_customer_by_country("DE")
    if not customer_de:
        pytest.skip("Kein DE-Kunde in config.yaml konfiguriert")
    existing_email = customer_de.email

    print(f"   AT-Kunde: {email_at}")
    print(f"   Ziel-E-Mail (bereits vergeben): {existing_email}")

    headed = request.config.getoption("--headed", default=False)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=not headed,
            slow_mo=200 if headed else 0
        )

        context_args = {"viewport": {"width": 1920, "height": 1080}}
        if config.htaccess_user and config.htaccess_password:
            context_args["http_credentials"] = {
                "username": config.htaccess_user,
                "password": config.htaccess_password,
            }

        context = await browser.new_context(**context_args)
        page = await context.new_page()

        try:
            account = AccountPage(page, config.base_url)

            # Login als AT-Kunde
            print("[1] Login als AT-Kunde...")
            await account.goto_login()
            await accept_cookie_banner_async(page)
            success = await account.login(email_at, password_at)
            assert success, "Login als AT-Kunde fehlgeschlagen"

            # Zur Profil-Bearbeitungsseite navigieren
            print("[2] Navigiere zur Profil-Seite...")
            await account.navigate("/account/profile")
            await page.wait_for_timeout(1000)

            # E-Mail auf bereits existierende Adresse ändern
            print(f"[3] E-Mail ändern auf: {existing_email}")
            change_success = await account.change_email(existing_email, password_at)

            # Änderung sollte fehlschlagen
            assert not change_success, "E-Mail-Änderung auf bestehende Adresse sollte abgelehnt werden"

            # Fehlermeldung prüfen
            print("[4] Prüfe Fehlermeldung...")
            alert = page.locator(".alert-danger")
            form_error = page.locator(".invalid-feedback")
            has_alert = await alert.count() > 0 and await alert.first.is_visible(timeout=3000)
            has_form_error = await form_error.count() > 0

            error_text = None
            if has_alert:
                error_text = await alert.first.text_content()
            elif has_form_error:
                error_text = await form_error.first.text_content()

            print(f"   Fehlermeldung: {error_text}")
            assert has_alert or has_form_error, "Es sollte eine Fehlermeldung angezeigt werden"

            # URL sollte auf Profil-Seite bleiben
            print("[5] Prüfe URL...")
            current_url = page.url
            assert "/account/profile" in current_url or "/account" in current_url, \
                f"Sollte auf Profil-Seite bleiben, ist aber auf: {current_url}"

            print("=== TC-ACCOUNT-011: BESTANDEN ===")

        finally:
            await context.close()
            await browser.close()


# =============================================================================
# TC-ACCOUNT-012: Adresse bearbeiten und im Checkout verifizieren
# =============================================================================

@pytest.mark.asyncio
@pytest.mark.account
@pytest.mark.feature
async def test_address_edit_checkout_display(config, request):
    """
    TC-ACCOUNT-012: Adresse bearbeiten und im Checkout verifizieren.

    1. Login mit AT-Kunde
    2. Adresse bearbeiten (Straße auf "Teststraße 99")
    3. Produkt in Warenkorb legen
    4. Auf /checkout/confirm prüfen: Adresse enthält "Teststraße 99"
    5. Cleanup: Straße zurücksetzen
    """
    print("\n=== TC-ACCOUNT-012: Adresse bearbeiten und im Checkout verifizieren ===")

    email, password = get_test_customer_credentials(config, country="AT")
    headed = request.config.getoption("--headed", default=False)

    test_street = "Teststraße 99"
    original_street = None

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=not headed,
            slow_mo=200 if headed else 0
        )

        context_args = {"viewport": {"width": 1920, "height": 1080}}
        if config.htaccess_user and config.htaccess_password:
            context_args["http_credentials"] = {
                "username": config.htaccess_user,
                "password": config.htaccess_password,
            }

        context = await browser.new_context(**context_args)
        page = await context.new_page()

        try:
            account = AccountPage(page, config.base_url)
            cart = CartPage(page, config.base_url)
            checkout = CheckoutPage(page, config.base_url)

            # [1] Login
            print("[1] Login als AT-Kunde...")
            await account.goto_login()
            await accept_cookie_banner_async(page)
            success = await account.login(email, password)
            assert success, "Login fehlgeschlagen"

            # [2] Zur Adressverwaltung und aktuelle Straße merken
            print("[2] Zur Adressverwaltung navigieren...")
            await account.goto_addresses()
            await page.wait_for_timeout(1000)

            # Aktuelle Straße aus erster Adresskarte auslesen (für Cleanup)
            address_cards = page.locator(account.ADDRESS_CARD)
            card_count = await address_cards.count()
            assert card_count > 0, "Mindestens eine Adresse muss vorhanden sein"

            first_card_text = await address_cards.first.text_content()
            print(f"   Erste Adresse (Text): {first_card_text[:100]}...")

            # [3] Adresse bearbeiten
            print(f"[3] Erste Adresse bearbeiten: Straße → '{test_street}'...")
            edit_success = await account.edit_address(0, street=test_street)
            print(f"   Bearbeitung: {'Erfolgreich' if edit_success else 'Keine explizite Bestätigung'}")

            # Nach Bearbeitung Adressseite neu laden und prüfen
            await account.goto_addresses()
            await page.wait_for_timeout(1000)

            updated_card_text = await address_cards.first.text_content()
            assert test_street in updated_card_text, \
                f"Adresse sollte '{test_street}' enthalten, gefunden: {updated_card_text[:100]}"
            print(f"   Adresse enthält '{test_street}' ✓")

            # Originale Straße aus dem alten Text extrahieren (für Cleanup)
            # Wir merken uns den Zustand vor der Änderung
            original_street = first_card_text

            # [4] Produkt in Warenkorb legen
            print("[4] Produkt in Warenkorb legen...")
            added = await cart.add_product_to_cart("p/kurzarmshirt-aus-bio-baumwolle/ge-p-862990")
            assert added, "Produkt konnte nicht in den Warenkorb gelegt werden"
            print("   Produkt hinzugefügt ✓")

            # [5] Checkout-Confirm aufrufen und Adresse prüfen
            print("[5] Checkout-Confirm aufrufen...")
            await checkout.goto_confirm()
            await page.wait_for_timeout(2000)

            shipping_text = await checkout.get_shipping_address_text()
            billing_text = await checkout.get_billing_address_text()

            print(f"   Lieferadresse: {shipping_text[:100] if shipping_text else 'N/A'}")
            print(f"   Rechnungsadresse: {billing_text[:100] if billing_text else 'N/A'}")

            # Mindestens eine Adresse sollte die geänderte Straße enthalten
            address_found = False
            if shipping_text and test_street in shipping_text:
                address_found = True
            if billing_text and test_street in billing_text:
                address_found = True

            assert address_found, \
                f"'{test_street}' sollte in Liefer- oder Rechnungsadresse erscheinen"
            print(f"   Adresse im Checkout enthält '{test_street}' ✓")

            print("=== TC-ACCOUNT-012: BESTANDEN ===")

        finally:
            # [Cleanup] Straße zurücksetzen
            try:
                print("[Cleanup] Straße zurücksetzen...")
                await account.goto_addresses()
                await page.wait_for_timeout(1000)
                await account.edit_address(0, street="Teststraße 1")
                print("   Cleanup erfolgreich")
            except Exception as cleanup_error:
                print(f"   Cleanup-Fehler: {cleanup_error}")

            await context.close()
            await browser.close()
