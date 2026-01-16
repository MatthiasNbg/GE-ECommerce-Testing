"""Utilities für automatische Zahlungsarten-Ermittlung."""
from pathlib import Path
import yaml
import shutil


def generate_aliases(discovered_methods: dict[str, list[str]]) -> dict[str, str]:
    """
    Generiert englische Aliases für deutsche Zahlungsarten-Labels.

    Args:
        discovered_methods: Dict[country_code, List[label]]

    Returns:
        Dict[alias, label] - Mapping von englischen Aliases zu deutschen Labels

    Examples:
        >>> generate_aliases({"AT": ["Rechnung", "Kreditkarte"]})
        {'invoice': 'Rechnung', 'credit_card': 'Kreditkarte'}
    """
    known_mappings = {
        "Rechnung": "invoice",
        "Kreditkarte": "credit_card",
        "Vorkasse": "prepayment",
        "PayPal": "paypal",
        "Klarna": "klarna",
        "Sofortüberweisung": "sofort",
    }

    aliases = {}
    all_labels = set()

    # Sammle alle einzigartigen Labels aus allen Ländern
    for labels in discovered_methods.values():
        all_labels.update(labels)

    # Erstelle Aliases
    for label in all_labels:
        if label in known_mappings:
            alias = known_mappings[label]
        else:
            # Generischer Alias: lowercase, Umlaute ersetzen
            alias = (
                label.lower()
                .replace("ä", "ae")
                .replace("ö", "oe")
                .replace("ü", "ue")
                .replace("ß", "ss")
                .replace(" ", "_")
            )

        aliases[alias] = label

    return aliases


def update_config_with_payment_methods(
    profile_name: str,
    discovered_methods: dict[str, list[str]],
    config_path: Path | None = None,
) -> None:
    """
    Aktualisiert config.yaml mit ermittelten Zahlungsarten.

    Args:
        profile_name: Name des Profils (staging, production)
        discovered_methods: Dict[country_code, List[label]]
        config_path: Pfad zur config.yaml (optional, default: config/config.yaml)

    Raises:
        FileNotFoundError: Wenn config.yaml nicht existiert
        KeyError: Wenn Profil nicht in Config existiert
    """
    # Standard-Pfad wenn nicht angegeben
    if config_path is None:
        # Projekt-Root finden (zwei Ebenen über diesem File)
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config" / "config.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"Config nicht gefunden: {config_path}")

    # Config laden
    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Validierung (vor Backup, um orphaned backups zu vermeiden)
    if "profiles" not in config or profile_name not in config["profiles"]:
        raise KeyError(f"Profil '{profile_name}' nicht in Config gefunden")

    # Backup erstellen (erst nach erfolgreicher Validierung)
    backup_path = config_path.with_suffix(".yaml.backup")
    shutil.copy2(config_path, backup_path)
    print(f"[Discovery] Backup erstellt: {backup_path}")

    # Country paths hinzufügen (nur für entdeckte Länder)
    if "country_paths" not in config["profiles"][profile_name]:
        config["profiles"][profile_name]["country_paths"] = {}

    # Standard-Pfade für entdeckte Länder
    default_paths = {
        "AT": "/",
        "DE": "/de-de",
        "CH": "/de-ch"
    }
    for country in discovered_methods.keys():
        if country not in config["profiles"][profile_name]["country_paths"]:
            config["profiles"][profile_name]["country_paths"][country] = default_paths.get(country, "/")

    # Payment methods hinzufügen
    config["profiles"][profile_name]["payment_methods"] = discovered_methods

    # Aliases generieren und mergen
    new_aliases = generate_aliases(discovered_methods)
    if "payment_method_aliases" not in config:
        config["payment_method_aliases"] = {}
    config["payment_method_aliases"].update(new_aliases)

    # Zurückschreiben mit UTF-8 encoding
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, sort_keys=False)

    print(f"[Discovery] Config aktualisiert: {config_path}")
