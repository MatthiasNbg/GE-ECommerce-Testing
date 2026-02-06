# Design: E2E Checkout Tests + Click & Collect

**Datum:** 2026-02-06
**Status:** In Umsetzung

---

## Ziel

Vollstaendige E2E-Tests mit Neuregistrierung/Login und Bestellabschluss auf Staging.
Dazu neue Click & Collect Tests fuer AT und DE.

---

## 1. E2E Checkout: TC-E2E-001

**Ein Testfall, 24 parametrisierte Varianten.**

### Varianten-Matrix

| # | Land | Zahlungsart | Versandart | Account |
|---|------|------------|------------|---------|
| 1 | AT | Vorkasse | Post | Neu |
| 2 | AT | Vorkasse | Spedition | Neu |
| 3 | AT | Vorkasse | Gemischt | Neu |
| 4 | AT | Rechnung | Post | Bestehend |
| 5 | AT | Rechnung | Spedition | Bestehend |
| 6 | AT | Rechnung | Gemischt | Bestehend |
| 7 | AT | Kreditkarte | Post | Neu |
| 8 | AT | Kreditkarte | Spedition | Bestehend |
| 9 | AT | Kreditkarte | Gemischt | Neu |
| 10 | DE | Vorkasse | Post | Bestehend |
| 11 | DE | Vorkasse | Spedition | Neu |
| 12 | DE | Vorkasse | Gemischt | Bestehend |
| 13 | DE | Rechnung | Post | Neu |
| 14 | DE | Rechnung | Spedition | Neu |
| 15 | DE | Rechnung | Gemischt | Bestehend |
| 16 | DE | Kreditkarte | Post | Bestehend |
| 17 | DE | Kreditkarte | Spedition | Neu |
| 18 | DE | Kreditkarte | Gemischt | Neu |
| 19 | CH | Vorkasse | Post | Neu |
| 20 | CH | Vorkasse | Spedition | Bestehend |
| 21 | CH | Vorkasse | Gemischt | Neu |
| 22 | CH | Kreditkarte | Post | Bestehend |
| 23 | CH | Kreditkarte | Spedition | Neu |
| 24 | CH | Kreditkarte | Gemischt | Bestehend |

**Hinweis:** CH hat KEINE Rechnung als Zahlungsart.

### Testflow pro Variante

1. **Account**: Neuregistrierung (mit Timestamp-E-Mail) ODER Login (bestehender Testaccount)
2. **Warenkorb befuellen**:
   - Post: Nur Post-Produkt (z.B. Kurzarmshirt ge-p-862990)
   - Spedition: Nur Spedi-Produkt (z.B. Polsterbett ge-p-693278)
   - Gemischt: Post-Produkt + Spedi-Produkt
3. **Zur Kasse gehen**
4. **Zahlungsart auswaehlen** (Vorkasse / Rechnung / Kreditkarte)
5. **AGB akzeptieren**
6. **Bestellung absenden**
7. **Bestaetigung pruefen**: Bestellnummer vorhanden

### Kreditkarte (GlobalPayments)

- Payment Provider: GlobalPayments
- Testdaten: Vorhanden (muessen in config.yaml hinterlegt werden)
- Technisch: iFrame-basiert, benoetigt Frame-Switch in Playwright
- Erweiterung checkout_page.py: `fill_credit_card_details()`

---

## 2. Click & Collect: TC-E2E-CC-001

**Ein Testfall, 4 parametrisierte Varianten.**

### Varianten

| # | Land | Abholort-PLZ | Produkt |
|---|------|-------------|---------|
| 1 | AT | Wien (1010) | Post-Produkt |
| 2 | AT | Linz (4020) | Speditions-Produkt |
| 3 | DE | Muenchen (80331) | Post-Produkt |
| 4 | DE | Berlin (10115) | Post-Produkt |

**Hinweis:** CH hat kein Click & Collect.

### Testflow

1. Neuregistrierung oder Login
2. Produkt in den Warenkorb
3. Zur Kasse
4. Versandart: Click & Collect auswaehlen
5. PLZ eingeben → Abholort aus Ergebnisliste waehlen
6. Zahlungsart: "Zahlung bei Abholung"
7. Bestellung absenden
8. Bestaetigung pruefen

### Page Object Erweiterungen

- `checkout_page.py`: Neue Methode `select_click_and_collect(plz, location_index=0)`
  - PLZ-Feld ausfuellen
  - Auf Ergebnisliste warten
  - Abholort aus Liste auswaehlen
- Zahlungsart "Zahlung bei Abholung" als neuer Alias in PAYMENT_ALIASES

---

## 3. Aenderungen an test-concept.md

### Neue Spalte "Varianten"

Alle Detail-Tabellen (mit Header "Test-ID | Name | Prioritaet | Status | Laender")
bekommen eine 6. Spalte "Varianten".

- Standard: `1` fuer Tests ohne Varianten
- TC-E2E-001: `24`
- TC-E2E-CC-001: `4`

### Neue Sektionen

1. **E2E Tests** (nach Critical Path, vor Warenkorb)
2. **Click & Collect Tests** (nach E2E Tests)

### Aktualisierungen

- Executive Summary: Testanzahl erhoehen (215 → 217, bzw. +28 Varianten)
- Uebersichtstabelle: Neue Zeilen fuer E2E und Click & Collect
- Inhaltsverzeichnis: Neue Eintraege
- Zahlungsarten-Tabelle: Kreditkarte hinzufuegen (AT, DE)

---

## 4. Neue Dateien

| Datei | Beschreibung |
|-------|-------------|
| `docs/plans/2026-02-06-e2e-checkout-design.md` | Dieses Design-Dokument |
| `schema/examples/TC-E2E-001_e2e-checkout-komplett.json` | Test-Contract E2E |
| `schema/examples/TC-E2E-CC-001_click-and-collect.json` | Test-Contract Click & Collect |
| `playwright_tests/tests/test_e2e_checkout.py` | E2E Checkout Testcode |
| `playwright_tests/tests/test_e2e_click_collect.py` | Click & Collect Testcode |

### Geaenderte Dateien

| Datei | Aenderung |
|-------|-----------|
| `docs/test-concept.md` | Neue Spalte + Sektionen |
| `docs/test-concept.html` | Regeneriert via generate_html_report.py |
| `playwright_tests/pages/checkout_page.py` | Kreditkarte + Click & Collect Methoden |
| `config/config.yaml` | Kreditkarten-Testdaten |
| `CLAUDE.md` | Neue Test-IDs (TC-E2E-*, TC-E2E-CC-*) |

---

## 5. Test-ID Schema

| Praefix | Kategorie | IDs |
|---------|-----------|-----|
| TC-E2E-* | E2E Checkout | TC-E2E-001 |
| TC-E2E-CC-* | Click & Collect | TC-E2E-CC-001 |
