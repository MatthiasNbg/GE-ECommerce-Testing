#!/usr/bin/env python3
"""
Migration script: Testfall-JSON v1 → v2

Migrates all test JSON files to schema v2 format:
- Adds schema_version, author, last_modified
- Makes preconditions required (adds defaults if missing)
- Distributes expected_behavior into step-level expected fields
- Generates postconditions from last expected_behavior entries
- Generates cleanup based on category
- Adds automation mapping based on test_id prefix
- Restructures test_data with product_ref
- Removes expected_behavior field
"""

import json
import os
import sys
from pathlib import Path

SCHEMA_VERSION = "2.0"
AUTHOR = "claude"
LAST_MODIFIED = "2026-02-03"

# Mapping: test_id prefix → playwright test file
PLAYWRIGHT_MAPPING = {
    "TC-SMOKE": "playwright_tests/tests/test_smoke.py",
    "TC-CRITICAL": "playwright_tests/tests/test_critical_path.py",
    "TC-CART": "playwright_tests/tests/test_cart.py",
    "TC-SEARCH": "playwright_tests/tests/test_search.py",
    "TC-ACCOUNT": "playwright_tests/tests/test_account.py",
    "TC-SHIP": "playwright_tests/tests/test_shipping_plz.py",
    "TC-DATA": "playwright_tests/tests/test_data_validation.py",
    "TC-PERF": "playwright_tests/tests/test_performance.py",
    "TC-PROMO": "playwright_tests/tests/test_promotions.py",
}

# Default preconditions by category
DEFAULT_PRECONDITIONS = {
    "smoke": ["Shop ist erreichbar"],
    "critical-path": ["Shop ist erreichbar"],
    "warenkorb": ["Shop ist erreichbar", "Warenkorb ist leer"],
    "suche": ["Shop ist erreichbar"],
    "account": ["Shop ist erreichbar"],
    "versandarten": ["Shop ist erreichbar"],
    "warenkorb-promotions": ["Shop ist erreichbar", "Warenkorb ist leer"],
    "gutschein-sicherheit": ["Shop ist erreichbar", "Warenkorb ist leer"],
    "gutschein-checkout-flows": ["Shop ist erreichbar", "Warenkorb ist leer"],
    "versandkostenfrei": ["Shop ist erreichbar"],
    "produktkategorien": ["Shop ist erreichbar"],
    "mindestbestellwert": ["Shop ist erreichbar", "Warenkorb ist leer"],
    "mengenrabatt": ["Shop ist erreichbar", "Warenkorb ist leer"],
    "aktionspreis": ["Shop ist erreichbar"],
    "mitarbeiterrabatt": ["Shop ist erreichbar"],
    "bundle": ["Shop ist erreichbar", "Warenkorb ist leer"],
    "promo-kombinationen": ["Shop ist erreichbar", "Warenkorb ist leer"],
    "data-validation": ["Shop ist erreichbar"],
    "performance": ["Shop ist erreichbar"],
}

# Cleanup actions by category
CLEANUP_BY_CATEGORY = {
    "warenkorb": ["Warenkorb leeren"],
    "critical-path": ["Warenkorb leeren"],
    "warenkorb-promotions": ["Warenkorb leeren", "Promotion-Code entfernen"],
    "gutschein-sicherheit": ["Warenkorb leeren", "Gutschein-Code entfernen"],
    "gutschein-checkout-flows": ["Warenkorb leeren", "Gutschein-Code entfernen"],
    "versandkostenfrei": ["Warenkorb leeren", "Promotion-Code entfernen"],
    "produktkategorien": ["Warenkorb leeren"],
    "mindestbestellwert": ["Warenkorb leeren", "Promotion-Code entfernen"],
    "mengenrabatt": ["Warenkorb leeren"],
    "aktionspreis": ["Warenkorb leeren"],
    "mitarbeiterrabatt": ["Warenkorb leeren"],
    "bundle": ["Warenkorb leeren"],
    "promo-kombinationen": ["Warenkorb leeren", "Alle Promotion-Codes entfernen"],
    "versandarten": ["Warenkorb leeren"],
}

# Product type reference mapping
PRODUCT_REF_MAP = {
    "639046": "nicht_rabattierbarer_artikel",
    "sale-product": "sale_product",
    "regular-product": "regular_product",
}


def get_playwright_path(test_id: str, status: str) -> str | None:
    """Map test_id to playwright test file path, only if implemented."""
    if status not in ("implemented", "passing", "failing"):
        return None
    for prefix, path in PLAYWRIGHT_MAPPING.items():
        if test_id.startswith(prefix):
            return path
    return None


def distribute_expected_behavior(test: dict) -> None:
    """Distribute expected_behavior entries into step-level expected fields."""
    expected_behaviors = test.get("expected_behavior", [])
    steps = test.get("steps", [])

    if not expected_behaviors or not steps:
        return

    # Find steps that are missing 'expected'
    missing_indices = [i for i, s in enumerate(steps) if "expected" not in s or not s["expected"]]

    if not missing_indices:
        # All steps already have expected - nothing to distribute
        return

    # Distribute expected_behavior entries to missing steps
    # Strategy: assign to LAST N missing steps (verification steps are at the end)
    # and use action-derived expected for earlier steps
    n_behaviors = len(expected_behaviors)
    n_missing = len(missing_indices)

    if n_behaviors >= n_missing:
        # More behaviors than missing slots: assign last N behaviors to missing steps
        for i, idx in enumerate(missing_indices):
            steps[idx]["expected"] = expected_behaviors[i]
    else:
        # Fewer behaviors than missing slots: assign behaviors to last missing steps
        # Earlier missing steps get action-derived expected
        start = n_missing - n_behaviors
        for i, idx in enumerate(missing_indices):
            if i >= start:
                steps[idx]["expected"] = expected_behaviors[i - start]

    # Generate contextual expected for any remaining steps without expected
    for step in steps:
        if "expected" not in step or not step.get("expected"):
            action = step.get("action", "").lower()
            if "warenkorb" in action or "hinzuf" in action:
                step["expected"] = "Produkt ist im Warenkorb"
            elif "kasse" in action or "checkout" in action or "navigieren" in action:
                step["expected"] = "Seite wird korrekt geladen"
            elif "plz" in action or "adresse" in action or "eingeben" in action:
                step["expected"] = "Eingabe wird akzeptiert"
            elif "pruefen" in action or "validieren" in action or "check" in action:
                step["expected"] = "Anzeige ist korrekt"
            elif "code" in action or "promotion" in action or "gutschein" in action:
                step["expected"] = "Code wird verarbeitet"
            else:
                step["expected"] = "Aktion erfolgreich ausgefuehrt"


def generate_postconditions(test: dict) -> list[str]:
    """Generate postconditions from the last expected_behavior entries."""
    expected_behaviors = test.get("expected_behavior", [])
    if not expected_behaviors:
        return []

    # Use the last 1-2 expected_behavior entries as postconditions
    # These typically describe the final state
    postconditions = []
    for eb in expected_behaviors:
        # Filter for state-describing entries (not action descriptions)
        lower = eb.lower()
        if any(kw in lower for kw in [
            "wird angezeigt", "ist sichtbar", "werden angezeigt", "enthält",
            "zeigt", "bleibt", "ist korrekt", "sind korrekt", "funktioniert",
            "wird geladen", "ist erreichbar", "kann", "keine fehler",
            "wird akzeptiert", "wird abgelehnt", "wird gespeichert",
            "wird entfernt", "aktualisiert", "wurde"
        ]):
            postconditions.append(eb)

    # Limit to last 3 most relevant
    return postconditions[-3:] if len(postconditions) > 3 else postconditions


def migrate_test_data(test: dict) -> dict | None:
    """Restructure test_data with product_ref references."""
    test_data = test.get("test_data")
    if not test_data:
        return None

    new_data = {}

    # Handle products - add ref field, keep structure
    products = test_data.get("products", [])
    if products:
        new_products = []
        for p in products:
            new_p = dict(p)
            pid = p.get("id", "")
            if pid in PRODUCT_REF_MAP:
                new_p["ref"] = PRODUCT_REF_MAP[pid]
            elif pid:
                # Generate a ref from the id
                ptype = p.get("type", "product")
                new_p["ref"] = f"{ptype}_{pid}"
            new_products.append(new_p)
        new_data["products"] = new_products
    elif not any(k in test_data for k in ["plz", "carrier", "carrier_code"]):
        # For simple tests without products array, add product_ref
        category = test.get("category", "")
        if category in ("smoke", "critical-path", "warenkorb"):
            new_data["product_ref"] = "simple_product_post"

    # Copy other test_data fields (promo_codes, amounts, plz data, etc.)
    for key in test_data:
        if key == "products" and "products" in new_data:
            continue
        if key not in new_data:
            new_data[key] = test_data[key]

    return new_data if new_data else None


def ensure_preconditions(test: dict) -> list[str]:
    """Ensure preconditions exist, merging defaults with existing ones."""
    existing = test.get("preconditions", [])
    category = test.get("category", "")
    defaults = DEFAULT_PRECONDITIONS.get(category, ["Shop ist erreichbar"])

    # Merge: defaults first, then existing (dedup)
    merged = list(defaults)
    for pc in existing:
        if pc not in merged:
            merged.append(pc)

    return merged


def migrate_test(test: dict) -> dict:
    """Migrate a single test from v1 to v2 format."""
    # Start with new required fields
    migrated = {
        "schema_version": SCHEMA_VERSION,
        "test_id": test["test_id"],
        "name": test["name"],
        "category": test["category"],
        "priority": test["priority"],
        "status": test.get("status", "defined"),
        "channels": test["channels"],
        "author": AUTHOR,
        "last_modified": LAST_MODIFIED,
        "description": test["description"],
    }

    # Preconditions (now required)
    migrated["preconditions"] = ensure_preconditions(test)

    # Promo config (keep if exists)
    if "promo_config" in test:
        migrated["promo_config"] = test["promo_config"]

    # Test data (restructured)
    new_test_data = migrate_test_data(test)
    if new_test_data:
        migrated["test_data"] = new_test_data

    # Steps - distribute expected_behavior to steps missing expected
    steps = [dict(s) for s in test.get("steps", [])]
    migrated["steps"] = steps

    # Distribute expected_behavior into steps before removing it
    temp = dict(test)
    temp["steps"] = steps
    distribute_expected_behavior(temp)
    migrated["steps"] = temp["steps"]

    # Ensure every step has expected
    for step in migrated["steps"]:
        if "expected" not in step or not step.get("expected"):
            step["expected"] = "Erwartetes Ergebnis wird korrekt angezeigt"

    # Postconditions (generated from expected_behavior)
    postconditions = generate_postconditions(test)
    if postconditions:
        migrated["postconditions"] = postconditions

    # Cleanup (based on category)
    category = test.get("category", "")
    cleanup = CLEANUP_BY_CATEGORY.get(category, [])
    if cleanup:
        migrated["cleanup"] = list(cleanup)

    # Automation mapping
    playwright_path = get_playwright_path(test["test_id"], migrated["status"])
    migrated["automation"] = {
        "playwright": playwright_path,
        "cypress": None,
        "manual": True,
    }

    # References (keep if exists)
    if "references" in test:
        migrated["references"] = test["references"]
    else:
        migrated["references"] = []

    # Tags (keep)
    migrated["tags"] = test.get("tags", [])

    return migrated


def migrate_file(filepath: str) -> list[dict]:
    """Migrate all tests in a JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        tests = json.load(f)

    return [migrate_test(t) for t in tests]


def save_file(filepath: str, tests: list[dict]) -> None:
    """Save migrated tests to JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(tests, f, indent=2, ensure_ascii=False)
        f.write("\n")


def validate_against_schema(tests: list[dict], schema: dict) -> list[str]:
    """Basic validation of migrated tests against schema v2."""
    errors = []
    required_fields = schema.get("required", [])

    for test in tests:
        tid = test.get("test_id", "UNKNOWN")

        # Check required fields
        for field in required_fields:
            if field not in test:
                errors.append(f"{tid}: missing required field '{field}'")

        # Check schema_version
        if test.get("schema_version") != "2.0":
            errors.append(f"{tid}: schema_version is not '2.0'")

        # Check all steps have expected
        for step in test.get("steps", []):
            if "expected" not in step:
                errors.append(f"{tid}: step {step.get('step', '?')} missing 'expected'")

        # Check expected_behavior is removed
        if "expected_behavior" in test:
            errors.append(f"{tid}: still has 'expected_behavior' field")

        # Check preconditions is present and non-empty
        if not test.get("preconditions"):
            errors.append(f"{tid}: preconditions is empty or missing")

    return errors


def main():
    base_dir = Path(__file__).parent

    # Source files (individual category files)
    source_files = [
        "tests_basis.json",
        "tests_versandarten.json",
        "tests_data_performance.json",
        "promotion_tests_warenkorb.json",
        "promotion_tests_sicherheit_checkout.json",
        "promotion_tests_versandkostenfrei.json",
        "promotion_tests_weitere.json",
    ]

    # Load schema for validation
    schema_path = base_dir / "testcase_schema.json"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    all_migrated = []
    all_errors = []
    test_ids_seen = set()

    print("=" * 60)
    print("Migration v1 -> v2: Starting...")
    print("=" * 60)

    # Migrate individual files
    for filename in source_files:
        filepath = base_dir / filename
        if not filepath.exists():
            print(f"  SKIP {filename} (not found)")
            continue

        tests = migrate_file(str(filepath))
        errors = validate_against_schema(tests, schema)
        all_errors.extend(errors)

        # Check for duplicates
        for t in tests:
            tid = t["test_id"]
            if tid in test_ids_seen:
                all_errors.append(f"DUPLICATE: {tid} in {filename}")
            test_ids_seen.add(tid)

        save_file(str(filepath), tests)
        all_migrated.extend(tests)
        print(f"  OK {filename}: {len(tests)} tests migrated")

    # Build promotion_tests.json (combined promos)
    promo_files = [
        "promotion_tests_warenkorb.json",
        "promotion_tests_sicherheit_checkout.json",
        "promotion_tests_versandkostenfrei.json",
        "promotion_tests_weitere.json",
    ]
    promo_combined = []
    for pf in promo_files:
        ppath = base_dir / pf
        if ppath.exists():
            with open(ppath, "r", encoding="utf-8") as f:
                promo_combined.extend(json.load(f))

    save_file(str(base_dir / "promotion_tests.json"), promo_combined)
    print(f"  OK promotion_tests.json: {len(promo_combined)} tests (combined)")

    # Build all_tests.json (everything)
    # all_migrated already has basis + versandarten + data_performance
    # promo_combined has all promo tests
    # But all_migrated already includes promo tests from individual files
    save_file(str(base_dir / "all_tests.json"), all_migrated)
    print(f"  OK all_tests.json: {len(all_migrated)} tests (total)")

    # Summary
    print()
    print("=" * 60)
    print(f"Total tests migrated: {len(all_migrated)}")
    print(f"Unique test IDs: {len(test_ids_seen)}")
    print(f"Validation errors: {len(all_errors)}")

    if all_errors:
        print()
        print("ERRORS:")
        for e in all_errors[:20]:
            print(f"  - {e}")
        if len(all_errors) > 20:
            print(f"  ... and {len(all_errors) - 20} more")

    # Verify counts
    expected_counts = {
        "tests_basis.json": 38,
        "tests_versandarten.json": 98,
        "tests_data_performance.json": 18,
        "promotion_tests_warenkorb.json": 5,
        "promotion_tests_sicherheit_checkout.json": 9,
        "promotion_tests_versandkostenfrei.json": 6,
        "promotion_tests_weitere.json": 20,
    }

    print()
    print("Count verification:")
    for fn, expected in expected_counts.items():
        fp = base_dir / fn
        with open(fp, "r", encoding="utf-8") as f:
            actual = len(json.load(f))
        status = "OK" if actual == expected else "MISMATCH"
        print(f"  {status} {fn}: {actual} (expected {expected})")

    total = len(all_migrated)
    print(f"  {'OK' if total == 194 else 'MISMATCH'} all_tests.json: {total} (expected 194)")

    print("=" * 60)

    if all_errors:
        print("Migration completed WITH ERRORS")
        return 1
    else:
        print("Migration completed successfully!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
