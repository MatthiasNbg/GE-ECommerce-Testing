# Shopware 6 E2E Testing Framework

End-to-End Testing Framework für den Grüne Erde Shopware 6 Shop mit Fokus auf Massentests bei Bestellungen und Betriebstests zur Funktionalitätsprüfung.

## Projektübersicht

Dieses Projekt implementiert automatisierte Oberflächentests für unseren Shopware 6 Shop. Der gewählte Ansatz kombiniert die Performance und Flexibilität von Playwright mit der Orchestrierungsfähigkeit von Robot Framework.

### Technologie-Stack

| Komponente | Technologie | Zweck |
|------------|-------------|-------|
| Test-Engine | Playwright | Browser-Automatisierung, parallele Ausführung |
| Orchestrierung | Robot Framework | Test-Suites, Tagging, Reporting |
| Sprache | Python 3.11+ | Test-Implementierung |
| CI/CD | GitHub Actions | Automatisierte Ausführung |

### Warum Playwright?

- **Performance:** Direktes DevTools Protocol ohne WebDriver-Overhead
- **Stabilität:** Auto-Wait-Mechanismen reduzieren Flaky Tests
- **Parallelisierung:** Native Unterstützung für parallele Browser-Instanzen
- **Ressourceneffizienz:** ~50-80 MB pro Browser-Kontext (vs. ~150-300 MB bei Selenium)
- **Shopware-Kompatibilität:** Shopware nutzt intern ebenfalls Playwright

## Migrations-Roadmap

Das Projekt folgt einem phasenweisen Ansatz, der schnelle Ergebnisse mit langfristiger Wartbarkeit verbindet.

```
Phase 1                 Phase 2                 Phase 3                 Phase 4
────────────────────    ────────────────────    ────────────────────    ────────────────────
Playwright pur          Library Wrapper         Robot Framework         Vollständige
                                                Integration             Integration
                                                
• Massentests           • Python Library        • Orchestrierung        • Test Management
  entwickeln              erstellen               aufsetzen               Interface
• Validierung           • Keywords definieren   • Tagging & Reporting   • Jira-Anbindung
• Performance-Tests     • Wiederverwendbare     • CI/CD Pipeline        • Rollenbasierte
                          Komponenten                                     Berechtigungen

[Aktuell] ──────────►  [Nächster Schritt]  ──►  [Geplant]  ──────────►  [Zukunft]
```

### Phase 1: Playwright Massentests (aktuell)

Entwicklung der Kern-Testfunktionalität mit purem Playwright für maximale Flexibilität und schnelle Iteration.

### Phase 2: Library Wrapper

Kapselung der Playwright-Tests als Python-Library für die Integration in Robot Framework.

### Phase 3: Robot Framework Integration

Aufsetzen von Robot Framework als Orchestrierungsschicht mit Tagging, Filtering und integriertem Reporting.

### Phase 4: Test Management Interface

Integration in das geplante E2E-Testmanagement-Interface mit Jira-Anbindung und rollenbasierten Berechtigungen.

## Projektstruktur

```
shopware-e2e-tests/
├── README.md
├── requirements.txt
├── pyproject.toml
├── .env.example
│
├── playwright_tests/           # Phase 1: Pure Playwright Tests
│   ├── __init__.py
│   ├── conftest.py             # Pytest Fixtures & Konfiguration
│   ├── config.py               # Umgebungskonfiguration
│   │
│   ├── pages/                  # Page Object Models
│   │   ├── __init__.py
│   │   ├── base_page.py
│   │   ├── product_page.py
│   │   ├── cart_page.py
│   │   ├── checkout_page.py
│   │   └── confirmation_page.py
│   │
│   ├── tests/                  # Testfälle
│   │   ├── __init__.py
│   │   ├── test_checkout_single.py
│   │   ├── test_checkout_mass.py
│   │   └── test_payment_methods.py
│   │
│   └── utils/                  # Hilfsfunktionen
│       ├── __init__.py
│       ├── test_data.py
│       └── reporting.py
│
├── libraries/                  # Phase 2: Robot Framework Libraries
│   ├── __init__.py
│   ├── checkout_library.py
│   └── massentest_library.py
│
├── robot_tests/                # Phase 3: Robot Framework Tests
│   ├── resources/
│   │   ├── keywords.robot
│   │   └── variables.robot
│   │
│   └── suites/
│       ├── smoke.robot
│       ├── checkout.robot
│       └── massentests.robot
│
├── reports/                    # Test-Reports
│   └── .gitkeep
│
└── docker/                     # Container-Konfiguration
    ├── Dockerfile
    └── docker-compose.yml
```

## Installation

### Voraussetzungen

- Python 3.11 oder höher
- Node.js 18+ (für Playwright Browser-Installation)
- Docker (optional, für isolierte Ausführung)

### Setup

```bash
# Repository klonen
git clone https://github.com/gruene-erde/shopware-e2e-tests.git
cd shopware-e2e-tests

# Virtual Environment erstellen
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# oder: .venv\Scripts\activate  # Windows

# Dependencies installieren
pip install -r requirements.txt

# Playwright Browser installieren
playwright install chromium

# Umgebungsvariablen konfigurieren
cp .env.example .env
# .env anpassen (Shop-URL, Credentials, etc.)
```

## Konfiguration

### Umgebungsvariablen (.env)

```bash
# Shop-Konfiguration
SHOP_BASE_URL=https://staging.gruene-erde.com
SHOP_ADMIN_URL=https://staging.gruene-erde.com/admin

# Test-Credentials
TEST_CUSTOMER_EMAIL=test@example.com
TEST_CUSTOMER_PASSWORD=secure_password

# Ausführungsoptionen
HEADLESS=true
PARALLEL_WORKERS=5
DEFAULT_TIMEOUT=30000

# Reporting
SCREENSHOT_ON_FAILURE=true
VIDEO_RECORDING=false
TRACE_ON_FAILURE=true
```

## Verwendung

### Einzelne Tests ausführen

```bash
# Alle Tests
pytest playwright_tests/

# Spezifische Test-Datei
pytest playwright_tests/tests/test_checkout_single.py

# Einzelner Test
pytest playwright_tests/tests/test_checkout_single.py::test_guest_checkout

# Mit sichtbarem Browser
pytest playwright_tests/ --headed

# Spezifischer Browser
pytest playwright_tests/ --browser firefox
```

### Massentests ausführen

```bash
# 100 parallele Bestellungen
pytest playwright_tests/tests/test_checkout_mass.py \
    --mass-orders=100 \
    --parallel=10

# Mit spezifischen Produkten
pytest playwright_tests/tests/test_checkout_mass.py \
    --products="SW-123,SW-456,SW-789" \
    --mass-orders=50
```

### Robot Framework Tests (ab Phase 3)

```bash
# Alle Robot Tests
robot robot_tests/

# Nach Tags filtern
robot --include smoke robot_tests/
robot --include massentest --exclude wip robot_tests/

# Mit spezifischem Report-Verzeichnis
robot --outputdir reports/$(date +%Y%m%d) robot_tests/
```

### Payment Discovery

Das Projekt unterstützt automatische Ermittlung länderspezifischer Zahlungsarten:

```bash
# Zahlungsarten für alle Länder ermitteln
pytest -m discovery

# Nur für bestimmtes Profil
pytest -m discovery --profile=production
```

Der Discovery-Test:
1. Navigiert zu AT/DE/CH Shop-URLs
2. Fügt Testprodukt zum Warenkorb hinzu
3. Geht zum Checkout
4. Extrahiert Zahlungsarten-Labels
5. Generiert englische Aliases
6. Aktualisiert `config/config.yaml`

Nach Discovery sind die ermittelten Zahlungsarten in `config.yaml` verfügbar:

```yaml
profiles:
  staging:
    payment_methods:
      AT: ["Kreditkarte", "Vorkasse", "Rechnung"]
      DE: ["Kreditkarte", "PayPal", "Rechnung"]
      CH: ["Kreditkarte", "Vorkasse"]

payment_method_aliases:
  invoice: "Rechnung"
  credit_card: "Kreditkarte"
  prepayment: "Vorkasse"
```

Tests verwenden automatisch die richtigen Zahlungsarten pro Land.

### Payment Methods Validation

Automatisierter Test zur Validierung, dass alle konfigurierten Zahlungsarten für Gast-User verfügbar sind:

```bash
# Alle Länder testen
pytest playwright_tests/tests/test_payment_methods_available.py -v

# Nur ein bestimmtes Land testen
pytest playwright_tests/tests/test_payment_methods_available.py::test_payment_methods_available[AT] -v
```

Der Test:
1. Fügt Testprodukt zum Warenkorb hinzu
2. Durchläuft Gast-Checkout-Formular
3. Navigiert zur Zahlungsarten-Seite
4. Extrahiert verfügbare Zahlungsarten
5. Validiert gegen `config.yaml` (payment_methods)

**Wichtig:** Test schlägt fehl, wenn eine erwartete Zahlungsart fehlt oder der Shop die Zahlungsarten geändert hat.

---

## Penetration Testing (Security Testing)

⚠️ **WICHTIGER HINWEIS**: Penetration Tests dürfen **NUR auf autorisierten Systemen** durchgeführt werden!

Dieses Projekt enthält eine umfassende Penetration Testing Suite für E-Commerce-Sicherheit.

### Dokumentation

Vollständige Dokumentation: [docs/penetration-testing-guide.md](docs/penetration-testing-guide.md)

Die Dokumentation umfasst:
- Einführung in Penetration Testing
- OWASP Top 10 für E-Commerce
- E-Commerce spezifische Angriffsvektoren
- Implementierungsbeispiele mit Playwright
- Best Practices & rechtliche Aspekte

### Penetration Tests ausführen

```bash
# ALLE Penetration Tests (Vorsicht: Nur auf Test-Umgebungen!)
pytest -m pentest

# Nur Injection-Tests (SQL, XSS, Command)
pytest -m injection

# Nur Authentication Tests
pytest -m auth

# Nur Authorization & Access Control Tests
pytest -m authz

# Nur E-Commerce Business Logic Tests
pytest -m business_logic

# Nur Session Security Tests
pytest -m session

# Bestimmte Test-Datei
pytest playwright_tests/tests/pentest/test_injection_attacks.py -v
```

### Test-Kategorien

#### 1. Injection Attacks (`-m injection`)

**Datei**: `playwright_tests/tests/pentest/test_injection_attacks.py`

Tests für:
- SQL Injection in Suchfeldern, Formularen
- Cross-Site Scripting (XSS) in Checkout, Produktbewertungen
- Command Injection in Datei-Operationen
- Path Traversal in Downloads

**Beispiel-Test:**
```python
@pytest.mark.pentest
@pytest.mark.injection
async def test_sql_injection_in_search(page: Page, base_url: str):
    """Testet Produktsuche auf SQL Injection-Anfälligkeit."""
```

#### 2. Authentication Security (`-m auth`)

**Datei**: `playwright_tests/tests/pentest/test_authentication.py`

Tests für:
- Brute-Force-Schutz
- Schwache Passwort-Policies
- Session Fixation
- Username Enumeration
- Default Credentials

#### 3. Authorization & Access Control (`-m authz`)

**Datei**: `playwright_tests/tests/pentest/test_authorization.py`

Tests für:
- IDOR (Insecure Direct Object References)
- Privilege Escalation
- Admin-Panel-Zugriff ohne Auth
- API-Endpoint-Schutz
- CORS-Fehlkonfigurationen

#### 4. E-Commerce Business Logic (`-m business_logic`)

**Datei**: `playwright_tests/tests/pentest/test_business_logic.py`

Tests für:
- **Price Manipulation** (Frontend & Backend)
- **Negative Quantity Injection**
- **Integer Overflow** bei Mengen
- **Inventory Bypass** (ausverkaufte Produkte bestellen)
- **Coupon Brute-Force**
- **Payment Bypass**
- **Race Conditions** (z.B. Einmal-Gutscheine mehrfach verwenden)

**Beispiel-Test:**
```python
@pytest.mark.pentest
@pytest.mark.business_logic
async def test_price_manipulation_frontend(page: Page, base_url: str):
    """Testet Price Manipulation via Frontend (DevTools/JavaScript)."""
```

#### 5. Session Security (`-m session`)

**Datei**: `playwright_tests/tests/pentest/test_session_security.py`

Tests für:
- Sichere Cookie-Attribute (HttpOnly, Secure, SameSite)
- Session-ID-Komplexität
- CSRF-Token-Validierung
- Session Hijacking
- Clickjacking-Schutz
- Security Headers (CSP, HSTS, X-Frame-Options)
- HTTPS-Only Enforcement

### Best Practices für Penetration Tests

1. **Autorisierung**: Immer schriftliche Genehmigung einholen
2. **Nur Test-Umgebungen**: Niemals auf Produktions-Systemen ohne explizite Erlaubnis
3. **Regelmäßige Ausführung**: In CI/CD-Pipeline integrieren (nur Staging)
4. **Dokumentation**: Gefundene Vulnerabilities sofort melden

### CI/CD Integration

```yaml
# .github/workflows/security-tests.yml
jobs:
  security-tests:
    runs-on: ubuntu-latest
    if: github.event_name != 'pull_request' || github.base_ref == 'staging'
    steps:
      - name: Run Penetration Tests
        run: pytest -m pentest
        env:
          SHOP_BASE_URL: ${{ secrets.STAGING_URL }}
```

**Wichtig**: Penetration Tests sollten **NICHT** auf Produktions-Umgebungen in CI/CD ausgeführt werden!

### Payload-Sammlung

Wiederverwendbare Attack-Payloads: `playwright_tests/utils/pentest_payloads.py`

Enthält:
- SQL Injection Payloads
- XSS Payloads
- Command Injection Payloads
- Path Traversal Payloads
- E-Commerce spezifische Payloads (Price Manipulation, Coupon Codes)

### Weiterführende Ressourcen

- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **OWASP Testing Guide**: https://owasp.org/www-project-web-security-testing-guide/
- **PortSwigger Web Security Academy**: https://portswigger.net/web-security

---

## Test-Szenarien

### Massentest: Bestellungen

Der primäre Massentest simuliert eine konfigurierbare Anzahl von Bestellungen mit verschiedenen Parametern.

**Ziele:**
- Validierung der Shop-Stabilität unter Last
- Erkennung von Race Conditions
- Performance-Baseline für Checkout-Flow

**Parameter:**
| Parameter | Beschreibung | Standard |
|-----------|--------------|----------|
| `anzahl` | Anzahl der Bestellungen | 100 |
| `parallel` | Gleichzeitige Browser-Instanzen | 5 |
| `produkte` | Liste der Produkt-IDs | Zufällige Auswahl |
| `zahlungsarten` | Zu testende Zahlungsarten | Alle aktiven |
| `laender` | Lieferländer | AT, DE |

**Erfolgskriterien:**
- Erfolgsrate ≥ 95%
- Durchschnittliche Checkout-Zeit < 60 Sekunden
- Keine HTTP 5xx Fehler

### Smoke Tests

Schnelle Validierung der Kernfunktionalität nach Deployments.

- [ ] Startseite erreichbar
- [ ] Produktsuche funktioniert
- [ ] Produkt zum Warenkorb hinzufügen
- [ ] Warenkorb anzeigen
- [ ] Checkout-Seite erreichbar
- [ ] Bestellung als Gast möglich

### Zahlungsarten-Matrix

Systematischer Test aller Zahlungsart/Land-Kombinationen.

| Zahlungsart | AT | DE | CH |
|-------------|----|----|-----|
| Rechnung | ✓ | ✓ | ✓ |
| Kreditkarte | ✓ | ✓ | ✓ |
| PayPal | ✓ | ✓ | - |
| Klarna | ✓ | ✓ | - |
| EPS | ✓ | - | - |

## Architektur

### Page Object Model

Alle Seiten-Interaktionen sind in Page Objects gekapselt für bessere Wartbarkeit.

```python
# Beispiel: checkout_page.py
class CheckoutPage(BasePage):
    
    # Selektoren
    EMAIL_INPUT = "css=#email"
    ADDRESS_FORM = "css=.checkout-address"
    PLACE_ORDER_BUTTON = "css=#place-order"
    
    async def fill_guest_address(self, address: dict):
        """Füllt das Adressformular für Gastbestellungen."""
        await self.page.fill(self.EMAIL_INPUT, address["email"])
        await self.page.fill("css=#firstName", address["first_name"])
        await self.page.fill("css=#lastName", address["last_name"])
        # ...
    
    async def place_order(self) -> str:
        """Schließt Bestellung ab und gibt Order-ID zurück."""
        await self.page.click(self.PLACE_ORDER_BUTTON)
        await self.page.wait_for_url("**/finish/**")
        return await self._extract_order_id()
```

### Massentest-Implementierung

```python
# Beispiel: test_checkout_mass.py
@pytest.mark.massentest
async def test_mass_orders(
    browser: Browser,
    mass_orders: int,
    parallel: int,
    products: list[str]
):
    """
    Führt n Bestellungen parallel aus.
    
    Args:
        mass_orders: Anzahl der Bestellungen
        parallel: Gleichzeitige Browser-Kontexte
        products: Liste der zu bestellenden Produkt-IDs
    """
    semaphore = asyncio.Semaphore(parallel)
    results = []
    
    async def single_order(order_num: int):
        async with semaphore:
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                product_id = random.choice(products)
                order_id = await execute_checkout(page, product_id)
                results.append({
                    "order_num": order_num,
                    "status": "success",
                    "order_id": order_id
                })
            except Exception as e:
                results.append({
                    "order_num": order_num,
                    "status": "failed",
                    "error": str(e)
                })
            finally:
                await context.close()
    
    # Alle Bestellungen parallel starten
    await asyncio.gather(*[
        single_order(i) for i in range(mass_orders)
    ])
    
    # Auswertung
    success_count = len([r for r in results if r["status"] == "success"])
    success_rate = success_count / len(results)
    
    assert success_rate >= 0.95, (
        f"Erfolgsrate {success_rate:.0%} unter Schwellwert 95%. "
        f"Fehlgeschlagen: {len(results) - success_count}/{len(results)}"
    )
```

## Reporting

### Playwright Reports

Nach jedem Testlauf werden HTML-Reports generiert:

```bash
# Report öffnen
npx playwright show-report reports/playwright
```

### Robot Framework Reports (ab Phase 3)

Robot Framework generiert automatisch:
- `report.html` – Übersichtlicher HTML-Report
- `log.html` – Detailliertes Ausführungslog
- `output.xml` – Maschinenlesbares Format für CI/CD

### Trace Viewer bei Fehlern

Bei fehlgeschlagenen Tests wird automatisch ein Trace erstellt:

```bash
# Trace analysieren
npx playwright show-trace reports/traces/failed-test.zip
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/e2e-tests.yml
name: E2E Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 6 * * *'  # Täglich 6:00 UTC

jobs:
  smoke-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install chromium
      
      - name: Run smoke tests
        run: pytest playwright_tests/ -m smoke
        env:
          SHOP_BASE_URL: ${{ secrets.STAGING_URL }}
      
      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-report
          path: reports/

  mass-tests:
    runs-on: ubuntu-latest
    if: github.event_name == 'schedule'
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install chromium
      
      - name: Run mass order tests
        run: |
          pytest playwright_tests/tests/test_checkout_mass.py \
            --mass-orders=100 \
            --parallel=10
        env:
          SHOP_BASE_URL: ${{ secrets.STAGING_URL }}
```

## Entwicklung

### Neue Tests hinzufügen

1. Page Object erstellen/erweitern in `playwright_tests/pages/`
2. Testfall in `playwright_tests/tests/` anlegen
3. Passende Marker setzen (`@pytest.mark.smoke`, `@pytest.mark.massentest`, etc.)
4. Lokal testen mit `pytest --headed`
5. PR erstellen

### Code-Stil

```bash
# Formatierung
black playwright_tests/
isort playwright_tests/

# Linting
ruff check playwright_tests/

# Type Checking
mypy playwright_tests/
```

## Bekannte Einschränkungen

- **Payment Gateway Mocking:** Echte Zahlungen werden nicht ausgeführt; Payment-Responses werden gemockt
- **Testdaten:** Tests verwenden dedizierte Testprodukte und -kunden
- **Rate Limiting:** Bei sehr hoher Parallelisierung können Shop-seitige Limits greifen

## Roadmap

- [x] Projektstruktur aufsetzen
- [ ] Phase 1: Playwright Massentests
  - [ ] Page Objects für Checkout-Flow
  - [ ] Massentest-Implementation
  - [ ] Payment-Mocking
  - [ ] Reporting-Integration
- [ ] Phase 2: Library Wrapper
  - [ ] Python Library für Robot Framework
  - [ ] Keyword-Definition
- [ ] Phase 3: Robot Framework
  - [ ] Suite-Struktur
  - [ ] Tagging-Konzept
  - [ ] CI/CD-Anpassung
- [ ] Phase 4: Test Management Interface
  - [ ] Jira-Integration
  - [ ] Rollenkonzept

## Mitwirkende

- Grüne Erde E-Commerce Team
- Strix Development

## Lizenz

Proprietär – Grüne Erde GmbH
