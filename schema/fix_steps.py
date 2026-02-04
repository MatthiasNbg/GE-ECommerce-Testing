#!/usr/bin/env python3
"""Fixes contracts where steps are strings instead of objects."""
import json
from pathlib import Path

EXAMPLES_DIR = Path(__file__).parent / "examples"


def fix_steps(contract: dict) -> bool:
    """Fix steps that are strings instead of objects. Returns True if fixed."""
    if "steps" not in contract:
        return False

    steps = contract["steps"]
    if not steps or isinstance(steps[0], dict):
        return False

    # Convert string steps to proper objects
    new_steps = []
    for i, step in enumerate(steps, 1):
        if isinstance(step, str):
            new_steps.append({
                "step": i,
                "action": step,
                "expected": "Schritt erfolgreich ausgefuehrt"
            })
        else:
            new_steps.append(step)

    contract["steps"] = new_steps
    return True


def main():
    fixed = 0
    for filepath in sorted(EXAMPLES_DIR.glob("*.json")):
        try:
            data = json.loads(filepath.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print(f"SKIP (JSON error): {filepath.name}")
            continue

        if fix_steps(data):
            filepath.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            fixed += 1
            print(f"FIXED: {filepath.name}")

    print(f"\n{fixed} Dateien repariert.")


if __name__ == "__main__":
    main()
