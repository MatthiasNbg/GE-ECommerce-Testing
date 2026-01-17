"""
Checkout Page Object - Interaktionen mit dem Shopware Checkout.
"""
from dataclasses import dataclass
from typing import Optional

from playwright.async_api import Page, expect

from .base_page import BasePage
from ..config import get_config


@dataclass
class Address:
    """Adressdaten für den Checkout."""
    salutation: str = "mr"  # mr, mrs
    first_name: str = "Test"
    last_name: str = "Kunde"
    street: str = "Teststraße 1"
    zip_code: str = "4020"
    city: str = "Linz"
    country: str = "AT"  # ISO-Code
    email: str = "test@example.com"
    phone: Optional[str] = None


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
    Page Object für den Shopware 6 Checkout.
    
    Unterstützt Gast-Checkout und angemeldete Benutzer.
    """
    
    # =========================================================================
    # Selektoren - Shopware 6 Standard-Theme
    # =========================================================================
    
    # Checkout-Schritte Navigation
    STEP_PERSONAL = "css=[data-checkout-step='personal']"
    STEP_ADDRESS = "css=[data-checkout-step='address']"
    STEP_PAYMENT = "css=[data-checkout-step='payment']"
    STEP_CONFIRM = "css=[data-checkout-step='confirm']"
    
    # Gast vs. Login
    GUEST_CHECKOUT_BUTTON = "button:has-text('Als Gast')"
    GUEST_CHECKOUT_BUTTON_ALT = "css=[data-toggle='collapse'][href='#collapseGuestCheckout']"
    GUEST_CHECKOUT_FORM = "css=#collapseGuestCheckout"
    
    # Persönliche Daten
    SALUTATION_SELECT = "css=#personalSalutation"
    FIRST_NAME_INPUT = "css=#billingAddress-personalFirstName"
    LAST_NAME_INPUT = "css=#billingAddress-personalLastName"
    EMAIL_INPUT = "css=#personalMail"

    # Adresse
    STREET_INPUT = "css=#billingAddress-AddressStreet"
    ZIP_CODE_INPUT = "css=#billingAddressAddressZipcode"
    CITY_INPUT = "css=#billingAddressAddressCity"
    COUNTRY_SELECT = "css=#billingAddressAddressCountry"
    
    # Lieferadresse
    DIFFERENT_SHIPPING_CHECKBOX = "css=#differentShippingAddress"
    
    # Zahlungsarten
    PAYMENT_METHOD_RADIO = "css=input[name='paymentMethodId']"
    PAYMENT_INVOICE = "css=#paymentMethod-invoice"
    PAYMENT_CREDIT_CARD = "css=#paymentMethod-creditcard"
    PAYMENT_PAYPAL = "css=#paymentMethod-paypal"
    
    # Versandarten
    SHIPPING_METHOD_RADIO = "css=input[name='shippingMethodId']"
    
    # Datenschutz (Register-Seite)
    PRIVACY_CHECKBOX = "css=#acceptedDataProtection, input[name='acceptedDataProtection']"
    CONTINUE_BUTTON = "button:has-text('Weiter')"

    # AGB & Bestellung (Confirm-Seite)
    AGB_CHECKBOX = "css=#tos"
    REVOCATION_CHECKBOX = "css=#revocation"
    SUBMIT_ORDER_BUTTON = "css=#confirmFormSubmit, button:has-text('Kostenpflichtig bestellen')"
    
    # Bestätigungsseite
    ORDER_CONFIRMATION = "css=.finish-header, .checkout-finish"
    ORDER_NUMBER = "css=.finish-ordernumber, [data-order-number]"
    
    # =========================================================================
    # Konstruktor
    # =========================================================================
    
    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.checkout_path = "/checkout/register"  # Shopware 6 Checkout-Einstieg
        self.checkout_confirm_path = "/checkout/confirm"
    
    # =========================================================================
    # Navigation
    # =========================================================================
    
    async def goto_checkout(self) -> None:
        """Navigiert direkt zum Checkout."""
        await self.navigate(self.checkout_path)
        await self.accept_cookies_if_visible()
    
    # =========================================================================
    # Gast-Checkout
    # =========================================================================
    
    async def start_guest_checkout(self) -> None:
        """Startet den Gast-Checkout."""
        # Primärer Selektor: "Als Gast bestellen" Button
        guest_button = self.page.locator(self.GUEST_CHECKOUT_BUTTON)
        if await guest_button.count() > 0 and await guest_button.is_visible():
            await guest_button.click()
            # Warte auf Navigation zur Gast-Checkout-Seite oder Formular
            await self.page.wait_for_load_state("domcontentloaded")
            return

        # Fallback: Collapse-Button (ältere Shopware-Versionen)
        guest_button_alt = self.page.locator(self.GUEST_CHECKOUT_BUTTON_ALT)
        if await guest_button_alt.count() > 0 and await guest_button_alt.is_visible():
            await guest_button_alt.click()
            await self.page.locator(self.GUEST_CHECKOUT_FORM).wait_for(state="visible")
    
    async def fill_personal_data(self, address: Address) -> None:
        """Füllt die persönlichen Daten aus."""
        # Anrede: Mapping von Kurzform zu deutschem Label
        salutation_map = {
            "mr": "Herr",
            "mrs": "Frau",
            "": "Keine Angabe",
        }
        salutation_label = salutation_map.get(address.salutation, address.salutation)
        await self.select_option_by_label(self.SALUTATION_SELECT, salutation_label)

        await self.fill(self.FIRST_NAME_INPUT, address.first_name)
        await self.fill(self.LAST_NAME_INPUT, address.last_name)
        await self.fill(self.EMAIL_INPUT, address.email)
    
    async def fill_billing_address(self, address: Address) -> None:
        """Füllt die Rechnungsadresse aus."""
        await self.fill(self.STREET_INPUT, address.street)
        await self.fill(self.ZIP_CODE_INPUT, address.zip_code)
        await self.fill(self.CITY_INPUT, address.city)

        # Land: Mapping von ISO-Code zu deutschem Label
        country_map = {
            "AT": "Österreich",
            "DE": "Deutschland",
            "CH": "Schweiz",
        }
        country_label = country_map.get(address.country, address.country)
        await self.select_option_by_label(self.COUNTRY_SELECT, country_label)
    
    async def fill_guest_address(self, address: Address) -> None:
        """Füllt alle Adressdaten für Gast-Checkout aus."""
        await self.fill_personal_data(address)
        await self.fill_billing_address(address)
    
    # =========================================================================
    # Zahlungsart
    # =========================================================================
    
    async def select_payment_method(self, method: str) -> None:
        """
        Wählt eine Zahlungsart aus - unterstützt englische Aliases und deutsche Labels.

        Args:
            method: Englischer Alias (z.B. "invoice", "credit_card")
                   oder deutscher Label (z.B. "Rechnung", "Kreditkarte")

        Raises:
            ValueError: Wenn Zahlungsart nicht im DOM gefunden wurde

        Examples:
            await page.select_payment_method("invoice")     # Alias
            await page.select_payment_method("Rechnung")    # Direkter Label
        """
        # Config laden und Alias-Mapping holen
        config = get_config()
        aliases = config.payment_method_aliases

        # Alias zu Label übersetzen (falls method ein Alias ist)
        label = aliases.get(method, method)

        # Strategie 1: Container mit Text finden, der den Radio-Button enthält
        # Shopware 6 verwendet verschiedene Strukturen für Zahlungsmethoden
        selectors = [
            # Shopware 6 Standard-Theme Selektoren
            ".payment-method",
            ".confirm-payment-method",
            ".payment-methods .payment-method-item",
            ".confirm-checkout-payment .payment-method",
            # Label-basierte Selektoren
            "label[for*='paymentMethod']",
            ".payment-method-label",
            # Fallback: Div/Container mit Radio-Button
            "div:has(input[name='paymentMethodId'])",
        ]

        for selector in selectors:
            containers = self.page.locator(selector)
            if await containers.count() > 0:
                # Nach Container mit passendem Text filtern
                matching = containers.filter(has_text=label)
                if await matching.count() > 0:
                    # Radio-Button im Container finden und klicken
                    radio = matching.first.locator("input[type='radio'], input[name='paymentMethodId']")
                    if await radio.count() > 0:
                        await radio.first.click()
                        return
                    # Falls kein Radio im Container, Container selbst klicken
                    await matching.first.click()
                    return

        # Strategie 2: Direkt nach Radio-Button mit Label-Text suchen
        # Suche nach allen Radio-Buttons und prüfe deren Labels
        radios = self.page.locator("input[name='paymentMethodId']")
        radio_count = await radios.count()

        for i in range(radio_count):
            radio = radios.nth(i)
            radio_id = await radio.get_attribute("id")

            if radio_id:
                # Zugehöriges Label finden
                label_elem = self.page.locator(f"label[for='{radio_id}']")
                if await label_elem.count() > 0:
                    label_text = await label_elem.text_content() or ""
                    if label.lower() in label_text.lower():
                        await radio.click()
                        return

            # Fallback: Parent-Element prüfen
            parent = radio.locator("xpath=..")
            parent_text = await parent.text_content() or ""
            if label.lower() in parent_text.lower():
                await radio.click()
                return

        # Wenn nichts gefunden, Fehler mit Debug-Info
        raise ValueError(
            f"Zahlungsart '{label}' nicht gefunden. "
            f"Input: '{method}', verfügbare Aliases: {list(aliases.keys())}. "
            f"Gefundene Radio-Buttons: {radio_count}"
        )
    
    async def get_selected_payment_method(self) -> Optional[str]:
        """Gibt die aktuell ausgewählte Zahlungsart zurück."""
        selected = self.page.locator(f"{self.PAYMENT_METHOD_RADIO}:checked")
        if await selected.count() > 0:
            return await selected.get_attribute("value")
        return None
    
    # =========================================================================
    # Versandart
    # =========================================================================
    
    async def select_shipping_method(self, method_id: str) -> None:
        """Wählt eine Versandart aus."""
        await self.page.click(f"css=input[name='shippingMethodId'][value='{method_id}']")
    
    # =========================================================================
    # AGB & Bestellung abschließen
    # =========================================================================
    
    async def accept_terms(self) -> None:
        """Akzeptiert AGB und Widerrufsbelehrung."""
        agb = self.page.locator(self.AGB_CHECKBOX)
        if await agb.is_visible() and not await agb.is_checked():
            await agb.check()
        
        revocation = self.page.locator(self.REVOCATION_CHECKBOX)
        if await revocation.is_visible() and not await revocation.is_checked():
            await revocation.check()
    
    async def place_order(self) -> None:
        """Klickt auf den Bestellen-Button."""
        await self.page.click(self.SUBMIT_ORDER_BUTTON)
    
    async def wait_for_confirmation(self, timeout: int = 30000) -> None:
        """Wartet auf die Bestellbestätigung."""
        await self.page.wait_for_url("**/checkout/finish/**", timeout=timeout)
        await self.page.locator(self.ORDER_CONFIRMATION).wait_for(
            state="visible", 
            timeout=timeout
        )
    
    # =========================================================================
    # Bestellinformationen
    # =========================================================================
    
    async def get_order_number(self) -> Optional[str]:
        """Extrahiert die Bestellnummer von der Bestätigungsseite."""
        order_element = self.page.locator(self.ORDER_NUMBER)
        if await order_element.is_visible():
            text = await order_element.text_content()
            # Bestellnummer aus Text extrahieren (Format variiert)
            if text:
                # Typisches Format: "Bestellnummer: 10001" oder nur "10001"
                import re
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
        """Akzeptiert Datenschutz und klickt 'Weiter' zur Confirm-Seite."""
        # Datenschutz-Checkbox akzeptieren
        privacy = self.page.locator(self.PRIVACY_CHECKBOX)
        if await privacy.count() > 0:
            if not await privacy.first.is_checked():
                await privacy.first.check()

        # "Weiter"-Button klicken
        continue_btn = self.page.locator(self.CONTINUE_BUTTON)
        if await continue_btn.count() > 0:
            await continue_btn.first.click()
            # Warten auf Navigation zur Confirm-Seite
            await self.page.wait_for_url("**/checkout/confirm**", timeout=30000)
            await self.page.wait_for_load_state("domcontentloaded")

    async def execute_guest_checkout(
        self,
        address: Address,
        payment_method: str = "invoice"
    ) -> CheckoutResult:
        """
        Führt einen kompletten Gast-Checkout durch.

        Shopware 6 zweistufiger Prozess:
        1. /checkout/register - Adresse eingeben, Datenschutz
        2. /checkout/confirm - Zahlungsart, AGB, Bestellen

        Args:
            address: Adressdaten für die Bestellung
            payment_method: Gewünschte Zahlungsart

        Returns:
            CheckoutResult mit Erfolg/Misserfolg und Details
        """
        import time
        start_time = time.time()

        try:
            # === SCHRITT 1: Register-Seite ===
            # Gast-Checkout starten
            await self.start_guest_checkout()

            # Adresse eingeben
            await self.fill_guest_address(address)

            # Datenschutz akzeptieren und "Weiter"
            await self.accept_privacy_and_continue()

            # === SCHRITT 2: Confirm-Seite ===
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
