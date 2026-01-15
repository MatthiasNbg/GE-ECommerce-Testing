# Docker-First E2E Testing Setup

## Zusammenfassung

Docker-basiertes Setup für das Shopware 6 E2E Testing Framework mit:
- Headless Test-Ausführung im Container
- Trace Viewer für nachträgliche Analyse
- YAML-Konfiguration mit Profilen (staging, production, local)
- Integrierter Report-Server für Browser-Zugriff auf Ergebnisse

## Docker-Architektur

```
┌─────────────────────────────────────────────────────────┐
│  test-runner                                            │
│  - Python 3.11 + Playwright + Chromium                  │
│  - Führt Tests headless aus                             │
│  - Speichert Traces & Reports in /reports Volume        │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼ schreibt nach
┌─────────────────────────────────────────────────────────┐
│  reports/  (Volume, gemountet)                          │
│  ├── traces/        # Playwright Traces (.zip)          │
│  ├── html/          # HTML-Reports                      │
│  └── screenshots/   # Failure Screenshots               │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼ served durch
┌─────────────────────────────────────────────────────────┐
│  report-server                                          │
│  - nginx:alpine (minimal)                               │
│  - Statische Dateien unter localhost:8080               │
└─────────────────────────────────────────────────────────┘
```

## Projektstruktur

```
GE-ECommerce-Testing/
├── config/
│   ├── config.yaml              # Profile (staging, production, local)
│   └── .env.example             # Secret-Template
│
├── docker/
│   ├── Dockerfile               # Python + Playwright + Chromium
│   └── docker-compose.yml       # test-runner + report-server
│
├── playwright_tests/
│   ├── __init__.py
│   ├── conftest.py              # Pytest Fixtures, Profil-Laden
│   ├── config.py                # Pydantic Settings Klasse
│   │
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── base_page.py         # Basis-Klasse für Page Objects
│   │   └── checkout_page.py     # Checkout Page Object
│   │
│   └── tests/
│       ├── __init__.py
│       ├── test_smoke.py        # Einfacher Einstiegstest
│       └── test_checkout_mass.py # Massentests
│
├── reports/                     # Von Docker gemountet
│   └── .gitkeep
│
├── requirements.txt
└── README.md
```

## Konfiguration

### config/config.yaml

```yaml
profiles:
  staging:
    base_url: "https://staging.gruene-erde.com"
    timeout: 30000
    parallel_workers: 5
    headless: true

  production:
    base_url: "https://www.gruene-erde.com"
    timeout: 45000
    parallel_workers: 2
    headless: true

  local:
    base_url: "http://localhost:8000"
    timeout: 15000
    parallel_workers: 3
    headless: false

default_profile: staging

browser: chromium
locale: de-AT
trace_on_failure: true
screenshot_on_failure: true
```

### Secrets via .env

```bash
TEST_CUSTOMER_EMAIL=test@example.com
TEST_CUSTOMER_PASSWORD=geheim123
SHOP_ADMIN_USER=admin
SHOP_ADMIN_PASSWORD=admin123
```

## Workflow

### Tests ausführen

```bash
# Container bauen
docker-compose build

# Tests ausführen
docker-compose run test-runner pytest

# Mit spezifischem Profil
docker-compose run -e TEST_PROFILE=production test-runner pytest

# Nur Smoke-Tests
docker-compose run test-runner pytest -m smoke

# Massentests
docker-compose run test-runner pytest -m massentest --mass-orders=50
```

### Reports ansehen

```bash
# Report-Server läuft auf localhost:8080
# - /html/report.html     → Pytest HTML Report
# - /traces/              → Trace-Dateien
```

### Trace analysieren

```bash
# Lokal
npx playwright show-trace reports/traces/test-xyz.zip

# Online
# https://trace.playwright.dev → Trace-Datei hochladen
```

## Zu erstellende Dateien

| Datei | Beschreibung |
|-------|--------------|
| `docker/Dockerfile` | Python 3.11 + Playwright + Chromium |
| `docker/docker-compose.yml` | test-runner + report-server Services |
| `config/config.yaml` | Profile-Konfiguration |
| `config/.env.example` | Secret-Template |
| `playwright_tests/__init__.py` | Package Init |
| `playwright_tests/conftest.py` | Pytest Fixtures |
| `playwright_tests/config.py` | Pydantic Settings |
| `playwright_tests/pages/__init__.py` | Package Init |
| `playwright_tests/pages/base_page.py` | Basis Page Object |
| `playwright_tests/tests/__init__.py` | Package Init |
| `playwright_tests/tests/test_smoke.py` | Smoke Test |
| `reports/.gitkeep` | Placeholder für Reports |

## Zu verschiebende Dateien

| Von | Nach |
|-----|------|
| `checkout_page.py` | `playwright_tests/pages/checkout_page.py` |
| `test_checkout_mass.py` | `playwright_tests/tests/test_checkout_mass.py` |
