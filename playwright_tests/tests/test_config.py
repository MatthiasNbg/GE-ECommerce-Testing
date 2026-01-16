"""Tests für Konfigurationsmanagement."""
import pytest
from playwright_tests.config import TestConfig


def test_config_has_payment_method_aliases():
    """Config unterstützt payment_method_aliases Dict."""
    config = TestConfig.load()
    assert hasattr(config, "payment_method_aliases")
    assert isinstance(config.payment_method_aliases, dict)


def test_config_has_payment_methods():
    """Config unterstützt payment_methods Dict mit Länder-Keys."""
    config = TestConfig.load()
    assert hasattr(config, "payment_methods")
    assert isinstance(config.payment_methods, dict)


def test_config_has_country_paths():
    """Config hat Standard country_paths für AT/DE/CH."""
    config = TestConfig.load()
    assert hasattr(config, "country_paths")
    assert config.country_paths["AT"] == "/"
    assert config.country_paths["DE"] == "/de-de"
    assert config.country_paths["CH"] == "/de-ch"
