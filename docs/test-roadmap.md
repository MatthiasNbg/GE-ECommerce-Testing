# Test-Roadmap: Nächste Schritte

## ✅ Status Quo (bereits vorhanden)

```
✅ Smoke Tests: test_shop_smoke.py
✅ Payment Discovery: test_payment_discovery.py
✅ Payment Validation: test_payment_methods_available.py
✅ Mass Orders: test_checkout_mass.py
✅ Unit Tests: Config, Utils, CheckoutPage (22 Tests)
```

---

## 🎯 Phase 1: Kritische Flows (Diese Woche)

### Priorität 1: Vollständiger Gast-Checkout
**Datei:** `tests/critical/test_checkout_guest_complete.py`

```python
@pytest.mark.critical
@pytest.mark.parametrize("country", ["AT", "DE", "CH"])
def test_guest_checkout_creates_order(page, country):
    """
    Gast-User kann vollständige Bestellung aufgeben.

    Flow:
    1. Produkt suchen/auswählen
    2. Zum Warenkorb hinzufügen
    3. Gast-Checkout-Formular ausfüllen
    4. Zahlungsart auswählen
    5. AGB akzeptieren
    6. Bestellung abschicken
    7. Bestätigungsseite mit Bestellnummer prüfen

    Erwartetes Ergebnis:
    - Bestellnummer vorhanden
    - Bestätigungs-E-Mail versendet (optional)
    - Bestellung in System sichtbar
    """
    # TODO: Implementieren
```

**Geschätzter Aufwand:** 2-3 Stunden
**Business Value:** Kritisch (Umsatz-relevant)

---

### Priorität 2: Test-Marker Setup
**Datei:** `pytest.ini` (erweitern)

```ini
[pytest]
markers =
    smoke: Schnelle Basis-Checks (< 5 min)
    critical: Kritische Business-Flows (10-30 min)
    feature: Spezifische Feature-Tests
    regression: Regression-Tests
    load: Load/Stress-Tests
    data_validation: Daten-Validierung
    discovery: Discovery-Tests (manuell)

    # Feature-spezifische Marker
    checkout: Checkout-bezogene Tests
    cart: Warenkorb-Tests
    search: Such-Tests
    account: Account-Management-Tests
```

**Geschätzter Aufwand:** 15 Minuten
**Nutzen:** Strukturierte Test-Ausführung

---

### Priorität 3: CI/CD-Integration vorbereiten
**Datei:** `.github/workflows/tests.yml` (falls GitHub) oder ähnlich

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  smoke-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run smoke tests
        run: pytest -m smoke --maxfail=3

  critical-tests:
    runs-on: ubuntu-latest
    needs: smoke-tests
    steps:
      - uses: actions/checkout@v3
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run critical tests
        run: pytest -m critical -v
```

**Geschätzter Aufwand:** 1 Stunde
**Nutzen:** Automatische Qualitätssicherung

---

## 🚀 Phase 2: Feature-Abdeckung (Nächste 2 Wochen)

### Test 1: Warenkorb-Operationen
**Datei:** `tests/features/cart/test_cart_operations.py`

```python
@pytest.mark.feature
@pytest.mark.cart
class TestCartOperations:

    def test_add_product_shows_in_cart(self, page):
        """Produkt zum Warenkorb hinzufügen zeigt es im Warenkorb"""

    def test_update_quantity_changes_total(self, page):
        """Menge ändern aktualisiert Gesamtpreis"""

    def test_remove_product_updates_cart(self, page):
        """Produkt entfernen aktualisiert Warenkorb"""

    def test_empty_cart_shows_message(self, page):
        """Leerer Warenkorb zeigt entsprechende Meldung"""

    def test_cart_persists_between_pages(self, page):
        """Warenkorb bleibt bei Navigation erhalten"""
```

**Geschätzter Aufwand:** 3-4 Stunden
**Business Value:** Hoch

---

### Test 2: Produktsuche
**Datei:** `tests/features/search/test_search_basic.py`

```python
@pytest.mark.feature
@pytest.mark.search
class TestProductSearch:

    def test_search_by_name_returns_results(self, page):
        """Suche nach Produktname liefert Ergebnisse"""

    def test_search_no_results_shows_message(self, page):
        """Suche ohne Ergebnisse zeigt Meldung"""

    def test_search_autocomplete(self, page):
        """Autocomplete zeigt Vorschläge während Eingabe"""

    def test_search_special_characters(self, page):
        """Suche mit Sonderzeichen funktioniert"""
```

**Geschätzter Aufwand:** 2-3 Stunden
**Business Value:** Mittel-Hoch

---

### Test 3: Account-Registrierung
**Datei:** `tests/features/account/test_registration.py`

```python
@pytest.mark.feature
@pytest.mark.account
class TestAccountRegistration:

    def test_register_new_user_successful(self, page):
        """Neue User-Registrierung erfolgreich"""

    def test_register_duplicate_email_fails(self, page):
        """Registrierung mit bereits verwendeter E-Mail schlägt fehl"""

    def test_register_invalid_email_shows_error(self, page):
        """Ungültige E-Mail zeigt Validierungsfehler"""

    def test_register_weak_password_rejected(self, page):
        """Schwaches Passwort wird abgelehnt"""
```

**Geschätzter Aufwand:** 2-3 Stunden
**Business Value:** Mittel

---

## 📊 Phase 3: Data Validation erweitern (Nächste 2 Wochen)

### Test 1: Produktpreise validieren
**Datei:** `tests/data_validation/test_product_prices.py`

```python
@pytest.mark.data_validation
class TestProductPrices:

    def test_all_products_have_valid_prices(self, page):
        """Alle aktiven Produkte haben gültige Preise (> 0)"""

    def test_product_prices_match_display(self, page):
        """Angezeigter Preis entspricht Checkout-Preis"""

    def test_discounted_prices_calculated_correctly(self, page):
        """Rabattierte Preise korrekt berechnet"""
```

**Geschätzter Aufwand:** 2 Stunden
**Business Value:** Hoch (Vertrauen)

---

### Test 2: Versandkosten validieren
**Datei:** `tests/data_validation/test_shipping_costs.py`

```python
@pytest.mark.data_validation
@pytest.mark.parametrize("country", ["AT", "DE", "CH"])
class TestShippingCosts:

    def test_shipping_costs_configured(self, page, country):
        """Versandkosten für Land konfiguriert"""

    def test_free_shipping_threshold(self, page, country):
        """Versandkostenfrei ab Mindestbestellwert"""

    def test_shipping_costs_displayed_at_checkout(self, page, country):
        """Versandkosten im Checkout angezeigt"""
```

**Geschätzter Aufwand:** 2 Stunden
**Business Value:** Mittel

---

## 🔄 Phase 4: Regression Tests (Laufend)

### Regression-Test-Template
**Datei:** `tests/regression/test_checkout_regression.py`

```python
@pytest.mark.regression
class TestCheckoutRegression:
    """
    Regression-Tests für Checkout nach Änderungen.

    Diese Tests sichern ab, dass nach Refactorings
    oder neuen Features alte Funktionalität weiterhin
    funktioniert.
    """

    def test_legacy_payment_selection_works(self, page):
        """Alte Payment-Selection-Methode funktioniert noch"""
        # Nach CheckoutPage-Refactoring wichtig!

    def test_address_validation_rules_unchanged(self, page):
        """Validierungsregeln für Adressen unverändert"""
        # PLZ-Format, Pflichtfelder, etc.

    def test_discount_codes_still_apply(self, page):
        """Rabattcodes werden weiterhin angewendet"""
        # Nach Checkout-Änderungen prüfen
```

**Geschätzter Aufwand:** Ad-hoc bei Änderungen
**Business Value:** Hoch (Stabilität)

---

## 📈 Phase 5: Metriken und Monitoring (Monat 2)

### Test-Metriken erfassen
**Datei:** `scripts/generate_test_report.py`

```python
"""
Generiert Test-Metriken und Reports:
- Test-Coverage
- Erfolgsquote
- Ausführungsdauer
- Flaky Tests
"""
```

### Monitoring-Dashboard
- Playwright Traces für fehlerhafte Tests
- Screenshots bei Failures
- Test-Trend über Zeit
- Kritische vs. Nicht-Kritische Failures

---

## 🎯 Zusammenfassung: Prioritäten

### Woche 1:
1. ✅ Test-Marker in pytest.ini
2. ✅ Vollständiger Gast-Checkout-Test
3. ✅ Smoke-Test-Suite (< 5 Min)

### Woche 2-3:
4. ⬜ Warenkorb-Operationen (5 Tests)
5. ⬜ Produktsuche (4 Tests)
6. ⬜ Account-Registrierung (4 Tests)

### Woche 4:
7. ⬜ Data-Validation: Preise + Versandkosten
8. ⬜ CI/CD-Integration
9. ⬜ Test-Reports

### Laufend:
- Neue Features → TDD (Test first!)
- Bug gefunden → Regression-Test
- Vor jedem Release → Vollständige Test-Suite

---

## 📊 Erwartete Test-Coverage

| Bereich | Aktuell | Ziel (Phase 1) | Ziel (Phase 2) |
|---------|---------|----------------|----------------|
| Checkout | 60% | 90% | 95% |
| Zahlungsarten | 100% ✅ | 100% | 100% |
| Warenkorb | 20% | 50% | 80% |
| Suche | 0% | 30% | 70% |
| Account | 0% | 40% | 80% |
| **Gesamt** | **40%** | **65%** | **85%** |

---

## 💡 Quick Wins (sofort umsetzbar)

1. **Test-Marker hinzufügen** (15 Min)
   ```python
   # In bestehende Tests einfach hinzufügen:
   @pytest.mark.critical
   @pytest.mark.smoke
   ```

2. **Ausführungs-Skripte erstellen** (30 Min)
   ```bash
   # scripts/run_smoke.sh
   pytest -m smoke --maxfail=3 -v

   # scripts/run_critical.sh
   pytest -m critical -v
   ```

3. **Test-Dokumentation in README** (15 Min)
   ```markdown
   ## Test-Ausführung

   # Smoke Tests (5 Min)
   pytest -m smoke

   # Kritische Tests (30 Min)
   pytest -m critical
   ```

---

## 🤝 Hilfe benötigt?

Bei Fragen zu:
- Test-Implementierung
- Page Object Pattern
- Pytest Fixtures
- CI/CD-Integration

→ Einfach fragen! 😊
