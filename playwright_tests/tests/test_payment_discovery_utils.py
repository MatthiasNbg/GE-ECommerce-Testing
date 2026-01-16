"""Tests für Payment Discovery Utilities."""
import pytest
from pathlib import Path
import yaml
import tempfile
import shutil
from playwright_tests.utils.payment_discovery import generate_aliases, update_config_with_payment_methods


def test_generate_aliases_known_mappings():
    """Bekannte deutsche Labels werden zu englischen Aliases."""
    discovered = {
        "AT": ["Rechnung", "Kreditkarte", "Vorkasse", "Sofortüberweisung"]
    }

    aliases = generate_aliases(discovered)

    assert aliases["invoice"] == "Rechnung"
    assert aliases["credit_card"] == "Kreditkarte"
    assert aliases["prepayment"] == "Vorkasse"
    assert aliases["sofort"] == "Sofortüberweisung"


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
        "AT": ["Überweisung"]
    }

    aliases = generate_aliases(discovered)

    # Generischer Alias: lowercase, Umlaute ersetzen (ü→ue)
    assert aliases["ueberweisung"] == "Überweisung"


def test_generate_aliases_empty_input():
    """Leere discovered_methods liefern leeres Dict."""
    discovered = {}
    aliases = generate_aliases(discovered)
    assert aliases == {}


def test_update_config_adds_payment_methods():
    """Config wird mit discovered payment methods aktualisiert."""
    # Temporäres Config-Verzeichnis
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / "config"
        config_dir.mkdir()
        config_path = config_dir / "config.yaml"

        # Minimale Config erstellen
        initial_config = {
            "profiles": {
                "staging": {
                    "base_url": "https://example.com"
                }
            }
        }
        with open(config_path, "w") as f:
            yaml.dump(initial_config, f)

        # Update ausführen
        discovered = {
            "AT": ["Rechnung", "Kreditkarte"],
            "DE": ["PayPal", "Rechnung"]
        }
        update_config_with_payment_methods("staging", discovered, config_path)

        # Config neu laden
        with open(config_path) as f:
            updated = yaml.safe_load(f)

        # Validierung
        assert "payment_methods" in updated["profiles"]["staging"]
        assert updated["profiles"]["staging"]["payment_methods"]["AT"] == ["Rechnung", "Kreditkarte"]
        assert updated["profiles"]["staging"]["payment_methods"]["DE"] == ["PayPal", "Rechnung"]


def test_update_config_adds_aliases():
    """Config wird mit generierten Aliases aktualisiert."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / "config"
        config_dir.mkdir()
        config_path = config_dir / "config.yaml"

        initial_config = {
            "profiles": {
                "staging": {
                    "base_url": "https://example.com"
                }
            }
        }
        with open(config_path, "w") as f:
            yaml.dump(initial_config, f)

        discovered = {
            "AT": ["Rechnung"]
        }
        update_config_with_payment_methods("staging", discovered, config_path)

        with open(config_path) as f:
            updated = yaml.safe_load(f)

        assert "payment_method_aliases" in updated
        assert updated["payment_method_aliases"]["invoice"] == "Rechnung"


def test_update_config_creates_backup():
    """Backup wird vor Update erstellt."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / "config"
        config_dir.mkdir()
        config_path = config_dir / "config.yaml"
        backup_path = config_dir / "config.yaml.backup"

        initial_config = {"profiles": {"staging": {"base_url": "https://example.com"}}}
        with open(config_path, "w") as f:
            yaml.dump(initial_config, f)

        discovered = {"AT": ["Rechnung"]}
        update_config_with_payment_methods("staging", discovered, config_path)

        assert backup_path.exists()


def test_update_config_adds_country_paths():
    """Country paths werden hinzugefügt nur für entdeckte Länder."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / "config"
        config_dir.mkdir()
        config_path = config_dir / "config.yaml"

        initial_config = {
            "profiles": {
                "staging": {
                    "base_url": "https://example.com"
                }
            }
        }
        with open(config_path, "w") as f:
            yaml.dump(initial_config, f)

        discovered = {"AT": ["Rechnung"], "DE": ["PayPal"]}
        update_config_with_payment_methods("staging", discovered, config_path)

        with open(config_path) as f:
            updated = yaml.safe_load(f)

        assert "country_paths" in updated["profiles"]["staging"]
        assert updated["profiles"]["staging"]["country_paths"]["AT"] == "/"
        assert updated["profiles"]["staging"]["country_paths"]["DE"] == "/de-de"
        # CH sollte NICHT hinzugefügt werden, da nicht in discovered_methods
        assert "CH" not in updated["profiles"]["staging"]["country_paths"]


def test_update_config_raises_error_for_invalid_profile():
    """KeyError wird geworfen wenn Profil nicht existiert."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / "config"
        config_dir.mkdir()
        config_path = config_dir / "config.yaml"

        initial_config = {
            "profiles": {
                "staging": {
                    "base_url": "https://example.com"
                }
            }
        }
        with open(config_path, "w") as f:
            yaml.dump(initial_config, f)

        discovered = {"AT": ["Rechnung"]}

        with pytest.raises(KeyError, match="Profil 'invalid_profile' nicht in Config gefunden"):
            update_config_with_payment_methods("invalid_profile", discovered, config_path)


def test_update_config_raises_error_for_missing_file():
    """FileNotFoundError wird geworfen wenn config.yaml nicht existiert."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config" / "config.yaml"
        discovered = {"AT": ["Rechnung"]}

        with pytest.raises(FileNotFoundError, match="Config nicht gefunden"):
            update_config_with_payment_methods("staging", discovered, config_path)
