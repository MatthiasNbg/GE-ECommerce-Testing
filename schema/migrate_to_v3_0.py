#!/usr/bin/env python3
"""
Migration script to update all schema examples from v2.2.0 to v3.0.0.
Moves scope.channels into test_data as {"type": "channel", "name": "XX"} entries.
"""

import json
from pathlib import Path


def migrate_file(filepath: Path) -> bool:
    """Migrate a single JSON file to v3.0.0."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        test_id = data.get("test_id", "")
        if not test_id:
            print(f"  SKIP: No test_id in {filepath.name}")
            return False

        # Extract channels from scope
        channels = data.get("scope", {}).get("channels", [])
        if not channels:
            print(f"  SKIP: No scope.channels in {filepath.name}")
            return False

        # Update schema_version
        data["schema_version"] = "3.0.0"

        # Remove channels from scope
        if "scope" in data and "channels" in data["scope"]:
            del data["scope"]["channels"]

        # If scope is now empty or only has no meaningful keys, keep it with remaining props
        # (environments, shop_system may still be there)

        # Ensure test_data is an array
        test_data = data.get("test_data", [])
        if not isinstance(test_data, list):
            # Convert old object format to array if needed
            test_data = []

        # Add channel entries at the beginning of test_data
        channel_entries = [{"type": "channel", "name": ch} for ch in channels]
        data["test_data"] = channel_entries + test_data

        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
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

    print(f"Migrating {len(json_files)} files to schema v3.0.0...")
    print(f"  Moving scope.channels -> test_data channel entries")
    print()

    success = 0
    skipped = 0

    for filepath in json_files:
        if migrate_file(filepath):
            success += 1
            print(f"  OK: {filepath.name}")
        else:
            skipped += 1

    print()
    print(f"Migration complete: {success} migrated, {skipped} skipped")


if __name__ == "__main__":
    main()
