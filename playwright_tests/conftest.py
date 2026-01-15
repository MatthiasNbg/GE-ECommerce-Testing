"""
Pytest Fixtures für Playwright E2E Tests.

Stellt Browser, Pages und Konfiguration für alle Tests bereit.
"""
import pytest
from pathlib import Path
from typing import AsyncGenerator

from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)

from .config import TestConfig, get_config


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
    config.addinivalue_line("markers", "slow: Langsame Tests (explizit anfordern)")


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
    """Basis-URL des zu testenden Shops."""
    return config.base_url


@pytest.fixture(scope="session")
def shop_config(config: TestConfig) -> dict:
    """Shop-Konfiguration als Dictionary (für Legacy-Kompatibilität)."""
    return {
        "base_url": config.base_url,
        "timeout": config.timeout,
        "parallel_workers": config.parallel_workers,
    }


@pytest.fixture(scope="session")
def test_product_id(config: TestConfig) -> str:
    """Erste Produkt-ID für einfache Tests."""
    return config.test_products[0] if config.test_products else "SW-10001"


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
    return config.test_products


# =============================================================================
# Playwright Fixtures
# =============================================================================

@pytest.fixture(scope="session")
async def playwright() -> AsyncGenerator[Playwright, None]:
    """Playwright-Instanz für die Session."""
    async with async_playwright() as p:
        yield p


@pytest.fixture(scope="session")
async def browser(playwright: Playwright, config: TestConfig) -> AsyncGenerator[Browser, None]:
    """
    Browser-Instanz für die gesamte Test-Session.

    Der Browser wird einmal gestartet und für alle Tests wiederverwendet.
    """
    browser_type = getattr(playwright, config.browser)

    browser = await browser_type.launch(
        headless=config.headless,
        slow_mo=config.slow_mo,
    )

    yield browser

    await browser.close()


@pytest.fixture
async def context(
    browser: Browser,
    config: TestConfig
) -> AsyncGenerator[BrowserContext, None]:
    """
    Browser-Kontext für einen einzelnen Test.

    Jeder Test bekommt einen isolierten Kontext mit eigenem Storage.
    """
    # HTTP Basic Auth für .htaccess-geschützte Staging-Umgebungen
    http_credentials = None
    if config.htaccess_user and config.htaccess_password:
        http_credentials = {
            "username": config.htaccess_user,
            "password": config.htaccess_password,
        }

    context = await browser.new_context(
        viewport={
            "width": config.viewport.width,
            "height": config.viewport.height,
        },
        locale=config.locale,
        http_credentials=http_credentials,
    )

    # Tracing aktivieren wenn konfiguriert
    if config.trace_on_failure:
        await context.tracing.start(
            screenshots=True,
            snapshots=True,
            sources=True,
        )

    yield context

    await context.close()


@pytest.fixture
async def page(
    context: BrowserContext,
    config: TestConfig,
    request,
) -> AsyncGenerator[Page, None]:
    """
    Page-Instanz für einen einzelnen Test.

    Bei Fehlern werden automatisch Screenshots und Traces gespeichert.
    """
    page = await context.new_page()

    yield page

    # Bei Test-Fehler: Debugging-Artefakte speichern
    if request.node.rep_call.failed if hasattr(request.node, "rep_call") else False:
        # Screenshot speichern
        if config.screenshot_on_failure:
            screenshot_path = Path(config.reports.screenshots) / f"{request.node.name}.png"
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            await page.screenshot(path=str(screenshot_path), full_page=True)

        # Trace speichern
        if config.trace_on_failure:
            trace_path = Path(config.reports.traces) / f"{request.node.name}.zip"
            trace_path.parent.mkdir(parents=True, exist_ok=True)
            await context.tracing.stop(path=str(trace_path))

    await page.close()


# =============================================================================
# Pytest Hooks für Failure Detection
# =============================================================================

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Speichert Test-Ergebnis für Fixture-Cleanup."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)
