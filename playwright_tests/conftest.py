"""
Pytest Fixtures für Playwright E2E Tests.

Nutzt pytest-playwright's eingebaute Fixtures und erweitert sie.
"""
import pytest
from pathlib import Path
from typing import Generator

from playwright.sync_api import Page, BrowserContext

from .config import TestConfig, get_config


# =============================================================================
# Cookie-Banner Hilfsfunktionen
# =============================================================================

def accept_cookie_banner(page: Page, timeout: int = 3000) -> bool:
    """
    Akzeptiert das Cookie-Banner, falls sichtbar (sync Version).

    Unterstützt:
    - Usercentrics Banner (#accept.uc-accept-button)
    - Shopware 6 Standard Banner (.js-cookie-accept-all-button)

    Args:
        page: Playwright Page-Instanz
        timeout: Timeout in ms für die Sichtbarkeitsprüfung

    Returns:
        True wenn Banner akzeptiert wurde, False wenn nicht vorhanden
    """
    # Selektoren für verschiedene Cookie-Banner
    cookie_selectors = [
        "button#accept",  # Usercentrics (primär)
        "#accept",  # Usercentrics (alternativ)
        "button[data-action-type='accept']",  # Usercentrics data-attribute
        ".js-cookie-accept-all-button",  # Shopware 6
        "[data-cookie-accept-all]",  # Shopware 6 alternativ
    ]

    for selector in cookie_selectors:
        try:
            button = page.locator(selector)
            if button.is_visible(timeout=timeout):
                button.click()
                # Warten bis Banner verschwindet
                page.wait_for_timeout(1000)
                # Prüfen ob Banner weg ist
                banner = page.locator("#usercentrics-cmp-ui")
                try:
                    banner.wait_for(state="hidden", timeout=5000)
                except Exception:
                    pass  # Banner evtl. anders strukturiert
                return True
        except Exception:
            continue

    return False


async def accept_cookie_banner_async(page, timeout: int = 3000) -> bool:
    """
    Akzeptiert das Cookie-Banner, falls sichtbar (async Version).

    Unterstützt:
    - Usercentrics Banner (#accept.uc-accept-button)
    - Shopware 6 Standard Banner (.js-cookie-accept-all-button)

    Args:
        page: Playwright async Page-Instanz
        timeout: Timeout in ms für die Sichtbarkeitsprüfung

    Returns:
        True wenn Banner akzeptiert wurde, False wenn nicht vorhanden
    """
    # Selektoren für verschiedene Cookie-Banner
    cookie_selectors = [
        "button#accept",  # Usercentrics (primär)
        "#accept",  # Usercentrics (alternativ)
        "button[data-action-type='accept']",  # Usercentrics data-attribute
        ".js-cookie-accept-all-button",  # Shopware 6
        "[data-cookie-accept-all]",  # Shopware 6 alternativ
    ]

    for selector in cookie_selectors:
        try:
            button = page.locator(selector)
            if await button.is_visible(timeout=timeout):
                await button.click()
                # Warten bis Banner verschwindet
                await page.wait_for_timeout(1000)
                # Prüfen ob Banner weg ist
                banner = page.locator("#usercentrics-cmp-ui")
                try:
                    await banner.wait_for(state="hidden", timeout=5000)
                except Exception:
                    pass  # Banner evtl. anders strukturiert
                return True
        except Exception:
            continue

    return False


# =============================================================================
# Pytest Hooks
# =============================================================================

def pytest_addoption(parser):
    """Fügt CLI-Optionen für Tests hinzu."""
    parser.addoption(
        "--profile",
        action="store",
        default=None,
        help="Konfigurationsprofil (staging, production, local)"
    )
    parser.addoption(
        "--mass-orders",
        action="store",
        type=int,
        default=None,
        help="Anzahl der Bestellungen für Massentests"
    )
    parser.addoption(
        "--parallel",
        action="store",
        type=int,
        default=None,
        help="Anzahl paralleler Browser-Instanzen"
    )
    parser.addoption(
        "--products",
        action="store",
        default=None,
        help="Komma-separierte Liste von Produkt-IDs"
    )


def pytest_configure(config):
    """Registriert custom Marker."""
    config.addinivalue_line("markers", "smoke: Smoke-Tests für schnelle Validierung")
    config.addinivalue_line("markers", "massentest: Massentests für Bestellungen")
    config.addinivalue_line("markers", "performance: Performance-Tests (150+ Bestellungen)")
    config.addinivalue_line("markers", "slow: Langsame Tests (explizit anfordern)")
    config.addinivalue_line("markers", "discovery: Discovery-Tests für automatische Ermittlung")


# =============================================================================
# Konfiguration Fixtures
# =============================================================================

@pytest.fixture(scope="session")
def config(request) -> TestConfig:
    """Lädt die Testkonfiguration."""
    cfg = get_config()

    # CLI-Optionen überschreiben Konfiguration
    profile = request.config.getoption("--profile")
    if profile:
        import os
        os.environ["TEST_PROFILE"] = profile
        cfg = TestConfig.load()

    return cfg


@pytest.fixture(scope="session")
def base_url(config: TestConfig) -> str:
    """Basis-URL des zu testenden Shops (überschreibt pytest-playwright)."""
    return config.base_url


@pytest.fixture(scope="session")
def shop_config(config: TestConfig) -> dict:
    """Shop-Konfiguration als Dictionary (für Legacy-Kompatibilität)."""
    return {
        "base_url": config.base_url,
        "timeout": config.timeout,
        "parallel_workers": config.parallel_workers,
        "payment_methods": getattr(config, 'payment_methods', {}),
        "payment_method_aliases": getattr(config, 'payment_method_aliases', {}),
        "country": "AT",
        "htaccess_user": config.htaccess_user,
        "htaccess_password": config.htaccess_password,
    }


@pytest.fixture(scope="session")
def test_product_id(config: TestConfig) -> str:
    """Erste Produkt-ID für einfache Tests."""
    products = config.get_all_products()
    return products[0] if products else "SW-10001"


@pytest.fixture(scope="session")
def test_search_term(config: TestConfig) -> str:
    """Suchbegriff für Search-Tests."""
    return config.test_search_term


# =============================================================================
# Massentest Fixtures
# =============================================================================

@pytest.fixture(scope="session")
def mass_orders(request, config: TestConfig) -> int:
    """Anzahl der Bestellungen für Massentests."""
    cli_value = request.config.getoption("--mass-orders")
    if cli_value is not None:
        return cli_value
    return config.mass_test.default_orders


@pytest.fixture(scope="session")
def parallel(request, config: TestConfig) -> int:
    """Anzahl paralleler Worker."""
    cli_value = request.config.getoption("--parallel")
    if cli_value is not None:
        return cli_value
    return config.parallel_workers


@pytest.fixture(scope="session")
def products(request, config: TestConfig) -> list[str]:
    """Liste der Produkt-IDs für Tests."""
    cli_value = request.config.getoption("--products")
    if cli_value:
        return [p.strip() for p in cli_value.split(",")]
    return config.get_all_products()


# =============================================================================
# pytest-playwright Konfiguration
# =============================================================================

@pytest.fixture(scope="session")
def browser_type_launch_args(request, config: TestConfig) -> dict:
    """Browser-Launch-Argumente für pytest-playwright."""
    # CLI --headed überschreibt Konfiguration
    headless = config.headless
    if request.config.getoption("--headed", default=False):
        headless = False

    # CLI --slowmo überschreibt Konfiguration
    slow_mo = config.slow_mo
    cli_slowmo = request.config.getoption("--slowmo", default=None)
    if cli_slowmo is not None:
        slow_mo = int(cli_slowmo)

    return {
        "headless": headless,
        "slow_mo": slow_mo,
    }


@pytest.fixture(scope="session")
def browser_context_args(config: TestConfig) -> dict:
    """Browser-Context-Argumente für pytest-playwright."""
    args = {
        "viewport": {
            "width": config.viewport.width,
            "height": config.viewport.height,
        },
        "locale": config.locale,
    }

    # HTTP Basic Auth für .htaccess-geschützte Staging-Umgebungen
    if config.htaccess_user and config.htaccess_password:
        args["http_credentials"] = {
            "username": config.htaccess_user,
            "password": config.htaccess_password,
        }

    return args


# =============================================================================
# Pytest Hooks für Failure Detection & Reporting
# =============================================================================

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Speichert Test-Ergebnis und extras für Report."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)

    # Extras (Screenshots etc.) zum Report hinzufügen
    if hasattr(item, "extras"):
        rep.extras = item.extras
