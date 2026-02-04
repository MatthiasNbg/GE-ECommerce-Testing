#!/usr/bin/env python3
"""Generates shipping test contract JSON files from shipping rules."""
import json
import re
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright_tests.data.shipping_rules import SHIPPING_TEST_CASES

OUTPUT_DIR = Path(__file__).parent / "examples"


def sanitize_filename(test_id: str, country: str, carrier: str, plz: str, position: str) -> str:
    """Create a safe filename from test parameters."""
    # e.g. TC-SHIP-AT-FINK-MIN-1000 -> TC-SHIP-AT-FINK-MIN-1000_versand-at-fink-1000
    carrier_short = carrier.split()[0].lower()  # "Fink AT" -> "fink"
    return f"{test_id}_versand-{country.lower()}-{carrier_short}-{plz}"


def create_contract(test_id: str, country: str, carrier: str, plz: str, city: str, expected_label: str) -> dict:
    """Create a single shipping test contract."""
    # Determine position (MIN/MAX) from test_id
    is_min = "-MIN-" in test_id
    position = "Minimum" if is_min else "Maximum"

    # Channel mapping
    channels = [country]

    return {
        "test_id": test_id,
        "name": f"Versandart {carrier} fuer PLZ {plz} ({city}) - {position} Grenzwert",
        "category": "e2e",
        "priority": "P1",
        "schema_version": "1.0.0",
        "scope": {
            "channels": channels,
            "environments": ["staging"],
            "shop_system": "Shopware 6"
        },
        "preconditions": [
            "Shop ist erreichbar",
            "Speditionsprodukt (Polsterbett Almeno) ist verfuegbar und auf Lager",
            "Warenkorb ist leer"
        ],
        "steps": [
            {
                "step": 1,
                "action": "Speditionsprodukt zum Warenkorb hinzufuegen (Polsterbett Almeno, ge-p-693278)",
                "expected": "Produkt ist im Warenkorb",
                "selector_hint": "button.btn-buy"
            },
            {
                "step": 2,
                "action": "Zur Kasse navigieren",
                "expected": "Checkout-Seite wird geladen",
                "selector_hint": "a:has-text('Zur Kasse')"
            },
            {
                "step": 3,
                "action": "Gast-Checkout starten",
                "expected": "Gast-Checkout-Formular wird angezeigt",
                "selector_hint": "button:has-text('Als Gast bestellen')"
            },
            {
                "step": 4,
                "action": f"Adresse mit PLZ {plz} ({city}, {country}) eingeben",
                "expected": "Adressformular ist ausgefuellt",
                "selector_hint": "#billingAddressAddressZipcode"
            },
            {
                "step": 5,
                "action": "Datenschutz akzeptieren und zur Confirm-Seite navigieren",
                "expected": "Confirm-Seite wird geladen",
                "selector_hint": "#acceptedDataProtection"
            },
            {
                "step": 6,
                "action": "Angezeigte Versandart pruefen",
                "expected": f"'{expected_label}' wird als Versandart angezeigt oder ist in den verfuegbaren Versandarten enthalten",
                "selector_hint": "input[name='shippingMethodId']"
            }
        ],
        "test_data": {
            "product_path": "p/polsterbett-almeno/ge-p-693278",
            "country": country,
            "carrier": carrier,
            "plz": plz,
            "city": city,
            "expected_label": expected_label,
            "grenzwert": "minimum" if is_min else "maximum"
        },
        "automation": {
            "status": "automated",
            "framework": "Playwright + pytest",
            "repo": "GE-ECommerce-Testing",
            "spec_file": "playwright_tests/tests/test_shipping_plz.py",
            "function_name": "test_shipping_method_for_plz",
            "tags": ["shipping", "e2e", "spedition", country.lower(), carrier.split()[0].lower()]
        },
        "orchestration": {
            "parallel_safe": False,
            "timeout_seconds": 120,
            "retry_count": 1
        },
        "meta": {
            "author": "QA Team",
            "created": "2026-02-03",
            "last_modified": "2026-02-03",
            "version": "1.0"
        }
    }


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Remove old generic shipping contracts
    for old_file in ["TC-SHIP-001_versandart-plz.json", "TC-SHIP-002_versand-at-fink.json", "TC-SHIP-003_versand-de-logsens.json"]:
        old_path = OUTPUT_DIR / old_file
        if old_path.exists():
            old_path.unlink()
            print(f"Entfernt: {old_file}")

    created = 0
    for test_id, country, carrier, plz, city, expected_label in SHIPPING_TEST_CASES:
        contract = create_contract(test_id, country, carrier, plz, city, expected_label)

        carrier_short = carrier.split()[0].lower()
        filename = f"{test_id}_versand-{country.lower()}-{carrier_short}-{plz}.json"

        filepath = OUTPUT_DIR / filename
        filepath.write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        created += 1

    print(f"\n{created} Shipping-Contracts erstellt.")
    print(f"Verzeichnis: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
