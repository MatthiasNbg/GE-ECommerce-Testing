"""
PLZ-basierte Versandregeln fuer AT, DE, CH - SPEDITIONSVERSAND.

Diese Datei definiert, welcher Logistikpartner (Spedition) fuer welche
PLZ-Bereiche zustaendig ist. Die Tests pruefen, ob die korrekte
Spedition im Checkout angezeigt wird.

WICHTIG: Diese Regeln gelten NUR fuer Speditionsware (grosse Produkte
wie Moebel, Matratzen etc.), NICHT fuer Paketversand!

Quelle: test-concept.md - 98 Versandarten-Tests
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class PLZRule:
    """Eine PLZ-Regel fuer einen Speditions-Logistikpartner."""
    country: str  # AT, DE, CH
    carrier: str  # Logistikpartner-Name (Spedition)
    carrier_code: str  # Kurzcode fuer Test-IDs (z.B. "FINK", "LN")
    plz_min: str  # Minimale PLZ
    plz_max: str  # Maximale PLZ
    expected_label: Optional[str] = None  # Erwarteter Text in der Versandart-Anzeige


# =============================================================================
# Oesterreich (AT) - Speditionsversand
# =============================================================================

AT_SPEDITION_RULES = [
    # Post AT - Fallback/Standard (wenn keine Spedition)
    PLZRule("AT", "Post AT", "POST", "0000", "9999", "Postversand"),

    # Wetsch AT - Spedition fuer Tirol/Vorarlberg
    PLZRule("AT", "Wetsch AT", "WETSCH", "6000", "6999", "Spedition Wetsch"),

    # Fink AT - Spedition fuer mehrere PLZ-Bereiche
    PLZRule("AT", "Fink AT", "FINK", "1000", "1199", "Spedition Fink"),
    PLZRule("AT", "Fink AT", "FINK", "3000", "3399", "Spedition Fink"),
    PLZRule("AT", "Fink AT", "FINK", "3600", "3699", "Spedition Fink"),
    PLZRule("AT", "Fink AT", "FINK", "4000", "4699", "Spedition Fink"),
    PLZRule("AT", "Fink AT", "FINK", "8000", "9999", "Spedition Fink"),

    # Cargoe AT - Spedition fuer mehrere PLZ-Bereiche
    PLZRule("AT", "Cargoe AT", "CARGO", "1200", "1399", "Spedition Cargoe"),
    PLZRule("AT", "Cargoe AT", "CARGO", "2000", "2999", "Spedition Cargoe"),
    PLZRule("AT", "Cargoe AT", "CARGO", "3400", "3599", "Spedition Cargoe"),
    PLZRule("AT", "Cargoe AT", "CARGO", "3700", "3999", "Spedition Cargoe"),
    PLZRule("AT", "Cargoe AT", "CARGO", "7000", "7999", "Spedition Cargoe"),

    # Thurner AT - Spedition
    PLZRule("AT", "Thurner AT", "TH", "4700", "5799", "Spedition Thurner"),
]


# =============================================================================
# Deutschland (DE) - Speditionsversand
# =============================================================================

DE_SPEDITION_RULES = [
    # Post DE - Fallback/Standard
    PLZRule("DE", "Post DE", "POST", "00000", "99999", "Postversand"),

    # Logsens Nord - Spedition
    PLZRule("DE", "Logsens Nord", "LN", "19000", "29999", "Spedition Logsens"),
    PLZRule("DE", "Logsens Nord", "LN", "30000", "32999", "Spedition Logsens"),
    PLZRule("DE", "Logsens Nord", "LN", "34000", "37139", "Spedition Logsens"),
    PLZRule("DE", "Logsens Nord", "LN", "37140", "37199", "Spedition Logsens"),
    PLZRule("DE", "Logsens Nord", "LN", "37200", "37399", "Spedition Logsens"),
    PLZRule("DE", "Logsens Nord", "LN", "37400", "39174", "Spedition Logsens"),
    PLZRule("DE", "Logsens Nord", "LN", "39326", "39499", "Spedition Logsens"),
    PLZRule("DE", "Logsens Nord", "LN", "39500", "39699", "Spedition Logsens"),
    PLZRule("DE", "Logsens Nord", "LN", "49000", "49999", "Spedition Logsens"),

    # Logsens Ost - Spedition
    PLZRule("DE", "Logsens Ost", "LO", "00000", "09999", "Spedition Logsens"),
    PLZRule("DE", "Logsens Ost", "LO", "10000", "15999", "Spedition Logsens"),
    PLZRule("DE", "Logsens Ost", "LO", "16000", "18999", "Spedition Logsens"),
    PLZRule("DE", "Logsens Ost", "LO", "39175", "39319", "Spedition Logsens"),
    PLZRule("DE", "Logsens Ost", "LO", "95000", "96999", "Spedition Logsens"),
    PLZRule("DE", "Logsens Ost", "LO", "98000", "99999", "Spedition Logsens"),

    # Logsens Sued - Spedition
    PLZRule("DE", "Logsens Sued", "LS", "54000", "54999", "Spedition Logsens"),
    PLZRule("DE", "Logsens Sued", "LS", "56000", "56999", "Spedition Logsens"),
    PLZRule("DE", "Logsens Sued", "LS", "66000", "67999", "Spedition Logsens"),
    PLZRule("DE", "Logsens Sued", "LS", "72000", "72999", "Spedition Logsens"),
    PLZRule("DE", "Logsens Sued", "LS", "75000", "79999", "Spedition Logsens"),
    PLZRule("DE", "Logsens Sued", "LS", "80000", "89999", "Spedition Logsens"),

    # Logsens West - Spedition
    PLZRule("DE", "Logsens West", "LW", "33000", "33999", "Spedition Logsens"),
    PLZRule("DE", "Logsens West", "LW", "41000", "41999", "Spedition Logsens"),
    PLZRule("DE", "Logsens West", "LW", "42000", "48999", "Spedition Logsens"),
    PLZRule("DE", "Logsens West", "LW", "50000", "53999", "Spedition Logsens"),
    PLZRule("DE", "Logsens West", "LW", "57000", "57999", "Spedition Logsens"),
    PLZRule("DE", "Logsens West", "LW", "58000", "59999", "Spedition Logsens"),

    # Thurner DE - Spedition
    PLZRule("DE", "Thurner DE", "TH", "55000", "55999", "Spedition Thurner"),
    PLZRule("DE", "Thurner DE", "TH", "60000", "65999", "Spedition Thurner"),
    PLZRule("DE", "Thurner DE", "TH", "68000", "71999", "Spedition Thurner"),
    PLZRule("DE", "Thurner DE", "TH", "73000", "74999", "Spedition Thurner"),
    PLZRule("DE", "Thurner DE", "TH", "90000", "94999", "Spedition Thurner"),
    PLZRule("DE", "Thurner DE", "TH", "97000", "97999", "Spedition Thurner"),
]


# =============================================================================
# Schweiz (CH) - Speditionsversand
# =============================================================================

CH_SPEDITION_RULES = [
    # Post CH - Paketversand (fuer kleine Produkte)
    PLZRule("CH", "Post CH", "POST", "1000", "9658", "Postversand"),

    # Kuoni CH - Spedition fuer grosse Produkte
    PLZRule("CH", "Kuoni CH", "KUONI", "1000", "9658", "Spedition Kuoni"),
]


# =============================================================================
# Alle Regeln kombiniert
# =============================================================================

ALL_SPEDITION_RULES = AT_SPEDITION_RULES + DE_SPEDITION_RULES + CH_SPEDITION_RULES


def get_test_plz_for_rule(rule: PLZRule, position: str = "min") -> str:
    """
    Generiert eine Test-PLZ fuer eine Regel.

    Args:
        rule: Die PLZ-Regel
        position: "min" fuer minimale PLZ, "max" fuer maximale

    Returns:
        Test-PLZ als String
    """
    if position == "min":
        return rule.plz_min
    elif position == "max":
        return rule.plz_max
    else:
        # Mittlere PLZ berechnen
        min_val = int(rule.plz_min)
        max_val = int(rule.plz_max)
        mid_val = (min_val + max_val) // 2
        # PLZ-Format beibehalten (4 oder 5 Stellen)
        plz_len = len(rule.plz_min)
        return str(mid_val).zfill(plz_len)


def get_city_for_plz(country: str, plz: str) -> str:
    """
    Gibt einen Stadtnamen fuer eine PLZ zurueck.

    Verwendet bekannte Staedte wo moeglich, sonst generisch.
    """
    # Bekannte Staedte fuer Tests
    known_cities = {
        "AT": {
            "1010": "Wien",
            "1000": "Wien",
            "1199": "Wien",
            "1200": "Wien",
            "1399": "Wien",
            "2000": "Stockerau",
            "2999": "Bad Fischau",
            "3000": "St. Poelten",
            "3399": "Gaming",
            "3400": "Klosterneuburg",
            "3599": "Purkersdorf",
            "3600": "Tulln",
            "3699": "Krems",
            "3700": "Krems",
            "3999": "Gmüend",
            "4000": "Linz",
            "4020": "Linz",
            "4699": "Wels",
            "4700": "Schwanenstadt",
            "5020": "Salzburg",
            "5799": "Zell am See",
            "6000": "Innsbruck",
            "6020": "Innsbruck",
            "6999": "Bregenz",
            "7000": "Eisenstadt",
            "7999": "Oberwart",
            "8000": "Graz",
            "8010": "Graz",
            "9000": "Klagenfurt",
            "9020": "Klagenfurt",
            "9999": "Lienz",
        },
        "DE": {
            "00000": "Dresden",
            "01067": "Dresden",
            "09999": "Chemnitz",
            "10000": "Berlin",
            "10115": "Berlin",
            "15999": "Frankfurt/Oder",
            "16000": "Oranienburg",
            "18999": "Rostock",
            "19000": "Schwerin",
            "20095": "Hamburg",
            "29999": "Lueneburg",
            "30000": "Hannover",
            "30159": "Hannover",
            "32999": "Minden",
            "33000": "Paderborn",
            "33999": "Bielefeld",
            "34000": "Kassel",
            "37139": "Goettingen",
            "37140": "Northeim",
            "37199": "Duderstadt",
            "37200": "Hann. Muenden",
            "37399": "Osterode",
            "37400": "Herzberg",
            "39174": "Magdeburg",
            "39175": "Schoenebeck",
            "39319": "Burg",
            "39326": "Wolmirstedt",
            "39499": "Stendal",
            "39500": "Havelberg",
            "39699": "Salzwedel",
            "41000": "Moenchengladbach",
            "41999": "Viersen",
            "42000": "Wuppertal",
            "48999": "Muenster",
            "49000": "Osnabrueck",
            "49999": "Lingen",
            "50000": "Koeln",
            "50667": "Koeln",
            "53999": "Bonn",
            "54000": "Trier",
            "54999": "Bitburg",
            "55000": "Mainz",
            "55131": "Mainz",
            "55999": "Bad Kreuznach",
            "56000": "Koblenz",
            "56999": "Neuwied",
            "57000": "Siegen",
            "57999": "Olpe",
            "58000": "Hagen",
            "59999": "Arnsberg",
            "60000": "Frankfurt",
            "60311": "Frankfurt",
            "65999": "Wiesbaden",
            "66000": "Saarbruecken",
            "67999": "Kaiserslautern",
            "68000": "Mannheim",
            "71999": "Heidelberg",
            "72000": "Tuebingen",
            "72999": "Reutlingen",
            "73000": "Goeppingen",
            "74999": "Heilbronn",
            "75000": "Pforzheim",
            "79999": "Freiburg",
            "80000": "Muenchen",
            "80331": "Muenchen",
            "89999": "Augsburg",
            "90000": "Nuernberg",
            "90402": "Nuernberg",
            "94999": "Passau",
            "95000": "Hof",
            "96999": "Bayreuth",
            "97000": "Wuerzburg",
            "97999": "Schweinfurt",
            "98000": "Erfurt",
            "99999": "Nordhausen",
        },
        "CH": {
            "1000": "Lausanne",
            "3000": "Bern",
            "4000": "Basel",
            "6003": "Luzern",
            "8001": "Zuerich",
            "9000": "St. Gallen",
            "9658": "Wildhaus",
        },
    }

    # Exakte Uebereinstimmung
    if plz in known_cities.get(country, {}):
        return known_cities[country][plz]

    # Generischer Stadtname
    return f"Teststadt-{plz}"


def generate_test_cases() -> list[tuple]:
    """
    Generiert Testfaelle fuer pytest.mark.parametrize.

    Returns:
        Liste von Tupeln: (test_id, country, carrier, plz, city, expected_label)
    """
    test_cases = []

    for rule in ALL_SPEDITION_RULES:
        # Skip POST-Regeln (die gelten nur als Fallback)
        if rule.carrier_code == "POST":
            continue

        # Min-Test
        plz_min = get_test_plz_for_rule(rule, "min")
        city_min = get_city_for_plz(rule.country, plz_min)
        test_id_min = f"TC-SHIP-{rule.country}-{rule.carrier_code}-MIN-{plz_min}"
        test_cases.append((
            test_id_min,
            rule.country,
            rule.carrier,
            plz_min,
            city_min,
            rule.expected_label,
        ))

        # Max-Test (nur wenn unterschiedlich von Min)
        plz_max = get_test_plz_for_rule(rule, "max")
        if plz_max != plz_min:
            city_max = get_city_for_plz(rule.country, plz_max)
            test_id_max = f"TC-SHIP-{rule.country}-{rule.carrier_code}-MAX-{plz_max}"
            test_cases.append((
                test_id_max,
                rule.country,
                rule.carrier,
                plz_max,
                city_max,
                rule.expected_label,
            ))

    return test_cases


# Vorgenerierte Testfaelle fuer schnellen Import
SHIPPING_TEST_CASES = generate_test_cases()


if __name__ == "__main__":
    # Debug: Zeige alle generierten Testfaelle
    print(f"Generierte Testfaelle: {len(SHIPPING_TEST_CASES)}")
    print()
    print("=== Oesterreich (AT) ===")
    for tc in SHIPPING_TEST_CASES:
        if tc[1] == "AT":
            print(f"  {tc[0]}: PLZ {tc[3]} ({tc[4]}) -> {tc[5]}")
    print()
    print("=== Deutschland (DE) ===")
    for tc in SHIPPING_TEST_CASES:
        if tc[1] == "DE":
            print(f"  {tc[0]}: PLZ {tc[3]} ({tc[4]}) -> {tc[5]}")
    print()
    print("=== Schweiz (CH) ===")
    for tc in SHIPPING_TEST_CASES:
        if tc[1] == "CH":
            print(f"  {tc[0]}: PLZ {tc[3]} ({tc[4]}) -> {tc[5]}")
