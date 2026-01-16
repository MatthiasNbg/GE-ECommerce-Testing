"""Utilities für automatische Zahlungsarten-Ermittlung."""


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
            # Generischer Alias: lowercase, Umlaute entfernen
            alias = (
                label.lower()
                .replace("ä", "a")
                .replace("ö", "o")
                .replace("ü", "u")
                .replace("ß", "ss")
                .replace(" ", "_")
            )

        aliases[alias] = label

    return aliases
