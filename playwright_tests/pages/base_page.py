"""
Basis Page Object - gemeinsame Funktionalität für alle Seiten.
"""
from typing import Optional

from playwright.async_api import Page, expect


class BasePage:
    """
    Basisklasse für alle Page Objects.

    Stellt gemeinsame Methoden für Navigation, Waits und
    häufige Interaktionen bereit.
    """

    # Cookie-Banner Selektoren (Shopware 6 Standard + Usercentrics)
    COOKIE_ACCEPT_BUTTON = "css=.js-cookie-accept-all-button, [data-cookie-accept-all], button#accept, #accept, button[data-action-type='accept']"
    COOKIE_BANNER = "css=.cookie-permission-container, .js-cookie-permission, #usercentrics-cmp-ui"

    # Allgemeine Fehler-Selektoren
    ERROR_ALERT = "css=.alert-danger, .alert-error"

    def __init__(self, page: Page, base_url: str):
        """
        Initialisiert das Page Object.

        Args:
            page: Playwright Page-Instanz
            base_url: Basis-URL des Shops (z.B. https://staging.gruene-erde.com)
        """
        self.page = page
        self.base_url = base_url.rstrip("/")

    # =========================================================================
    # Navigation
    # =========================================================================

    async def navigate(self, path: str = "/") -> None:
        """
        Navigiert zu einem Pfad relativ zur Basis-URL.

        Args:
            path: Relativer Pfad (z.B. "/checkout/confirm")
        """
        url = f"{self.base_url}{path}"
        await self.page.goto(url)
        await self.page.wait_for_load_state("domcontentloaded")

    async def navigate_to_url(self, url: str) -> None:
        """Navigiert zu einer absoluten URL."""
        await self.page.goto(url)
        await self.page.wait_for_load_state("domcontentloaded")

    async def reload(self) -> None:
        """Lädt die aktuelle Seite neu."""
        await self.page.reload()
        await self.page.wait_for_load_state("domcontentloaded")

    # =========================================================================
    # Cookie-Banner
    # =========================================================================

    async def accept_cookies_if_visible(self, timeout: int = 5000) -> bool:
        """
        Akzeptiert das Cookie-Banner, falls sichtbar.

        Unterstützt Usercentrics (mit Shadow DOM) und Shopware 6 Standard-Banner.

        Returns:
            True wenn Banner akzeptiert wurde, False wenn nicht vorhanden
        """
        # Warten bis Seite vollständig geladen ist
        await self.page.wait_for_load_state("networkidle")

        # Kurz warten, damit Usercentrics-Banner Zeit hat zu erscheinen
        await self.page.wait_for_timeout(2000)

        # Methode 1: Usercentrics Shadow DOM - per JavaScript klicken
        try:
            clicked = await self.page.evaluate("""
                () => {
                    // Usercentrics Banner im Shadow DOM finden
                    const ucBanner = document.querySelector('#usercentrics-cmp-ui');
                    if (ucBanner && ucBanner.shadowRoot) {
                        const acceptBtn = ucBanner.shadowRoot.querySelector('button#accept, button[data-action-type="accept"], .uc-accept-button');
                        if (acceptBtn) {
                            acceptBtn.click();
                            return true;
                        }
                    }
                    // Fallback: Button direkt im DOM (ohne Shadow DOM)
                    const directBtn = document.querySelector('button#accept, button[data-action-type="accept"]');
                    if (directBtn) {
                        directBtn.click();
                        return true;
                    }
                    return false;
                }
            """)
            if clicked:
                print("   Cookie-Banner akzeptiert (via Shadow DOM)")
                await self.page.wait_for_timeout(1500)
                return True
        except Exception as e:
            pass

        # Methode 2: Shopware 6 Standard-Banner (kein Shadow DOM)
        cookie_selectors = [
            ".js-cookie-accept-all-button",  # Shopware 6
            "[data-cookie-accept-all]",  # Shopware 6 alternativ
        ]

        for selector in cookie_selectors:
            try:
                button = self.page.locator(selector)
                if await button.count() > 0:
                    if await button.first.is_visible(timeout=timeout):
                        print(f"   Cookie-Banner gefunden: {selector}")
                        await button.first.click()
                        await self.page.wait_for_timeout(1500)
                        return True
            except Exception:
                continue

        print("   Kein Cookie-Banner gefunden")
        return False

    # =========================================================================
    # Formular-Interaktionen
    # =========================================================================

    async def fill(self, selector: str, value: str) -> None:
        """
        Füllt ein Eingabefeld aus.

        Args:
            selector: CSS-Selektor
            value: Einzugebender Wert
        """
        await self.page.fill(selector, value)

    async def click(self, selector: str) -> None:
        """Klickt auf ein Element."""
        await self.page.click(selector)

    async def select_option(self, selector: str, value: str) -> None:
        """
        Wählt eine Option in einem Select-Element.

        Args:
            selector: CSS-Selektor des Select-Elements
            value: Wert der zu wählenden Option
        """
        await self.page.select_option(selector, value)

    async def select_option_by_label(self, selector: str, label: str) -> None:
        """
        Wählt eine Option in einem Select-Element anhand des Labels.

        Args:
            selector: CSS-Selektor des Select-Elements
            label: Sichtbarer Text der Option
        """
        await self.page.select_option(selector, label=label)

    async def check(self, selector: str) -> None:
        """Aktiviert eine Checkbox."""
        checkbox = self.page.locator(selector)
        if not await checkbox.is_checked():
            await checkbox.check()

    async def uncheck(self, selector: str) -> None:
        """Deaktiviert eine Checkbox."""
        checkbox = self.page.locator(selector)
        if await checkbox.is_checked():
            await checkbox.uncheck()

    # =========================================================================
    # Warten & Assertions
    # =========================================================================

    async def wait_for_selector(
        self,
        selector: str,
        state: str = "visible",
        timeout: int = 30000
    ) -> None:
        """
        Wartet auf ein Element.

        Args:
            selector: CSS-Selektor
            state: "visible", "hidden", "attached", "detached"
            timeout: Timeout in Millisekunden
        """
        await self.page.locator(selector).wait_for(state=state, timeout=timeout)

    async def wait_for_url(self, url_pattern: str, timeout: int = 30000) -> None:
        """
        Wartet bis die URL einem Pattern entspricht.

        Args:
            url_pattern: URL oder Glob-Pattern (z.B. "**/checkout/**")
            timeout: Timeout in Millisekunden
        """
        await self.page.wait_for_url(url_pattern, timeout=timeout)

    async def is_visible(self, selector: str, timeout: int = 5000) -> bool:
        """Prüft ob ein Element sichtbar ist."""
        try:
            await self.page.locator(selector).wait_for(
                state="visible",
                timeout=timeout
            )
            return True
        except Exception:
            return False

    # =========================================================================
    # Fehlerbehandlung
    # =========================================================================

    async def get_error_message(self) -> Optional[str]:
        """
        Extrahiert eine Fehlermeldung von der Seite, falls vorhanden.

        Returns:
            Fehlermeldung oder None
        """
        error_element = self.page.locator(self.ERROR_ALERT)
        if await error_element.is_visible(timeout=1000):
            return await error_element.text_content()
        return None

    async def has_error(self) -> bool:
        """Prüft ob ein Fehler auf der Seite angezeigt wird."""
        return await self.is_visible(self.ERROR_ALERT, timeout=1000)

    # =========================================================================
    # Screenshots & Debugging
    # =========================================================================

    async def screenshot(self, path: str, full_page: bool = False) -> None:
        """
        Erstellt einen Screenshot.

        Args:
            path: Speicherpfad
            full_page: Gesamte Seite oder nur Viewport
        """
        await self.page.screenshot(path=path, full_page=full_page)

    async def get_current_url(self) -> str:
        """Gibt die aktuelle URL zurück."""
        return self.page.url

    async def get_title(self) -> str:
        """Gibt den Seitentitel zurück."""
        return await self.page.title()
