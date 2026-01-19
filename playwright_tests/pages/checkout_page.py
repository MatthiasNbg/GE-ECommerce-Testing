"""
Checkout Page Object - Interaktionen mit dem Shopware Checkout.

Gescannte Selektoren von: grueneerde.scalecommerce.cloud
Letzte Aktualisierung: 2026-01-17
"""
from dataclasses import dataclass, field
from typing import Optional

from playwright.async_api import Page, expect

from .base_page import BasePage
from ..config import get_config


@dataclass
class Address:
    """Adressdaten für den Checkout."""
    salutation: str = "mr"  # mr, mrs, none
    first_name: str = "Test"
    last_name: str = "Kunde"
    street: str = "Teststraße 1"
    zip_code: str = "4020"
    city: str = "Linz"
    country: str = "AT"  # ISO-Code
    email: str = "test@example.com"
    phone: Optional[str] = None
    # Geschäftskunde
    account_type: str = "private"  # private, business
    company: Optional[str] = None
    department: Optional[str] = None
    vat_id: Optional[str] = None


@dataclass
class ShippingAddress:
    """Separate Lieferadresse (falls abweichend)."""
    salutation: str = "mr"
    first_name: str = ""
    last_name: str = ""
    street: str = ""
    zip_code: str = ""
    city: str = ""
    country: str = "AT"
    company: Optional[str] = None
    department: Optional[str] = None


@dataclass
class CheckoutResult:
    """Ergebnis einer Checkout-Ausführung."""
    success: bool
    order_id: Optional[str] = None
    order_number: Optional[str] = None
    error_message: Optional[str] = None
    duration_seconds: float = 0.0


class CheckoutPage(BasePage):
    """
    Page Object für den Shopware 6 Checkout (Grüne Erde).

    Unterstützt:
    - Gast-Checkout
    - Registrierung
    - Login für bestehende Kunden
    - Verschiedene Zahlungs- und Versandarten
    """

    # =========================================================================
    # REGISTER-SEITE Selektoren (/checkout/register)
    # =========================================================================

    # --- Login (bestehender Kunde) ---
    LOGIN_EMAIL_INPUT = "#loginMail"
    LOGIN_PASSWORD_INPUT = "#loginPassword"
    LOGIN_SUBMIT_BUTTON = "button:has-text('Anmelden')"
    FORGOT_PASSWORD_LINK = "a:has-text('Passwort vergessen')"

    # --- Gast vs. Registrierung ---
    GUEST_CHECKOUT_BUTTON = "button:has-text('Als Gast bestellen')"
    GUEST_CHECKOUT_BUTTON_ALT = "button:has-text('Als Gast')"
    REGISTER_BUTTON = "button:has-text('Kundenkonto anlegen')"
    GUEST_RADIO = "#personalGuest"
    REGISTER_RADIO = "#personalRegister"

    # --- Kontotyp ---
    ACCOUNT_TYPE_SELECT = "#-accountType"  # Privat, Gewerblich

    # --- Persönliche Daten ---
    SALUTATION_SELECT = "#personalSalutation"  # Keine Angabe, Frau, Herr
    FIRST_NAME_INPUT = "#billingAddress-personalFirstName"
    LAST_NAME_INPUT = "#billingAddress-personalLastName"
    EMAIL_INPUT = "#personalMail"

    # --- Geburtsdatum (optional) ---
    BIRTHDAY_DAY_SELECT = "#personalBirthday"
    BIRTHDAY_MONTH_SELECT = "#personalBirthdayMonth"
    BIRTHDAY_YEAR_SELECT = "#personalBirthdayYear"

    # --- Passwort (nur bei Registrierung) ---
    PASSWORD_INPUT = "#personalPassword"
    PASSWORD_CONFIRM_INPUT = "#personalPasswordConfirmation"

    # --- Geschäftskunde (nur bei accountType=Gewerblich) ---
    COMPANY_INPUT = "#billingAddresscompany"
    DEPARTMENT_INPUT = "#billingAddressdepartment"
    VAT_ID_INPUT = "#vatIds"

    # --- Rechnungsadresse ---
    STREET_INPUT = "#billingAddress-AddressStreet"
    ZIP_CODE_INPUT = "#billingAddressAddressZipcode"
    CITY_INPUT = "#billingAddressAddressCity"
    COUNTRY_SELECT = "#billingAddressAddressCountry"
    COUNTRY_STATE_SELECT = "#billingAddressAddressCountryState"
    PHONE_INPUT = "#billingAddressAddressPhoneNumber"

    # --- Abweichende Lieferadresse ---
    DIFFERENT_SHIPPING_CHECKBOX = "#differentShippingAddress"

    # Lieferadresse-Felder (sichtbar wenn DIFFERENT_SHIPPING_CHECKBOX aktiviert)
    SHIPPING_ACCOUNT_TYPE_SELECT = "#shippingAddress-accountType"
    SHIPPING_SALUTATION_SELECT = "#shippingAddresspersonalSalutation"
    SHIPPING_FIRST_NAME_INPUT = "#shippingAddress-personalFirstName"
    SHIPPING_LAST_NAME_INPUT = "#shippingAddress-personalLastName"
    SHIPPING_COMPANY_INPUT = "#shippingAddresscompany"
    SHIPPING_DEPARTMENT_INPUT = "#shippingAddressdepartment"
    SHIPPING_STREET_INPUT = "#shippingAddress-AddressStreet"
    SHIPPING_ZIP_CODE_INPUT = "#shippingAddressAddressZipcode"
    SHIPPING_CITY_INPUT = "#shippingAddressAddressCity"
    SHIPPING_COUNTRY_SELECT = "#shippingAddressAddressCountry"
    SHIPPING_COUNTRY_STATE_SELECT = "#shippingAddressAddressCountryState"
    SHIPPING_PHONE_INPUT = "#shippingAddressAddressPhoneNumber"

    # --- Checkboxen (Register-Seite) ---
    PRIVACY_CHECKBOX = "#acceptedDataProtection"
    NEWSLETTER_CHECKBOX = "#acceptedNewsletter"
    FRIENDS_CIRCLE_CHECKBOX = "#acceptedFriendscircle"

    # --- Navigation ---
    CONTINUE_BUTTON = "button:has-text('Weiter')"
    BACK_TO_SHOP_BUTTON = "a:has-text('Zurück zum Shop')"

    # =========================================================================
    # CONFIRM-SEITE Selektoren (/checkout/confirm)
    # =========================================================================

    # --- Adresse ändern ---
    CHANGE_ADDRESS_BUTTON = "button:has-text('Lieferadresse ändern')"

    # --- Zahlungsarten (dynamische IDs - Label-basierte Selektion empfohlen) ---
    PAYMENT_METHOD_RADIO = "input[name='paymentMethodId']"
    # Aktuelle Payment-IDs auf grueneerde.scalecommerce.cloud:
    PAYMENT_CREDIT_CARD = "#paymentMethod019685c086307133b77e4197e87e2996"
    PAYMENT_PREPAYMENT = "#paymentMethod01954d38abc77123ad8eef6b26c5c0cc"  # Vorkasse
    PAYMENT_INVOICE = "#paymentMethod01954d38abc47169b446b1a3660bfc51"  # Rechnung

    # Label-basierte Selektoren (stabiler als IDs)
    PAYMENT_CREDIT_CARD_LABEL = ".payment-method:has-text('Kreditkarte')"
    PAYMENT_PREPAYMENT_LABEL = ".payment-method:has-text('Vorkasse')"
    PAYMENT_INVOICE_LABEL = ".payment-method:has-text('Rechnung')"

    # --- Versandarten (dynamische IDs) ---
    SHIPPING_METHOD_RADIO = "input[name='shippingMethodId']"
    # Aktuelle Shipping-IDs:
    SHIPPING_POST_AT = "#shippingMethod019730a691677bfca7dfd9e2e804c15e"  # Postversand Österreich
    SHIPPING_STORE = "#shippingMethoda37c78a6a0e649f7a5995c73ff002599"  # Lieferung an Store

    # Label-basierte Selektoren
    SHIPPING_POST_LABEL = ".shipping-method:has-text('Postversand')"
    SHIPPING_STORE_LABEL = ".shipping-method:has-text('Store')"

    # --- Warenkorb auf Confirm-Seite ---
    CART_ITEM = ".line-item"
    CART_ITEM_QUANTITY = "input[name='quantity']"
    CART_ITEM_DELETE = ".line-item-remove"

    # --- Zusammenfassung ---
    SUBTOTAL = ".checkout-aside-summary-value:first-of-type"
    SHIPPING_COST = ".checkout-aside-summary-list dt:has-text('Versandkosten') + dd"
    TOTAL = ".checkout-aside-summary-total"

    # --- AGB & Checkboxen (Confirm-Seite) ---
    TOS_CHECKBOX = "#tos"  # AGB akzeptieren
    CONFIRM_NEWSLETTER_CHECKBOX = "#acceptedNewsletter"
    CONFIRM_FRIENDS_CIRCLE_CHECKBOX = "#acceptedFriendscircle"

    # --- Bestellung abschließen ---
    SUBMIT_ORDER_BUTTON = "button:has-text('Zahlungspflichtig bestellen')"
    SUBMIT_ORDER_BUTTON_ALT = "#confirmFormSubmit"

    # =========================================================================
    # FINISH-SEITE Selektoren (/checkout/finish)
    # =========================================================================

    ORDER_CONFIRMATION = ".finish-header, .checkout-finish"
    ORDER_NUMBER = ".finish-ordernumber, [data-order-number]"
    ORDER_SUCCESS_MESSAGE = ".finish-message, .alert-success"

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
        "LI": "Liechtenstein",
    }

    ACCOUNT_TYPE_MAP = {
        "private": "Privat",
        "business": "Gewerblich",
    }

    # =========================================================================
    # Konstruktor
    # =========================================================================

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.checkout_path = "/checkout/register"
        self.checkout_confirm_path = "/checkout/confirm"
        self.checkout_finish_path = "/checkout/finish"

    # =========================================================================
    # Navigation
    # =========================================================================

    async def goto_checkout(self) -> None:
        """Navigiert direkt zum Checkout (Register-Seite)."""
        await self.navigate(self.checkout_path)
        await self.accept_cookies_if_visible()

    async def goto_confirm(self) -> None:
        """Navigiert zur Bestätigungsseite."""
        await self.navigate(self.checkout_confirm_path)

    # =========================================================================
    # Login (bestehender Kunde)
    # =========================================================================

    async def login(self, email: str, password: str) -> None:
        """
        Meldet einen bestehenden Kunden an.

        Args:
            email: E-Mail-Adresse
            password: Passwort
        """
        await self.fill(self.LOGIN_EMAIL_INPUT, email)
        await self.fill(self.LOGIN_PASSWORD_INPUT, password)
        await self.page.click(self.LOGIN_SUBMIT_BUTTON)
        await self.page.wait_for_load_state("domcontentloaded")

    # =========================================================================
    # Gast-Checkout
    # =========================================================================

    async def start_guest_checkout(self) -> None:
        """Startet den Gast-Checkout."""
        # Primärer Selektor: "Als Gast bestellen" Button
        guest_button = self.page.locator(self.GUEST_CHECKOUT_BUTTON)
        if await guest_button.count() > 0 and await guest_button.first.is_visible():
            await guest_button.first.click()
            await self.page.wait_for_load_state("domcontentloaded")
            return

        # Fallback: Kürzerer Text
        guest_button_alt = self.page.locator(self.GUEST_CHECKOUT_BUTTON_ALT)
        if await guest_button_alt.count() > 0 and await guest_button_alt.first.is_visible():
            await guest_button_alt.first.click()
            await self.page.wait_for_load_state("domcontentloaded")
            return

        # Fallback: Radio-Button
        guest_radio = self.page.locator(self.GUEST_RADIO)
        if await guest_radio.count() > 0 and await guest_radio.is_visible():
            await guest_radio.check()

    async def start_registration(self) -> None:
        """Startet die Kunden-Registrierung."""
        register_button = self.page.locator(self.REGISTER_BUTTON)
        if await register_button.count() > 0 and await register_button.first.is_visible():
            await register_button.first.click()
            await self.page.wait_for_load_state("domcontentloaded")
            return

        # Fallback: Radio-Button
        register_radio = self.page.locator(self.REGISTER_RADIO)
        if await register_radio.count() > 0 and await register_radio.is_visible():
            await register_radio.check()

    # =========================================================================
    # Persönliche Daten
    # =========================================================================

    async def fill_personal_data(self, address: Address) -> None:
        """Füllt die persönlichen Daten aus."""
        # Kontotyp (falls Geschäftskunde)
        if address.account_type == "business":
            await self.select_option_by_label(self.ACCOUNT_TYPE_SELECT, "Gewerblich")
            # Warte auf Geschäftskunde-Felder
            await self.page.wait_for_timeout(500)

        # Anrede
        salutation_label = self.SALUTATION_MAP.get(address.salutation, address.salutation)
        await self.select_option_by_label(self.SALUTATION_SELECT, salutation_label)

        # Name
        await self.fill(self.FIRST_NAME_INPUT, address.first_name)
        await self.fill(self.LAST_NAME_INPUT, address.last_name)

        # Email
        await self.fill(self.EMAIL_INPUT, address.email)

        # Telefon (optional)
        if address.phone:
            await self.fill(self.PHONE_INPUT, address.phone)

        # Geschäftskunde-Felder
        if address.account_type == "business":
            if address.company:
                await self.fill(self.COMPANY_INPUT, address.company)
            if address.department:
                await self.fill(self.DEPARTMENT_INPUT, address.department)
            if address.vat_id:
                await self.fill(self.VAT_ID_INPUT, address.vat_id)

    async def fill_billing_address(self, address: Address) -> None:
        """Füllt die Rechnungsadresse aus."""
        await self.fill(self.STREET_INPUT, address.street)
        await self.fill(self.ZIP_CODE_INPUT, address.zip_code)
        await self.fill(self.CITY_INPUT, address.city)

        # Land
        country_label = self.COUNTRY_MAP.get(address.country, address.country)
        await self.select_option_by_label(self.COUNTRY_SELECT, country_label)

    async def fill_shipping_address(self, shipping: ShippingAddress) -> None:
        """
        Füllt eine abweichende Lieferadresse aus.

        Args:
            shipping: Lieferadressdaten
        """
        # Checkbox aktivieren
        checkbox = self.page.locator(self.DIFFERENT_SHIPPING_CHECKBOX)
        if not await checkbox.is_checked():
            await checkbox.check()
            await self.page.wait_for_timeout(500)  # Warte auf Felder

        # Anrede
        salutation_label = self.SALUTATION_MAP.get(shipping.salutation, shipping.salutation)
        await self.select_option_by_label(self.SHIPPING_SALUTATION_SELECT, salutation_label)

        # Name
        await self.fill(self.SHIPPING_FIRST_NAME_INPUT, shipping.first_name)
        await self.fill(self.SHIPPING_LAST_NAME_INPUT, shipping.last_name)

        # Adresse
        await self.fill(self.SHIPPING_STREET_INPUT, shipping.street)
        await self.fill(self.SHIPPING_ZIP_CODE_INPUT, shipping.zip_code)
        await self.fill(self.SHIPPING_CITY_INPUT, shipping.city)

        # Land
        country_label = self.COUNTRY_MAP.get(shipping.country, shipping.country)
        await self.select_option_by_label(self.SHIPPING_COUNTRY_SELECT, country_label)

        # Firma (optional)
        if shipping.company:
            await self.fill(self.SHIPPING_COMPANY_INPUT, shipping.company)

    async def fill_guest_address(self, address: Address) -> None:
        """Füllt alle Adressdaten für Gast-Checkout aus."""
        await self.fill_personal_data(address)
        await self.fill_billing_address(address)
    
    # =========================================================================
    # Zahlungsart
    # =========================================================================

    async def select_payment_method(self, method: str) -> None:
        """
        Wählt eine Zahlungsart aus.

        Args:
            method: Alias (invoice, credit_card, prepayment) oder deutscher Label

        Supported methods:
            - "invoice" / "Rechnung"
            - "credit_card" / "Kreditkarte"
            - "prepayment" / "Vorkasse"

        Raises:
            ValueError: Wenn Zahlungsart nicht gefunden
        """
        config = get_config()
        aliases = config.payment_method_aliases

        # Alias zu Label übersetzen
        label = aliases.get(method, method)

        # Strategie 1: Label-basierte Container suchen
        container_selectors = [
            "div:has(input[name='paymentMethodId'])",
            ".payment-method",
            ".payment-methods .payment-method-item",
            "label[for*='paymentMethod']",
        ]

        for selector in container_selectors:
            containers = self.page.locator(selector)
            if await containers.count() > 0:
                matching = containers.filter(has_text=label)
                if await matching.count() > 0:
                    # Radio-Button im Container klicken
                    radio = matching.first.locator("input[type='radio']")
                    if await radio.count() > 0:
                        await radio.first.click()
                        return
                    # Container klicken (aktiviert Radio)
                    await matching.first.click()
                    return

        # Strategie 2: Direkt alle Radio-Buttons prüfen
        radios = self.page.locator(self.PAYMENT_METHOD_RADIO)
        radio_count = await radios.count()

        for i in range(radio_count):
            radio = radios.nth(i)
            radio_id = await radio.get_attribute("id")

            if radio_id:
                # Label suchen
                label_elem = self.page.locator(f"label[for='{radio_id}']")
                if await label_elem.count() > 0:
                    label_text = await label_elem.text_content() or ""
                    if label.lower() in label_text.lower():
                        await radio.click()
                        return

            # Parent-Element prüfen
            parent = radio.locator("xpath=..")
            parent_text = await parent.text_content() or ""
            if label.lower() in parent_text.lower():
                await radio.click()
                return

        raise ValueError(
            f"Zahlungsart '{label}' nicht gefunden. "
            f"Input: '{method}', Aliases: {list(aliases.keys())}, "
            f"Gefundene Radios: {radio_count}"
        )

    async def get_selected_payment_method(self) -> Optional[str]:
        """Gibt die aktuell ausgewählte Zahlungsart zurück."""
        selected = self.page.locator(f"{self.PAYMENT_METHOD_RADIO}:checked")
        if await selected.count() > 0:
            return await selected.get_attribute("value")
        return None

    async def get_available_payment_methods(self) -> list[str]:
        """
        Gibt alle verfügbaren Zahlungsarten zurück.

        Returns:
            Liste der Zahlungsarten-Labels
        """
        methods = []
        radios = self.page.locator(self.PAYMENT_METHOD_RADIO)
        count = await radios.count()

        for i in range(count):
            radio = radios.nth(i)
            radio_id = await radio.get_attribute("id")
            if radio_id:
                label_elem = self.page.locator(f"label[for='{radio_id}']")
                if await label_elem.count() > 0:
                    text = await label_elem.text_content()
                    if text:
                        # Bereinigen (Whitespace entfernen)
                        methods.append(text.strip().split("\n")[0].strip())
        return methods

    # =========================================================================
    # Versandart
    # =========================================================================

    async def select_shipping_method(self, method: str) -> None:
        """
        Wählt eine Versandart aus.

        Args:
            method: "post" für Postversand, "store" für Store-Lieferung,
                   oder ein Teil des Labels
        """
        method_lower = method.lower()

        # Mapping
        if method_lower in ["post", "postversand"]:
            label_part = "Postversand"
        elif method_lower in ["store", "abholung"]:
            label_part = "Store"
        else:
            label_part = method

        # Radio-Buttons durchsuchen
        radios = self.page.locator(self.SHIPPING_METHOD_RADIO)
        count = await radios.count()

        for i in range(count):
            radio = radios.nth(i)
            radio_id = await radio.get_attribute("id")
            if radio_id:
                label_elem = self.page.locator(f"label[for='{radio_id}']")
                if await label_elem.count() > 0:
                    label_text = await label_elem.text_content() or ""
                    if label_part.lower() in label_text.lower():
                        await radio.click()
                        return

        raise ValueError(f"Versandart '{method}' nicht gefunden")

    async def get_available_shipping_methods(self) -> list[str]:
        """Gibt alle verfügbaren Versandarten zurück."""
        methods = []
        radios = self.page.locator(self.SHIPPING_METHOD_RADIO)
        count = await radios.count()

        for i in range(count):
            radio = radios.nth(i)
            radio_id = await radio.get_attribute("id")
            if radio_id:
                label_elem = self.page.locator(f"label[for='{radio_id}']")
                if await label_elem.count() > 0:
                    text = await label_elem.text_content()
                    if text:
                        methods.append(text.strip())
        return methods

    # =========================================================================
    # AGB & Bestellung abschließen
    # =========================================================================

    async def accept_terms(self) -> None:
        """Akzeptiert AGB auf der Confirm-Seite."""
        tos = self.page.locator(self.TOS_CHECKBOX)
        if await tos.count() > 0 and await tos.is_visible():
            if not await tos.is_checked():
                await tos.check()

    async def place_order(self) -> None:
        """Klickt auf den Bestellen-Button."""
        submit_btn = self.page.locator(self.SUBMIT_ORDER_BUTTON)
        if await submit_btn.count() > 0 and await submit_btn.first.is_visible():
            await submit_btn.first.click()
            return

        # Fallback
        submit_btn_alt = self.page.locator(self.SUBMIT_ORDER_BUTTON_ALT)
        if await submit_btn_alt.count() > 0:
            await submit_btn_alt.click()

    async def wait_for_confirmation(self, timeout: int = 30000) -> None:
        """Wartet auf die Bestellbestätigung."""
        await self.page.wait_for_url("**/checkout/finish**", timeout=timeout)
        # Warte auf Bestätigungs-Element
        confirmation = self.page.locator(self.ORDER_CONFIRMATION)
        await confirmation.wait_for(state="visible", timeout=timeout)
    
    # =========================================================================
    # Bestellinformationen
    # =========================================================================

    async def get_order_number(self) -> Optional[str]:
        """Extrahiert die Bestellnummer von der Bestätigungsseite."""
        import re
        order_element = self.page.locator(self.ORDER_NUMBER)
        if await order_element.count() > 0 and await order_element.is_visible():
            text = await order_element.text_content()
            if text:
                # Format: "Bestellnummer: 10001" oder nur "10001"
                match = re.search(r'(\d{5,})', text)
                if match:
                    return match.group(1)
        return None

    async def get_order_id_from_url(self) -> Optional[str]:
        """Extrahiert die Order-ID aus der URL."""
        import re
        url = self.page.url
        # Format: /checkout/finish?orderId=xxx
        match = re.search(r'orderId=([a-f0-9-]+)', url)
        if match:
            return match.group(1)
        return None

    # =========================================================================
    # Kompletter Checkout-Flow
    # =========================================================================

    async def accept_privacy_and_continue(self) -> None:
        """Akzeptiert Datenschutz und navigiert zur Confirm-Seite."""
        # Datenschutz-Checkbox akzeptieren
        privacy = self.page.locator(self.PRIVACY_CHECKBOX)
        if await privacy.count() > 0 and await privacy.is_visible():
            if not await privacy.is_checked():
                await privacy.check()

        # "Weiter"-Button klicken
        continue_btn = self.page.locator(self.CONTINUE_BUTTON)
        if await continue_btn.count() > 0 and await continue_btn.first.is_visible():
            await continue_btn.first.click()
            # Warten auf Navigation zur Confirm-Seite
            await self.page.wait_for_url("**/checkout/confirm**", timeout=30000)
            await self.page.wait_for_load_state("domcontentloaded")

    async def execute_guest_checkout(
        self,
        address: Address,
        payment_method: str = "invoice",
        shipping_method: Optional[str] = None
    ) -> CheckoutResult:
        """
        Führt einen kompletten Gast-Checkout durch.

        Shopware 6 zweistufiger Prozess:
        1. /checkout/register - Adresse eingeben, Datenschutz
        2. /checkout/confirm - Zahlungsart, Versandart, AGB, Bestellen

        Args:
            address: Adressdaten für die Bestellung
            payment_method: Zahlungsart (invoice, credit_card, prepayment)
            shipping_method: Versandart (post, store) - optional

        Returns:
            CheckoutResult mit Erfolg/Misserfolg und Details
        """
        import time
        start_time = time.time()

        try:
            # === SCHRITT 1: Register-Seite ===
            await self.start_guest_checkout()
            await self.fill_guest_address(address)
            await self.accept_privacy_and_continue()

            # === SCHRITT 2: Confirm-Seite ===
            # Versandart wählen (falls angegeben)
            if shipping_method:
                await self.select_shipping_method(shipping_method)

            # Zahlungsart wählen
            await self.select_payment_method(payment_method)

            # AGB akzeptieren
            await self.accept_terms()

            # Bestellung abschließen
            await self.place_order()

            # Auf Bestätigung warten
            await self.wait_for_confirmation()

            # Bestellinformationen sammeln
            order_number = await self.get_order_number()
            order_id = await self.get_order_id_from_url()

            return CheckoutResult(
                success=True,
                order_id=order_id,
                order_number=order_number,
                duration_seconds=time.time() - start_time
            )

        except Exception as e:
            error_msg = await self.get_error_message()
            return CheckoutResult(
                success=False,
                error_message=error_msg or str(e),
                duration_seconds=time.time() - start_time
            )

    async def execute_registered_checkout(
        self,
        email: str,
        password: str,
        payment_method: str = "invoice",
        shipping_method: Optional[str] = None
    ) -> CheckoutResult:
        """
        Führt einen Checkout für registrierte Kunden durch.

        Args:
            email: Kunden-Email
            password: Kunden-Passwort
            payment_method: Zahlungsart
            shipping_method: Versandart (optional)

        Returns:
            CheckoutResult mit Erfolg/Misserfolg und Details
        """
        import time
        start_time = time.time()

        try:
            # Login
            await self.login(email, password)

            # Falls nicht automatisch auf Confirm-Seite
            if "confirm" not in self.page.url:
                await self.goto_confirm()

            # Versandart
            if shipping_method:
                await self.select_shipping_method(shipping_method)

            # Zahlungsart
            await self.select_payment_method(payment_method)

            # AGB
            await self.accept_terms()

            # Bestellen
            await self.place_order()
            await self.wait_for_confirmation()

            order_number = await self.get_order_number()
            order_id = await self.get_order_id_from_url()

            return CheckoutResult(
                success=True,
                order_id=order_id,
                order_number=order_number,
                duration_seconds=time.time() - start_time
            )

        except Exception as e:
            error_msg = await self.get_error_message()
            return CheckoutResult(
                success=False,
                error_message=error_msg or str(e),
                duration_seconds=time.time() - start_time
            )

    # =========================================================================
    # Hilfsmethoden
    # =========================================================================

    async def is_on_register_page(self) -> bool:
        """Prüft ob wir auf der Register-Seite sind."""
        return "checkout/register" in self.page.url

    async def is_on_confirm_page(self) -> bool:
        """Prüft ob wir auf der Confirm-Seite sind."""
        return "checkout/confirm" in self.page.url

    async def is_on_finish_page(self) -> bool:
        """Prüft ob wir auf der Finish-Seite sind."""
        return "checkout/finish" in self.page.url

    async def get_cart_total(self) -> Optional[str]:
        """Gibt die Gesamtsumme des Warenkorbs zurück."""
        total = self.page.locator(self.TOTAL)
        if await total.count() > 0:
            return await total.text_content()
        return None

    async def has_form_errors(self) -> bool:
        """Prüft ob Formularfehler vorhanden sind."""
        errors = self.page.locator(self.FORM_ERROR)
        return await errors.count() > 0

    async def get_form_errors(self) -> list[str]:
        """Gibt alle Formularfehler zurück."""
        errors = []
        error_elements = self.page.locator(self.FORM_ERROR)
        count = await error_elements.count()
        for i in range(count):
            text = await error_elements.nth(i).text_content()
            if text and text.strip():
                errors.append(text.strip())
        return errors
