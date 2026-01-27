"""
Cart Page Object - Interaktionen mit dem Shopware Warenkorb.

Unterstützt:
- Warenkorb-Seite (/checkout/cart)
- Offcanvas-Cart (Slide-out)
- Header Cart-Widget
"""
import re
from dataclasses import dataclass
from typing import Optional

from playwright.async_api import Page

from .base_page import BasePage


@dataclass
class CartItem:
    """Repräsentiert ein Produkt im Warenkorb."""
    name: str
    quantity: int
    unit_price: float
    total_price: float
    index: int


class CartPage(BasePage):
    """
    Page Object für den Shopware 6 Warenkorb.

    Unterstützt:
    - Produkte zum Warenkorb hinzufügen
    - Mengen ändern
    - Produkte entfernen
    - Preisberechnungen prüfen
    """

    # =========================================================================
    # URLs
    # =========================================================================
    CART_PATH = "/checkout/cart"

    # =========================================================================
    # Header Cart Widget
    # =========================================================================
    CART_WIDGET = ".header-cart, [data-cart-widget]"
    CART_COUNTER = ".header-cart-total, .cart-quantity, .badge"
    CART_ICON = ".header-cart-icon, .cart-icon"

    # =========================================================================
    # Offcanvas Cart (Slide-out)
    # =========================================================================
    OFFCANVAS_CART = ".offcanvas-cart, .cart-offcanvas, .offcanvas.show"
    OFFCANVAS_CLOSE = ".offcanvas-close, .btn-close, [data-bs-dismiss='offcanvas']"
    OFFCANVAS_ITEMS = ".offcanvas-cart .line-item"

    # =========================================================================
    # Cart Page (/checkout/cart)
    # =========================================================================
    CART_CONTAINER = ".checkout-cart, .cart-main, .cart-container"
    CART_EMPTY_MESSAGE = ".cart-empty, .empty-cart"
    CART_EMPTY_TEXT = ":has-text('Ihr Warenkorb ist leer')"

    # Cart Items
    CART_ITEM = ".line-item"
    CART_ITEM_NAME = ".line-item-label, .line-item-details-container a"
    CART_ITEM_QUANTITY = "input[name='quantity'], input.quantity-input"
    CART_ITEM_UNIT_PRICE = ".line-item-unit-price, .line-item-price"
    CART_ITEM_TOTAL_PRICE = ".line-item-total-price, .line-item-total"
    CART_ITEM_REMOVE = ".line-item-remove, .line-item-remove-button"

    # Cart Summary
    CART_SUBTOTAL = ".checkout-aside-summary-value"
    CART_SHIPPING = ".checkout-aside-summary-list dt:has-text('Versand') + dd"
    CART_TOTAL = ".checkout-aside-summary-total, .cart-total"

    # Buttons
    CHECKOUT_BUTTON = "a:has-text('Zur Kasse'), button:has-text('Zur Kasse'), .begin-checkout-btn"
    UPDATE_CART_BUTTON = "button:has-text('Aktualisieren'), button.cart-update"
    CONTINUE_SHOPPING = "a:has-text('Weiter einkaufen'), a:has-text('Zurück zum Shop')"

    # =========================================================================
    # Promotion / Rabattcode
    # =========================================================================
    PROMOTION_CODE_INPUT = "input[name='promotionCode'], #promotionCode, input[placeholder*='Gutschein'], input[placeholder*='Code']"
    PROMOTION_CODE_SUBMIT = "button[type='submit']:has-text('Einlösen'), button:has-text('Gutschein einlösen'), .promotion-submit"
    PROMOTION_COLLAPSE_TOGGLE = "[data-bs-toggle='collapse'][href='#promotionContainer'], button:has-text('Gutschein einlösen')"
    PROMOTION_CONTAINER = "#promotionContainer, .promotion-container, .checkout-promotion"
    PROMOTION_SUCCESS_MESSAGE = ".alert-success, .promotion-success"
    PROMOTION_ERROR_MESSAGE = ".alert-danger, .promotion-error, .invalid-feedback"
    PROMOTION_LINE_ITEM = ".line-item-promotion, .line-item:has-text('Rabatt'), .line-item:has-text('Promotion')"
    PROMOTION_DISCOUNT_VALUE = ".line-item-promotion .line-item-total-price, .promotion-discount-value"

    # =========================================================================
    # Product Page - Add to Cart
    # =========================================================================
    ADD_TO_CART_BUTTON = "button.btn-buy, [data-add-to-cart]"
    PRODUCT_QUANTITY_INPUT = "input#productQuantityInput, input[name='lineItems']"

    # =========================================================================
    # Navigation
    # =========================================================================

    async def navigate_to_cart(self) -> None:
        """Navigiert zur Warenkorb-Seite."""
        await self.navigate(self.CART_PATH)
        await self.page.wait_for_timeout(1000)

    async def open_cart_offcanvas(self) -> None:
        """Öffnet den Offcanvas-Warenkorb durch Klick auf das Cart-Widget."""
        cart_widget = self.page.locator(self.CART_WIDGET)
        if await cart_widget.count() > 0:
            await cart_widget.first.click()
            await self.page.wait_for_timeout(1000)

    async def close_cart_offcanvas(self) -> None:
        """Schließt den Offcanvas-Warenkorb."""
        close_btn = self.page.locator(self.OFFCANVAS_CLOSE)
        if await close_btn.count() > 0:
            try:
                if await close_btn.first.is_visible(timeout=2000):
                    await close_btn.first.click()
                    await self.page.wait_for_timeout(500)
            except Exception:
                pass

    # =========================================================================
    # Cart Status
    # =========================================================================

    async def is_cart_empty(self) -> bool:
        """Prüft ob der Warenkorb leer ist."""
        empty_msg = self.page.locator(f"{self.CART_EMPTY_MESSAGE}, {self.CART_EMPTY_TEXT}")
        try:
            return await empty_msg.first.is_visible(timeout=2000)
        except Exception:
            # Alternativ: Keine Items vorhanden
            items = self.page.locator(self.CART_ITEM)
            return await items.count() == 0

    async def get_cart_count(self) -> int:
        """Gibt die Anzahl der Artikel im Warenkorb zurück (aus Header-Widget)."""
        counter = self.page.locator(self.CART_COUNTER)
        if await counter.count() > 0:
            try:
                text = await counter.first.text_content()
                if text:
                    # Extrahiere Zahl aus Text (z.B. "3" oder "(3)")
                    match = re.search(r'\d+', text)
                    if match:
                        return int(match.group())
            except Exception:
                pass
        return 0

    async def get_cart_item_count(self) -> int:
        """Gibt die Anzahl der verschiedenen Produkte im Warenkorb zurück."""
        items = self.page.locator(self.CART_ITEM)
        return await items.count()

    # =========================================================================
    # Cart Items
    # =========================================================================

    async def get_cart_items(self) -> list[CartItem]:
        """
        Gibt alle Produkte im Warenkorb zurück.

        Returns:
            Liste von CartItem-Objekten
        """
        items = []
        item_elements = self.page.locator(self.CART_ITEM)
        count = await item_elements.count()

        for i in range(count):
            item = item_elements.nth(i)

            # Name
            name_el = item.locator(self.CART_ITEM_NAME)
            name = await name_el.first.text_content() if await name_el.count() > 0 else ""

            # Menge
            qty_input = item.locator(self.CART_ITEM_QUANTITY)
            quantity = 1
            if await qty_input.count() > 0:
                qty_value = await qty_input.first.input_value()
                quantity = int(qty_value) if qty_value else 1

            # Einzelpreis
            unit_price_el = item.locator(self.CART_ITEM_UNIT_PRICE)
            unit_price = 0.0
            if await unit_price_el.count() > 0:
                unit_price = await self._parse_price(await unit_price_el.first.text_content())

            # Gesamtpreis
            total_price_el = item.locator(self.CART_ITEM_TOTAL_PRICE)
            total_price = 0.0
            if await total_price_el.count() > 0:
                total_price = await self._parse_price(await total_price_el.first.text_content())

            items.append(CartItem(
                name=name.strip() if name else "",
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price,
                index=i
            ))

        return items

    async def get_item_by_index(self, index: int) -> Optional[CartItem]:
        """Gibt ein bestimmtes Produkt anhand des Index zurück."""
        items = await self.get_cart_items()
        if 0 <= index < len(items):
            return items[index]
        return None

    # =========================================================================
    # Cart Actions
    # =========================================================================

    async def set_item_quantity(self, index: int, quantity: int) -> None:
        """
        Ändert die Menge eines Produkts im Warenkorb.

        Args:
            index: Index des Produkts (0-basiert)
            quantity: Neue Menge
        """
        item = self.page.locator(self.CART_ITEM).nth(index)
        qty_input = item.locator(self.CART_ITEM_QUANTITY)

        if await qty_input.count() > 0:
            await qty_input.first.fill(str(quantity))
            await qty_input.first.press("Enter")
            await self.page.wait_for_timeout(2000)  # Warten auf AJAX-Update

    async def remove_item(self, index: int) -> None:
        """
        Entfernt ein Produkt aus dem Warenkorb.

        Args:
            index: Index des Produkts (0-basiert)
        """
        item = self.page.locator(self.CART_ITEM).nth(index)
        remove_btn = item.locator(self.CART_ITEM_REMOVE)

        if await remove_btn.count() > 0:
            await remove_btn.first.click()
            await self.page.wait_for_timeout(2000)  # Warten auf AJAX-Update

    async def clear_cart(self) -> None:
        """Entfernt alle Produkte aus dem Warenkorb."""
        while True:
            items = self.page.locator(self.CART_ITEM)
            if await items.count() == 0:
                break
            await self.remove_item(0)
            await self.page.wait_for_timeout(500)

    # =========================================================================
    # Prices & Totals
    # =========================================================================

    async def get_cart_total(self) -> float:
        """Gibt die Gesamtsumme des Warenkorbs zurück."""
        total_el = self.page.locator(self.CART_TOTAL)
        if await total_el.count() > 0:
            return await self._parse_price(await total_el.first.text_content())
        return 0.0

    async def get_cart_subtotal(self) -> float:
        """Gibt die Zwischensumme (ohne Versand) zurück."""
        subtotal_el = self.page.locator(self.CART_SUBTOTAL)
        if await subtotal_el.count() > 0:
            return await self._parse_price(await subtotal_el.first.text_content())
        return 0.0

    async def _parse_price(self, price_text: Optional[str]) -> float:
        """
        Parst einen Preistext in einen Float-Wert.

        Args:
            price_text: Preistext (z.B. "€ 29,90" oder "29.90 €")

        Returns:
            Preis als Float
        """
        if not price_text:
            return 0.0

        # Entferne Währungssymbole und Whitespace
        cleaned = re.sub(r'[€$£\s]', '', price_text)

        # Ersetze Komma durch Punkt (europäisches Format)
        cleaned = cleaned.replace(',', '.')

        # Extrahiere Zahl
        match = re.search(r'[\d.]+', cleaned)
        if match:
            try:
                return float(match.group())
            except ValueError:
                pass

        return 0.0

    # =========================================================================
    # Add to Cart (from Product Page)
    # =========================================================================

    async def add_product_to_cart(self, product_path: str, quantity: int = 1) -> bool:
        """
        Fügt ein Produkt zum Warenkorb hinzu.

        Args:
            product_path: Produktpfad (z.B. "p/kurzarmshirt/ge-p-862990")
            quantity: Menge (Standard: 1)

        Returns:
            True wenn erfolgreich
        """
        # Zur Produktseite navigieren
        await self.navigate(f"/{product_path}")
        await self.page.wait_for_load_state("domcontentloaded")
        await self.page.wait_for_timeout(1000)

        # Cookie-Banner akzeptieren
        await self.accept_cookies_if_visible()

        # Menge setzen (falls > 1)
        if quantity > 1:
            qty_input = self.page.locator(self.PRODUCT_QUANTITY_INPUT)
            if await qty_input.count() > 0:
                await qty_input.first.fill(str(quantity))

        # In den Warenkorb
        add_btn = self.page.locator(self.ADD_TO_CART_BUTTON)
        if await add_btn.count() == 0:
            return False

        await add_btn.first.click()
        await self.page.wait_for_timeout(3000)  # Warten auf AJAX

        # Offcanvas schließen
        await self.close_cart_offcanvas()

        return True

    # =========================================================================
    # Promotion / Rabattcode
    # =========================================================================

    async def apply_promotion_code(self, code: str) -> bool:
        """
        Wendet einen Rabattcode/Gutscheincode an.

        Args:
            code: Der Promotion-Code

        Returns:
            True wenn erfolgreich angewendet
        """
        # Promotion-Container öffnen falls nötig
        toggle = self.page.locator(self.PROMOTION_COLLAPSE_TOGGLE)
        if await toggle.count() > 0:
            try:
                if await toggle.first.is_visible():
                    await toggle.first.click()
                    await self.page.wait_for_timeout(500)
            except Exception:
                pass

        # Code-Eingabefeld finden
        code_input = self.page.locator(self.PROMOTION_CODE_INPUT)
        if await code_input.count() == 0:
            return False

        # Code eingeben
        await code_input.first.fill(code)
        await self.page.wait_for_timeout(300)

        # Code absenden
        submit_btn = self.page.locator(self.PROMOTION_CODE_SUBMIT)
        if await submit_btn.count() > 0:
            await submit_btn.first.click()
        else:
            # Fallback: Enter drücken
            await code_input.first.press("Enter")

        await self.page.wait_for_timeout(2000)  # Warten auf Server-Antwort

        # Prüfe ob erfolgreich
        success = self.page.locator(self.PROMOTION_SUCCESS_MESSAGE)
        return await success.count() > 0

    async def get_promotion_error(self) -> Optional[str]:
        """Gibt die Fehlermeldung zurück, falls ein Promotion-Code abgelehnt wurde."""
        error = self.page.locator(self.PROMOTION_ERROR_MESSAGE)
        if await error.count() > 0:
            return await error.first.text_content()
        return None

    async def has_promotion_applied(self) -> bool:
        """Prüft ob eine Promotion/Rabatt im Warenkorb aktiv ist."""
        promo_line = self.page.locator(self.PROMOTION_LINE_ITEM)
        return await promo_line.count() > 0

    async def get_promotion_discount(self) -> float:
        """Gibt den Rabattbetrag der aktiven Promotion zurück."""
        discount_el = self.page.locator(self.PROMOTION_DISCOUNT_VALUE)
        if await discount_el.count() > 0:
            text = await discount_el.first.text_content()
            return await self._parse_price(text)
        return 0.0

    async def remove_promotion(self) -> bool:
        """Entfernt eine aktive Promotion aus dem Warenkorb."""
        promo_line = self.page.locator(self.PROMOTION_LINE_ITEM)
        if await promo_line.count() == 0:
            return False

        remove_btn = promo_line.locator(self.CART_ITEM_REMOVE)
        if await remove_btn.count() > 0:
            await remove_btn.first.click()
            await self.page.wait_for_timeout(2000)
            return True
        return False

    # =========================================================================
    # Checkout Navigation
    # =========================================================================

    async def proceed_to_checkout(self) -> None:
        """Navigiert zur Kasse."""
        checkout_btn = self.page.locator(self.CHECKOUT_BUTTON)
        if await checkout_btn.count() > 0:
            await checkout_btn.first.click()
            await self.page.wait_for_load_state("domcontentloaded")
