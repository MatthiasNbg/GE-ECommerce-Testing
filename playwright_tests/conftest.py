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
    }


@pytest.fixture(scope="session")
def test_product_id(config: TestConfig) -> str:
    """Erste Produkt-ID für einfache Tests."""
    return config.test_products[0] if config.test_products else "SW-10001"


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
    return config.test_products


# =============================================================================
# pytest-playwright Konfiguration
# =============================================================================

@pytest.fixture(scope="session")
def browser_type_launch_args(config: TestConfig) -> dict:
    """Browser-Launch-Argumente für pytest-playwright."""
    return {
        "headless": config.headless,
        "slow_mo": config.slow_mo,
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
