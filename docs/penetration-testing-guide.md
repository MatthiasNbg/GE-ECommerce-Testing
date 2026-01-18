# Penetration Testing Guide für E-Commerce Systeme

## Inhaltsverzeichnis

1. [Einführung in Penetration Testing](#einführung)
2. [Penetration Testing vs. andere Tests](#unterschiede)
3. [OWASP Top 10 für E-Commerce](#owasp-top-10)
4. [E-Commerce spezifische Angriffsvektoren](#e-commerce-angriffe)
5. [Automatisierte vs. Manuelle Tests](#test-strategien)
6. [Implementierung mit Playwright](#implementierung)
7. [Best Practices](#best-practices)
8. [Rechtliche & Ethische Aspekte](#rechtliches)

---

## Einführung in Penetration Testing {#einführung}

### Was sind Penetration Tests?

**Penetration Tests** (Pentests) sind **autorisierte, simulierte Cyberangriffe** auf ein System, eine Webanwendung oder ein Netzwerk mit dem Ziel:

- **Sicherheitslücken zu identifizieren**, bevor echte Angreifer sie ausnutzen
- **Schwachstellen aktiv auszunutzen** (in kontrollierter Umgebung), um deren Auswirkungen zu verstehen
- **Sicherheitsmechanismen zu testen** und deren Wirksamkeit zu überprüfen
- **Realistische Angriffsszenarien** durchzuspielen

### Zielsetzung

Penetration Tests beantworten Fragen wie:
- Können Angreifer sensible Kundendaten stehlen?
- Ist es möglich, Preise zu manipulieren?
- Können Zahlungsprozesse umgangen werden?
- Sind Admin-Bereiche ausreichend geschützt?
- Können Race Conditions ausgenutzt werden?

### Wichtige Einschränkungen

⚠️ **KRITISCH**: Penetration Tests dürfen NUR auf autorisierten Systemen durchgeführt werden!

- **Autorisierung erforderlich**: Schriftliche Genehmigung vom Systemeigentümer
- **Produktionsumgebungen**: Nur mit expliziter Erlaubnis und in Wartungsfenstern
- **Staging/Test-Umgebungen**: Bevorzugter Ort für aggressive Tests
- **Rechtliche Konsequenzen**: Unautorisierte Tests können Strafverfolgung nach sich ziehen

---

## Penetration Testing vs. andere Tests {#unterschiede}

| Test-Typ | Ziel | Perspektive | Beispiel |
|----------|------|-------------|----------|
| **Unit Tests** | Prüfen einzelne Funktionen | Developer | Testet `calculatePrice()` Funktion |
| **Integration Tests** | Prüfen Zusammenspiel von Komponenten | Developer | Testet Warenkorb + Zahlungsgateway |
| **End-to-End Tests** | Prüfen komplette User Journeys | User | Testet gesamten Checkout-Flow |
| **Penetration Tests** | Aktiv Sicherheitslücken ausnutzen | **Angreifer** | Versucht Preise zu manipulieren |

**Der entscheidende Unterschied**: Pentests nehmen die Perspektive eines Angreifers ein und versuchen **aktiv, Sicherheitsmaßnahmen zu umgehen**.

---

## OWASP Top 10 für E-Commerce {#owasp-top-10}

Die [OWASP Top 10](https://owasp.org/www-project-top-ten/) sind die kritischsten Sicherheitsrisiken für Webanwendungen.

### 1. Broken Access Control

**Was ist das?**
Nutzer können auf Ressourcen zugreifen, für die sie keine Berechtigung haben.

**E-Commerce Beispiele:**
- Bestellungen anderer Kunden einsehen/ändern
- Zugriff auf Admin-Panel ohne Admin-Rechte
- Produkte mit deaktiviertem Status kaufen

**Angriffsvektoren:**
```http
# Insecure Direct Object Reference (IDOR)
GET /api/orders/12345  # Order-ID erraten/ändern
GET /admin/products    # Admin-Route ohne Auth
```

**Playwright Test-Ansatz:**
```python
# Versuch, fremde Bestellung zu öffnen
await page.goto(f"{base_url}/order/999999")
# Erwartung: 403 Forbidden oder Redirect zu Login
```

---

### 2. Injection (SQL, XSS, Command)

**Was ist das?**
Schadsoftware wird durch unsichere Eingabefelder eingeschleust.

#### 2.1 SQL Injection

**E-Commerce Beispiele:**
- Produktsuche manipulieren
- Login-Formulare umgehen
- Datenbank-Dumps extrahieren

**Angriffsvektoren:**
```sql
-- In Suchfeld eingeben:
' OR '1'='1
' UNION SELECT * FROM users--
admin'--
```

**Playwright Test-Ansatz:**
```python
# SQL Injection in Produktsuche
search_payloads = [
    "' OR '1'='1",
    "' UNION SELECT null, username, password FROM users--",
    "admin'--"
]

for payload in search_payloads:
    await page.fill("#search-input", payload)
    await page.click("#search-button")

    # Prüfen auf SQL-Fehler in Antwort
    content = await page.content()
    assert "SQL syntax error" not in content
    assert "mysql_fetch" not in content
```

#### 2.2 Cross-Site Scripting (XSS)

**E-Commerce Beispiele:**
- Schadcode in Produktbewertungen
- XSS in Checkout-Formularfeldern
- Stored XSS in Kundenprofilen

**Angriffsvektoren:**
```html
<!-- In Namen-Feld eingeben -->
<script>alert('XSS')</script>
<img src=x onerror=alert('XSS')>
<svg onload=alert('XSS')>
```

**Playwright Test-Ansatz:**
```python
xss_payloads = [
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert('XSS')>",
    "javascript:alert('XSS')"
]

for payload in xss_payloads:
    await page.fill("#first-name", payload)
    await page.click("#submit")

    # Dialog-Handler registrieren (sollte NICHT auslösen)
    page.on("dialog", lambda dialog: pytest.fail("XSS executed!"))

    # Prüfen, ob Payload escaped wurde
    escaped_content = await page.inner_html("#customer-name")
    assert "<script>" not in escaped_content
```

---

### 3. Cryptographic Failures

**Was ist das?**
Sensible Daten werden unverschlüsselt übertragen oder gespeichert.

**E-Commerce Beispiele:**
- Kreditkartendaten im Klartext
- Passwörter ohne Hashing
- Session-Tokens über HTTP statt HTTPS

**Playwright Test-Ansatz:**
```python
# Prüfen, dass alle Requests über HTTPS laufen
page.on("request", lambda request:
    assert request.url.startswith("https://"),
    f"Insecure HTTP request: {request.url}"
)

# Prüfen, dass Passwörter nicht im Klartext gesendet werden
page.on("request", lambda request:
    assert "password=123456" not in request.url,
    "Password sent in URL!"
)
```

---

### 4. Identification and Authentication Failures

**Was ist das?**
Schwache oder fehlerhafte Authentifizierungsmechanismen.

**E-Commerce Beispiele:**
- Schwache Passwort-Policies
- Brute-Force-Angriffe möglich
- Session Fixation
- Fehlende Multi-Faktor-Authentifizierung

**Angriffsvektoren:**
```python
# Brute-Force Login
common_passwords = ["123456", "password", "admin123"]

for pwd in common_passwords:
    await page.fill("#password", pwd)
    await page.click("#login")

    # Prüfen auf Rate Limiting / CAPTCHA
```

---

### 5. Security Misconfiguration

**Was ist das?**
Unsichere Default-Konfigurationen, unnötige Features, Debug-Modus in Produktion.

**E-Commerce Beispiele:**
- Debug-Modus aktiviert (Stack Traces sichtbar)
- Directory Listing aktiviert
- Default Admin-Passwörter
- Unnötige HTTP-Methoden (PUT, DELETE)

**Playwright Test-Ansatz:**
```python
# Prüfen auf Debug-Informationen
response = await page.goto(f"{base_url}/nonexistent")
content = await page.content()

assert "Stack trace" not in content
assert "Shopware\\Core\\" not in content  # Shopware-spezifisch
assert "/var/www/" not in content
```

---

### 6. Vulnerable and Outdated Components

**Was ist das?**
Verwendung von Libraries/Frameworks mit bekannten Sicherheitslücken.

**E-Commerce Beispiele:**
- Veraltete Shopware-Version
- Vulnerable jQuery-Version
- Ungesicherte Dependencies

**Test-Ansatz:**
- Dependency-Scanning-Tools (npm audit, Snyk, OWASP Dependency-Check)
- Versionsprüfung via HTTP-Header oder JavaScript

---

### 7. Software and Data Integrity Failures

**Was ist das?**
Code/Daten werden ohne Integritätsprüfung verarbeitet.

**E-Commerce Beispiele:**
- Unsignierte Auto-Updates
- Deserialisierung von untrusted Data
- CI/CD ohne Signaturprüfung

---

### 8. Security Logging and Monitoring Failures

**Was ist das?**
Unzureichendes Logging, fehlende Alerting bei Angriffen.

**E-Commerce Beispiele:**
- Fehlgeschlagene Logins werden nicht geloggt
- Keine Alerts bei massenhaften Bestellungen
- SQL Injection-Versuche werden nicht erkannt

**Test-Ansatz:**
- Manuelle Überprüfung der Log-Files
- Simulierte Angriffe → Prüfen, ob Alerts ausgelöst werden

---

### 9. Server-Side Request Forgery (SSRF)

**Was ist das?**
Angreifer können Server dazu bringen, Requests an beliebige Ziele zu senden.

**E-Commerce Beispiele:**
- Produktbild-Upload mit URL → Server fetcht URL
- Webhook-Callbacks manipulieren

**Angriffsvektoren:**
```python
# In Produktbild-URL-Feld:
http://localhost/admin
http://169.254.169.254/latest/meta-data/  # AWS Metadata
```

---

### 10. Cross-Site Request Forgery (CSRF)

**Was ist das?**
Angreifer kann authentifizierte User dazu bringen, ungewollte Aktionen auszuführen.

**E-Commerce Beispiele:**
- Ungewollte Bestellungen auslösen
- Adresse ändern
- Passwort ändern

**Playwright Test-Ansatz:**
```python
# Prüfen auf CSRF-Tokens in Formularen
form_html = await page.inner_html("form#checkout")
assert 'name="_csrf_token"' in form_html or 'name="csrf"' in form_html
```

---

## E-Commerce spezifische Angriffsvektoren {#e-commerce-angriffe}

Zusätzlich zu OWASP Top 10 gibt es E-Commerce-spezifische Schwachstellen:

### 1. Price Manipulation

**Beschreibung**: Angreifer ändern Produktpreise im Checkout-Prozess.

**Angriffsvektoren:**
```javascript
// Browser Console / DevTools
document.querySelector("#price-input").value = "0.01";

// HTTP Request Manipulation (Burp Suite, OWASP ZAP)
POST /checkout
{
  "product_id": "123",
  "price": 0.01  // Statt 99.99
}
```

**Playwright Test:**
```python
async def test_price_manipulation(page):
    """Versucht, Produktpreis zu manipulieren."""

    # Produkt zum Warenkorb hinzufügen
    await page.goto(f"{base_url}/product/expensive-item")
    original_price = await page.text_content(".product-price")
    await page.click("#add-to-cart")

    # JavaScript ausführen, um Preis zu ändern
    await page.evaluate("""
        document.querySelectorAll('.price').forEach(el => {
            el.textContent = '0.01';
            el.setAttribute('data-price', '0.01');
        });
    """)

    # Checkout abschließen
    await page.goto(f"{base_url}/checkout")
    await page.click("#place-order")

    # ERFOLGS-KRITERIUM: Server sollte Original-Preis verwenden
    order_total = await page.text_content(".order-total")
    assert original_price in order_total, "Price manipulation succeeded!"
```

---

### 2. Inventory Bypass

**Beschreibung**: Produkte bestellen, die nicht auf Lager sind.

**Angriffsvektoren:**
```javascript
// Ausverkauftes Produkt - Button manuell enablen
document.querySelector("#add-to-cart").disabled = false;
```

**Playwright Test:**
```python
async def test_out_of_stock_bypass(page):
    """Versucht, ausverkauftes Produkt zu bestellen."""

    # Produkt, das ausverkauft ist
    await page.goto(f"{base_url}/product/sold-out-item")

    # Button sollte disabled sein
    is_disabled = await page.is_disabled("#add-to-cart")
    assert is_disabled, "Out-of-stock product has enabled button"

    # JavaScript: Button enablen
    await page.evaluate('document.querySelector("#add-to-cart").disabled = false')
    await page.click("#add-to-cart")

    # Server sollte Bestellung ablehnen
    error_msg = await page.text_content(".error-message")
    assert "nicht verfügbar" in error_msg or "out of stock" in error_msg.lower()
```

---

### 3. Coupon/Promo Code Abuse

**Beschreibung**: Gutscheine mehrfach verwenden oder ungültige Codes akzeptieren.

**Angriffsvektoren:**
```python
# Brute-Force Gutscheincodes
for code in ["SAVE10", "SAVE20", "WELCOME", "PROMO2024"]:
    await page.fill("#coupon-code", code)
    await page.click("#apply-coupon")
```

---

### 4. Payment Bypass

**Beschreibung**: Zahlungsprozess umgehen und Bestellungen ohne Zahlung abschließen.

**Angriffsvektoren:**
- Payment-Gateway-Callback manipulieren
- Payment-Status direkt auf "paid" setzen
- Race Condition zwischen Payment & Order-Completion

**Playwright Test:**
```python
async def test_payment_bypass(page):
    """Versucht, Bestellung ohne Zahlung abzuschließen."""

    # Checkout-Prozess bis Payment
    await complete_checkout_until_payment(page)

    # Direkt zur "Order Completed"-Seite springen (ohne Payment)
    await page.goto(f"{base_url}/checkout/finish?orderId=12345")

    # Server sollte Redirect zu Payment oder Error zeigen
    current_url = page.url
    assert "/finish" not in current_url or "error" in current_url
```

---

### 5. Negative Quantity / Integer Overflow

**Beschreibung**: Negative Mengen oder extreme Werte im Warenkorb.

**Angriffsvektoren:**
```javascript
// Negative Menge
document.querySelector("#quantity").value = "-5";

// Integer Overflow
document.querySelector("#quantity").value = "2147483648";
```

**Playwright Test:**
```python
async def test_negative_quantity(page):
    """Versucht, negative Menge einzugeben."""

    await page.goto(f"{base_url}/product/item")

    # Negative Menge via DevTools
    await page.evaluate('document.querySelector("#quantity").value = "-5"')
    await page.click("#add-to-cart")

    # Server sollte Fehler oder 0 anzeigen
    cart_quantity = await page.text_content(".cart-quantity")
    assert int(cart_quantity) >= 0, "Negative quantity accepted!"
```

---

### 6. Order Manipulation (IDOR)

**Beschreibung**: Bestellungen anderer Kunden einsehen/ändern.

**Angriffsvektoren:**
```http
GET /order/10001  # Eigene Order
GET /order/10002  # Fremde Order → sollte 403 geben
```

**Playwright Test:**
```python
async def test_order_idor(page, context):
    """Versucht, fremde Bestellungen zu öffnen."""

    # User A: Bestellung erstellen
    order_id_a = await create_order_as_user_a(page)

    # User B: Neuer Browser-Context
    page_b = await context.new_page()
    await login_as_user_b(page_b)

    # Versuche, Order von User A zu öffnen
    response = await page_b.goto(f"{base_url}/order/{order_id_a}")

    # ERFOLGS-KRITERIUM: 403 Forbidden oder 404 Not Found
    assert response.status in [403, 404], f"IDOR vulnerability! Status: {response.status}"
```

---

### 7. Race Conditions

**Beschreibung**: Gleichzeitige Requests führen zu inkonsistentem Zustand.

**Beispiel**: Gutschein mehrfach verwenden durch parallele Requests.

**Playwright Test:**
```python
async def test_coupon_race_condition(browser):
    """Versucht, Gutschein mehrfach zu verwenden."""

    # 10 parallele Browser-Contexts
    contexts = [await browser.new_context() for _ in range(10)]
    pages = [await ctx.new_page() for ctx in contexts]

    # Alle verwenden denselben Einmal-Gutschein
    async def apply_coupon(page):
        await checkout_with_coupon(page, "SINGLE_USE_CODE")

    # Parallel ausführen
    results = await asyncio.gather(*[apply_coupon(p) for p in pages])

    # ERFOLGS-KRITERIUM: Nur 1 Request sollte erfolgreich sein
    successful = sum(1 for r in results if r.success)
    assert successful == 1, f"Race condition: {successful} orders with same coupon!"
```

---

## Automatisierte vs. Manuelle Tests {#test-strategien}

### Automatisierte Penetration Tests

**Vorteile:**
- Schnell wiederholbar
- CI/CD-Integration möglich
- Regression-Testing
- Konsistente Ausführung

**Einschränkungen:**
- Können nur bekannte Angriffsmuster testen
- Keine kreative "Hacker-Denkweise"
- Komplex zu implementieren

**Beste Tools:**
- **Playwright/Selenium**: Browser-basierte Tests
- **OWASP ZAP**: Automatisierter Vulnerability Scanner
- **Burp Suite Pro**: Automatische Scans
- **SQLMap**: SQL Injection-Tests

**Unser Ansatz:**
```python
# playwright_tests/tests/pentest/test_injection_attacks.py
@pytest.mark.pentest
@pytest.mark.injection
async def test_sql_injection_in_search(page):
    """Automatisierter SQL Injection Test."""
    # Implementation siehe unten
```

---

### Manuelle Penetration Tests

**Vorteile:**
- Kreative Angriffe möglich
- Business-Logic-Flaws erkennen
- Komplexe Angriffsketten

**Einschränkungen:**
- Zeitaufwändig
- Erfordert Expertise
- Schwer reproduzierbar

**Beste Tools:**
- **Burp Suite**: Manuelle Request-Manipulation
- **OWASP ZAP**: Intercepting Proxy
- **Browser DevTools**: JavaScript-Manipulation

---

### Hybrid-Ansatz (Empfohlen)

Kombination aus automatisierten Tests für bekannte Angriffe + manuelle Tests für komplexe Szenarien.

**Workflow:**
1. **Automatisiert**: OWASP Top 10-Checks (täglich in CI/CD)
2. **Manuell**: Quartalweise professionelle Pentests
3. **Bug Bounty**: Community-basierte Security-Reviews

---

## Implementierung mit Playwright {#implementierung}

### Projekt-Struktur

```
playwright_tests/
├── tests/
│   └── pentest/
│       ├── __init__.py
│       ├── test_injection_attacks.py
│       ├── test_authentication.py
│       ├── test_authorization.py
│       ├── test_business_logic.py
│       └── test_session_security.py
├── utils/
│   └── pentest_payloads.py  # SQL Injection, XSS payloads
└── conftest.py
```

### Pytest Marker

```python
# pytest.ini
[pytest]
markers =
    pentest: Penetration testing markers
    injection: Injection attack tests (SQL, XSS, etc.)
    auth: Authentication security tests
    authz: Authorization & Access Control tests
    business_logic: E-Commerce business logic tests
    session: Session security tests
```

### Beispiel-Implementierung

```python
# playwright_tests/tests/pentest/test_injection_attacks.py

import pytest
from playwright.async_api import Page, expect

# SQL Injection Payloads
SQL_INJECTION_PAYLOADS = [
    "' OR '1'='1",
    "' OR '1'='1' --",
    "' OR '1'='1' /*",
    "admin'--",
    "' UNION SELECT NULL--",
    "1' AND '1'='1",
]

# XSS Payloads
XSS_PAYLOADS = [
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert('XSS')>",
    "<svg onload=alert('XSS')>",
    "javascript:alert('XSS')",
    "<iframe src='javascript:alert(\"XSS\")'></iframe>",
]


@pytest.mark.pentest
@pytest.mark.injection
async def test_sql_injection_in_search(page: Page, base_url: str):
    """
    Testet Produktsuche auf SQL Injection-Anfälligkeit.

    ERWARTUNG: Alle Payloads sollten escaped/validiert werden.
    """

    for payload in SQL_INJECTION_PAYLOADS:
        await page.goto(f"{base_url}/search")
        await page.fill("input[name='search']", payload)
        await page.click("button[type='submit']")

        # Warte auf Ergebnis
        await page.wait_for_load_state("networkidle")

        content = await page.content()

        # Prüfe auf SQL-Fehler
        sql_errors = [
            "SQL syntax error",
            "mysql_fetch",
            "mysqli",
            "PDOException",
            "SQLSTATE",
            "syntax error at or near"
        ]

        for error in sql_errors:
            assert error.lower() not in content.lower(), (
                f"SQL Injection vulnerability detected! "
                f"Payload '{payload}' caused SQL error: {error}"
            )


@pytest.mark.pentest
@pytest.mark.injection
async def test_xss_in_checkout_fields(page: Page, base_url: str):
    """
    Testet Checkout-Formulare auf XSS-Anfälligkeit.

    ERWARTUNG: Alle Payloads sollten escaped werden.
    """

    # Dialog-Handler: Falls XSS ausgeführt wird
    dialog_triggered = False

    def handle_dialog(dialog):
        nonlocal dialog_triggered
        dialog_triggered = True
        dialog.dismiss()

    page.on("dialog", handle_dialog)

    # Zum Checkout
    await page.goto(f"{base_url}/checkout")

    for payload in XSS_PAYLOADS:
        # In verschiedene Felder eingeben
        fields = [
            "input[name='firstName']",
            "input[name='lastName']",
            "input[name='street']",
            "input[name='city']",
        ]

        for field in fields:
            await page.fill(field, payload)

        await page.click("button[name='submit']")
        await page.wait_for_timeout(1000)

        # XSS sollte NICHT ausgelöst werden
        assert not dialog_triggered, (
            f"XSS vulnerability detected! Payload '{payload}' executed."
        )

        # Prüfe, ob Payload escaped wurde
        content = await page.content()
        assert "<script>" not in content, "Script tag not escaped!"


@pytest.mark.pentest
@pytest.mark.injection
async def test_command_injection_in_file_operations(page: Page, base_url: str):
    """
    Testet Datei-Upload/-Download auf Command Injection.

    ERWARTUNG: Shell-Befehle sollten nicht ausgeführt werden.
    """

    command_payloads = [
        "; ls -la",
        "| cat /etc/passwd",
        "& whoami",
        "`id`",
        "$(whoami)",
    ]

    for payload in command_payloads:
        # Beispiel: Dateiname mit Command Injection
        filename = f"invoice{payload}.pdf"

        await page.goto(f"{base_url}/order/download?file={filename}")

        content = await page.content()

        # Prüfe, ob Shell-Befehle ausgeführt wurden
        shell_outputs = [
            "root:x:0:0",  # /etc/passwd
            "uid=",        # id/whoami output
            "total ",      # ls output
        ]

        for output in shell_outputs:
            assert output not in content, (
                f"Command Injection vulnerability! "
                f"Payload '{payload}' executed shell command."
            )
```

---

## Best Practices {#best-practices}

### 1. Sicherheits-Anforderungen vor Entwicklung

✅ **DO**: Security Requirements in User Stories einbauen
```
User Story: Als Admin möchte ich Produkte bearbeiten
Acceptance Criteria:
- [ ] Nur Admins können Produkte bearbeiten
- [ ] Input-Validierung für alle Felder
- [ ] XSS-Protection auf allen Eingaben
- [ ] CSRF-Token in Formularen
```

❌ **DON'T**: Security als Nachgedanken

---

### 2. Defense in Depth

Mehrschichtige Sicherheit statt Single Point of Failure:

```
Layer 1: Input Validation (Frontend)
Layer 2: Input Sanitization (Backend)
Layer 3: Parameterized Queries (Database)
Layer 4: WAF (Web Application Firewall)
Layer 5: Rate Limiting
```

---

### 3. Secure Coding Guidelines

**Input Validation:**
```python
# ❌ Unsicher
search_term = request.GET['q']
sql = f"SELECT * FROM products WHERE name = '{search_term}'"

# ✅ Sicher
search_term = request.GET.get('q', '')
sql = "SELECT * FROM products WHERE name = %s"
cursor.execute(sql, (search_term,))
```

**Output Encoding:**
```python
# ❌ Unsicher
return f"<h1>Hello {user_name}</h1>"

# ✅ Sicher
from html import escape
return f"<h1>Hello {escape(user_name)}</h1>"
```

---

### 4. Security Testing in CI/CD

```yaml
# .github/workflows/security-tests.yml
name: Security Tests

on: [push, pull_request]

jobs:
  pentest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Penetration Tests
        run: pytest -m pentest

      - name: OWASP Dependency Check
        uses: dependency-check/Dependency-Check_Action@main

      - name: Snyk Security Scan
        uses: snyk/actions/node@master
```

---

### 5. Regelmäßige Security Audits

- **Täglich**: Automatisierte Pentests in CI/CD
- **Wöchentlich**: Dependency-Scans
- **Monatlich**: Manual Security Review
- **Quartalsweise**: Professioneller Pentest durch externe Firma
- **Jährlich**: Compliance-Audit (DSGVO, PCI-DSS)

---

## Rechtliche & Ethische Aspekte {#rechtliches}

### ⚠️ Rechtliche Grundlagen

**Computer Fraud and Abuse Act (USA)**
- Unautorisierter Zugriff auf Computersysteme = Straftat
- Strafen: Bis zu 10 Jahre Gefängnis + Geldstrafen

**StGB §202a (Deutschland) - Ausspähen von Daten**
- Unautorisiertes Verschaffen von Daten = Straftat
- Strafen: Freiheitsstrafe bis zu 3 Jahren oder Geldstrafe

**DSGVO Artikel 32 (EU)**
- Unternehmen müssen "geeignete technische und organisatorische Maßnahmen" treffen
- Penetration Tests = Nachweis für Security Measures

---

### ✅ Ethische Richtlinien

**1. Autorisierung einholen**
- Schriftliche Genehmigung vom System-Owner
- Scope klar definieren (welche Systeme, welche Methoden)
- Zeitfenster festlegen

**2. Responsible Disclosure**
Falls Schwachstellen gefunden werden:
1. **NICHT** öffentlich machen
2. System-Owner **sofort** informieren
3. **Angemessene Frist** zur Behebung geben (30-90 Tage)
4. Erst dann (optional) veröffentlichen

**3. Minimaler Schaden**
- Keine produktiven Daten löschen/ändern
- Keine DoS-Angriffe
- Keine unnötigen Störungen

---

### 🛡️ Bug Bounty Programme

Alternative zu eigenem Pentest: Bug Bounty-Plattformen nutzen

**Vorteile:**
- Community von Security-Experten
- Pay-per-Bug (kein Upfront-Cost)
- Continuous Testing

**Plattformen:**
- HackerOne
- Bugcrowd
- Intigriti
- YesWeHack

---

## Zusammenfassung

Penetration Testing ist ein **essentieller Bestandteil** der Sicherheitsstrategie für E-Commerce-Systeme:

1. **Identifiziert Schwachstellen**, bevor Angreifer sie finden
2. **Validiert Sicherheitsmaßnahmen** in realistischen Szenarien
3. **Kombiniert automatisierte & manuelle Tests** für maximale Abdeckung
4. **Erfordert Autorisierung** und ethisches Handeln
5. **Sollte regelmäßig durchgeführt werden** (nicht nur einmalig)

**Nächste Schritte:**
- Automatisierte Pentests in diesem Projekt einrichten
- Regelmäßige Test-Runs in CI/CD
- Quartalsweise externe Pentests
- Bug Bounty-Programm evaluieren

---

## Weitere Ressourcen

- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **OWASP Testing Guide**: https://owasp.org/www-project-web-security-testing-guide/
- **PortSwigger Web Security Academy**: https://portswigger.net/web-security
- **OWASP ZAP**: https://www.zaproxy.org/
- **Burp Suite**: https://portswigger.net/burp
- **PCI DSS**: https://www.pcisecuritystandards.org/

---

**Autoren**: Grüne Erde E-Commerce Team
**Letzte Aktualisierung**: 2026-01-18
**Version**: 1.0
