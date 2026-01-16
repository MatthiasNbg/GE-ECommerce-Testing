"""Tests für Payment Discovery Utilities."""
import pytest
from playwright_tests.utils.payment_discovery import generate_aliases


def test_generate_aliases_known_mappings():
    """Bekannte deutsche Labels werden zu englischen Aliases."""
    discovered = {
        "AT": ["Rechnung", "Kreditkarte", "Vorkasse"]
    }

    aliases = generate_aliases(discovered)

    assert aliases["invoice"] == "Rechnung"
    assert aliases["credit_card"] == "Kreditkarte"
    assert aliases["prepayment"] == "Vorkasse"


def test_generate_aliases_handles_duplicates():
    """Labels aus mehreren Ländern werden dedupliziert."""
    discovered = {
        "AT": ["Rechnung", "Kreditkarte"],
        "DE": ["Rechnung", "PayPal"]
    }

    aliases = generate_aliases(discovered)

    # "Rechnung" sollte nur einmal vorkommen
    assert aliases["invoice"] == "Rechnung"
    assert len([v for v in aliases.values() if v == "Rechnung"]) == 1


def test_generate_aliases_unknown_labels():
    """Unbekannte Labels bekommen generischen Alias."""
    discovered = {
        "AT": ["Sofortüberweisung"]
    }

    aliases = generate_aliases(discovered)

    # Generischer Alias: lowercase, keine Umlaute/Sonderzeichen
    assert aliases["sofortuberweisung"] == "Sofortüberweisung"


def test_generate_aliases_empty_input():
    """Leere discovered_methods liefern leeres Dict."""
    discovered = {}
    aliases = generate_aliases(discovered)
    assert aliases == {}
