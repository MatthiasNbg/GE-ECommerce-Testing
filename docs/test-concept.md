# Test-Konzept: Grüne Erde E-Commerce Shop

**Projekt:** GE-ECommerce-Testing
**Datum:** 2026-01-16
**Version:** 1.0
**Status:** Entwurf zur Abstimmung

---

## Executive Summary

Dieses Dokument beschreibt die Teststrategie für den Grüne Erde Online-Shop mit **81-101 Testfällen** in 10 Kategorien. 
Der aktuelle Implementierungsstand liegt bei **~9%**.

**Aktuelle Situation:**
- ✅ Basis-Tests (Smoke: 5/5) implementiert
- ⚠️ Critical Path (3/8) 
(5/8 offen)
- ⚠️ Feature-Tests (1/38 implementiert)

**Prioritäten:**
1. **Kritische Business-Flows** (Gast-Checkout, Zahlungsarten) → Phase 1
2. **Feature-Abdeckung** (Warenkorb, Suche, Account) → Phase 2-4
3. **Versandarten & Promotions** → Phase 5-6
4. **Qualitätssicherung** (Regression, Load-Tests) → Phase 7-9

---

## Thematische Übersicht der Testfälle

**Schnellübersicht: Was wird wo getestet?**

### Nach Funktionsbereichen

| Funktionsbereich | Tests | Status | Priorität | Was wird geprüft? |
|------------------|-------|--------|-----------|-------------------|
| 🏠 **Smoke Tests** | 5 | ✅ 5/5 | 🔴 P0 | Homepage, Produktseiten, Navigation |
| 🛒 **Critical Path Tests** | 8 | ⚠️ 3/8 | 🔴 P0 | Gast-Checkout, Registrierter Checkout, Zahlungsarten |
| 🛍️ **Feature Tests - Warenkorb** | 8 | ❌ 0/8 | 🟠 P1 | Produkte hinzufügen, Mengen ändern, Preis-Berechnung |
| 🔍 **Feature Tests - Suche** | 6 | ⚠️ 1/6 | 🟠 P1 | Produktsuche, Filter, Autocomplete, Kategorien |
| 👤 **Feature Tests - Account** | 8 | ❌ 0/8 | 🟠 P1 | Registrierung, Login, Profil, Adressen |
| 📦 **Feature Tests - Versandarten** | 8 | ❌ 0/8 | 🟡 P2 | Post, Spedi, Abholung, Versandkosten |
| 🎟️ **Feature Tests - Promotions** | 8 | ❌ 0/8 | 🟡 P2 | Rabattcodes, Mindestbestellwert, Versandkostenfrei |
| 📊 **Data Validation Tests** | 10 | ⚠️ 1/10 | 🟠 P1 | Preise, Versandkosten, MwSt., Verfügbarkeit |
| 🔄 **Regression Tests** | 15-20 | ⚠️ 3/15-20 | 🟡 P2 | Regression-Tests nach Änderungen |
| ⚡ **Load Tests** | 5 | ❌ 0/5 | 🟡 P2 | Load-Tests, Response-Zeiten, Race Conditions |

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
8. [Feature Tests - Versandarten](#shipping) - (8 Tests)
9. [Feature Tests - Promotions](#promotions) - (8 Tests)
10. [Data Validation Tests](#data-validation) - (10 Tests)
11. [Regression Tests](#regression) - (15-20 Tests)
12. [Load Tests](#load) - (5 Tests)
13. [Implementierungs-Roadmap](#implementierungs-roadmap) - Welche Reihenfolge?

---

## Testfall-Übersicht

### Gesamtübersicht

**Gesamt:** 91 Tests
- ✅ Implementiert: 8
- ❌ Fehlend: 83
- ⚠️ Teilweise: 0
- **Abdeckung:** 9%

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

**Priorität:** P2
**Tests:** 0/8 implementiert
**Beschreibung:** Post, Spedi, Abholung, Versandkosten
**Dauer:** 10-20 Min
**Ausführung:** In CI/CD, vor Feature-Release

---

### 🎟️ Feature Tests - Promotions

**Priorität:** P2
**Tests:** 0/8 implementiert
**Beschreibung:** Rabattcodes, Mindestbestellwert, Versandkostenfrei
**Dauer:** 10-20 Min
**Ausführung:** In CI/CD, vor Feature-Release

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
**Tests:** 0/5 implementiert
**Beschreibung:** Load-Tests, Response-Zeiten, Race Conditions
**Dauer:** 30 Min - 4 Std
**Ausführung:** Vor Releases, bei Performance-Änderungen

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


*Generiert am 2026-01-16 18:12 aus test-inventory.yaml*
