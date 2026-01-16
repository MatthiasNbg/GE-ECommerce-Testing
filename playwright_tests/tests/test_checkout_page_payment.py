"""
Unit tests für flexible payment selection in CheckoutPage.

Diese Tests verwenden Mocks und benötigen keine Browser-Interaktion.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from playwright_tests.pages.checkout_page import CheckoutPage
from playwright_tests.config import TestConfig


@pytest.fixture
def mock_page():
    """Mock Playwright Page object."""
    page = MagicMock()
    page.locator = MagicMock()
    page.click = AsyncMock()
    return page


@pytest.fixture
def mock_config():
    """Mock TestConfig with payment_method_aliases."""
    config = MagicMock(spec=TestConfig)
    config.payment_method_aliases = {
        "invoice": "Rechnung",
        "credit_card": "Kreditkarte",
        "paypal": "PayPal",
        "prepayment": "Vorkasse",
    }
    return config


@pytest.fixture
def checkout_page(mock_page):
    """CheckoutPage instance with mocked dependencies."""
    return CheckoutPage(mock_page, "https://example.com")


@pytest.mark.asyncio
async def test_select_payment_by_alias(checkout_page, mock_page, mock_config):
    """
    Test: Auswahl einer Zahlungsart per englischem Alias.

    Erwartung:
    - Alias "invoice" wird zu "Rechnung" übersetzt
    - DOM-Suche nach Label "Rechnung"
    - Radio-Button wird geklickt
    """
    # Mock: Radio button
    mock_radio = MagicMock()
    mock_radio.click = AsyncMock()

    # Mock: Label mit radio button
    mock_first_label = MagicMock()
    mock_first_label.locator = MagicMock(return_value=mock_radio)

    # Mock: Filtered labels
    mock_filtered = MagicMock()
    mock_filtered.count = AsyncMock(return_value=1)
    mock_filtered.first = mock_first_label

    # Mock: All labels
    mock_labels = MagicMock()
    mock_labels.filter = MagicMock(return_value=mock_filtered)

    mock_page.locator.return_value = mock_labels

    # Mock: get_config() gibt unsere mock_config zurück
    with patch("playwright_tests.pages.checkout_page.get_config", return_value=mock_config):
        await checkout_page.select_payment_method("invoice")

    # Assertions
    mock_page.locator.assert_called_once()
    mock_radio.click.assert_called_once()


@pytest.mark.asyncio
async def test_select_payment_by_german_label(checkout_page, mock_page, mock_config):
    """
    Test: Auswahl einer Zahlungsart per deutschem Label (direkter Passthrough).

    Erwartung:
    - "Rechnung" ist kein Alias, wird direkt verwendet
    - DOM-Suche nach Label "Rechnung"
    - Radio-Button wird geklickt
    """
    # Mock: Radio button
    mock_radio = MagicMock()
    mock_radio.click = AsyncMock()

    # Mock: Label mit radio button
    mock_first_label = MagicMock()
    mock_first_label.locator = MagicMock(return_value=mock_radio)

    # Mock: Filtered labels
    mock_filtered = MagicMock()
    mock_filtered.count = AsyncMock(return_value=1)
    mock_filtered.first = mock_first_label

    # Mock: All labels
    mock_labels = MagicMock()
    mock_labels.filter = MagicMock(return_value=mock_filtered)

    mock_page.locator.return_value = mock_labels

    with patch("playwright_tests.pages.checkout_page.get_config", return_value=mock_config):
        await checkout_page.select_payment_method("Rechnung")

    # Assertions
    mock_page.locator.assert_called_once()
    mock_radio.click.assert_called_once()


@pytest.mark.asyncio
async def test_select_payment_not_found(checkout_page, mock_page, mock_config):
    """
    Test: Fehlerfall - Zahlungsart nicht gefunden.

    Erwartung:
    - ValueError mit klarer Fehlermeldung
    """
    # Mock: Filtered labels (count = 0)
    mock_filtered = MagicMock()
    mock_filtered.count = AsyncMock(return_value=0)

    # Mock: All labels
    mock_labels = MagicMock()
    mock_labels.filter = MagicMock(return_value=mock_filtered)

    mock_page.locator.return_value = mock_labels

    with patch("playwright_tests.pages.checkout_page.get_config", return_value=mock_config):
        with pytest.raises(ValueError, match="Zahlungsart.*nicht gefunden"):
            await checkout_page.select_payment_method("unknown_method")
