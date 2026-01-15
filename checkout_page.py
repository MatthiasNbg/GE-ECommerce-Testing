"""
Checkout Page Object - Interaktionen mit dem Shopware Checkout.
"""
from dataclasses import dataclass
from typing import Optional

from playwright.async_api import Page, expect

from .base_page import BasePage


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
    GUEST_CHECKOUT_BUTTON = "css=[data-toggle='collapse'][href='#collapseGuestCheckout']"
    GUEST_CHECKOUT_FORM = "css=#collapseGuestCheckout"
    
    # Persönliche Daten
    SALUTATION_SELECT = "css=#personalSalutation"
    FIRST_NAME_INPUT = "css=#personalFirstName"
    LAST_NAME_INPUT = "css=#personalLastName"
    EMAIL_INPUT = "css=#personalMail"
    
    # Adresse
    STREET_INPUT = "css=#billingAddressAddressStreet"
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
    
    # AGB & Bestellung
    AGB_CHECKBOX = "css=#tos"
    REVOCATION_CHECKBOX = "css=#revocation"
    SUBMIT_ORDER_BUTTON = "css=#confirmFormSubmit"
    
    # Bestätigungsseite
    ORDER_CONFIRMATION = "css=.finish-header, .checkout-finish"
    ORDER_NUMBER = "css=.finish-ordernumber, [data-order-number]"
    
    # =========================================================================
    # Konstruktor
    # =========================================================================
    
    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.checkout_path = "/checkout/confirm"
    
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
        guest_button = self.page.locator(self.GUEST_CHECKOUT_BUTTON)
        if await guest_button.is_visible():
            await guest_button.click()
            await self.page.locator(self.GUEST_CHECKOUT_FORM).wait_for(state="visible")
    
    async def fill_personal_data(self, address: Address) -> None:
        """Füllt die persönlichen Daten aus."""
        await self.select_option(self.SALUTATION_SELECT, address.salutation)
        await self.fill(self.FIRST_NAME_INPUT, address.first_name)
        await self.fill(self.LAST_NAME_INPUT, address.last_name)
        await self.fill(self.EMAIL_INPUT, address.email)
    
    async def fill_billing_address(self, address: Address) -> None:
        """Füllt die Rechnungsadresse aus."""
        await self.fill(self.STREET_INPUT, address.street)
        await self.fill(self.ZIP_CODE_INPUT, address.zip_code)
        await self.fill(self.CITY_INPUT, address.city)
        await self.select_option(self.COUNTRY_SELECT, address.country)
    
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
            method: invoice, credit_card, paypal, klarna, etc.
        """
        selector_map = {
            "invoice": self.PAYMENT_INVOICE,
            "rechnung": self.PAYMENT_INVOICE,
            "credit_card": self.PAYMENT_CREDIT_CARD,
            "kreditkarte": self.PAYMENT_CREDIT_CARD,
            "paypal": self.PAYMENT_PAYPAL,
        }
        
        selector = selector_map.get(method.lower())
        if selector:
            payment_option = self.page.locator(selector)
            if await payment_option.is_visible():
                await payment_option.click()
        else:
            # Fallback: Versuche nach data-Attribut oder ID zu suchen
            await self.page.click(f"css=[data-payment-method='{method}'], #paymentMethod-{method}")
    
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
    
    async def execute_guest_checkout(
        self, 
        address: Address,
        payment_method: str = "invoice"
    ) -> CheckoutResult:
        """
        Führt einen kompletten Gast-Checkout durch.
        
        Args:
            address: Adressdaten für die Bestellung
            payment_method: Gewünschte Zahlungsart
            
        Returns:
            CheckoutResult mit Erfolg/Misserfolg und Details
        """
        import time
        start_time = time.time()
        
        try:
            # Gast-Checkout starten
            await self.start_guest_checkout()
            
            # Adresse eingeben
            await self.fill_guest_address(address)
            
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
