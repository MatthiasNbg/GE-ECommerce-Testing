# Wartungs-Anleitung: Test-Dokumentation

Diese Anleitung beschreibt, wie die Test-Dokumentation aktuell gehalten wird.

---

## 🎯 Überblick: Das System

### Single Source of Truth

**`test-inventory.yaml`** ist die **einzige** Quelle für:
- Alle Testfälle und deren Status
- Kategorien und Prioritäten
- Statistiken und Coverage
- Phasen-Planung

**Alle anderen Dokumente werden daraus generiert:**
- `docs/test-concept.md` (Markdown)
- `docs/test-concept.html` (HTML)
- `README.md` (Test-Status Badge)

### Warum dieser Ansatz?

✅ **Konsistenz garantiert** - Eine Änderung aktualisiert alle Dokumente
✅ **Struktur bleibt erhalten** - Template-basierte Generierung
✅ **Automatisiert** - CI/CD, Git Hooks, Scripts
✅ **Validierung** - Fehler werden sofort erkannt
✅ **Wartbar** - Einfache YAML-Struktur statt komplexem Markdown

---

## 📝 Workflow: Neuen Test hinzufügen

### Schritt 1: Test implementieren

```bash
# Neuen Test schreiben
vim playwright_tests/tests/test_warenkorb.py
```

### Schritt 2: In test-inventory.yaml eintragen

```yaml
# test-inventory.yaml
tests:
  - id: TC-CART-001
    name: "Produkt hinzufügen"
    category: cart
    priority: P1
    status: implemented              # ← Status auf 'implemented' setzen
    countries: [AT, DE, CH]
    file: "playwright_tests/tests/test_warenkorb.py"
    markers: ["feature", "cart"]
```

### Schritt 3: Metadaten aktualisieren

```yaml
# test-inventory.yaml - ganz oben
metadata:
  project: GE-ECommerce-Testing
  total_tests: 81-101
  implemented: 9                     # ← Von 8 auf 9 erhöhen
  coverage_percent: 11               # ← Wird automatisch berechnet, aber zur Sicherheit
```

### Schritt 4: Kategorie-Zählung aktualisieren

```yaml
# test-inventory.yaml
categories:
  - id: cart
    name: Feature Tests - Warenkorb
    count: 8
    implemented: 1                   # ← Von 0 auf 1 erhöhen
    status: partial                  # ← Von 'missing' auf 'partial'
```

### Schritt 5: Dokumentation neu generieren

```bash
# Validieren und generieren
python scripts/sync_test_documentation.py

# Mit README.md Update
python scripts/sync_test_documentation.py --update-readme
```

### Schritt 6: Committen

```bash
git add test-inventory.yaml
git add playwright_tests/tests/test_warenkorb.py
git add docs/test-concept.md docs/test-concept.html
git commit -m "feat: Add TC-CART-001 - Produkt hinzufügen"

# Pre-commit Hook validiert automatisch!
```

---

## 🔄 Automatisierung

### Git Hooks (Lokal)

**Installation:**
```bash
# Einmalig aktivieren
git config core.hooksPath .githooks
```

**Was passiert:**
- ✅ Bei Commit: Validierung von `test-inventory.yaml`
- ✅ YAML-Syntax-Check
- ✅ Konsistenz-Check (Zählungen, IDs, etc.)
- ❌ Commit wird abgelehnt bei Fehlern

### CI/CD Integration

**GitHub Actions / GitLab CI Beispiel:**

```yaml
# .github/workflows/test-docs.yml
name: Test Documentation

on:
  push:
    paths:
      - 'test-inventory.yaml'
      - 'playwright_tests/tests/**'

jobs:
  validate-and-update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install pyyaml

      - name: Validate test inventory
        run: python scripts/sync_test_documentation.py --check

      - name: Generate documentation
        run: python scripts/sync_test_documentation.py --update-readme

      - name: Commit updated docs
        uses: stefanzweifel/git-auto-commit-action@v4
        with:
          commit_message: "docs: Auto-update test documentation"
          file_pattern: docs/*.md docs/*.html README.md
```

### Wöchentliche Synchronisation

**Cron Job / Scheduled Task:**

```bash
# Linux/Mac: crontab -e
0 9 * * 1 cd /path/to/project && python scripts/sync_test_documentation.py --update-readme

# Windows: Task Scheduler
# Trigger: Weekly, Monday, 9:00 AM
# Action: python C:\Projekte\GE-ECommerce-Testing\scripts\sync_test_documentation.py --update-readme
```

---

## 🔍 Validierung durchführen

### Nur Validieren (ohne Generierung)

```bash
python scripts/sync_test_documentation.py --check
```

**Prüft:**
- ✅ YAML-Syntax korrekt?
- ✅ Alle Test-IDs eindeutig?
- ✅ Kategorien konsistent?
- ✅ Zählungen stimmen überein?
- ✅ Alle Kategorien verwendet?
- ✅ Metadaten aktuell?

### Fehlerbehandlung

**Typische Fehler und Lösungen:**

| Fehler | Ursache | Lösung |
|--------|---------|--------|
| "Inkonsistenz: 9 Tests implementiert, aber metadata.implemented sagt 8" | `metadata.implemented` nicht aktualisiert | `metadata.implemented: 9` setzen |
| "Kategorie 'cart': 1 Tests definiert, erwartet 8" | Test vergessen einzutragen | Alle 8 Tests in `tests:` Sektion eintragen |
| "Doppelte Test-IDs: TC-CART-001" | Test-ID bereits verwendet | Eindeutige ID vergeben |
| "Undefinierte Kategorien in Tests: xyz" | Tippfehler in `category` | Kategorie-ID korrigieren |

---

## 📊 Status-Tracking

### Test-Status-Werte

| Status | Bedeutung | Wann verwenden? |
|--------|-----------|-----------------|
| `implemented` | Test vollständig implementiert und läuft | Test existiert in Code und funktioniert |
| `missing` | Test noch nicht geschrieben | Test geplant, aber noch nicht erstellt |
| `partial` | Test teilweise vorhanden | Test existiert, aber unvollständig/disabled |
| `deprecated` | Test veraltet, wird entfernt | Test nicht mehr relevant |

### Kategorie-Status

| Status | Bedeutung |
|--------|-----------|
| `complete` | Alle Tests implementiert |
| `partial` | Einige Tests implementiert |
| `missing` | Keine Tests implementiert |

---

## 🎨 Template: Neuer Test

```yaml
# Kopieren und anpassen
  - id: TC-XXX-###                   # Format: TC-<KATEGORIE>-<NUMMER>
    name: "Testfall-Name"            # Kurz und prägnant
    category: category_id             # Muss in categories existieren
    priority: P0|P1|P2                # P0=Kritisch, P1=Hoch, P2=Mittel
    status: missing                   # missing → implemented
    countries: [AT, DE, CH]           # Welche Länder?
    file: "path/to/test_file.py"     # Relativer Pfad oder null
    markers: ["marker1", "marker2"]   # pytest markers
    description: "Optional: Details"  # Nur bei komplexen Tests
```

---

## 🚨 Probleme & Troubleshooting

### "Dokumentation ist veraltet"

**Problem:** Markdown/HTML zeigt alte Zahlen

**Lösung:**
```bash
python scripts/sync_test_documentation.py
```

### "Pre-commit Hook schlägt fehl"

**Problem:** Git lehnt Commit ab

**Lösung:**
```bash
# Fehler anzeigen
python scripts/sync_test_documentation.py --check

# Beheben, dann erneut committen
git commit
```

### "Ich habe vergessen, test-inventory.yaml zu aktualisieren"

**Lösung:**
```bash
# Nachträglich aktualisieren
vim test-inventory.yaml

# Dokumente neu generieren
python scripts/sync_test_documentation.py

# Nachträglicher Commit
git add test-inventory.yaml docs/
git commit -m "docs: Update test inventory"
```

---

## 📋 Checkliste: Test hinzufügen

- [ ] Test implementiert in `playwright_tests/tests/`
- [ ] Test-Eintrag in `test-inventory.yaml` erstellt
- [ ] `metadata.implemented` erhöht
- [ ] `category.implemented` erhöht
- [ ] `category.status` aktualisiert (missing → partial → complete)
- [ ] Validierung durchgeführt: `python scripts/sync_test_documentation.py --check`
- [ ] Dokumentation generiert: `python scripts/sync_test_documentation.py`
- [ ] Alle Dateien committet (inventory + docs + test-code)

---

## 🔮 Best Practices

### DO ✅

- ✅ **Immer** `test-inventory.yaml` aktualisieren, wenn Tests hinzugefügt werden
- ✅ **Vor jedem Commit** Validierung durchführen
- ✅ **Wöchentlich** Dokumentation synchronisieren
- ✅ **Bei Phase-Abschluss** Metadaten aktualisieren
- ✅ **Atomare Commits** (Test + Inventory + Docs zusammen)

### DON'T ❌

- ❌ **Niemals** `test-concept.md` oder `.html` manuell bearbeiten
- ❌ **Niemals** Statistiken selbst ausrechnen
- ❌ **Niemals** Test-Code ohne Inventar-Update committen
- ❌ **Niemals** Struktur in YAML ändern ohne Script-Update

---

## 🆘 Support

**Bei Fragen:**
1. Diese Anleitung lesen
2. Validierung ausführen: `python scripts/sync_test_documentation.py --check`
3. Team fragen (Slack/E-Mail)

**Dokumentations-Updates:**
- Maintainer: [Ihr Name]
- Letzte Aktualisierung: 2026-01-16
- Nächstes Review: Nach Phase 1
