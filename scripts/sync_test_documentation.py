#!/usr/bin/env python3
"""
Synchronisiert Test-Dokumentation aus test-inventory.yaml
Stellt sicher, dass alle Dokumente konsistent und aktuell sind.

Verwendung:
    python scripts/sync_test_documentation.py           # Generiert alle Dokumente
    python scripts/sync_test_documentation.py --check   # Nur Validierung
"""

import sys
from pathlib import Path
from datetime import datetime
import yaml
import argparse


def load_inventory(inventory_file: Path) -> dict:
    """Lädt das Test-Inventar."""
    if not inventory_file.exists():
        print(f"[FEHLER] Inventar nicht gefunden: {inventory_file}")
        sys.exit(1)

    with open(inventory_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def validate_inventory(inventory: dict) -> list[str]:
    """Validiert das Test-Inventar auf Konsistenz."""
    errors = []
    warnings = []

    # Prüfe Metadaten
    if 'metadata' not in inventory:
        errors.append("Fehlende 'metadata' Sektion")

    if 'categories' not in inventory:
        errors.append("Fehlende 'categories' Sektion")

    if 'tests' not in inventory:
        errors.append("Fehlende 'tests' Sektion")

    if errors:
        return errors

    # Zähle implementierte Tests
    implemented_count = sum(1 for test in inventory['tests'] if test.get('status') == 'implemented')
    declared_implemented = inventory['metadata'].get('implemented', 0)

    if implemented_count != declared_implemented:
        errors.append(
            f"Inkonsistenz: {implemented_count} Tests implementiert, "
            f"aber metadata.implemented sagt {declared_implemented}"
        )

    # Prüfe, ob Tests undefinierte Kategorien verwenden
    category_ids = {cat['id'] for cat in inventory['categories']}
    used_categories = {test['category'] for test in inventory['tests']}

    undefined = used_categories - category_ids
    if undefined:
        errors.append(f"Undefinierte Kategorien in Tests: {', '.join(undefined)}")

    # Warnung für ungenutzte Kategorien (kein Fehler, da Tests schrittweise hinzugefügt werden)
    unused = category_ids - used_categories
    if unused:
        warnings.append(f"Ungenutzte Kategorien (Tests noch nicht definiert): {', '.join(unused)}")

    # Prüfe Test-IDs auf Duplikate
    test_ids = [test['id'] for test in inventory['tests']]
    duplicates = [tid for tid in test_ids if test_ids.count(tid) > 1]
    if duplicates:
        errors.append(f"Doppelte Test-IDs: {', '.join(set(duplicates))}")

    # Prüfe Kategorie-Zählungen nur für Kategorien mit definierten Tests
    for category in inventory['categories']:
        cat_id = category['id']
        expected_count = category['count']
        actual_count = sum(1 for test in inventory['tests'] if test['category'] == cat_id)
        cat_status = category.get('status', 'missing')

        # Überspringe Prüfung wenn Kategorie als 'missing' markiert ist und keine Tests definiert
        if cat_status == 'missing' and actual_count == 0:
            continue

        # Umgang mit Bereichen (z.B. "15-20")
        if isinstance(expected_count, str) and '-' in expected_count:
            min_count, max_count = map(int, expected_count.split('-'))
            if actual_count > 0 and not (min_count <= actual_count <= max_count):
                warnings.append(
                    f"Kategorie '{cat_id}': {actual_count} Tests definiert, "
                    f"erwartet {expected_count} (wird später vervollständigt)"
                )
        elif isinstance(expected_count, int):
            if actual_count > 0 and actual_count != expected_count:
                warnings.append(
                    f"Kategorie '{cat_id}': {actual_count} Tests definiert, "
                    f"erwartet {expected_count} (wird später vervollständigt)"
                )

    # Gebe Warnungen aus, aber breche nicht ab
    if warnings:
        for warning in warnings:
            print(f"[WARNUNG] {warning}")

    return errors


def calculate_statistics(inventory: dict) -> dict:
    """Berechnet aktuelle Statistiken."""
    tests = inventory['tests']
    metadata = inventory.get('metadata', {})

    # Anzahl definierter Tests
    defined_count = len(tests)
    implemented = sum(1 for t in tests if t['status'] == 'implemented')
    missing_defined = sum(1 for t in tests if t['status'] == 'missing')
    partial = sum(1 for t in tests if t['status'] == 'partial')

    # Gesamtzahl geplanter Tests (aus Metadaten)
    total_tests_meta = metadata.get('total_tests', defined_count)

    # Behandle Bereiche wie "81-101"
    if isinstance(total_tests_meta, str) and '-' in total_tests_meta:
        min_tests, max_tests = map(int, total_tests_meta.split('-'))
        total_planned = (min_tests + max_tests) // 2  # Mittelwert
    elif isinstance(total_tests_meta, int):
        total_planned = total_tests_meta
    else:
        total_planned = defined_count

    # Coverage basiert auf geplanten Tests
    coverage = round(implemented / total_planned * 100) if total_planned > 0 else 0

    # Missing = geplante Tests - definierte Tests + definierte fehlende Tests
    missing_total = (total_planned - defined_count) + missing_defined

    return {
        'total': total_planned,  # Geplante Tests
        'defined': defined_count,  # Tatsächlich im YAML definierte Tests
        'implemented': implemented,
        'missing': missing_total,
        'partial': partial,
        'coverage': coverage
    }


def generate_markdown(inventory: dict, output_file: Path):
    """Generiert das Markdown-Dokument aus dem Inventar."""
    stats = calculate_statistics(inventory)
    metadata = inventory['metadata']
    categories = inventory['categories']
    tests = inventory['tests']

    # Gruppiere Tests nach Kategorie
    tests_by_category = {}
    for test in tests:
        cat_id = test['category']
        if cat_id not in tests_by_category:
            tests_by_category[cat_id] = []
        tests_by_category[cat_id].append(test)

    # Generiere Markdown
    md_lines = []

    # Header
    md_lines.append(f"# Test-Konzept: Grüne Erde E-Commerce Shop\n")
    md_lines.append(f"**Projekt:** {metadata['project']}")
    md_lines.append(f"**Datum:** {datetime.now().strftime('%Y-%m-%d')}")
    md_lines.append(f"**Version:** 1.0")
    md_lines.append(f"**Status:** Entwurf zur Abstimmung\n")
    md_lines.append("---\n")

    # Executive Summary
    md_lines.append("## Executive Summary\n")
    total_str = metadata.get('total_tests', 'unbekannt')
    md_lines.append(f"Dieses Dokument beschreibt die Teststrategie für den Grüne Erde Online-Shop mit **{total_str} Testfällen** in {len(categories)} Kategorien. ")
    md_lines.append(f"Der aktuelle Implementierungsstand liegt bei **~{stats['coverage']}%**.\n")

    # Status pro Kategorie (Quick Summary)
    smoke_cat = next((c for c in categories if c['id'] == 'smoke'), None)
    critical_cat = next((c for c in categories if c['id'] == 'critical_path'), None)

    md_lines.append("**Aktuelle Situation:**")
    if smoke_cat:
        status_icon = "✅" if smoke_cat['status'] == 'complete' else "⚠️" if smoke_cat['status'] == 'partial' else "❌"
        md_lines.append(f"- {status_icon} Basis-Tests (Smoke: {smoke_cat['implemented']}/{smoke_cat['count']}) implementiert")
    if critical_cat:
        status_icon = "✅" if critical_cat['status'] == 'complete' else "⚠️" if critical_cat['status'] == 'partial' else "❌"
        md_lines.append(f"- {status_icon} Critical Path ({critical_cat['implemented']}/{critical_cat['count']}) ")
        if critical_cat['status'] != 'complete':
            md_lines.append(f"({critical_cat['count'] - critical_cat['implemented']}/{critical_cat['count']} offen)")

    # Feature-Tests Summary
    feature_cats = [c for c in categories if c['id'] in ['cart', 'search', 'account', 'shipping', 'promotions']]
    total_feature_tests = sum(c.get('count', 0) for c in feature_cats)
    implemented_feature_tests = sum(c.get('implemented', 0) for c in feature_cats)
    if total_feature_tests > 0:
        status_icon = "❌" if implemented_feature_tests == 0 else "⚠️"
        md_lines.append(f"- {status_icon} Feature-Tests ({implemented_feature_tests}/{total_feature_tests} implementiert)\n")

    md_lines.append("**Prioritäten:**")
    md_lines.append("1. **Kritische Business-Flows** (Gast-Checkout, Zahlungsarten) → Phase 1")
    md_lines.append("2. **Feature-Abdeckung** (Warenkorb, Suche, Account) → Phase 2-4")
    md_lines.append("3. **Versandarten & Promotions** → Phase 5-6")
    md_lines.append("4. **Qualitätssicherung** (Regression, Load-Tests) → Phase 7-9\n")
    md_lines.append("---\n")

    # Funktionsbereiche Übersicht
    md_lines.append("## Thematische Übersicht der Testfälle\n")
    md_lines.append("**Schnellübersicht: Was wird wo getestet?**\n")
    md_lines.append("### Nach Funktionsbereichen\n")

    # Fortschrittsanzeige berechnen - zähle DEFINIERTE Tests (im YAML vorhanden)
    total_planned = sum(c.get('count', 0) if isinstance(c.get('count', 0), int) else int(c.get('count', '0').split('-')[0]) for c in categories)

    # Zähle tatsächlich im YAML definierte Tests pro Kategorie
    defined_by_cat = {}
    for test in tests:
        cat_id = test['category']
        defined_by_cat[cat_id] = defined_by_cat.get(cat_id, 0) + 1

    total_defined = sum(defined_by_cat.values())
    progress_percent = round(total_defined / total_planned * 100) if total_planned > 0 else 0

    md_lines.append(f"<!-- PROGRESS_BAR:{total_defined}:{total_planned}:{progress_percent} -->")
    md_lines.append("")
    md_lines.append("| Funktionsbereich | Tests | Status | Priorität | Was wird geprüft? |")
    md_lines.append("|------------------|-------|--------|-----------|-------------------|")

    for cat in categories:
        icon = cat.get('icon', '📋')
        name = cat.get('name', cat['id'])
        count = cat.get('count', 0)
        impl = cat.get('implemented', 0)
        status = cat.get('status', 'missing')
        priority = cat.get('priority', 'P2')
        desc = cat.get('description', '')

        # Status-Icon
        status_display = f"✅ {impl}/{count}" if status == 'complete' else f"⚠️ {impl}/{count}" if status == 'partial' else f"❌ {impl}/{count}"

        # Priorität-Icon
        prio_icon = "🔴" if priority == "P0" else "🟠" if priority == "P1" else "🟡"

        md_lines.append(f"| {icon} **{name}** | {count} | {status_display} | {prio_icon} {priority} | {desc} |")

    md_lines.append("\n**Legende:** ✅ Vollständig | ⚠️ Teilweise | ❌ Fehlend\n")
    md_lines.append("---\n")

    # Inhaltsverzeichnis
    md_lines.append("## Inhaltsverzeichnis\n")
    idx = 1
    md_lines.append(f"{idx}. [Testfall-Übersicht](#testfall-übersicht) - Alle Tests auf einen Blick")
    idx += 1
    md_lines.append(f"{idx}. [Test-Kategorien](#test-kategorien) - Was wird getestet?")
    idx += 1

    for cat in categories:
        cat_id = cat['id']
        cat_name = cat.get('name', cat_id)
        count = cat.get('count', 0)
        anchor = cat_id.replace('_', '-')
        md_lines.append(f"{idx}. [{cat_name}](#{anchor}) - ({count} Tests)")
        idx += 1

    md_lines.append(f"{idx}. [Implementierungs-Roadmap](#implementierungs-roadmap) - Welche Reihenfolge?")
    md_lines.append("\n---\n")

    # Testfall-Übersicht
    md_lines.append("## Testfall-Übersicht\n")
    md_lines.append("### Gesamtübersicht\n")
    md_lines.append(f"**Gesamt:** {stats['total']} Tests")
    md_lines.append(f"- ✅ Implementiert: {stats['implemented']}")
    md_lines.append(f"- ❌ Fehlend: {stats['missing']}")
    md_lines.append(f"- ⚠️ Teilweise: {stats['partial']}")
    md_lines.append(f"- **Abdeckung:** {stats['coverage']}%\n")
    md_lines.append("---\n")

    # Kategorien im Detail
    md_lines.append("## Test-Kategorien\n")

    for cat in categories:
        cat_id = cat['id']
        cat_name = cat.get('name', cat_id)
        icon = cat.get('icon', '📋')
        description = cat.get('description', '')
        count = cat.get('count', 0)
        impl = cat.get('implemented', 0)
        priority = cat.get('priority', 'P2')
        duration = cat.get('duration', 'Unbekannt')
        execution = cat.get('execution', '')

        md_lines.append(f"### {icon} {cat_name}\n")
        md_lines.append(f"**Priorität:** {priority}")
        md_lines.append(f"**Tests:** {impl}/{count} implementiert")
        md_lines.append(f"**Beschreibung:** {description}")
        if duration:
            md_lines.append(f"**Dauer:** {duration}")
        if execution:
            md_lines.append(f"**Ausführung:** {execution}")
        md_lines.append("")

        # Tests in dieser Kategorie
        cat_tests = tests_by_category.get(cat_id, [])
        if cat_tests:
            md_lines.append("| Test-ID | Name | Priorität | Status | Länder |")
            md_lines.append("|---------|------|-----------|--------|--------|")

            for test in cat_tests:
                test_id = test.get('id', '')
                name = test.get('name', '')
                priority = test.get('priority', 'P2')
                status = test.get('status', 'missing')
                countries = ', '.join(test.get('countries', []))

                status_icon = "✅" if status == 'implemented' else "⚠️" if status == 'partial' else "❌"

                md_lines.append(f"| {test_id} | {name} | {priority} | {status_icon} | {countries} |")

            md_lines.append("")

        md_lines.append("---\n")

    # Roadmap
    if 'phases' in inventory:
        md_lines.append("## Implementierungs-Roadmap\n")
        md_lines.append("| Phase | Name | Status | Tests | Abdeckung-Ziel |")
        md_lines.append("|-------|------|--------|-------|----------------|")

        for phase in inventory['phases']:
            phase_name = phase.get('name', '')
            status = phase.get('status', 'pending')
            tests_completed = phase.get('tests_completed', 0)
            tests_planned = phase.get('tests_planned', '-')
            coverage_target = phase.get('coverage_target', '-')

            status_icon = "✅" if status == 'complete' else "⏳"
            display_tests = f"{tests_completed}" if status == 'complete' else f"{tests_planned}"

            md_lines.append(f"| {phase.get('id', '')} | {phase_name} | {status_icon} | {display_tests} | {coverage_target}% |")

        md_lines.append("\n---\n")

    # Footer
    md_lines.append(f"\n*Generiert am {datetime.now().strftime('%Y-%m-%d %H:%M')} aus test-inventory.yaml*\n")

    # Schreibe Datei
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text('\n'.join(md_lines), encoding='utf-8')
    print(f"[OK] Markdown generiert: {output_file}")
    print(f"     {stats['total']} Tests, {stats['implemented']} implementiert, {stats['coverage']}% Abdeckung")


def generate_html(inventory: dict, output_file: Path):
    """Generiert HTML-Dokument aus dem Inventar."""
    # Generiere zuerst Markdown
    md_file = output_file.with_suffix('.md')
    if not md_file.exists():
        print(f"[INFO] Generiere zuerst Markdown...")
        generate_markdown(inventory, md_file)

    # Verwende das vorhandene HTML-Generator-Script
    html_gen_script = output_file.parent.parent / "scripts" / "generate_html_report.py"

    if html_gen_script.exists():
        print(f"[INFO] Verwende {html_gen_script.name} für HTML-Generierung")
        import subprocess
        result = subprocess.run(
            [sys.executable, str(html_gen_script)],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"[OK] HTML generiert: {output_file}")
        else:
            print(f"[WARNUNG] HTML-Generierung fehlgeschlagen: {result.stderr}")
    else:
        print(f"[WARNUNG] HTML-Generator nicht gefunden: {html_gen_script}")


def update_readme(inventory: dict, readme_file: Path):
    """Aktualisiert README.md mit aktuellen Statistiken."""
    stats = calculate_statistics(inventory)

    if not readme_file.exists():
        print(f"[WARNUNG] README nicht gefunden: {readme_file}")
        return

    content = readme_file.read_text(encoding='utf-8')

    # Suche Test-Status-Sektion und aktualisiere
    badge_pattern = r'!\[Tests\]\(https://img\.shields\.io/badge/Tests-\d+%2F\d+-[a-z]+\)'
    new_badge = f"![Tests](https://img.shields.io/badge/Tests-{stats['implemented']}%2F{stats['total']}-{'green' if stats['coverage'] >= 80 else 'yellow' if stats['coverage'] >= 40 else 'red'})"

    if badge_pattern in content:
        # Aktualisiere Badge
        import re
        content = re.sub(badge_pattern, new_badge, content)
        readme_file.write_text(content, encoding='utf-8')
        print(f"[OK] README.md aktualisiert: {stats['implemented']}/{stats['total']} Tests ({stats['coverage']}%)")


def main():
    parser = argparse.ArgumentParser(description='Synchronisiert Test-Dokumentation')
    parser.add_argument('--check', action='store_true', help='Nur Validierung, keine Generierung')
    parser.add_argument('--update-readme', action='store_true', help='Aktualisiere README.md')
    args = parser.parse_args()

    # Pfade
    project_root = Path(__file__).parent.parent
    inventory_file = project_root / "test-inventory.yaml"

    print("=" * 60)
    print("Test-Dokumentation Synchronisation")
    print("=" * 60)

    # Lade Inventar
    print(f"\n[1/4] Lade Inventar: {inventory_file}")
    inventory = load_inventory(inventory_file)
    print(f"      {len(inventory.get('tests', []))} Tests gefunden")

    # Validiere
    print(f"\n[2/4] Validiere Inventar...")
    errors = validate_inventory(inventory)

    if errors:
        print("[FEHLER] Validierung fehlgeschlagen:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    print("      Validierung erfolgreich")

    # Statistiken
    print(f"\n[3/4] Berechne Statistiken...")
    stats = calculate_statistics(inventory)
    print(f"      Total: {stats['total']}")
    print(f"      Implementiert: {stats['implemented']}")
    print(f"      Fehlend: {stats['missing']}")
    print(f"      Teilweise: {stats['partial']}")
    print(f"      Abdeckung: {stats['coverage']}%")

    if args.check:
        print("\n[OK] Validierung abgeschlossen (--check Modus)")
        return

    # Generiere Dokumente
    print(f"\n[4/4] Generiere Dokumente...")

    # Markdown
    md_file = project_root / "docs" / "test-concept.md"
    generate_markdown(inventory, md_file)

    # HTML
    html_file = project_root / "docs" / "test-concept.html"
    generate_html(inventory, html_file)

    # README aktualisieren
    if args.update_readme:
        readme_file = project_root / "README.md"
        update_readme(inventory, readme_file)

    print("\n" + "=" * 60)
    print("[OK] Synchronisation abgeschlossen")
    print("=" * 60)


if __name__ == "__main__":
    main()
