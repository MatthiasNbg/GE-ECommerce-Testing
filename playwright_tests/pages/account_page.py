"""
Account Page Object - Login, Registrierung und Profil-Verwaltung.

Für Shopware 6 basierte E-Commerce-Seiten (Grüne Erde).
"""
import time
from dataclasses import dataclass
from typing import Optional

from playwright.async_api import Page

from .base_page import BasePage


@dataclass
class RegistrationData:
    """Daten für die Kundenregistrierung."""
    salutation: str = "mr"  # mr, mrs, none
    first_name: str = "Test"
    last_name: str = "Kunde"
    email: str = ""
    password: str = ""
    street: str = "Teststraße 1"
    zip_code: str = "4020"
    city: str = "Linz"
    country: str = "AT"
    account_type: str = "private"  # private, business
    company: Optional[str] = None
    phone: Optional[str] = None


class AccountPage(BasePage):
    """
    Page Object für Account-Verwaltung im Shopware 6 Shop.

    Unterstützt:
    - Login/Logout
    - Registrierung
    - Profil anzeigen/bearbeiten
    - Adressverwaltung
    """

    # =========================================================================
    # URLs / Pfade
    # =========================================================================

    LOGIN_PATH = "/account/login"
    REGISTER_PATH = "/account/login"  # Registrierung ist auf Login-Seite als Collapse
    PROFILE_PATH = "/account"
    ADDRESS_PATH = "/account/address"
    ORDERS_PATH = "/account/order"

    # Button um Registrierungsformular aufzuklappen
    REGISTER_COLLAPSE_BUTTON = "button[data-bs-target='.register-collapse']:has-text('Jetzt registrieren')"

    # =========================================================================
    # LOGIN-SEITE Selektoren
    # =========================================================================

    LOGIN_EMAIL = "#loginMail"
    LOGIN_PASSWORD = "#loginPassword"
    LOGIN_SUBMIT = "button:has-text('Anmelden')"
    LOGIN_SUBMIT_ALT = "button[type='submit']:has-text('Anmelden')"
    LOGIN_ERROR = ".alert-danger"
    FORGOT_PASSWORD_LINK = "a:has-text('Passwort vergessen')"

    # =========================================================================
    # REGISTRIERUNGS-SEITE Selektoren
    # =========================================================================

    # Persönliche Daten
    REGISTER_SALUTATION = "#personalSalutation"
    REGISTER_FIRST_NAME = "#personalFirstName"
    REGISTER_LAST_NAME = "#personalLastName"
    REGISTER_EMAIL = "#personalMail"
    REGISTER_PASSWORD = "#personalPassword"
    REGISTER_PASSWORD_CONFIRM = "#personalPasswordConfirmation"

    # Alternative Selektoren (Shopware-Varianten)
    REGISTER_FIRST_NAME_ALT = "#billingAddress-personalFirstName"
    REGISTER_LAST_NAME_ALT = "#billingAddress-personalLastName"

    # Adresse
    REGISTER_STREET = "#billingAddressAddressStreet"
    REGISTER_STREET_ALT = "#billingAddress-AddressStreet"
    REGISTER_ZIP = "#billingAddressAddressZipcode"
    REGISTER_CITY = "#billingAddressAddressCity"
    REGISTER_COUNTRY = "#billingAddressAddressCountry"

    # Checkboxen
    REGISTER_PRIVACY = "#acceptedDataProtection"
    REGISTER_NEWSLETTER = "#acceptedNewsletter"

    # Submit
    REGISTER_SUBMIT = "button:has-text('Registrieren')"
    REGISTER_SUBMIT_ALT = "button[type='submit']:has-text('Konto erstellen')"

    # =========================================================================
    # PROFIL-SEITE Selektoren
    # =========================================================================

    PROFILE_OVERVIEW = ".account-overview"
    PROFILE_WELCOME = ".account-welcome"
    PROFILE_GREETING = ".account-welcome-headline, h1:has-text('Willkommen')"
    ACCOUNT_CONTENT = ".account-content"

    # Profil-Navigation
    NAV_OVERVIEW = "a:has-text('Übersicht')"
    NAV_PROFILE = "a:has-text('Persönliche Daten')"
    NAV_ADDRESSES = "a:has-text('Adressen')"
    NAV_ORDERS = "a:has-text('Bestellungen')"
    NAV_PAYMENT = "a:has-text('Zahlungsarten')"

    # Logout
    LOGOUT_BUTTON = "a:has-text('Abmelden')"
    LOGOUT_LINK = ".account-aside a:has-text('Abmelden')"

    # =========================================================================
    # PROFIL BEARBEITEN Selektoren
    # =========================================================================

    PROFILE_EDIT_SALUTATION = "#personalSalutation"
    PROFILE_EDIT_FIRST_NAME = "#personalFirstName"
    PROFILE_EDIT_LAST_NAME = "#personalLastName"
    PROFILE_SAVE_BUTTON = "button:has-text('Speichern')"
    PROFILE_SUCCESS_MESSAGE = ".alert-success"

    # =========================================================================
    # ADRESS-VERWALTUNG Selektoren
    # =========================================================================

    ADDRESS_LIST = ".address-list"
    ADDRESS_CARD = ".address-card, .card.address"
    ADD_ADDRESS_BUTTON = "a:has-text('Adresse hinzufügen'), button:has-text('Adresse hinzufügen')"
    EDIT_ADDRESS_BUTTON = "a:has-text('Bearbeiten'), button:has-text('Bearbeiten')"
    DELETE_ADDRESS_BUTTON = "button:has-text('Löschen'), a:has-text('Löschen')"
    CONFIRM_DELETE_BUTTON = "button:has-text('Löschen'), .btn-danger:has-text('Löschen')"

    # Adress-Formular (Modal oder Seite)
    ADDRESS_FORM_SALUTATION = "#addresspersonalSalutation"
    ADDRESS_FORM_FIRST_NAME = "#addresspersonalFirstName"
    ADDRESS_FORM_LAST_NAME = "#addresspersonalLastName"
    ADDRESS_FORM_STREET = "#addressAddressStreet"
    ADDRESS_FORM_ZIP = "#addressAddressZipcode"
    ADDRESS_FORM_CITY = "#addressAddressCity"
    ADDRESS_FORM_COUNTRY = "#addressAddressCountry"
    ADDRESS_FORM_SAVE = "button:has-text('Adresse speichern'), button[type='submit']"

    # =========================================================================
    # Fehler-Selektoren
    # =========================================================================

    FORM_ERROR = ".invalid-feedback"
    ALERT_DANGER = ".alert-danger"
    FIELD_ERROR = ".is-invalid"

    # =========================================================================
    # Mappings
    # =========================================================================

    SALUTATION_MAP = {
        "mr": "Herr",
        "mrs": "Frau",
        "none": "Keine Angabe",
        "": "Keine Angabe",
    }

    COUNTRY_MAP = {
        "AT": "Österreich",
        "DE": "Deutschland",
        "CH": "Schweiz",
    }

    # =========================================================================
    # Konstruktor
    # =========================================================================

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

    # =========================================================================
    # Navigation
    # =========================================================================

    async def goto_login(self) -> None:
        """Navigiert zur Login-Seite."""
        await self.navigate(self.LOGIN_PATH)
        await self.accept_cookies_if_visible()

    async def goto_register(self) -> None:
        """Navigiert zur Registrierungs-Seite und klappt das Formular auf."""
        await self.navigate(self.REGISTER_PATH)
        await self.accept_cookies_if_visible()

        # Registrierungsformular aufklappen (ist als Collapse auf Login-Seite)
        register_btn = self.page.locator(self.REGISTER_COLLAPSE_BUTTON)
        if await register_btn.count() > 0 and await register_btn.is_visible():
            await register_btn.click()
            await self.page.wait_for_timeout(500)  # Warten auf Animation

    async def goto_profile(self) -> None:
        """Navigiert zur Profil-Übersicht."""
        await self.navigate(self.PROFILE_PATH)

    async def goto_addresses(self) -> None:
        """Navigiert zur Adressverwaltung."""
        await self.navigate(self.ADDRESS_PATH)

    async def goto_orders(self) -> None:
        """Navigiert zur Bestellübersicht."""
        await self.navigate(self.ORDERS_PATH)

    # =========================================================================
    # Login
    # =========================================================================

    async def login(self, email: str, password: str) -> bool:
        """
        Meldet einen Kunden an.

        Args:
            email: E-Mail-Adresse
            password: Passwort

        Returns:
            True wenn Login erfolgreich, False bei Fehler
        """
        await self.fill(self.LOGIN_EMAIL, email)
        await self.fill(self.LOGIN_PASSWORD, password)

        # Submit
        submit_btn = self.page.locator(self.LOGIN_SUBMIT)
        if await submit_btn.count() > 0:
            await submit_btn.first.click()
        else:
            await self.page.locator(self.LOGIN_SUBMIT_ALT).click()

        await self.page.wait_for_load_state("domcontentloaded")
        await self.page.wait_for_timeout(1000)

        # Prüfen ob erfolgreich (nicht mehr auf Login-Seite)
        return not await self.is_on_login_page()

    async def is_on_login_page(self) -> bool:
        """Prüft ob wir auf der Login-Seite sind."""
        return "account/login" in self.page.url

    async def get_login_error(self) -> Optional[str]:
        """Gibt die Login-Fehlermeldung zurück, falls vorhanden."""
        error = self.page.locator(self.LOGIN_ERROR)
        if await error.count() > 0 and await error.is_visible(timeout=2000):
            return await error.text_content()
        return None

    # =========================================================================
    # Logout
    # =========================================================================

    async def logout(self) -> None:
        """Meldet den Kunden ab."""
        # Erst zum Profil navigieren
        await self.goto_profile()
        await self.page.wait_for_timeout(500)

        # Logout-Button klicken
        logout_btn = self.page.locator(self.LOGOUT_BUTTON)
        if await logout_btn.count() > 0 and await logout_btn.first.is_visible():
            await logout_btn.first.click()
            await self.page.wait_for_load_state("domcontentloaded")
            return

        # Fallback
        logout_link = self.page.locator(self.LOGOUT_LINK)
        if await logout_link.count() > 0:
            await logout_link.first.click()
            await self.page.wait_for_load_state("domcontentloaded")

    # =========================================================================
    # Registrierung
    # =========================================================================

    async def register(self, data: RegistrationData) -> bool:
        """
        Registriert einen neuen Kunden.

        Args:
            data: Registrierungsdaten

        Returns:
            True wenn Registrierung erfolgreich
        """
        # Anrede
        salutation_label = self.SALUTATION_MAP.get(data.salutation, data.salutation)
        salutation_select = self.page.locator(self.REGISTER_SALUTATION)
        if await salutation_select.count() > 0:
            await self.select_option_by_label(self.REGISTER_SALUTATION, salutation_label)

        # Name - primäre Selektoren
        first_name_input = self.page.locator(self.REGISTER_FIRST_NAME)
        if await first_name_input.count() > 0:
            await self.fill(self.REGISTER_FIRST_NAME, data.first_name)
            await self.fill(self.REGISTER_LAST_NAME, data.last_name)
        else:
            # Fallback: Alternative Selektoren
            await self.fill(self.REGISTER_FIRST_NAME_ALT, data.first_name)
            await self.fill(self.REGISTER_LAST_NAME_ALT, data.last_name)

        # E-Mail
        await self.fill(self.REGISTER_EMAIL, data.email)

        # Passwort
        await self.fill(self.REGISTER_PASSWORD, data.password)
        password_confirm = self.page.locator(self.REGISTER_PASSWORD_CONFIRM)
        if await password_confirm.count() > 0:
            await self.fill(self.REGISTER_PASSWORD_CONFIRM, data.password)

        # Adresse
        street_input = self.page.locator(self.REGISTER_STREET)
        if await street_input.count() > 0:
            await self.fill(self.REGISTER_STREET, data.street)
        else:
            await self.fill(self.REGISTER_STREET_ALT, data.street)

        await self.fill(self.REGISTER_ZIP, data.zip_code)
        await self.fill(self.REGISTER_CITY, data.city)

        # Land
        country_label = self.COUNTRY_MAP.get(data.country, data.country)
        country_select = self.page.locator(self.REGISTER_COUNTRY)
        if await country_select.count() > 0:
            await self.select_option_by_label(self.REGISTER_COUNTRY, country_label)

        # Datenschutz akzeptieren
        privacy = self.page.locator(self.REGISTER_PRIVACY)
        if await privacy.count() > 0 and await privacy.is_visible():
            if not await privacy.is_checked():
                await privacy.check()

        # Submit
        submit_btn = self.page.locator(self.REGISTER_SUBMIT)
        if await submit_btn.count() > 0 and await submit_btn.first.is_visible():
            await submit_btn.first.click()
        else:
            submit_alt = self.page.locator(self.REGISTER_SUBMIT_ALT)
            if await submit_alt.count() > 0:
                await submit_alt.first.click()

        await self.page.wait_for_load_state("domcontentloaded")
        await self.page.wait_for_timeout(1000)

        # Erfolgreich wenn auf Profil-Seite
        return await self.is_logged_in()

    async def get_registration_error(self) -> Optional[str]:
        """Gibt Registrierungs-Fehlermeldungen zurück."""
        # Prüfen auf Alert
        alert = self.page.locator(self.ALERT_DANGER)
        if await alert.count() > 0 and await alert.first.is_visible(timeout=2000):
            return await alert.first.text_content()

        # Prüfen auf Formular-Fehler
        errors = await self.get_form_errors()
        if errors:
            return "; ".join(errors)

        return None

    async def get_form_errors(self) -> list[str]:
        """Gibt alle Formular-Fehlermeldungen zurück."""
        errors = []
        error_elements = self.page.locator(self.FORM_ERROR)
        count = await error_elements.count()
        for i in range(count):
            text = await error_elements.nth(i).text_content()
            if text and text.strip():
                errors.append(text.strip())
        return errors

    async def has_form_errors(self) -> bool:
        """Prüft ob Formular-Fehler vorhanden sind."""
        return await self.page.locator(self.FORM_ERROR).count() > 0

    # =========================================================================
    # Login-Status prüfen
    # =========================================================================

    async def is_logged_in(self) -> bool:
        """
        Prüft ob der Benutzer eingeloggt ist.

        Returns:
            True wenn eingeloggt
        """
        # Methode 1: Logout-Button sichtbar
        logout = self.page.locator(self.LOGOUT_BUTTON)
        if await logout.count() > 0:
            try:
                if await logout.first.is_visible(timeout=1000):
                    return True
            except Exception:
                pass

        # Methode 2: Account-Übersicht sichtbar
        overview = self.page.locator(self.PROFILE_OVERVIEW)
        if await overview.count() > 0:
            try:
                if await overview.first.is_visible(timeout=1000):
                    return True
            except Exception:
                pass

        # Methode 3: Account-Content sichtbar
        content = self.page.locator(self.ACCOUNT_CONTENT)
        if await content.count() > 0:
            try:
                if await content.first.is_visible(timeout=1000):
                    return True
            except Exception:
                pass

        # Methode 4: URL prüfen (auf Account-Seite und kein Login)
        url = self.page.url
        if "/account" in url and "/login" not in url:
            return True

        return False

    async def get_welcome_message(self) -> Optional[str]:
        """Gibt die Willkommensnachricht zurück, falls vorhanden."""
        greeting = self.page.locator(self.PROFILE_GREETING)
        if await greeting.count() > 0 and await greeting.first.is_visible():
            return await greeting.first.text_content()
        return None

    # =========================================================================
    # Profil bearbeiten
    # =========================================================================

    async def navigate_to_profile_edit(self) -> None:
        """Navigiert zur Profil-Bearbeitung."""
        nav = self.page.locator(self.NAV_PROFILE)
        if await nav.count() > 0:
            await nav.first.click()
            await self.page.wait_for_load_state("domcontentloaded")

    async def update_profile(self, first_name: str = None, last_name: str = None) -> bool:
        """
        Aktualisiert das Profil.

        Args:
            first_name: Neuer Vorname (optional)
            last_name: Neuer Nachname (optional)

        Returns:
            True wenn erfolgreich
        """
        if first_name:
            await self.fill(self.PROFILE_EDIT_FIRST_NAME, first_name)
        if last_name:
            await self.fill(self.PROFILE_EDIT_LAST_NAME, last_name)

        # Speichern
        save_btn = self.page.locator(self.PROFILE_SAVE_BUTTON)
        if await save_btn.count() > 0:
            await save_btn.first.click()
            await self.page.wait_for_load_state("domcontentloaded")
            await self.page.wait_for_timeout(1000)

        # Erfolgsmeldung prüfen
        success = self.page.locator(self.PROFILE_SUCCESS_MESSAGE)
        return await success.count() > 0 and await success.first.is_visible(timeout=3000)

    # =========================================================================
    # Adressverwaltung
    # =========================================================================

    async def get_address_count(self) -> int:
        """Gibt die Anzahl der gespeicherten Adressen zurück."""
        addresses = self.page.locator(self.ADDRESS_CARD)
        return await addresses.count()

    async def add_address(
        self,
        first_name: str,
        last_name: str,
        street: str,
        zip_code: str,
        city: str,
        country: str = "AT"
    ) -> bool:
        """
        Fügt eine neue Adresse hinzu.

        Returns:
            True wenn erfolgreich
        """
        # Adresse hinzufügen Button
        add_btn = self.page.locator(self.ADD_ADDRESS_BUTTON)
        if await add_btn.count() > 0:
            await add_btn.first.click()
            await self.page.wait_for_timeout(1000)

        # Formular ausfüllen
        await self.fill(self.ADDRESS_FORM_FIRST_NAME, first_name)
        await self.fill(self.ADDRESS_FORM_LAST_NAME, last_name)
        await self.fill(self.ADDRESS_FORM_STREET, street)
        await self.fill(self.ADDRESS_FORM_ZIP, zip_code)
        await self.fill(self.ADDRESS_FORM_CITY, city)

        country_label = self.COUNTRY_MAP.get(country, country)
        country_select = self.page.locator(self.ADDRESS_FORM_COUNTRY)
        if await country_select.count() > 0:
            await self.select_option_by_label(self.ADDRESS_FORM_COUNTRY, country_label)

        # Speichern
        save_btn = self.page.locator(self.ADDRESS_FORM_SAVE)
        if await save_btn.count() > 0:
            await save_btn.first.click()
            await self.page.wait_for_load_state("domcontentloaded")
            await self.page.wait_for_timeout(1000)

        # Erfolgsmeldung
        success = self.page.locator(self.PROFILE_SUCCESS_MESSAGE)
        return await success.count() > 0

    async def delete_address(self, index: int = 0) -> bool:
        """
        Löscht eine Adresse.

        Args:
            index: Index der Adresse (0-basiert)

        Returns:
            True wenn erfolgreich
        """
        addresses = self.page.locator(self.ADDRESS_CARD)
        count = await addresses.count()

        if index >= count:
            return False

        address_card = addresses.nth(index)
        delete_btn = address_card.locator(self.DELETE_ADDRESS_BUTTON)

        if await delete_btn.count() > 0:
            await delete_btn.first.click()
            await self.page.wait_for_timeout(500)

            # Bestätigungsdialog
            confirm_btn = self.page.locator(self.CONFIRM_DELETE_BUTTON)
            if await confirm_btn.count() > 0 and await confirm_btn.first.is_visible():
                await confirm_btn.first.click()
                await self.page.wait_for_load_state("domcontentloaded")

            return True

        return False

    # =========================================================================
    # Hilfsmethoden
    # =========================================================================

    @staticmethod
    def generate_unique_email(prefix: str = "test") -> str:
        """
        Generiert eine einzigartige E-Mail-Adresse mit Timestamp.

        Args:
            prefix: Präfix für die E-Mail

        Returns:
            Einzigartige E-Mail-Adresse
        """
        timestamp = int(time.time() * 1000)
        return f"{prefix}-{timestamp}@test-example.com"

    @staticmethod
    def generate_registration_data(
        email: str = None,
        password: str = "Test1234!"
    ) -> RegistrationData:
        """
        Generiert vollständige Registrierungsdaten.

        Args:
            email: E-Mail (oder None für automatische Generierung)
            password: Passwort

        Returns:
            RegistrationData mit allen Feldern ausgefüllt
        """
        if email is None:
            email = AccountPage.generate_unique_email()

        return RegistrationData(
            salutation="mr",
            first_name="Test",
            last_name="Kunde",
            email=email,
            password=password,
            street="Teststraße 123",
            zip_code="4020",
            city="Linz",
            country="AT"
        )
