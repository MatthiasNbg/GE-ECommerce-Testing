#!/usr/bin/env python3
"""Validiert Test-Contract-JSON-Dateien gegen das zentrale Schema (per HTTP)."""
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

try:
    from jsonschema import Draft202012Validator, ValidationError
except ImportError:
    print("FEHLER: jsonschema nicht installiert. Bitte ausführen:")
    print("  pip install 'jsonschema[format]>=4.20.0'")
    sys.exit(2)

SCHEMA_URL = "https://www.matthias-sax.de/TestHubPro911/test-contract.schema.json"
CACHE_DIR = Path(__file__).parent / ".cache"
CACHE_FILE = CACHE_DIR / "test-contract.schema.json"


def fetch_schema() -> dict:
    """Schema per HTTP holen, lokal cachen. Bei Offline-Modus Cache verwenden."""
    CACHE_DIR.mkdir(exist_ok=True)

    try:
        with urllib.request.urlopen(SCHEMA_URL, timeout=10) as resp:
            data = resp.read().decode("utf-8")
        schema = json.loads(data)
        CACHE_FILE.write_text(data, encoding="utf-8")
        print(f"Schema geladen von {SCHEMA_URL}")
        return schema
    except (urllib.error.URLError, OSError, TimeoutError) as e:
        if CACHE_FILE.exists():
            print(f"WARNUNG: Schema-URL nicht erreichbar ({e}), verwende Cache.")
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        print(f"FEHLER: Schema nicht erreichbar und kein Cache vorhanden: {e}")
        sys.exit(2)


def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def validate_file(schema: dict, file_path: Path) -> list[str]:
    """Validiert eine einzelne JSON-Datei. Gibt Liste von Fehlern zurück."""
    try:
        instance = load_json(file_path)
    except json.JSONDecodeError as e:
        return [f"JSON-Parse-Fehler: {e}"]

    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
    return [
        f"  - {'.'.join(str(p) for p in err.absolute_path) or '(root)'}: {err.message}"
        for err in errors
    ]


def main():
    if len(sys.argv) < 2:
        print(f"Verwendung: {sys.argv[0]} <datei_oder_verzeichnis> [...]")
        sys.exit(2)

    schema = fetch_schema()
    Draft202012Validator.check_schema(schema)

    targets: list[Path] = []
    for arg in sys.argv[1:]:
        p = Path(arg)
        if p.is_dir():
            targets.extend(sorted(p.glob("*.json")))
        elif p.is_file():
            targets.append(p)
        else:
            print(f"WARNUNG: '{arg}' nicht gefunden, übersprungen.")

    if not targets:
        print("Keine JSON-Dateien gefunden.")
        sys.exit(2)

    total = 0
    failed = 0

    for file_path in targets:
        total += 1
        errors = validate_file(schema, file_path)
        if errors:
            failed += 1
            print(f"FEHLER  {file_path.name}")
            for e in errors:
                print(e)
        else:
            print(f"OK      {file_path.name}")

    print(f"\n{total} Dateien geprüft, {total - failed} OK, {failed} fehlerhaft.")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
