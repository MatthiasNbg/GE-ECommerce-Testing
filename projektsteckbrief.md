# Projektsteckbrief

---

**Matthias Sax GmbH**
Mühlstraße 18
90762 Fürth

**Telefon:** (+49) 151 20 792 782
**E-Mail:** m.sax@matthias-sax.de

---

## Projektübersicht

| **Auftraggeber** | Grüne Erde GmbH, Scharnstein, Österreich |
|------------------|------------------------------------------|
| **Rolle** | Architekt, IT Projektmanager E-Commerce |
| **Branche** | E-Commerce, Nachhaltiger Handel (Möbel, Textilien, Naturprodukte) |
| **Projektart** | E-Commerce-Transformation, Systemintegration, Test-Automatisierung |
| **Team-Größe** | 15+ Personen (inkl. externe Dienstleister) |

---

## Aufgabenbereiche

### Projektleitung & Organisation

• Steuerung eines komplexen E-Commerce-Programms mit fachlichen und technischen Teilprojekten
• Leitung von Workshops mit Stakeholdern, Fachbereichen und Implementierungspartnern
• Ressourcen- und Terminverantwortung; Steuerung externer Dienstleister (Strix, Patchworks u. a.)
• Etablierung hybrider Projektmethodik (Scrum / klassisch) und Reporting an Management

---

### Systemarchitektur, Integration & PIM-Einführung

• Definition der Zielarchitektur zwischen Shopware, Odoo, Pimcore, Emarsys und Nosto
• Leitung der Einführung des PIM-Systems (Pimcore) inkl. Prozessanalyse und Datenmodellierung
• Aufbau von Attributgruppen, Klassen, Workflows und Übersetzungslogik
• Gestaltung und Dokumentation der Datenflüsse (Shopware ↔ Odoo ↔ Pimcore)
• Definition von Synchronisations-, Mapping- und Validierungsregeln
• Sicherstellung der Datenqualität und Governance über Systemgrenzen hinweg

---

### Performance-Monitoring & Integration

**Eigenentwicklung „PatchworksAnalyzer"**
Performance-Analyse-Tool für Datenintegrationsflows

**Kernfunktionen:**
- Automatisierte Erkennung von Performance-Bottlenecks (N+1 Queries, Burst Patterns, Duplicate Requests, Slow Operations)
- Queue-basiertes Log-Fetching-System mit Retry-Logik und Parallelisierbarkeit für skalierbare Datenverarbeitung
- Web-Dashboard mit interaktiven KPIs, Zeitverläufen, System-Statistiken und detaillierten Request-Analysen
- REST-API für Flow-Run-Statistiken, Performance-Insights, HTTP-Error-Analysen und Duplicate Detection
- Generierung interaktiver HTML-Reports mit Filter- und Drill-Down-Funktionen
- Dark/Light-Mode, responsives Design und Request-Detail-Modal mit Syntax-Highlighting
- GDPR-konformes Sanitizing sensibler Daten (Authorization-Header, JWT-Masking)

**Ergebnisse:**
- Identifikation und Dokumentation von Anti-Patterns in der Systemkommunikation
- Grundlage für Optimierungen der Datenintegration und Reduktion von API-Calls um >30%
- Kontinuierliches Monitoring der Integration zwischen Shopware, Odoo, Pimcore, Emarsys und Nosto

---

### Testing & Qualitätssicherung

#### Test-Management-System „Testpanda"

**Eigenentwicklung:** Web-basierte E2E-Testplattform (PHP/Slim 4, MySQL)

**Kernfunktionen:**
- Rollenbasierte Zugriffskontrolle (Tester, Projektleiter, Admin)
- Excel-Import für Testszenarien mit automatischer Verarbeitung und Screenshot-Verwaltung
- Pool-Management zur Zuweisung von Testvarianten an Tester-Gruppen
- Strukturierte Testausführung mit Step-by-Step-Dokumentation und Statusverfolgung
- Integriertes Bug-Tracking mit Screenshot-Upload, Kommentarfunktion und Statusworkflow
- Dashboard mit KPIs (Testfortschritt, Bug-Statistiken, Tester-Performance)
- Geplante Jira-Integration für bidirektionales Defect-Management

---

#### Umfassendes Testkonzept mit 171 Testfällen

**Entwicklung und Dokumentation von 171 strukturierten Testfällen** in 10 Kategorien:

##### 🏠 Smoke Tests (5 Tests)
Basis-Funktionalität für schnelles Feedback
- Homepage-Verfügbarkeit, Produktseiten-Rendering, Navigation
- Produkt zum Warenkorb, Checkout-Erreichbarkeit, Grundfunktionen der Suche

##### 🛒 Critical Path Tests (8 Tests)
Umsatzrelevante Business-Flows
- Vollständiger Gast-Checkout (AT, DE, CH)
- Registrierter User-Checkout mit Account-Persistenz
- Zahlungsarten-Verfügbarkeit pro Land (Kreditkarte, Rechnung, Vorkasse, PayPal, etc.)
- Warenkorb-Persistenz über Sessions hinweg

##### 🛍️ Feature Tests – Warenkorb (8 Tests)
- Produkt hinzufügen/entfernen, Mengenänderung
- Preisberechnung (Brutto/Netto, MwSt.)
- Warenkorbpersistenz zwischen Seiten
- Leerer Warenkorb-Status

##### 🔍 Feature Tests – Suche (6 Tests)
- Produktsuche nach Name, Kategorie, Attributen
- Autocomplete-Funktionalität
- Filter (Preis, Farbe, Größe, etc.)
- Sonderzeichen und Fehlerbehandlung

##### 👤 Feature Tests – Account (8 Tests)
- Registrierung (Gültige/Ungültige Eingaben)
- Login/Logout, Passwort-Validierung
- Profilbearbeitung, Adressverwaltung
- Bestellhistorie

##### 📦 Feature Tests – Versandarten (98 Tests)
PLZ-basierte Logistikpartner-Zuordnung
- **Österreich (26 Tests):** Post, Wetsch (Vorarlberg), Fink (Wien, NÖ, OÖ, Steiermark), Cargoe (NÖ, Wien, Burgenland), Thurner (Salzburg)
- **Deutschland (68 Tests):** Post, Logsens Nord/Ost/Süd/West (regionale PLZ-Bereiche), Thurner (Hessen, BW, Bayern, Franken)
- **Schweiz (4 Tests):** Post, Spedition Kuoni (landesweit)
- Min/Max-PLZ-Grenzwertprüfung pro Logistikpartner und Region

##### 🎟️ Feature Tests – Promotions (8 Tests)
- Rabattcodes (Prozent, Fix, Mindestbestellwert)
- Versandkostenfrei-Aktionen
- Nicht-rabattierbarer Artikel-Status
- Kombinierbarkeit von Aktionen

##### 📊 Data Validation Tests (10 Tests)
Datenqualität und Konsistenz
- Preise (Anzeige vs. Checkout)
- Versandkosten-Konfiguration pro Land
- MwSt.-Berechnung (AT 20%, DE 19%, CH 7.7%)
- Produktverfügbarkeit und Lagerbestand

##### 🔄 Regression Tests (15 Tests)
Stabilität nach Änderungen
- Legacy Payment-Selection nach Refactoring
- Adressvalidierungsregeln (PLZ-Format, Pflichtfelder)
- Rabattcode-Anwendung nach Checkout-Änderungen
- Browser-Kompatibilität (Chrome, Firefox, Safari)

##### ⚡ Load & Performance Tests (5 Tests)
- Massentest: 150 parallele Bestellungen (Race Conditions, Stabilität)
- Performance-Baseline: Response-Zeiten < 2s (Checkout-Flow)
- Inventory Race Conditions (letztes Produkt von 10 Usern gleichzeitig)
- Stress-Test: 1000 Bestellungen in 60 Minuten
- API-Performance-Monitoring (Patchworks-Integration)

##### 🔒 Security Testing – Penetration Tests (OWASP Top 10)
- **Injection Attacks:** SQL Injection, XSS (Suche, Checkout, Produktbewertungen), Command Injection, Path Traversal
- **Authentication Security:** Brute-Force-Schutz, Session Fixation, Username Enumeration, Default Credentials
- **Authorization & Access Control:** IDOR, Privilege Escalation, Admin-Panel-Schutz, API-Endpoint-Security, CORS
- **E-Commerce Business Logic:** Price Manipulation (Frontend/Backend), Negative Quantity Injection, Integer Overflow, Inventory Bypass, Coupon Brute-Force, Payment Bypass, Race Conditions
- **Session Security:** Cookie-Attribute (HttpOnly, Secure, SameSite), CSRF-Token-Validierung, Clickjacking-Schutz, Security Headers (CSP, HSTS, X-Frame-Options)

---

#### Automatisierung & Frameworks

• Entwicklung automatisierter Tests mit **Python 3.11, Playwright, Robot Framework**
  - Page Object Model für wartbare Testarchitektur
  - Pytest-basierte Test-Suites mit Tagging (smoke, critical, feature, regression, load, pentest)
  - Parallelisierung für schnelle Ausführung (bis zu 10 gleichzeitige Browser-Instanzen)
  - Automatische Screenshot- und Trace-Erstellung bei Failures

• **Payment Discovery-System:** Automatische Ermittlung länderspezifischer Zahlungsarten inkl. YAML-Config-Update

• **Data-Driven Testing:** Parametrisierte Tests für Multi-Country-Support (AT, DE, CH)

---

#### Test-Management & Reporting

• Erstellung und Pflege von Testkonzepten, Testfällen und Abnahmeprotokollen
• Koordination des Defect-Managements in Jira
• Test-Coverage-Monitoring (aktuell: ~70%, Ziel: 90%)
• Implementierungs-Roadmap in 9 Phasen (Smoke → Critical Path → Features → Regression → Load)
• CI/CD-Integration für automatisierte Testausführung (GitHub Actions)

---

### Stakeholder-Kommunikation & Schulung

• Schulung von Key-Usern und Produktmanagern für Pimcore und Shopware
• Erstellung von Entscheidungsvorlagen, Dashboards und Management-Reports
• Enge Abstimmung mit Geschäftsführung und Fachbereichen

---

## Technologie- und Tool-Stack

### E-Commerce & Integration
Shopware 6 | Odoo ERP | Pimcore PIM | Emarsys | Nosto | Patchworks (iPaaS)

### Performance-Monitoring
**PatchworksAnalyzer** (Eigenentwicklung)
Python 3.10+ | PHP 8.1 | MySQL | JavaScript | Bootstrap 5 | Chart.js | Syntax-Highlighting

### Testing & QA
**Testpanda** (Eigenentwicklung)
PHP 8.1/Slim 4 | MySQL | Bootstrap 5 | PhpSpreadsheet

Python 3.11 | Playwright | Robot Framework | Pytest | Postman | OWASP ZAP

### Projektmanagement
Jira | Confluence | Miro | Asana | Power BI | GitLab | Excel | BPMN 2.0

### Projektsprache
Deutsch (österreichischer Dialekt)

---

## Projektergebnisse & Key Performance Indicators

| **Bereich** | **Ergebnis** |
|-------------|--------------|
| **API-Performance** | >30% Reduktion von API-Calls durch PatchworksAnalyzer |
| **Test-Coverage** | 171 strukturierte Testfälle, 70% Coverage (Ziel: 90%) |
| **Testfälle gesamt** | 171 Tests in 10 Kategorien |
| **Versandlogistik** | 98 PLZ-basierte Versandarten-Tests (AT, DE, CH) |
| **Security** | OWASP Top 10 Coverage durch Penetration Testing |
| **Automatisierung** | Parallelisierung: bis zu 150 Bestellungen gleichzeitig |
| **Load-Testing** | 1000 Bestellungen/60 Min ohne Performance-Degradation |
| **Systemintegration** | 5 Systeme nahtlos integriert (Shopware, Odoo, Pimcore, Emarsys, Nosto) |

---

## Methodiken & Ansätze

- **Hybride Projektmethodik:** Kombination von Scrum und klassischem Projektmanagement
- **Page Object Model:** Wartbare Test-Automatisierung
- **Test-Driven Development:** Systematischer Test-First-Ansatz
- **CI/CD-Integration:** Automatisierte Testausführung in GitHub Actions
- **OWASP-Standards:** Sicherheitsbasiertes Testing nach OWASP Top 10
- **Data-Driven Testing:** Parametrisierte Tests für Multi-Country-Support
- **Performance-First:** Kontinuierliches Performance-Monitoring

---

## Besondere Herausforderungen & Lösungen

### Herausforderung 1: Performance-Bottlenecks in Datenintegration
**Lösung:** Eigenentwicklung PatchworksAnalyzer mit automatisierter Bottleneck-Erkennung
**Ergebnis:** >30% Reduktion von API-Calls

### Herausforderung 2: Komplexe Versandlogistik mit 98 PLZ-Varianten
**Lösung:** Strukturiertes Testkonzept mit Min/Max-Grenzwertprüfung pro Logistikpartner
**Ergebnis:** 100% Coverage aller PLZ-Bereiche (AT, DE, CH)

### Herausforderung 3: Manuelle Test-Prozesse ohne zentrale Verwaltung
**Lösung:** Eigenentwicklung Testpanda mit Excel-Import, Pool-Management und Bug-Tracking
**Ergebnis:** Starke Verbesserung des Testprozesses durch strukturierte Testausführung

### Herausforderung 4: E-Commerce Security-Risiken
**Lösung:** OWASP Top 10-basiertes Penetration Testing mit Playwright
**Ergebnis:** Systematische Identifikation und Dokumentation von Sicherheitslücken

---

## Projektdauer & Umfang

| **Parameter** | **Details** |
|---------------|-------------|
| **Projektdauer** | 12+ Monate (laufend) |
| **Aufwand** | Vollzeit (100%) |
| **Team-Größe** | 15+ Personen (inkl. externe Dienstleister) |
| **Länder-Coverage** | AT, DE, CH (Multi-Country E-Commerce) |

---

**Stand:** Januar 2026

---

**Matthias Sax GmbH**
m.sax@matthias-sax.de | (+49) 151 20 792 782
