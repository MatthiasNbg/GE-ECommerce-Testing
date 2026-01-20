# Test-Konzept: Grüne Erde E-Commerce Shop

**Projekt:** GE-ECommerce-Testing
**Datum:** 2026-01-20
**Version:** 1.0
**Status:** Entwurf zur Abstimmung

---

## Executive Summary

Dieses Dokument beschreibt die Teststrategie für den Grüne Erde Online-Shop mit **115 Testfällen** in 10 Kategorien. 
Der aktuelle Implementierungsstand liegt bei **~10%**.

**Aktuelle Situation:**
- ✅ Basis-Tests (Smoke: 5/5) implementiert
- ⚠️ Critical Path (3/8) 
(5/8 offen)
- ⚠️ Feature-Tests (1/128 implementiert)

**Prioritäten:**
1. **Kritische Business-Flows** (Gast-Checkout, Zahlungsarten) → Phase 1
2. **Feature-Abdeckung** (Warenkorb, Suche, Account) → Phase 2-4
3. **Versandarten & Promotions** → Phase 5-6
4. **Qualitätssicherung** (Regression, Load-Tests) → Phase 7-9

---

## Thematische Übersicht der Testfälle

**Schnellübersicht: Was wird wo getestet?**

### Nach Funktionsbereichen

<!-- PROGRESS_BAR:115:171:67 -->

| Funktionsbereich | Tests | Status | Priorität | Was wird geprüft? |
|------------------|-------|--------|-----------|-------------------|
| 🏠 **Smoke Tests** | 5 | ✅ 5/5 | 🔴 P0 | Homepage, Produktseiten, Navigation |
| 🛒 **Critical Path Tests** | 8 | ⚠️ 3/8 | 🔴 P0 | Gast-Checkout, Registrierter Checkout, Zahlungsarten |
| 🛍️ **Feature Tests - Warenkorb** | 8 | ❌ 0/8 | 🟠 P1 | Produkte hinzufügen, Mengen ändern, Preis-Berechnung |
| 🔍 **Feature Tests - Suche** | 6 | ⚠️ 1/6 | 🟠 P1 | Produktsuche, Filter, Autocomplete, Kategorien |
| 👤 **Feature Tests - Account** | 8 | ❌ 0/8 | 🟠 P1 | Registrierung, Login, Profil, Adressen |
| 📦 **Feature Tests - Versandarten** | 98 | ❌ 0/98 | 🟠 P1 | Post, Spedition, PLZ-Bereiche, Logistikpartner |
| 🎟️ **Feature Tests - Promotions** | 8 | ❌ 0/8 | 🟡 P2 | Rabattcodes, Mindestbestellwert, Versandkostenfrei |
| 📊 **Data Validation Tests** | 10 | ⚠️ 1/10 | 🟠 P1 | Preise, Versandkosten, MwSt., Verfügbarkeit |
| 🔄 **Regression Tests** | 15-20 | ⚠️ 3/15-20 | 🟡 P2 | Regression-Tests nach Änderungen |
| ⚡ **Load Tests** | 5 | ⚠️ 3/5 | 🟡 P2 | Load-Tests, Response-Zeiten, Race Conditions |

**Legende:** ✅ Vollständig | ⚠️ Teilweise | ❌ Fehlend

---

## Inhaltsverzeichnis

1. [Testfall-Übersicht](#testfall-übersicht) - Alle Tests auf einen Blick
2. [Test-Kategorien](#test-kategorien) - Was wird getestet?
3. [Smoke Tests](#smoke) - (5 Tests)
4. [Critical Path Tests](#critical-path) - (8 Tests)
5. [Feature Tests - Warenkorb](#cart) - (8 Tests)
6. [Feature Tests - Suche](#search) - (6 Tests)
7. [Feature Tests - Account](#account) - (8 Tests)
8. [Feature Tests - Versandarten](#shipping) - (98 Tests)
9. [Feature Tests - Promotions](#promotions) - (8 Tests)
10. [Data Validation Tests](#data-validation) - (10 Tests)
11. [Regression Tests](#regression) - (15-20 Tests)
12. [Load Tests](#load) - (5 Tests)
13. [Implementierungs-Roadmap](#implementierungs-roadmap) - Welche Reihenfolge?

---

## Testfall-Übersicht

### Gesamtübersicht

**Gesamt:** 115 Tests
- ✅ Implementiert: 11
- ❌ Fehlend: 104
- ⚠️ Teilweise: 0
- **Abdeckung:** 10%

---

## Test-Kategorien

### 🏠 Smoke Tests

**Priorität:** P0
**Tests:** 5/5 implementiert
**Beschreibung:** Homepage, Produktseiten, Navigation
**Dauer:** < 5 Min
**Ausführung:** Bei jedem Build, vor jedem Deployment

| Test-ID | Name | Priorität | Status | Länder |
|---------|------|-----------|--------|--------|
| TC-SMOKE-001 | Homepage lädt erfolgreich | P0 | ✅ | AT, DE, CH |
| TC-SMOKE-002 | Produktseite lädt erfolgreich | P0 | ✅ | AT, DE, CH |
| TC-SMOKE-003 | Produkt zum Warenkorb hinzufügen | P0 | ✅ | AT, DE, CH |
| TC-SMOKE-004 | Checkout-Seite erreichbar | P0 | ✅ | AT, DE, CH |
| TC-SMOKE-005 | Suche funktioniert | P0 | ✅ | AT, DE, CH |

---

### 🛒 Critical Path Tests

**Priorität:** P0
**Tests:** 3/8 implementiert
**Beschreibung:** Gast-Checkout, Registrierter Checkout, Zahlungsarten
**Dauer:** 10-30 Min
**Ausführung:** Vor jedem Deployment (Staging + Production)

| Test-ID | Name | Priorität | Status | Länder |
|---------|------|-----------|--------|--------|
| TC-CRITICAL-001 | Gast-Checkout vollständig (AT) | P0 | ❌ | AT |
| TC-CRITICAL-002 | Gast-Checkout vollständig (DE) | P0 | ❌ | DE |
| TC-CRITICAL-003 | Gast-Checkout vollständig (CH) | P0 | ❌ | CH |
| TC-CRITICAL-004 | Registrierter User Checkout | P0 | ❌ | AT |
| TC-CRITICAL-005 | Zahlungsarten verfügbar (AT) | P0 | ✅ | AT |
| TC-CRITICAL-006 | Zahlungsarten verfügbar (DE) | P0 | ✅ | DE |
| TC-CRITICAL-007 | Zahlungsarten verfügbar (CH) | P0 | ✅ | CH |
| TC-CRITICAL-008 | Warenkorb-Persistenz | P1 | ❌ | AT, DE, CH |

---

### 🛍️ Feature Tests - Warenkorb

**Priorität:** P1
**Tests:** 0/8 implementiert
**Beschreibung:** Produkte hinzufügen, Mengen ändern, Preis-Berechnung
**Dauer:** 5-15 Min
**Ausführung:** In CI/CD, vor Feature-Release

---

### 🔍 Feature Tests - Suche

**Priorität:** P1
**Tests:** 1/6 implementiert
**Beschreibung:** Produktsuche, Filter, Autocomplete, Kategorien
**Dauer:** 5-15 Min
**Ausführung:** In CI/CD, vor Feature-Release

---

### 👤 Feature Tests - Account

**Priorität:** P1
**Tests:** 0/8 implementiert
**Beschreibung:** Registrierung, Login, Profil, Adressen
**Dauer:** 10-20 Min
**Ausführung:** In CI/CD, vor Feature-Release

---

### 📦 Feature Tests - Versandarten

**Priorität:** P1
**Tests:** 0/98 implementiert
**Beschreibung:** Post, Spedition, PLZ-Bereiche, Logistikpartner
**Dauer:** 30-60 Min
**Ausführung:** In CI/CD, vor Feature-Release

| Test-ID | Name | Priorität | Status | Länder |
|---------|------|-----------|--------|--------|
| TC-SHIP-AT-POST-001 | Post AT - PLZ 0000-9999 Min | P1 | ❌ | AT |
| TC-SHIP-AT-POST-002 | Post AT - PLZ 0000-9999 Max | P1 | ❌ | AT |
| TC-SHIP-AT-WETSCH-001 | Wetsch AT - PLZ 6000-6999 Min | P1 | ❌ | AT |
| TC-SHIP-AT-WETSCH-002 | Wetsch AT - PLZ 6000-6999 Max | P1 | ❌ | AT |
| TC-SHIP-AT-FINK-001 | Fink AT - PLZ 1000-1199 Min | P1 | ❌ | AT |
| TC-SHIP-AT-FINK-002 | Fink AT - PLZ 1000-1199 Max | P1 | ❌ | AT |
| TC-SHIP-AT-FINK-003 | Fink AT - PLZ 3000-3399 Min | P1 | ❌ | AT |
| TC-SHIP-AT-FINK-004 | Fink AT - PLZ 3000-3399 Max | P1 | ❌ | AT |
| TC-SHIP-AT-FINK-005 | Fink AT - PLZ 3600-3699 Min | P1 | ❌ | AT |
| TC-SHIP-AT-FINK-006 | Fink AT - PLZ 3600-3699 Max | P1 | ❌ | AT |
| TC-SHIP-AT-FINK-007 | Fink AT - PLZ 4000-4699 Min | P1 | ❌ | AT |
| TC-SHIP-AT-FINK-008 | Fink AT - PLZ 4000-4699 Max | P1 | ❌ | AT |
| TC-SHIP-AT-FINK-009 | Fink AT - PLZ 8000-9999 Min | P1 | ❌ | AT |
| TC-SHIP-AT-FINK-010 | Fink AT - PLZ 8000-9999 Max | P1 | ❌ | AT |
| TC-SHIP-AT-CARGO-001 | Cargoe AT - PLZ 1200-1399 Min | P1 | ❌ | AT |
| TC-SHIP-AT-CARGO-002 | Cargoe AT - PLZ 1200-1399 Max | P1 | ❌ | AT |
| TC-SHIP-AT-CARGO-003 | Cargoe AT - PLZ 2000-2999 Min | P1 | ❌ | AT |
| TC-SHIP-AT-CARGO-004 | Cargoe AT - PLZ 2000-2999 Max | P1 | ❌ | AT |
| TC-SHIP-AT-CARGO-005 | Cargoe AT - PLZ 3400-3599 Min | P1 | ❌ | AT |
| TC-SHIP-AT-CARGO-006 | Cargoe AT - PLZ 3400-3599 Max | P1 | ❌ | AT |
| TC-SHIP-AT-CARGO-007 | Cargoe AT - PLZ 3700-3999 Min | P1 | ❌ | AT |
| TC-SHIP-AT-CARGO-008 | Cargoe AT - PLZ 3700-3999 Max | P1 | ❌ | AT |
| TC-SHIP-AT-CARGO-009 | Cargoe AT - PLZ 7000-7999 Min | P1 | ❌ | AT |
| TC-SHIP-AT-CARGO-010 | Cargoe AT - PLZ 7000-7999 Max | P1 | ❌ | AT |
| TC-SHIP-AT-TH-001 | Thurner AT - PLZ 4700-5799 Min | P1 | ❌ | AT |
| TC-SHIP-AT-TH-002 | Thurner AT - PLZ 4700-5799 Max | P1 | ❌ | AT |
| TC-SHIP-DE-POST-001 | Post DE - PLZ 00000-99999 Min | P1 | ❌ | DE |
| TC-SHIP-DE-POST-002 | Post DE - PLZ 00000-99999 Max | P1 | ❌ | DE |
| TC-SHIP-DE-LN-001 | Logsens Nord - PLZ 19000-29999 Min | P1 | ❌ | DE |
| TC-SHIP-DE-LN-002 | Logsens Nord - PLZ 19000-29999 Max | P1 | ❌ | DE |
| TC-SHIP-DE-LN-003 | Logsens Nord - PLZ 30000-32999 Min | P1 | ❌ | DE |
| TC-SHIP-DE-LN-004 | Logsens Nord - PLZ 30000-32999 Max | P1 | ❌ | DE |
| TC-SHIP-DE-LN-005 | Logsens Nord - PLZ 34000-37139 Min | P1 | ❌ | DE |
| TC-SHIP-DE-LN-006 | Logsens Nord - PLZ 34000-37139 Max | P1 | ❌ | DE |
| TC-SHIP-DE-LN-007 | Logsens Nord - PLZ 37140-37199 Min | P1 | ❌ | DE |
| TC-SHIP-DE-LN-008 | Logsens Nord - PLZ 37140-37199 Max | P1 | ❌ | DE |
| TC-SHIP-DE-LN-009 | Logsens Nord - PLZ 37200-37399 Min | P1 | ❌ | DE |
| TC-SHIP-DE-LN-010 | Logsens Nord - PLZ 37200-37399 Max | P1 | ❌ | DE |
| TC-SHIP-DE-LN-011 | Logsens Nord - PLZ 37400-39174 Min | P1 | ❌ | DE |
| TC-SHIP-DE-LN-012 | Logsens Nord - PLZ 37400-39174 Max | P1 | ❌ | DE |
| TC-SHIP-DE-LN-013 | Logsens Nord - PLZ 39326-39499 Min | P1 | ❌ | DE |
| TC-SHIP-DE-LN-014 | Logsens Nord - PLZ 39326-39499 Max | P1 | ❌ | DE |
| TC-SHIP-DE-LN-015 | Logsens Nord - PLZ 39500-39699 Min | P1 | ❌ | DE |
| TC-SHIP-DE-LN-016 | Logsens Nord - PLZ 39500-39699 Max | P1 | ❌ | DE |
| TC-SHIP-DE-LN-017 | Logsens Nord - PLZ 49000-49999 Min | P1 | ❌ | DE |
| TC-SHIP-DE-LN-018 | Logsens Nord - PLZ 49000-49999 Max | P1 | ❌ | DE |
| TC-SHIP-DE-LO-001 | Logsens Ost - PLZ 00000-09999 Min | P1 | ❌ | DE |
| TC-SHIP-DE-LO-002 | Logsens Ost - PLZ 00000-09999 Max | P1 | ❌ | DE |
| TC-SHIP-DE-LO-003 | Logsens Ost - PLZ 10000-15999 Min | P1 | ❌ | DE |
| TC-SHIP-DE-LO-004 | Logsens Ost - PLZ 10000-15999 Max | P1 | ❌ | DE |
| TC-SHIP-DE-LO-005 | Logsens Ost - PLZ 16000-18999 Min | P1 | ❌ | DE |
| TC-SHIP-DE-LO-006 | Logsens Ost - PLZ 16000-18999 Max | P1 | ❌ | DE |
| TC-SHIP-DE-LO-007 | Logsens Ost - PLZ 39175-39319 Min | P1 | ❌ | DE |
| TC-SHIP-DE-LO-008 | Logsens Ost - PLZ 39175-39319 Max | P1 | ❌ | DE |
| TC-SHIP-DE-LO-009 | Logsens Ost - PLZ 95000-96999 Min | P1 | ❌ | DE |
| TC-SHIP-DE-LO-010 | Logsens Ost - PLZ 95000-96999 Max | P1 | ❌ | DE |
| TC-SHIP-DE-LO-011 | Logsens Ost - PLZ 98000-99999 Min | P1 | ❌ | DE |
| TC-SHIP-DE-LO-012 | Logsens Ost - PLZ 98000-99999 Max | P1 | ❌ | DE |
| TC-SHIP-DE-LS-001 | Logsens Süd - PLZ 54000-54999 Min | P1 | ❌ | DE |
| TC-SHIP-DE-LS-002 | Logsens Süd - PLZ 54000-54999 Max | P1 | ❌ | DE |
| TC-SHIP-DE-LS-003 | Logsens Süd - PLZ 56000-56999 Min | P1 | ❌ | DE |
| TC-SHIP-DE-LS-004 | Logsens Süd - PLZ 56000-56999 Max | P1 | ❌ | DE |
| TC-SHIP-DE-LS-005 | Logsens Süd - PLZ 66000-67999 Min | P1 | ❌ | DE |
| TC-SHIP-DE-LS-006 | Logsens Süd - PLZ 66000-67999 Max | P1 | ❌ | DE |
| TC-SHIP-DE-LS-007 | Logsens Süd - PLZ 72000-72999 Min | P1 | ❌ | DE |
| TC-SHIP-DE-LS-008 | Logsens Süd - PLZ 72000-72999 Max | P1 | ❌ | DE |
| TC-SHIP-DE-LS-009 | Logsens Süd - PLZ 75000-79999 Min | P1 | ❌ | DE |
| TC-SHIP-DE-LS-010 | Logsens Süd - PLZ 75000-79999 Max | P1 | ❌ | DE |
| TC-SHIP-DE-LS-011 | Logsens Süd - PLZ 80000-89999 Min | P1 | ❌ | DE |
| TC-SHIP-DE-LS-012 | Logsens Süd - PLZ 80000-89999 Max | P1 | ❌ | DE |
| TC-SHIP-DE-LW-001 | Logsens West - PLZ 33000-33999 Min | P1 | ❌ | DE |
| TC-SHIP-DE-LW-002 | Logsens West - PLZ 33000-33999 Max | P1 | ❌ | DE |
| TC-SHIP-DE-LW-003 | Logsens West - PLZ 41000-41999 Min | P1 | ❌ | DE |
| TC-SHIP-DE-LW-004 | Logsens West - PLZ 41000-41999 Max | P1 | ❌ | DE |
| TC-SHIP-DE-LW-005 | Logsens West - PLZ 42000-48999 Min | P1 | ❌ | DE |
| TC-SHIP-DE-LW-006 | Logsens West - PLZ 42000-48999 Max | P1 | ❌ | DE |
| TC-SHIP-DE-LW-007 | Logsens West - PLZ 50000-53999 Min | P1 | ❌ | DE |
| TC-SHIP-DE-LW-008 | Logsens West - PLZ 50000-53999 Max | P1 | ❌ | DE |
| TC-SHIP-DE-LW-009 | Logsens West - PLZ 57000-57999 Min | P1 | ❌ | DE |
| TC-SHIP-DE-LW-010 | Logsens West - PLZ 57000-57999 Max | P1 | ❌ | DE |
| TC-SHIP-DE-LW-011 | Logsens West - PLZ 58000-59999 Min | P1 | ❌ | DE |
| TC-SHIP-DE-LW-012 | Logsens West - PLZ 58000-59999 Max | P1 | ❌ | DE |
| TC-SHIP-DE-TH-001 | Thurner DE - PLZ 55000-55999 Min | P1 | ❌ | DE |
| TC-SHIP-DE-TH-002 | Thurner DE - PLZ 55000-55999 Max | P1 | ❌ | DE |
| TC-SHIP-DE-TH-003 | Thurner DE - PLZ 60000-65999 Min | P1 | ❌ | DE |
| TC-SHIP-DE-TH-004 | Thurner DE - PLZ 60000-65999 Max | P1 | ❌ | DE |
| TC-SHIP-DE-TH-005 | Thurner DE - PLZ 68000-71999 Min | P1 | ❌ | DE |
| TC-SHIP-DE-TH-006 | Thurner DE - PLZ 68000-71999 Max | P1 | ❌ | DE |
| TC-SHIP-DE-TH-007 | Thurner DE - PLZ 73000-74999 Min | P1 | ❌ | DE |
| TC-SHIP-DE-TH-008 | Thurner DE - PLZ 73000-74999 Max | P1 | ❌ | DE |
| TC-SHIP-DE-TH-009 | Thurner DE - PLZ 90000-94999 Min | P1 | ❌ | DE |
| TC-SHIP-DE-TH-010 | Thurner DE - PLZ 90000-94999 Max | P1 | ❌ | DE |
| TC-SHIP-DE-TH-011 | Thurner DE - PLZ 97000-97999 Min | P1 | ❌ | DE |
| TC-SHIP-DE-TH-012 | Thurner DE - PLZ 97000-97999 Max | P1 | ❌ | DE |
| TC-SHIP-CH-001 | Post CH - PLZ Min (1000) | P1 | ❌ | CH |
| TC-SHIP-CH-002 | Post CH - PLZ Max (9658) | P1 | ❌ | CH |
| TC-SHIP-CH-003 | Spedition Kuoni CH - PLZ Min (1000) | P1 | ❌ | CH |
| TC-SHIP-CH-004 | Spedition Kuoni CH - PLZ Max (9658) | P1 | ❌ | CH |

---

### 🎟️ Feature Tests - Promotions

**Priorität:** P2
**Tests:** 0/8 implementiert
**Beschreibung:** Rabattcodes, Mindestbestellwert, Versandkostenfrei
**Dauer:** 10-20 Min
**Ausführung:** In CI/CD, vor Feature-Release

| Test-ID | Name | Priorität | Status | Länder |
|---------|------|-----------|--------|--------|
| TC-PROMO-001 | Nicht-rabattierbarer Artikel (639046) | P1 | ❌ | AT, DE, CH |

---

### 📊 Data Validation Tests

**Priorität:** P1
**Tests:** 1/10 implementiert
**Beschreibung:** Preise, Versandkosten, MwSt., Verfügbarkeit
**Dauer:** 5-15 Min
**Ausführung:** Täglich (Monitoring), vor Deployments

---

### 🔄 Regression Tests

**Priorität:** P2
**Tests:** 3/15-20 implementiert
**Beschreibung:** Regression-Tests nach Änderungen
**Dauer:** 1-4 Std
**Ausführung:** Nightly Builds, vor Major Releases

---

### ⚡ Load Tests

**Priorität:** P2
**Tests:** 3/5 implementiert
**Beschreibung:** Load-Tests, Response-Zeiten, Race Conditions
**Dauer:** 30 Min - 4 Std
**Ausführung:** Vor Releases, bei Performance-Änderungen

| Test-ID | Name | Priorität | Status | Länder |
|---------|------|-----------|--------|--------|
| TC-PERF-001 | Performance-Test 150 Bestellungen | P2 | ✅ | AT |
| TC-PERF-002 | Performance Quick-Test | P2 | ✅ | AT |
| TC-PERF-003 | Performance Stress-Test | P2 | ✅ | AT |

---

## Implementierungs-Roadmap

| Phase | Name | Status | Tests | Abdeckung-Ziel |
|-------|------|--------|-------|----------------|
| phase_0 | Phase 0 - Basis-Setup | ✅ | 8 | -% |
| phase_1 | Phase 1 - Critical Path | ⏳ | 5 | 15% |
| phase_2 | Phase 2 - Warenkorb | ⏳ | 8 | 25% |
| phase_3 | Phase 3 - Account | ⏳ | 8 | 35% |
| phase_4 | Phase 4 - Suche | ⏳ | 5 | 40% |
| phase_5 | Phase 5 - Versandarten | ⏳ | 8 | 50% |
| phase_6 | Phase 6 - Promotions | ⏳ | 8 | 60% |
| phase_7 | Phase 7 - Data Validation | ⏳ | 9 | 70% |
| phase_8 | Phase 8 - Regression | ⏳ | 15-20 | 85% |
| phase_9 | Phase 9 - Load Tests | ⏳ | 5 | 90% |

---


*Generiert am 2026-01-20 10:15 aus test-inventory.yaml*
