#!/usr/bin/env python3
"""
Migration script to update all schema examples to v2.2.0
Adds functional_area field based on test_id prefix
"""

import json
import os
from pathlib import Path

# Mapping from test_id prefix to functional_area
FUNCTIONAL_AREA_MAP = {
    "TC-SMOKE": "Feature Smoke",
    "TC-CART": "Feature Warenkorb",
    "TC-SEARCH": "Feature Suche",
    "TC-ACCOUNT": "Feature Account",
    "TC-CHECKOUT": "Feature Checkout",
    "TC-SHIP": "Feature Versandarten",
    "TC-PROMO": "Feature Promotion",
    "TC-PAY": "Feature Zahlung",
    "TC-DATA": "Feature Datenvalidierung",
    "TC-PERF": "Feature Performance",
    "TC-REG": "Feature Regression",
    "TC-CRITICAL": "Feature Critical Path",
}

def get_functional_area(test_id: str) -> str:
    """Determine functional_area based on test_id prefix."""
    for prefix, area in FUNCTIONAL_AREA_MAP.items():
        if test_id.startswith(prefix):
            return area
    # Default fallback
    return "Feature Sonstiges"

def migrate_file(filepath: Path) -> bool:
    """Migrate a single JSON file to v2.2.0."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Get test_id
        test_id = data.get("test_id", "")
        if not test_id:
            print(f"  SKIP: No test_id in {filepath.name}")
            return False

        # Update schema_version
        data["schema_version"] = "2.2.0"

        # Add functional_area based on test_id
        functional_area = get_functional_area(test_id)

        # Insert functional_area after priority (for consistent ordering)
        new_data = {}
        for key, value in data.items():
            new_data[key] = value
            if key == "priority":
                new_data["functional_area"] = functional_area

        # If priority wasn't found, just add it after schema_version
        if "functional_area" not in new_data:
            new_data = {}
            for key, value in data.items():
                new_data[key] = value
                if key == "schema_version":
                    new_data["functional_area"] = functional_area

        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=2, ensure_ascii=False)
            f.write('\n')

        return True
    except Exception as e:
        print(f"  ERROR: {filepath.name}: {e}")
        return False

def main():
    examples_dir = Path(__file__).parent / "examples"

    if not examples_dir.exists():
        print(f"Error: {examples_dir} does not exist")
        return

    json_files = sorted(examples_dir.glob("*.json"))

    print(f"Migrating {len(json_files)} files to schema v2.2.0...")
    print()

    success = 0
    failed = 0

    for filepath in json_files:
        if migrate_file(filepath):
            success += 1
            print(f"  OK: {filepath.name}")
        else:
            failed += 1

    print()
    print(f"Migration complete: {success} OK, {failed} failed")

if __name__ == "__main__":
    main()
