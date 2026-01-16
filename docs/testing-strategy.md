# Systematische Test-Strategie für E-Commerce

## Überblick

Diese Strategie beschreibt, wie Testfälle systematisch aufgebaut, priorisiert und organisiert werden.

## 1. Test-Kategorien

### 1.1 Smoke Tests (Sanity Checks)
**Zweck:** Schnelle Validierung, dass grundlegende Funktionen arbeiten
**Ausführung:** Vor jedem Deployment, nach jedem Build
**Dauer:** < 5 Minuten

**Beispiele:**
```python
@pytest.mark.smoke
def test_homepage_loads():
    """Homepage lädt ohne Fehler"""

@pytest.mark.smoke
def test_product_page_loads():
    """Produktseite lädt und zeigt Preis"""

@pytest.mark.smoke
def test_cart_add_product():
    """Produkt kann zum Warenkorb hinzugefügt werden"""

@pytest.mark.smoke
def test_checkout_reachable():
    """Checkout-Seite ist erreichbar"""
```

**Ihr Projekt:**
- ✅ `test_shop_smoke.py` - Homepage, Produktseite, Warenkorb

---

### 1.2 Critical Path Tests
**Zweck:** Die wichtigsten Business-Flows, die niemals brechen dürfen
**Ausführung:** Bei jedem Deployment (Staging + Production)
**Dauer:** 10-30 Minuten

**E-Commerce Critical Paths:**
1. **Purchase Flow (Gast)**
   - Produkt suchen → Warenkorb → Checkout → Bestellung

2. **Purchase Flow (Registrierter User)**
   - Login → Produkt → Warenkorb → Checkout → Bestellung

3. **Payment Methods** (länderspezifisch)
   - Alle konfigurierten Zahlungsarten verfügbar

4. **Account Management**
   - Registrierung → Login → Profil bearbeiten

**Beispiel-Struktur:**
```python
@pytest.mark.critical
@pytest.mark.parametrize("country", ["AT", "DE", "CH"])
def test_guest_checkout_complete_flow(country):
    """Gast kann kompletten Checkout durchlaufen"""
    # 1. Produkt zum Warenkorb
    # 2. Gast-Checkout-Formular
    # 3. Zahlungsart wählen
    # 4. Bestellung abschließen
    # 5. Bestätigungsseite prüfen
    assert order_number is not None
```

**Ihr Projekt:**
- ✅ `test_payment_methods_available.py` - Payment Critical Path
- ⚠️ Fehlend: Vollständiger Purchase Flow (mit echter Bestellung)

---

### 1.3 Feature Tests
**Zweck:** Spezifische Features isoliert testen
**Ausführung:** In CI/CD-Pipeline, vor Feature-Release
**Dauer:** Variabel (5-60 Minuten)

**Beispiel-Features:**
```python
# Suche
@pytest.mark.feature
class TestSearch:
    def test_search_by_product_name(self):
        """Suche nach Produktname liefert Ergebnisse"""

    def test_search_autocomplete(self):
        """Autocomplete zeigt Vorschläge"""

    def test_search_filters(self):
        """Filter reduzieren Suchergebnisse korrekt"""

# Warenkorb
@pytest.mark.feature
class TestCart:
    def test_add_multiple_products(self):
        """Mehrere Produkte können hinzugefügt werden"""

    def test_update_quantity(self):
        """Menge kann geändert werden"""

    def test_remove_product(self):
        """Produkt kann entfernt werden"""

    def test_cart_persists_after_login(self):
        """Warenkorb bleibt nach Login erhalten"""

# Zahlungsarten (Discovery)
@pytest.mark.feature
@pytest.mark.discovery
def test_discover_payment_methods():
    """Ermittelt verfügbare Zahlungsarten pro Land"""
```

**Ihr Projekt:**
- ✅ `test_payment_discovery.py` - Payment Discovery Feature
- ⚠️ Fehlend: Suche, Warenkorb-Operationen, Filter

---

### 1.4 Regression Tests
**Zweck:** Sicherstellen, dass alte Features nach Änderungen noch funktionieren
**Ausführung:** Nightly Builds, vor Major Releases
**Dauer:** 1-4 Stunden

**Beispiel-Struktur:**
```python
@pytest.mark.regression
class TestCheckoutRegression:
    """Regression-Tests für Checkout-Änderungen"""

    def test_old_payment_method_selection_still_works(self):
        """Legacy Payment Selection (vor Refactoring)"""

    def test_address_validation_rules(self):
        """Alte Validierungsregeln noch aktiv"""

    def test_discount_codes_applied_correctly(self):
        """Rabattcodes funktionieren weiterhin"""
```

**Ihr Projekt:**
- ✅ `test_checkout_mass.py` - Kombiniert Regression + Load
- ⚠️ Kann erweitert werden mit spezifischen Legacy-Checks

---

### 1.5 Load/Stress Tests
**Zweck:** Performance unter Last, Race Conditions, Stabilität
**Ausführung:** Vor Releases, bei Performance-Änderungen
**Dauer:** 30 Minuten - mehrere Stunden

**Beispiel-Szenarien:**
```python
@pytest.mark.load
@pytest.mark.parametrize("parallel", [5, 10, 20])
def test_concurrent_orders(parallel):
    """Mehrere gleichzeitige Bestellungen"""

@pytest.mark.stress
def test_checkout_under_load():
    """1000 Bestellungen in 10 Minuten"""

@pytest.mark.load
def test_inventory_race_condition():
    """Letztes Produkt von 10 Usern gleichzeitig gekauft"""
```

**Ihr Projekt:**
- ✅ `test_checkout_mass.py` - Mass Order Tests
- ⚠️ Kann erweitert werden mit Inventory-Tests

---

### 1.6 Data Validation Tests
**Zweck:** Sicherstellen, dass Daten korrekt sind und aktuell bleiben
**Ausführung:** Täglich (als Monitoring), vor Deployments
**Dauer:** 5-15 Minuten

**Beispiel-Validierungen:**
```python
@pytest.mark.data_validation
def test_payment_methods_match_config():
    """Shop-Zahlungsarten entsprechen config.yaml"""
    # ✅ Genau das macht test_payment_methods_available.py!

@pytest.mark.data_validation
def test_all_products_have_prices():
    """Alle aktiven Produkte haben gültige Preise"""

@pytest.mark.data_validation
def test_shipping_costs_configured():
    """Versandkosten für alle Länder konfiguriert"""

@pytest.mark.data_validation
@pytest.mark.parametrize("country", ["AT", "DE", "CH"])
def test_country_specific_tax_rates(country):
    """Steuersätze pro Land korrekt"""
```

**Ihr Projekt:**
- ✅ `test_payment_methods_available.py` - Payment Method Validation
- ⚠️ Fehlend: Preis-, Steuer-, Versandkosten-Validierung

---

## 2. Test-Priorisierung (Risikobasiert)

### 2.1 Risiko-Matrix

```
             │ Niedrige      │ Mittlere      │ Hohe
             │ Auswirkung    │ Auswirkung    │ Auswirkung
─────────────┼───────────────┼───────────────┼──────────────
Häufig       │               │               │
verwendet    │   Mittel      │    Hoch       │  Kritisch
             │               │               │
─────────────┼───────────────┼───────────────┼──────────────
Gelegentlich │               │               │
verwendet    │   Niedrig     │   Mittel      │    Hoch
             │               │               │
─────────────┼───────────────┼───────────────┼──────────────
Selten       │               │               │
verwendet    │   Niedrig     │   Niedrig     │   Mittel
             │               │               │
```

**Kritisch (täglich testen):**
- ✅ Checkout-Flow (Gast + Registriert)
- ✅ Zahlungsarten-Verfügbarkeit
- ✅ Produktseite laden
- ✅ Warenkorb-Funktionen

**Hoch (wöchentlich testen):**
- Suche und Filter
- Account-Management
- Bestellhistorie
- Rabattcodes

**Mittel (vor Releases testen):**
- Wunschliste
- Produktvergleich
- Newsletter-Anmeldung

**Niedrig (Ad-hoc testen):**
- Footer-Links
- Über uns
- FAQ

### 2.2 Priorisierung nach Business Value

**Formula:**
```
Priorität = (Business Value × Fehlerwahrscheinlichkeit) / Testkosten
```

**Beispiel E-Commerce:**

| Feature | Business Value | Fehler-Wahrscheinlichkeit | Testkosten | Priorität |
|---------|----------------|---------------------------|------------|-----------|
| Checkout | 10 | 8 | 5 | 16 ⭐⭐⭐ |
| Zahlungsarten | 10 | 7 | 3 | 23 ⭐⭐⭐ |
| Produktsuche | 8 | 6 | 4 | 12 ⭐⭐ |
| Warenkorb | 9 | 7 | 4 | 16 ⭐⭐⭐ |
| Wunschliste | 3 | 4 | 5 | 2 ⭐ |

---

## 3. Test-Struktur und Organisation

### 3.1 Datei-Organisation

```
playwright_tests/
├── tests/
│   ├── smoke/
│   │   ├── test_shop_smoke.py          # Grundlegende Funktionen
│   │   └── test_api_smoke.py           # API-Endpoints
│   │
│   ├── critical/
│   │   ├── test_checkout_guest.py      # Gast-Checkout Flow
│   │   ├── test_checkout_user.py       # User-Checkout Flow
│   │   └── test_payment_methods.py     # Zahlungsarten (bereits vorhanden)
│   │
│   ├── features/
│   │   ├── search/
│   │   │   ├── test_search_basic.py
│   │   │   └── test_search_filters.py
│   │   ├── cart/
│   │   │   ├── test_cart_operations.py
│   │   │   └── test_cart_persistence.py
│   │   └── account/
│   │       ├── test_registration.py
│   │       └── test_profile.py
│   │
│   ├── regression/
│   │   └── test_checkout_regression.py
│   │
│   ├── load/
│   │   └── test_checkout_mass.py        # Bereits vorhanden
│   │
│   └── data_validation/
│       ├── test_payment_methods_available.py  # Bereits vorhanden
│       ├── test_product_prices.py
│       └── test_shipping_costs.py
│
├── pages/                               # Page Objects
│   ├── base_page.py
│   ├── home_page.py
│   ├── product_page.py
│   ├── cart_page.py
│   └── checkout_page.py
│
├── utils/                               # Hilfsfunktionen
│   ├── payment_discovery.py            # Bereits vorhanden
│   ├── data_generators.py
│   └── test_helpers.py
│
└── fixtures/                            # Pytest Fixtures
    ├── conftest.py                      # Globale Fixtures
    ├── user_fixtures.py
    └── product_fixtures.py
```

### 3.2 Naming Conventions

**Test-Datei:**
```
test_<feature>_<aspect>.py

Beispiele:
- test_checkout_guest.py
- test_search_filters.py
- test_cart_operations.py
```

**Test-Funktion:**
```python
def test_<action>_<expected_result>_<context>():
    """Klare Beschreibung was getestet wird"""

# Gut:
def test_add_product_shows_in_cart():
    """Produkt zum Warenkorb hinzufügen zeigt es im Warenkorb"""

def test_guest_checkout_without_account_creates_order():
    """Gast-Checkout ohne Konto erstellt Bestellung"""

# Schlecht:
def test_checkout():
def test_cart():
def test_1():
```

---

## 4. Test-Daten-Strategie

### 4.1 Test-Daten-Typen

**1. Statische Daten (in Config/Fixtures):**
```python
# fixtures/product_fixtures.py
@pytest.fixture
def test_products():
    return {
        "low_price": "p/produkt-guenstig/ge-p-123",
        "high_price": "p/produkt-teuer/ge-p-456",
        "out_of_stock": "p/produkt-ausverkauft/ge-p-789",
    }

@pytest.fixture
def test_addresses():
    return {
        "AT": {"zip": "4020", "city": "Linz"},
        "DE": {"zip": "10115", "city": "Berlin"},
        "CH": {"zip": "8001", "city": "Zürich"},
    }
```

**2. Dynamische Daten (generiert):**
```python
# utils/data_generators.py
def generate_test_email():
    """Generiert eindeutige Test-E-Mail"""
    return f"test_{uuid.uuid4().hex[:8]}@example.com"

def generate_test_user():
    """Generiert Test-User-Daten"""
    return {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": generate_test_email(),
    }
```

**3. Entdeckte Daten (via Discovery):**
```python
# Bereits implementiert!
# config.yaml wird durch Discovery-Test aktualisiert
# Tests lesen dann payment_methods aus Config
```

### 4.2 Test-Daten-Isolation

**Wichtig:** Jeder Test sollte eigene Daten verwenden!

```python
# Gut: Jeder Test hat eigene Daten
@pytest.mark.parametrize("user_data", [
    {"country": "AT", "email": "test_at@example.com"},
    {"country": "DE", "email": "test_de@example.com"},
])
def test_checkout(user_data):
    # Eindeutige Daten pro Test
    pass

# Schlecht: Geteilte Daten zwischen Tests
shared_email = "test@example.com"  # ❌ Race Conditions!

def test_registration():
    register(shared_email)  # Kann bei parallel Tests fehlschlagen

def test_login():
    login(shared_email)  # Setzt voraus, dass test_registration lief
```

---

## 5. Praktischer Aufbau-Plan für Ihr Projekt

### Phase 1: Kritische Flows absichern (Jetzt)
```
✅ Zahlungsarten-Validierung (vorhanden)
⬜ Vollständiger Gast-Checkout mit Bestellung
⬜ Vollständiger User-Checkout mit Bestellung
⬜ Produktsuche + Zum-Warenkorb
```

### Phase 2: Feature-Abdeckung erweitern (Nächste Woche)
```
⬜ Warenkorb-Operationen (hinzufügen, ändern, löschen)
⬜ Account-Registrierung und Login
⬜ Adress-Verwaltung
⬜ Bestellhistorie
```

### Phase 3: Regression und Edge Cases (Laufend)
```
⬜ Ungültige Eingaben (Validierung)
⬜ Grenzwerte (max. Bestellmenge, min. Preis)
⬜ Browser-Kompatibilität
⬜ Mobile vs. Desktop
```

### Phase 4: Performance und Load (Monatlich)
```
✅ Mass Orders (vorhanden)
⬜ Inventory Race Conditions
⬜ Checkout unter Last
⬜ API-Performance
```

---

## 6. Test-Ausführungs-Strategie

### 6.1 Test-Suites definieren

```python
# pytest.ini
[pytest]
markers =
    smoke: Schnelle Basis-Checks (< 5 min)
    critical: Kritische Business-Flows (10-30 min)
    feature: Spezifische Feature-Tests (variabel)
    regression: Regression-Tests (1-4 h)
    load: Load/Stress-Tests (30 min - mehrere h)
    data_validation: Daten-Validierung (5-15 min)
    discovery: Discovery-Tests (manuell)
```

### 6.2 Ausführungs-Matrix

**Bei jedem Commit (CI/CD):**
```bash
pytest -m smoke --maxfail=3
# ~5 Minuten, stoppt bei 3 Fehlern
```

**Vor Deployment zu Staging:**
```bash
pytest -m "smoke or critical" -v
# ~30 Minuten
```

**Vor Deployment zu Production:**
```bash
pytest -m "smoke or critical or data_validation" -v
# ~45 Minuten
```

**Nightly Build:**
```bash
pytest -m "smoke or critical or feature or regression" -v
# ~2-4 Stunden
```

**Wöchentlich:**
```bash
pytest -m load --workers=10
# Load-Tests mit Parallelisierung
```

**Manuell (bei Shop-Änderungen):**
```bash
pytest -m discovery -v
# Discovery aktualisiert Config
```

---

## 7. Best Practices

### 7.1 Test-Design-Prinzipien

**1. FIRST-Prinzipien:**
- **F**ast: Tests sollten schnell sein (< 1s für Unit, < 30s für E2E)
- **I**ndependent: Tests sollten unabhängig voneinander laufen
- **R**epeatable: Tests sollten deterministisch sein
- **S**elf-Validating: Tests sollten pass/fail selbst bestimmen
- **T**imely: Tests sollten zeitnah geschrieben werden

**2. AAA-Pattern:**
```python
def test_add_product_to_cart():
    # Arrange (Setup)
    product = get_test_product()
    cart = CartPage(page)

    # Act (Ausführung)
    cart.add_product(product)

    # Assert (Validierung)
    assert cart.contains(product)
    assert cart.quantity(product) == 1
```

**3. DRY (Don't Repeat Yourself):**
```python
# Gut: Wiederverwendbare Helper-Funktionen
def complete_guest_checkout(page, country, product):
    add_product_to_cart(page, product)
    fill_guest_form(page, get_test_address(country))
    select_payment_method(page, "invoice")
    submit_order(page)

# Tests verwenden Helper
def test_guest_checkout_at():
    complete_guest_checkout(page, "AT", test_product)

def test_guest_checkout_de():
    complete_guest_checkout(page, "DE", test_product)
```

### 7.2 Wartbarkeit

**1. Page Object Pattern (bereits verwendet!):**
```python
# Gut: Logik in Page Objects
class CheckoutPage:
    def select_payment_method(self, method: str):
        # Implementierung hier

    def submit_order(self):
        # Implementierung hier

# Test ist lesbar und wartbar
def test_checkout():
    checkout = CheckoutPage(page)
    checkout.select_payment_method("invoice")
    checkout.submit_order()
    assert checkout.order_number is not None
```

**2. Konfiguration externalisieren:**
```yaml
# config.yaml (bereits vorhanden!)
test_products:
  - p/produkt1/ge-p-123
  - p/produkt2/ge-p-456

payment_methods:
  AT: ["Kreditkarte", "Vorkasse", "Rechnung"]
  DE: ["Kreditkarte", "Vorkasse", "Rechnung"]
  CH: ["Vorkasse", "Rechnung"]
```

**3. Selektoren wartbar halten:**
```python
# Gut: Selektoren als Klassenvariablen
class CheckoutPage:
    # Selektoren zentral definiert
    PAYMENT_METHOD_LABEL = ".payment-method-label strong"
    SUBMIT_BUTTON = "button[type='submit']"
    ORDER_NUMBER = ".order-number"

    def get_order_number(self):
        return self.page.locator(self.ORDER_NUMBER).inner_text()
```

---

## 8. Zusammenfassung: Ihre nächsten Schritte

### Sofort (diese Woche):
1. ✅ Test-Marker in `pytest.ini` definieren
2. ⬜ Kritischen Purchase-Flow implementieren (Gast + User)
3. ⬜ Smoke-Test-Suite erstellen (5 Min Laufzeit)

### Kurzfristig (nächste 2 Wochen):
4. ⬜ Feature-Tests für Warenkorb
5. ⬜ Feature-Tests für Suche
6. ⬜ Data-Validation für Preise/Versand

### Mittelfristig (nächster Monat):
7. ⬜ Regression-Test-Suite
8. ⬜ CI/CD-Integration
9. ⬜ Test-Reports und Metriken

### Laufend:
10. ⬜ Neue Features → neue Tests (TDD)
11. ⬜ Fehler gefunden → Regression-Test hinzufügen
12. ⬜ Test-Coverage monitoren

---

## Quellen und weitere Ressourcen

- [Test Pyramid - Martin Fowler](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Page Object Pattern](https://playwright.dev/docs/pom)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [Testing Strategies for E-Commerce](https://www.softwaretestinghelp.com/ecommerce-testing/)
