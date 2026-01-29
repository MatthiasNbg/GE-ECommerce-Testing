# Design: Promotion-Tests Erweiterung

**Datum:** 2026-01-29
**Status:** Entwurf
**Umfang:** 22 neue Testfälle (14 Happy-Path + 8 Negativ-Tests)

---

## 1. Übersicht

Erweiterung der bestehenden `test_promotions.py` um 22 neue Testfälle, die Rabattaktionen, Gutscheincodes und Gratis-Lieferung-Regeln im Grüne Erde Shopware 6 Shop verifizieren.

**Verifikationsstrategie:** Prüfung der Endsumme im Warenkorb, ohne Bestellabschluss. So bleiben einmal-einlösbare Gutscheincodes gültig und Tests sind wiederholbar.

**Toleranz:** ±0,01 EUR/CHF für Rundungsdifferenzen.

---

## 2. Happy-Path-Tests (14 Testfälle)

### Gruppe A — Automatische Prozent-Rabatte (ohne Code)

| ID | Testfall | Kunde | Channel | Produkt | Erwartung |
|----|----------|-------|---------|---------|-----------|
| PROMO-01 | 5% Kleidung (Freundeskreis) | Freundeskreis-Mitglied | AT/DE/CH | Kleidung | Endsumme = Preis x 0,95 |
| PROMO-02 | 10% Kleidung (alle) | Beliebig | AT/DE/CH | Kleidung | Endsumme = Preis x 0,90 |
| PROMO-03 | 20% Kleidung Kategorie | Beliebig | AT/DE/CH | Kleidung | Endsumme = Preis x 0,80 |
| PROMO-04 | 50% Mitarbeiter Kosmetik | Mitarbeiter | AT/DE | Kosmetik | Endsumme = Preis x 0,50 |
| PROMO-05 | 20% Mitarbeiter diverse | Mitarbeiter | AT/DE | Moebel/Schlafen/Heimtextilien/Kleidung | Endsumme = Preis x 0,80 |

**Hinweis PROMO-01:** Der 5%-Rabatt gilt "on Top" fuer Freundeskreismitglieder. Es ist zu pruefen, ob dieser zusaetzlich zum allgemeinen 10%-Kleidungsrabatt (PROMO-02) greift. Falls ja: Endsumme = Preis x 0,90 x 0,95.

**Hinweis PROMO-03 vs. PROMO-02:** Beide sind automatische Rabatte auf Kleidung (10% und 20%). Es muss geklaert werden, ob diese sich gegenseitig ausschliessen oder kumulieren. Die Testausfuehrung wird zeigen, welcher Rabatt Vorrang hat.

### Gruppe B — Gutschein-Codes (einmal je Kunde)

| ID | Testfall | Code | Channel | MBW | Erwartung |
|----|----------|------|---------|-----|-----------|
| PROMO-06 | EUR 10 Newsletter | NL10 | AT/DE | 25 EUR | Endsumme = Warenkorb - 10 |
| PROMO-07 | CHF 15 Newsletter | NL15CHF | CH | 30 CHF | Endsumme = Warenkorb - 15 |
| PROMO-08 | EUR 20 Gutschein | EUR20 | AT/DE | 100 EUR | Endsumme = Warenkorb - 20 |
| PROMO-09 | CHF 25 Gutschein | CHF25 | CH | 125 CHF | Endsumme = Warenkorb - 25 |
| PROMO-10 | 20% Lieblingsprodukt | Liebling20 | AT/DE/CH | Alle (nicht rabattierbar ausgenommen) | Endsumme = Gesamtpreis - (teuerstes x 0,20) |

**Bedingungen fuer PROMO-06 bis PROMO-09:**
- Lieferland muss zum Sales Channel passen (AT/DE bzw. CH/Liechtenstein)
- Odoo HC Code Name darf nicht "B9 Gutscheine an Geldes statt ohne Steuer" sein
- Produkt darf nicht `nicht_rabattierbar = True` sein

**Besonderheit PROMO-10 (Lieblingsprodukt):**
- Rabatt wird auf das teuerste Produkt im Warenkorb angewendet
- Sortierung nach Preis absteigend, Anwendung auf 1. Produkt
- Test benoetigt mindestens 2 Produkte im Warenkorb mit unterschiedlichen Preisen

### Gruppe C — Gratis Lieferung (ohne Code)

| ID | Testfall | Channel | MBW | Geltung | Erwartung |
|----|----------|---------|-----|---------|-----------|
| PROMO-11 | Gratis Lieferung AT/DE alle | AT/DE | 100 EUR | Alle Artikel | Versandkosten = 0 |
| PROMO-12 | Gratis Lieferung AT/DE Post | AT/DE | 100 EUR | Nur Post-Artikel | Versandkosten = 0 |
| PROMO-13 | Gratis Lieferung CH alle | CH | 125 CHF | Alle Artikel | Versandkosten = 0 |
| PROMO-14 | Gratis Lieferung CH Post | CH | 125 CHF | Nur Post-Artikel | Versandkosten = 0 |

---

## 3. Negativ-Tests (8 Testfälle)

| ID | Testfall | Vorbedingung | Erwartung |
|----|----------|-------------|-----------|
| PROMO-NEG-01 | Gutscheincode ungueltig | Code "FALSCHCODE" eingeben | Fehlermeldung, kein Rabatt |
| PROMO-NEG-02 | NL10 ohne MBW | Warenkorb < 25 EUR, Code NL10 | Code wird abgelehnt oder kein Rabatt |
| PROMO-NEG-03 | EUR20 ohne MBW | Warenkorb < 100 EUR, Code EUR20 | Code wird abgelehnt oder kein Rabatt |
| PROMO-NEG-04 | CHF25 ohne MBW | Warenkorb < 125 CHF, Code CHF25 | Code wird abgelehnt oder kein Rabatt |
| PROMO-NEG-05 | 5% Kleidung ohne Freundeskreis | Normaler Kunde, Kleidung im Warenkorb | Kein 5%-Rabatt, voller Preis |
| PROMO-NEG-06 | Mitarbeiterrabatt als Normalkunde | Normaler Kunde, Kosmetik im Warenkorb | Kein 50%-Rabatt, voller Preis |
| PROMO-NEG-07 | Kleidungsrabatt auf Nicht-Kleidung | Beliebiger Kunde, Produkt aus anderer Kategorie | Kein 10%/20%-Rabatt |
| PROMO-NEG-08 | Gratis Lieferung unter MBW | Warenkorb < 100 EUR (AT/DE) | Versandkosten > 0 |

---

## 4. Testablauf

Alle Tests folgen demselben Grundmuster, gestoppt **vor Bestellabschluss**:

```
1. Login (falls Kundengruppe/Flag erforderlich) oder Gastmodus
2. Testprodukt in den Warenkorb legen
3. Optional: Gutscheincode eingeben
4. Warenkorb-Endsumme auslesen
5. Erwartete Endsumme berechnen und gegen tatsaechliche pruefen
6. Warenkorb leeren (Cleanup)
```

### Berechnung der erwarteten Endsumme

- **Prozent-Rabatt:** `produktpreis x (1 - rabatt/100)`
- **Absoluter Rabatt:** `produktpreis - rabatt_betrag`
- **Lieblingsprodukt:** `gesamtpreis - (teuerstes_produkt x 0.20)`
- **Gratis Lieferung:** `versandkosten == 0`

---

## 5. Implementierungsdesign

### Betroffene Dateien

| Datei | Aenderung |
|-------|-----------|
| `config/config.yaml` | Neue Testprodukte, Testaccounts, Gutscheincodes |
| `playwright_tests/pages/cart_page.py` | Neue Methoden fuer Gutscheincode und Endsumme |
| `playwright_tests/tests/test_promotions.py` | 22 neue Testfaelle |

### Neue Page-Object-Methoden in `cart_page.py`

```python
async def enter_promotion_code(self, code: str) -> None:
    """Gutscheincode-Feld befuellen und absenden."""

async def get_cart_total(self) -> float:
    """Endsumme als Float auslesen."""

async def get_shipping_cost(self) -> float:
    """Versandkosten als Float auslesen (fuer Gratis-Lieferung-Tests)."""

async def clear_cart(self) -> None:
    """Warenkorb leeren fuer Cleanup."""
```

### Teststruktur in `test_promotions.py`

Parametrisierung mit `@pytest.mark.parametrize`:

- **Prozent-Rabatte:** Parameter = `(channel, kunde, produkt, rabatt_prozent)`
- **Gutschein-Codes:** Parameter = `(channel, code, produkt, mbw, rabatt_absolut)`
- **Gratis Lieferung:** Parameter = `(channel, produkt, mbw)`
- **Negativ-Tests:** Eigene Testfunktionen mit erwarteter Fehlermeldung

---

## 6. Testdaten-Anforderungen

### Neue Testaccounts in `config.yaml`

| Account | Typ | Eigenschaft | Channels |
|---------|-----|-------------|----------|
| Freundeskreis-Kunde | Registriert | Flag Freundeskreis = True | AT/DE/CH |
| Mitarbeiter-Kunde | Registriert | Kundengruppe = Mitarbeiter | AT/DE |

### Neue Testprodukte in `config.yaml`

| Produkt | Kategorie | Versandart-Flag | nicht_rabattierbar | Odoo HC Code != B9 | Zweck |
|---------|-----------|-----------------|--------------------|--------------------|-------|
| Kleidungsprodukt | Kleidung | Post | False | Ja | PROMO-01/02/03/05 |
| Kosmetikprodukt | Kosmetik | Post | False | Ja | PROMO-04 |
| Moebel-/Schlafprodukt | Moebel oder Schlafen | Spedition | False | Ja | PROMO-05 |
| Heimtextilien-Produkt | Heimtextilien | Post | False | Ja | PROMO-05 |
| Nicht-rabattierbares Produkt | Beliebig | Post | True | -- | PROMO-10 (Ausschluss) |
| Guenstiges Produkt (< 25 EUR) | Beliebig | Post | False | Ja | NEG-02 (unter MBW) |

### Offene Todos (vor Implementierung)

- [ ] Konkrete Produkt-URLs fuer jede Kategorie auf Staging identifizieren
- [ ] Produkte mit Custom Field "Odoo HC Code != B9" auf Staging verifizieren
- [ ] Versandart-Flag (Post vs. Spedition) pro Testprodukt dokumentieren
- [ ] Nicht-rabattierbares Produkt auf Staging identifizieren
- [ ] Guenstiges Produkt unter 25 EUR fuer MBW-Negativ-Tests finden
- [ ] Login-Daten Freundeskreis-Kunde in config.yaml aufnehmen
- [ ] Login-Daten Mitarbeiter-Kunde in config.yaml aufnehmen
- [ ] Gutscheincodes (NL10, NL15CHF, EUR20, CHF25, Liebling20) auf Staging pruefen

---

## 7. Implementierungsreihenfolge

1. **Testdaten sammeln** und `config.yaml` ergaenzen
2. **Page-Object-Methoden** in `cart_page.py` erweitern
3. **Happy-Path-Tests** implementieren (Gruppe A -> B -> C)
4. **Negativ-Tests** implementieren
