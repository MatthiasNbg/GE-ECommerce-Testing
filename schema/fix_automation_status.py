#!/usr/bin/env python3
"""
Fix automation.status in schema/examples JSON files.

Maps status from tests_basis.json to correct automation.status:
- "implemented" -> "automated"
- "defined" -> "planned"
- "missing" -> "manual"
"""

import json
from pathlib import Path

# Status mapping: test_id -> correct automation.status
# Based on tests_basis.json status field
STATUS_MAPPING = {
    # TC-SMOKE: all implemented -> automated (keep as-is)
    # TC-CRITICAL: mixed
    "TC-CRITICAL-001": "planned",  # status: defined
    "TC-CRITICAL-002": "planned",  # status: defined
    "TC-CRITICAL-003": "planned",  # status: defined
    "TC-CRITICAL-004": "planned",  # status: defined
    "TC-CRITICAL-005": "automated",  # status: implemented
    "TC-CRITICAL-006": "automated",  # status: implemented
    "TC-CRITICAL-007": "automated",  # status: implemented
    "TC-CRITICAL-008": "planned",  # status: defined
    # TC-CART: all implemented -> automated (keep as-is)
    # TC-SEARCH: all implemented -> automated (keep as-is)
    # TC-ACCOUNT: all implemented -> automated (keep as-is)
    # TC-REG: regression tests - planned
    "TC-REG-001": "planned",
    "TC-REG-002": "planned",
    "TC-REG-003": "planned",
    "TC-REG-004": "planned",
    "TC-REG-005": "planned",
    "TC-REG-006": "planned",
    "TC-REG-007": "planned",
    "TC-REG-008": "planned",
    "TC-REG-009": "planned",
    "TC-REG-010": "planned",
    "TC-REG-011": "planned",
    "TC-REG-012": "planned",
    "TC-REG-013": "planned",
    "TC-REG-014": "planned",
    "TC-REG-015": "planned",
    # TC-DATA: mostly missing/partial
    "TC-DATA-001": "automated",  # implemented
    "TC-DATA-002": "planned",
    "TC-DATA-003": "planned",
    "TC-DATA-004": "planned",
    "TC-DATA-005": "planned",
    "TC-DATA-006": "planned",
    "TC-DATA-007": "planned",
    "TC-DATA-008": "planned",
    "TC-DATA-009": "planned",
    "TC-DATA-010": "planned",
    # TC-PERF: partial
    "TC-PERF-001": "automated",  # implemented
    "TC-PERF-002": "automated",  # implemented
    "TC-PERF-003": "automated",  # implemented
    # TC-PROMO: all missing -> manual/planned
    "TC-PROMO-CART-PERCENT-001": "planned",
    "TC-PROMO-DISPLAY-001": "planned",
    "TC-PROMO-INVALID-001": "planned",
    "TC-PROMO-MBW-001": "planned",
    "TC-PROMO-MBW-002": "planned",
    "TC-PROMO-MOV-003": "planned",
    "TC-PROMO-PERSIST-001": "planned",
    "TC-PROMO-REMOVE-001": "planned",
    "TC-PROMO-SEC-005": "planned",
    "TC-PROMO-SHIP-001": "planned",
    "TC-PROMO-SHIP-003": "planned",
    # TC-CHECKOUT: planned/manual
    "TC-CHECKOUT-001": "planned",
    "TC-CHECKOUT-002": "planned",
    "TC-CHECKOUT-003": "planned",
    "TC-CHECKOUT-004": "planned",
    "TC-CHECKOUT-005": "planned",
    # TC-PAY: planned
    "TC-PAY-001": "planned",
    "TC-PAY-002": "planned",
}

def fix_file(filepath: Path) -> tuple[bool, str]:
    """Fix automation.status in a single JSON file.

    Returns (changed, status) tuple.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        test_id = data.get("test_id", "")
        if not test_id:
            return False, "no_test_id"

        # Check if we have a specific mapping for this test
        if test_id in STATUS_MAPPING:
            correct_status = STATUS_MAPPING[test_id]
            current_status = data.get("automation", {}).get("status", "")

            if current_status != correct_status:
                # Update the status
                if "automation" not in data:
                    data["automation"] = {}
                data["automation"]["status"] = correct_status

                # Write back
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                    f.write('\n')

                return True, f"{current_status} -> {correct_status}"
            else:
                return False, "already_correct"
        else:
            # No mapping - keep as-is (likely already correct)
            return False, "no_mapping"

    except Exception as e:
        return False, f"error: {e}"

def main():
    examples_dir = Path(__file__).parent / "examples"

    if not examples_dir.exists():
        print(f"Error: {examples_dir} does not exist")
        return

    json_files = sorted(examples_dir.glob("*.json"))

    print(f"Fixing automation.status in {len(json_files)} files...")
    print()

    changed = 0
    unchanged = 0

    for filepath in json_files:
        was_changed, status = fix_file(filepath)
        if was_changed:
            changed += 1
            print(f"  FIXED: {filepath.name} ({status})")
        else:
            unchanged += 1

    print()
    print(f"Done: {changed} fixed, {unchanged} unchanged")

if __name__ == "__main__":
    main()
