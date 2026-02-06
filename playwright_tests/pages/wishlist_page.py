"""
Wishlist (Merkliste) Page Object - Interaktionen mit der Shopware 6 Merkliste.

Unterstuetzt:
- Produkte zur Merkliste hinzufuegen/entfernen (Produktseite)
- Merklisten-Seite (/wishlist)
- Produkte aus Merkliste in den Warenkorb legen
"""
from typing import Optional

from playwright.async_api import Page

from .base_page import BasePage


class WishlistPage(BasePage):
    """
    Page Object fuer die Shopware 6 Merkliste (Wishlist).

    Unterstuetzt:
    - Herz-Button auf Produktseiten (hinzufuegen/entfernen)
    - Merklisten-Seite anzeigen
    - Produkte entfernen
    - Produkte in den Warenkorb legen
    """

    # =========================================================================
    # URLs
    # =========================================================================
    WISHLIST_PATH = "/wishlist"

    # =========================================================================
    # Produktseite - Wishlist Toggle (Herz-Button)
    # =========================================================================
    WISHLIST_BUTTON = "[data-add-to-wishlist]"
    WISHLIST_NOT_ADDED = ".product-wishlist-not-added"
    WISHLIST_ADDED = ".product-wishlist-added"

    # =========================================================================
    # Merklisten-Seite (/wishlist)
    # =========================================================================
    WISHLIST_LISTING = ".cms-listing-col, .wishlist-listing, .card-body"
    WISHLIST_PRODUCT = ".product-box.box-wishlist"
    WISHLIST_PRODUCT_NAME = ".product-name, .card-title, a.product-name"
    WISHLIST_REMOVE_BUTTON = ".product-wishlist-remove"
    WISHLIST_ADD_TO_CART = "button.btn-buy, [data-add-to-cart]"
    WISHLIST_EMPTY_MESSAGE = ".wishlist-empty, .alert-info"

    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)

    # =========================================================================
    # Produktseite - Wishlist Toggle
    # =========================================================================

    async def toggle_wishlist_on_product_page(self) -> None:
        """Klickt den Herz-Button auf der Produktseite (hinzufuegen/entfernen)."""
        wishlist_btn = self.page.locator(self.WISHLIST_BUTTON)
        if await wishlist_btn.count() > 0:
            await wishlist_btn.first.click()
            await self.page.wait_for_timeout(2000)

    async def is_product_on_wishlist(self) -> bool:
        """Prueft ob das aktuelle Produkt auf der Merkliste ist (Herz aktiv)."""
        added = self.page.locator(self.WISHLIST_ADDED)
        try:
            return await added.first.is_visible(timeout=2000)
        except Exception:
            return False

    async def add_product_to_wishlist(self, product_path: str) -> bool:
        """
        Navigiert zu einem Produkt und fuegt es zur Merkliste hinzu.

        Args:
            product_path: Produktpfad (z.B. "p/kurzarmshirt/ge-p-862990")

        Returns:
            True wenn erfolgreich
        """
        await self.navigate(f"/{product_path}")
        await self.page.wait_for_load_state("domcontentloaded")
        await self.page.wait_for_timeout(1000)
        await self.accept_cookies_if_visible()

        # Falls bereits auf Merkliste, nichts tun
        if await self.is_product_on_wishlist():
            return True

        await self.toggle_wishlist_on_product_page()
        return await self.is_product_on_wishlist()

    # =========================================================================
    # Merklisten-Seite
    # =========================================================================

    async def navigate_to_wishlist(self) -> None:
        """Navigiert zur Merklisten-Seite."""
        await self.navigate(self.WISHLIST_PATH)
        await self.page.wait_for_timeout(1000)

    async def get_wishlist_count(self) -> int:
        """Gibt die Anzahl der Produkte auf der Merkliste zurueck."""
        products = self.page.locator(self.WISHLIST_PRODUCT)
        return await products.count()

    async def get_wishlist_items(self) -> list[str]:
        """
        Gibt die Produktnamen auf der Merkliste zurueck.

        Returns:
            Liste von Produktnamen
        """
        names = []
        products = self.page.locator(self.WISHLIST_PRODUCT)
        count = await products.count()

        for i in range(count):
            product = products.nth(i)
            name_el = product.locator(self.WISHLIST_PRODUCT_NAME)
            if await name_el.count() > 0:
                text = await name_el.first.text_content()
                if text:
                    names.append(text.strip())
        return names

    async def is_wishlist_empty(self) -> bool:
        """Prueft ob die Merkliste leer ist."""
        # Methode 1: Leermeldung sichtbar
        empty_msg = self.page.locator(self.WISHLIST_EMPTY_MESSAGE)
        try:
            if await empty_msg.first.is_visible(timeout=2000):
                return True
        except Exception:
            pass

        # Methode 2: Keine Produkte vorhanden
        products = self.page.locator(self.WISHLIST_PRODUCT)
        return await products.count() == 0

    async def remove_item(self, index: int = 0) -> None:
        """
        Entfernt ein Produkt von der Merkliste via Form-Submit.

        Args:
            index: Index des Produkts (0-basiert)
        """
        forms = self.page.locator(".product-wishlist-form")
        if index < await forms.count():
            await self.page.evaluate(f"""(idx) => {{
                const forms = document.querySelectorAll('.product-wishlist-form');
                if (forms[idx]) forms[idx].submit();
            }}""", index)
            await self.page.wait_for_load_state("domcontentloaded")
            await self.page.wait_for_timeout(1000)

    async def add_item_to_cart(self, index: int = 0) -> None:
        """
        Legt ein Produkt aus der Merkliste in den Warenkorb.

        Args:
            index: Index des Produkts (0-basiert)
        """
        products = self.page.locator(self.WISHLIST_PRODUCT)
        if index < await products.count():
            product = products.nth(index)
            cart_btn = product.locator(self.WISHLIST_ADD_TO_CART)
            if await cart_btn.count() > 0:
                await cart_btn.first.click()
                await self.page.wait_for_timeout(3000)

    async def clear_wishlist(self) -> None:
        """Entfernt alle Produkte von der Merkliste."""
        while True:
            products = self.page.locator(self.WISHLIST_PRODUCT)
            if await products.count() == 0:
                break
            await self.remove_item(0)
