# Test-Konzept: Grüne Erde E-Commerce Shop

**Projekt:** GE-ECommerce-Testing
**Datum:** 2026-01-22
**Version:** 1.0
**Status:** Entwurf zur Abstimmung

---

## Executive Summary

Dieses Dokument beschreibt die Teststrategie für den Grüne Erde Online-Shop mit **215 Testfällen** in 10 Kategorien.
Der aktuelle Implementierungsstand liegt bei **~65%**.

**Aktuelle Situation:**
- ✅ Basis-Tests (Smoke: 5/5) implementiert
- ⚠️ Critical Path (3/8) 
(5/8 offen)
- ⚠️ Feature-Tests (123/131 implementiert)

**Prioritäten:**
1. **Kritische Business-Flows** (Gast-Checkout, Zahlungsarten) → Phase 1
2. **Feature-Abdeckung** (Warenkorb, Suche, Account) → Phase 2-4
3. **Versandarten & Promotions** → Phase 5-6
4. **Qualitätssicherung** (Regression, Load-Tests) → Phase 7-9

---

## Thematische Übersicht der Testfälle

**Schnellübersicht: Was wird wo getestet?**

### Nach Funktionsbereichen

<!-- PROGRESS_BAR:144:174:83 -->

| Funktionsbereich | Tests | Status | Priorität | Was wird geprüft? |
|------------------|-------|--------|-----------|-------------------|
| 🏠 **Smoke Tests** | 5 | ✅ 5/5 | 🔴 P0 | Homepage, Produktseiten, Navigation |
| 🛒 **Critical Path Tests** | 8 | ✅ 8/8 | 🔴 P0 | Gast-Checkout, Registrierter Checkout, Zahlungsarten |
| 🛍️ **Feature Tests - Warenkorb** | 8 | ✅ 8/8 | 🟠 P1 | Produkte hinzufügen, Mengen ändern, Preis-Berechnung |
| 🔍 **Feature Tests - Suche** | 9 | ✅ 9/9 | 🟠 P1 | Produktsuche, Filter, Autocomplete, Kategorien |
| 👤 **Feature Tests - Account** | 8 | ✅ 8/8 | 🟠 P1 | Registrierung, Login, Profil, Adressen |
| 📦 **Feature Tests - Versandarten** | 98 | ✅ 98/98 | 🟠 P1 | Post, Spedition, PLZ-Bereiche, Logistikpartner |
| 🎟️ **Feature Tests - Promotions** | 47 | ⚠️ 0/47 | 🟡 P2 | Rabattcodes, Mindestbestellwert, Versandkostenfrei, Gutscheine, Checkout-Flows |
| 📊 **Data Validation Tests** | 15 | ⚠️ 0/15 | 🟠 P1 | Preise, Versandkosten, MwSt., Verfügbarkeit, Produktdaten |
| 🔄 **Regression Tests** | 15 | ⚠️ 3/15 | 🟡 P2 | Regression-Tests nach Änderungen |
| ⚡ **Load Tests** | 5 | ⚠️ 3/5 | 🟡 P2 | Load-Tests, Response-Zeiten, Race Conditions |

**Legende:** ✅ Implementiert | ○ Definiert | ⚠️ Teilweise | ❌ Fehlend

---

## Inhaltsverzeichnis

1. [Testfall-Übersicht](#testfall-uebersicht) - Alle Tests auf einen Blick
2. [Test-Kategorien](#test-kategorien) - Was wird getestet?
3. [Smoke Tests](#smoke-tests) - (5 Tests)
4. [Critical Path Tests](#critical-path-tests) - (8 Tests)
5. [Feature Tests - Warenkorb](#feature-tests-warenkorb) - (8 Tests)
6. [Feature Tests - Suche](#feature-tests-suche) - (9 Tests)
7. [Feature Tests - Account](#feature-tests-account) - (8 Tests)
8. [Feature Tests - Versandarten](#feature-tests-versandarten) - (98 Tests)
9. [Feature Tests - Promotions](#feature-tests-promotions) - (47 Tests)
10. [Data Validation Tests](#data-validation-tests) - (15 Tests)
11. [Regression Tests](#regression-tests) - (15-20 Tests)
12. [Load Tests](#load-tests) - (5 Tests)
13. [Testdaten](#testdaten) - Testprodukte, Adressen, Gutscheine
14. [Implementierungs-Roadmap](#implementierungs-roadmap) - Welche Reihenfolge?

---

## Testfall-Übersicht

### Gesamtübersicht

**Gesamt:** 215 Tests
- ✅ Implementiert: 134
- ❌ Fehlend: 81
- ⚠️ Teilweise: 0
- **Abdeckung:** 65%

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
| TC-CRITICAL-001 | Gast-Checkout vollständig (AT) | P0 | ○ | AT |
| TC-CRITICAL-002 | Gast-Checkout vollständig (DE) | P0 | ○ | DE |
| TC-CRITICAL-003 | Gast-Checkout vollständig (CH) | P0 | ○ | CH |
| TC-CRITICAL-004 | Registrierter User Checkout | P0 | ○ | AT |
| TC-CRITICAL-005 | Zahlungsarten verfügbar (AT) | P0 | ✅ | AT |
| TC-CRITICAL-006 | Zahlungsarten verfügbar (DE) | P0 | ✅ | DE |
| TC-CRITICAL-007 | Zahlungsarten verfügbar (CH) | P0 | ✅ | CH |
| TC-CRITICAL-008 | Warenkorb-Persistenz | P1 | ○ | AT, DE, CH |

---

### 🛍️ Feature Tests - Warenkorb

**Priorität:** P1
**Tests:** 8/8 implementiert
**Beschreibung:** Produkte hinzufügen, Mengen ändern, Preis-Berechnung
**Dauer:** 5-15 Min
**Ausführung:** In CI/CD, vor Feature-Release

| Test-ID | Name | Priorität | Status | Länder |
|---------|------|-----------|--------|--------|
| TC-CART-001 | Produkt zum Warenkorb hinzufügen | P1 | ✅ | AT, DE, CH |
| TC-CART-002 | Warenkorb-Zähler aktualisiert sich | P1 | ✅ | AT, DE, CH |
| TC-CART-003 | Menge ändern aktualisiert Gesamtpreis | P1 | ✅ | AT, DE, CH |
| TC-CART-004 | Produkt entfernen aktualisiert Warenkorb | P1 | ✅ | AT, DE, CH |
| TC-CART-005 | Leerer Warenkorb zeigt Meldung | P1 | ✅ | AT, DE, CH |
| TC-CART-006 | Warenkorb bleibt zwischen Seiten erhalten | P1 | ✅ | AT, DE, CH |
| TC-CART-007 | Mehrere Produkte hinzufügen | P1 | ✅ | AT, DE, CH |
| TC-CART-008 | Preisberechnung korrekt | P1 | ✅ | AT, DE, CH |

---

### 🔍 Feature Tests - Suche

**Priorität:** P1
**Tests:** 9/9 implementiert
**Beschreibung:** Produktsuche, Filter, Autocomplete, Kategorien
**Dauer:** 5-15 Min
**Ausführung:** In CI/CD, vor Feature-Release

| Test-ID | Name | Priorität | Status | Länder |
|---------|------|-----------|--------|--------|
| TC-SEARCH-001 | Autocomplete zeigt korrektes Produkt | P1 | ✅ | AT, DE, CH |
| TC-SEARCH-002 | Autocomplete-Klick navigiert zu Produkt | P1 | ✅ | AT, DE, CH |
| TC-SEARCH-003 | Suchergebnisseite zeigt korrektes Produkt | P1 | ✅ | AT, DE, CH |
| TC-SEARCH-004 | Suchergebnis-Klick navigiert zu Produkt | P1 | ✅ | AT, DE, CH |
| TC-SEARCH-005 | Keine Ergebnisse bei ungültigem Artikel | P1 | ✅ | AT, DE, CH |
| TC-SEARCH-006 | Suchvorschläge erscheinen bei Eingabe | P1 | ✅ | AT, DE, CH |
| TC-SEARCH-007 | Suchvorschläge zeigen Kategorien | P1 | ✅ | AT, DE, CH |
| TC-SEARCH-008 | Autocomplete zeigt Produktbilder | P1 | ✅ | AT, DE, CH |
| TC-SEARCH-009 | Autocomplete Produktinfo vollständig | P1 | ✅ | AT, DE, CH |

---

### 👤 Feature Tests - Account

**Priorität:** P1
**Tests:** 8/8 implementiert
**Beschreibung:** Registrierung, Login, Profil, Adressen
**Dauer:** 10-20 Min
**Ausführung:** In CI/CD, vor Feature-Release

| Test-ID | Name | Priorität | Status | Länder |
|---------|------|-----------|--------|--------|
| TC-ACCOUNT-001 | Registrierung erfolgreich | P1 | ✅ | AT, DE, CH |
| TC-ACCOUNT-002 | Registrierung mit existierender Email schlägt fehl | P1 | ✅ | AT, DE, CH |
| TC-ACCOUNT-003 | Registrierung mit ungültiger Email zeigt Fehler | P1 | ✅ | AT, DE, CH |
| TC-ACCOUNT-004 | Schwaches Passwort wird abgelehnt | P1 | ✅ | AT, DE, CH |
| TC-ACCOUNT-005 | Login erfolgreich | P1 | ✅ | AT, DE, CH |
| TC-ACCOUNT-006 | Login mit falschen Daten schlägt fehl | P1 | ✅ | AT, DE, CH |
| TC-ACCOUNT-007 | Profil anzeigen und bearbeiten | P1 | ✅ | AT, DE, CH |
| TC-ACCOUNT-008 | Adressverwaltung | P1 | ✅ | AT, DE, CH |

---

### 📦 Feature Tests - Versandarten

**Priorität:** P1
**Tests:** 98/98 implementiert
**Beschreibung:** Post, Spedition, PLZ-Bereiche, Logistikpartner
**Dauer:** 30-60 Min
**Ausführung:** In CI/CD, vor Feature-Release

| Test-ID | Name | Priorität | Status | Länder |
|---------|------|-----------|--------|--------|
| TC-SHIP-AT-POST-001 | Post AT - PLZ 0000-9999 Min | P1 | ✅ | AT |
| TC-SHIP-AT-POST-002 | Post AT - PLZ 0000-9999 Max | P1 | ✅ | AT |
| TC-SHIP-AT-WETSCH-001 | Wetsch AT - PLZ 6000-6999 Min | P1 | ✅ | AT |
| TC-SHIP-AT-WETSCH-002 | Wetsch AT - PLZ 6000-6999 Max | P1 | ✅ | AT |
| TC-SHIP-AT-FINK-001 | Fink AT - PLZ 1000-1199 Min | P1 | ✅ | AT |
| TC-SHIP-AT-FINK-002 | Fink AT - PLZ 1000-1199 Max | P1 | ✅ | AT |
| TC-SHIP-AT-FINK-003 | Fink AT - PLZ 3000-3399 Min | P1 | ✅ | AT |
| TC-SHIP-AT-FINK-004 | Fink AT - PLZ 3000-3399 Max | P1 | ✅ | AT |
| TC-SHIP-AT-FINK-005 | Fink AT - PLZ 3600-3699 Min | P1 | ✅ | AT |
| TC-SHIP-AT-FINK-006 | Fink AT - PLZ 3600-3699 Max | P1 | ✅ | AT |
| TC-SHIP-AT-FINK-007 | Fink AT - PLZ 4000-4699 Min | P1 | ✅ | AT |
| TC-SHIP-AT-FINK-008 | Fink AT - PLZ 4000-4699 Max | P1 | ✅ | AT |
| TC-SHIP-AT-FINK-009 | Fink AT - PLZ 8000-9999 Min | P1 | ✅ | AT |
| TC-SHIP-AT-FINK-010 | Fink AT - PLZ 8000-9999 Max | P1 | ✅ | AT |
| TC-SHIP-AT-CARGO-001 | Cargoe AT - PLZ 1200-1399 Min | P1 | ✅ | AT |
| TC-SHIP-AT-CARGO-002 | Cargoe AT - PLZ 1200-1399 Max | P1 | ✅ | AT |
| TC-SHIP-AT-CARGO-003 | Cargoe AT - PLZ 2000-2999 Min | P1 | ✅ | AT |
| TC-SHIP-AT-CARGO-004 | Cargoe AT - PLZ 2000-2999 Max | P1 | ✅ | AT |
| TC-SHIP-AT-CARGO-005 | Cargoe AT - PLZ 3400-3599 Min | P1 | ✅ | AT |
| TC-SHIP-AT-CARGO-006 | Cargoe AT - PLZ 3400-3599 Max | P1 | ✅ | AT |
| TC-SHIP-AT-CARGO-007 | Cargoe AT - PLZ 3700-3999 Min | P1 | ✅ | AT |
| TC-SHIP-AT-CARGO-008 | Cargoe AT - PLZ 3700-3999 Max | P1 | ✅ | AT |
| TC-SHIP-AT-CARGO-009 | Cargoe AT - PLZ 7000-7999 Min | P1 | ✅ | AT |
| TC-SHIP-AT-CARGO-010 | Cargoe AT - PLZ 7000-7999 Max | P1 | ✅ | AT |
| TC-SHIP-AT-TH-001 | Thurner AT - PLZ 4700-5799 Min | P1 | ✅ | AT |
| TC-SHIP-AT-TH-002 | Thurner AT - PLZ 4700-5799 Max | P1 | ✅ | AT |
| TC-SHIP-DE-POST-001 | Post DE - PLZ 00000-99999 Min | P1 | ✅ | DE |
| TC-SHIP-DE-POST-002 | Post DE - PLZ 00000-99999 Max | P1 | ✅ | DE |
| TC-SHIP-DE-LN-001 | Logsens Nord - PLZ 19000-29999 Min | P1 | ✅ | DE |
| TC-SHIP-DE-LN-002 | Logsens Nord - PLZ 19000-29999 Max | P1 | ✅ | DE |
| TC-SHIP-DE-LN-003 | Logsens Nord - PLZ 30000-32999 Min | P1 | ✅ | DE |
| TC-SHIP-DE-LN-004 | Logsens Nord - PLZ 30000-32999 Max | P1 | ✅ | DE |
| TC-SHIP-DE-LN-005 | Logsens Nord - PLZ 34000-37139 Min | P1 | ✅ | DE |
| TC-SHIP-DE-LN-006 | Logsens Nord - PLZ 34000-37139 Max | P1 | ✅ | DE |
| TC-SHIP-DE-LN-007 | Logsens Nord - PLZ 37140-37199 Min | P1 | ✅ | DE |
| TC-SHIP-DE-LN-008 | Logsens Nord - PLZ 37140-37199 Max | P1 | ✅ | DE |
| TC-SHIP-DE-LN-009 | Logsens Nord - PLZ 37200-37399 Min | P1 | ✅ | DE |
| TC-SHIP-DE-LN-010 | Logsens Nord - PLZ 37200-37399 Max | P1 | ✅ | DE |
| TC-SHIP-DE-LN-011 | Logsens Nord - PLZ 37400-39174 Min | P1 | ✅ | DE |
| TC-SHIP-DE-LN-012 | Logsens Nord - PLZ 37400-39174 Max | P1 | ✅ | DE |
| TC-SHIP-DE-LN-013 | Logsens Nord - PLZ 39326-39499 Min | P1 | ✅ | DE |
| TC-SHIP-DE-LN-014 | Logsens Nord - PLZ 39326-39499 Max | P1 | ✅ | DE |
| TC-SHIP-DE-LN-015 | Logsens Nord - PLZ 39500-39699 Min | P1 | ✅ | DE |
| TC-SHIP-DE-LN-016 | Logsens Nord - PLZ 39500-39699 Max | P1 | ✅ | DE |
| TC-SHIP-DE-LN-017 | Logsens Nord - PLZ 49000-49999 Min | P1 | ✅ | DE |
| TC-SHIP-DE-LN-018 | Logsens Nord - PLZ 49000-49999 Max | P1 | ✅ | DE |
| TC-SHIP-DE-LO-001 | Logsens Ost - PLZ 00000-09999 Min | P1 | ✅ | DE |
| TC-SHIP-DE-LO-002 | Logsens Ost - PLZ 00000-09999 Max | P1 | ✅ | DE |
| TC-SHIP-DE-LO-003 | Logsens Ost - PLZ 10000-15999 Min | P1 | ✅ | DE |
| TC-SHIP-DE-LO-004 | Logsens Ost - PLZ 10000-15999 Max | P1 | ✅ | DE |
| TC-SHIP-DE-LO-005 | Logsens Ost - PLZ 16000-18999 Min | P1 | ✅ | DE |
| TC-SHIP-DE-LO-006 | Logsens Ost - PLZ 16000-18999 Max | P1 | ✅ | DE |
| TC-SHIP-DE-LO-007 | Logsens Ost - PLZ 39175-39319 Min | P1 | ✅ | DE |
| TC-SHIP-DE-LO-008 | Logsens Ost - PLZ 39175-39319 Max | P1 | ✅ | DE |
| TC-SHIP-DE-LO-009 | Logsens Ost - PLZ 95000-96999 Min | P1 | ✅ | DE |
| TC-SHIP-DE-LO-010 | Logsens Ost - PLZ 95000-96999 Max | P1 | ✅ | DE |
| TC-SHIP-DE-LO-011 | Logsens Ost - PLZ 98000-99999 Min | P1 | ✅ | DE |
| TC-SHIP-DE-LO-012 | Logsens Ost - PLZ 98000-99999 Max | P1 | ✅ | DE |
| TC-SHIP-DE-LS-001 | Logsens Süd - PLZ 54000-54999 Min | P1 | ✅ | DE |
| TC-SHIP-DE-LS-002 | Logsens Süd - PLZ 54000-54999 Max | P1 | ✅ | DE |
| TC-SHIP-DE-LS-003 | Logsens Süd - PLZ 56000-56999 Min | P1 | ✅ | DE |
| TC-SHIP-DE-LS-004 | Logsens Süd - PLZ 56000-56999 Max | P1 | ✅ | DE |
| TC-SHIP-DE-LS-005 | Logsens Süd - PLZ 66000-67999 Min | P1 | ✅ | DE |
| TC-SHIP-DE-LS-006 | Logsens Süd - PLZ 66000-67999 Max | P1 | ✅ | DE |
| TC-SHIP-DE-LS-007 | Logsens Süd - PLZ 72000-72999 Min | P1 | ✅ | DE |
| TC-SHIP-DE-LS-008 | Logsens Süd - PLZ 72000-72999 Max | P1 | ✅ | DE |
| TC-SHIP-DE-LS-009 | Logsens Süd - PLZ 75000-79999 Min | P1 | ✅ | DE |
| TC-SHIP-DE-LS-010 | Logsens Süd - PLZ 75000-79999 Max | P1 | ✅ | DE |
| TC-SHIP-DE-LS-011 | Logsens Süd - PLZ 80000-89999 Min | P1 | ✅ | DE |
| TC-SHIP-DE-LS-012 | Logsens Süd - PLZ 80000-89999 Max | P1 | ✅ | DE |
| TC-SHIP-DE-LW-001 | Logsens West - PLZ 33000-33999 Min | P1 | ✅ | DE |
| TC-SHIP-DE-LW-002 | Logsens West - PLZ 33000-33999 Max | P1 | ✅ | DE |
| TC-SHIP-DE-LW-003 | Logsens West - PLZ 41000-41999 Min | P1 | ✅ | DE |
| TC-SHIP-DE-LW-004 | Logsens West - PLZ 41000-41999 Max | P1 | ✅ | DE |
| TC-SHIP-DE-LW-005 | Logsens West - PLZ 42000-48999 Min | P1 | ✅ | DE |
| TC-SHIP-DE-LW-006 | Logsens West - PLZ 42000-48999 Max | P1 | ✅ | DE |
| TC-SHIP-DE-LW-007 | Logsens West - PLZ 50000-53999 Min | P1 | ✅ | DE |
| TC-SHIP-DE-LW-008 | Logsens West - PLZ 50000-53999 Max | P1 | ✅ | DE |
| TC-SHIP-DE-LW-009 | Logsens West - PLZ 57000-57999 Min | P1 | ✅ | DE |
| TC-SHIP-DE-LW-010 | Logsens West - PLZ 57000-57999 Max | P1 | ✅ | DE |
| TC-SHIP-DE-LW-011 | Logsens West - PLZ 58000-59999 Min | P1 | ✅ | DE |
| TC-SHIP-DE-LW-012 | Logsens West - PLZ 58000-59999 Max | P1 | ✅ | DE |
| TC-SHIP-DE-TH-001 | Thurner DE - PLZ 55000-55999 Min | P1 | ✅ | DE |
| TC-SHIP-DE-TH-002 | Thurner DE - PLZ 55000-55999 Max | P1 | ✅ | DE |
| TC-SHIP-DE-TH-003 | Thurner DE - PLZ 60000-65999 Min | P1 | ✅ | DE |
| TC-SHIP-DE-TH-004 | Thurner DE - PLZ 60000-65999 Max | P1 | ✅ | DE |
| TC-SHIP-DE-TH-005 | Thurner DE - PLZ 68000-71999 Min | P1 | ✅ | DE |
| TC-SHIP-DE-TH-006 | Thurner DE - PLZ 68000-71999 Max | P1 | ✅ | DE |
| TC-SHIP-DE-TH-007 | Thurner DE - PLZ 73000-74999 Min | P1 | ✅ | DE |
| TC-SHIP-DE-TH-008 | Thurner DE - PLZ 73000-74999 Max | P1 | ✅ | DE |
| TC-SHIP-DE-TH-009 | Thurner DE - PLZ 90000-94999 Min | P1 | ✅ | DE |
| TC-SHIP-DE-TH-010 | Thurner DE - PLZ 90000-94999 Max | P1 | ✅ | DE |
| TC-SHIP-DE-TH-011 | Thurner DE - PLZ 97000-97999 Min | P1 | ✅ | DE |
| TC-SHIP-DE-TH-012 | Thurner DE - PLZ 97000-97999 Max | P1 | ✅ | DE |
| TC-SHIP-CH-001 | Post CH - PLZ Min (1000) | P1 | ✅ | CH |
| TC-SHIP-CH-002 | Post CH - PLZ Max (9658) | P1 | ✅ | CH |
| TC-SHIP-CH-003 | Spedition Kuoni CH - PLZ Min (1000) | P1 | ✅ | CH |
| TC-SHIP-CH-004 | Spedition Kuoni CH - PLZ Max (9658) | P1 | ✅ | CH |

---

### 🎟️ Feature Tests - Promotions

**Priorität:** P2
**Tests:** 0/47 implementiert
**Beschreibung:** Rabattcodes, Mindestbestellwert, Versandkostenfrei, Gutscheine, Mengenrabatte, Promo-Kombinationen, Gutschein-Checkout-Flows, Automatisierte Promotions, Warenkorb-Rabatte
**Dauer:** 60-120 Min
**Ausführung:** In CI/CD, vor Feature-Release

#### Warenkorb-Promotions

| Test-ID | Name | Priorität | Status | Länder |
|---------|------|-----------|--------|--------|
| TC-PROMO-001 | Nicht-rabattierbarer Artikel (639046) | P1 | ○ | AT, DE, CH |
| TC-PROMO-002 | Ausschluss Kauf rabattierter Artikel | P1 | ○ | AT, DE, CH |
| TC-PROMO-003 | Ausschluss Kaufgutscheine mit Rabatten | P1 | ○ | AT, DE, CH |
| TC-PROMO-004 | Kein Rabatt auf Wertgutschein | P1 | ○ | AT, DE, CH |
| TC-PROMO-CART-PERCENT-001 | Prozentuale Aktion auf Warenkorb mit Ausschlüssen | P1 | ○ | AT, DE, CH |

**Detaillierte Testbeschreibungen:**

**TC-PROMO-CART-PERCENT-001: Prozentuale Aktion auf Warenkorb mit Ausschlüssen**
- **Beschreibung:** Vorlage für %-Aktionen auf Warenkorb - prüft prozentuale Rabatte auf den gesamten Warenkorb mit Produktausschlüssen
- **Bedingung:**
  - Ausschließen von folgenden Produkten:
    - nicht_rabattierbar (von Odoo je Variante) = true
    - Einkaufsgutscheine
  - Shopware-Regel: **[GE-Template-Warenkorb]**
- **Promo-Konfiguration:**
  - **Name (FE):** Promohülse
  - **Interner Name:** [je nach Kampagne]
  - **Gültig ab und bis:** [je nach Kampagne]
  - **Gesamtnutzung:** 1
  - **Nutzung je Kunde:** 5
  - **Aktiv:** true
  - **Aktionscodetyp:** je Kampagne
  - **Rabattkonfiguration für Odoo:** je Kampagne IDs und Rabattart
  - **Verkaufskanäle:** AT, DE, CH
  - **Warenkorb-Regel:** [GE-Template-Warenkorb]
  - **Rabatt: Anwenden auf:** Warenkorb
  - **Art:** Prozentual
- **Testschritte:**
  1. Warenkorb mit verschiedenen Produkten befüllen (normale Produkte, nicht-rabattierbare Produkte, Gutscheine)
  2. Promotion-Code eingeben
  3. Prüfen, dass Rabatt nur auf rabattierbare Produkte angewendet wird
  4. Verifizieren, dass nicht-rabattierbare Produkte ausgeschlossen werden
  5. Verifizieren, dass Einkaufsgutscheine ausgeschlossen werden
  6. Prozentuale Rabatt-Berechnung validieren
  7. Nutzungslimits prüfen (1x global, 5x pro Kunde)
  8. Test in allen Verkaufskanälen (AT, DE, CH) durchführen
- **Erwartetes Verhalten:**
  - Promotion wird mit gültigem Code angewendet
  - Rabatt wird nur auf rabattierbare Produkte angewendet
  - Nicht-rabattierbare Produkte (nicht_rabattierbar = true) werden ausgeschlossen
  - Einkaufsgutscheine werden vom Rabatt ausgeschlossen
  - Prozentuale Berechnung ist korrekt
  - Nutzungslimits werden eingehalten
  - Funktioniert in allen DACH-Verkaufskanälen
- **Referenzen:**
  - [Shopware-Regel Template](https://grueneerde.scalecommerce.cloud/admin#/sw/settings/rule/detail/019beaf9d194714dbe77b182ea9a1a02/base)
  - [Promotion Template](https://grueneerde.scalecommerce.cloud/admin#/sw/promotion/v2/detail/019beaf618b376a9b82416a15d3fc0c8/base)

#### Gutschein-Sicherheit (Brute-Force Tests)

| Test-ID | Name | Priorität | Status | Länder |
|---------|------|-----------|--------|--------|
| TC-PROMO-SEC-001 | Ausnutzungsmöglichkeiten Kaufgutscheine | P0 | ○ | AT, DE, CH |
| TC-PROMO-SEC-002 | Gutschein-Kombination für kostenlosen Warenkorb | P0 | ○ | AT, DE, CH |
| TC-PROMO-SEC-003 | Gutscheine zum Erreichen von MBW | P1 | ○ | AT, DE, CH |
| TC-PROMO-SEC-004 | Alle Gutschein-Kombinationen (Brute-Force) | P1 | ○ | AT, DE, CH |

#### Gutschein-Checkout-Flows

| Test-ID | Name | Priorität | Status | Länder |
|---------|------|-----------|--------|--------|
| TC-PROMO-CHK-001 | Gutschein zu regulärem Warenkorb blockiert | P0 | ○ | AT, DE, CH |
| TC-PROMO-CHK-002 | Reguläres Produkt zu Gutschein-Warenkorb blockiert | P0 | ○ | AT, DE, CH |
| TC-PROMO-CHK-003 | Promotion auf Gutschein blockiert | P0 | ○ | AT, DE, CH |
| TC-PROMO-CHK-004 | Gemischter Warenkorb im Checkout blockiert | P0 | ○ | AT, DE, CH |
| TC-PROMO-CHK-005 | Mehrere Gutscheine erlaubt | P1 | ○ | AT, DE, CH |

**Detaillierte Testbeschreibungen:**

**TC-PROMO-CHK-001: Gutschein zu regulärem Warenkorb blockiert**
- **Ausgangssituation:** Warenkorb enthält reguläres Produkt (z.B. Bett "Somnia")
- **Aktion:** User versucht Gutschein (Artikel 736675, HC Code 6609) hinzuzufügen
- **Event:** BeforeLineItemAddedEvent wird gefeuert
- **Erwartetes Verhalten:**
  - Event->stopPropagation() wird aufgerufen
  - Fehlermeldung: "Einkaufsgutscheine können nur separat gekauft werden. Bitte entfernen Sie zunächst die Produkte im Warenkorb, um die Einkaufsgutscheine kaufen zu können."
  - Gutschein wird NICHT hinzugefügt
  - User bleibt auf PDP oder wird zu Cart geleitet

**TC-PROMO-CHK-002: Reguläres Produkt zu Gutschein-Warenkorb blockiert**
- **Ausgangssituation:** Warenkorb enthält Einkaufsgutschein 50€ (Artikel 736675)
- **Aktion:** User versucht reguläres Produkt (z.B. Kissen) hinzuzufügen
- **Event:** BeforeLineItemAddedEvent wird gefeuert
- **Erwartetes Verhalten:**
  - Event->stopPropagation() wird aufgerufen
  - Fehlermeldung: "Einkaufsgutscheine können nur separat gekauft werden. Bitte schließen Sie den Kauf ab oder entfernen Sie die Einkaufsgutscheine von Ihrem Warenkorb."
  - Produkt wird NICHT hinzugefügt
  - User sieht Fehlermeldung im Frontend

**TC-PROMO-CHK-003: Promotion auf Gutschein blockiert**
- **Ausgangssituation:** Warenkorb enthält Einkaufsgutschein 100€
- **Aktion:** User gibt Promotion-Code "SOMMER20" im Gutscheinfeld ein
- **Event:** checkout.promotion.added wird gefeuert
- **Erwartetes Verhalten:**
  - Promotion wird aus cart.lineItems entfernt
  - Fehlermeldung: "Rabattcodes können nicht auf Einkaufsgutscheine angewendet werden."
  - Promotion-Code wird nicht angewendet
  - Warenkorb zeigt vollen Gutschein-Preis
  - **Alternative:** Button zum Anwenden von Codes wird bei Gutscheinen direkt ausgeblendet (bessere UX)

**TC-PROMO-CHK-004: Gemischter Warenkorb im Checkout blockiert**
- **Ausgangssituation:** User hat durch API/Manipulation gemischten Warenkorb (Gutschein + reguläres Produkt)
- **Aktion:** User klickt "Zur Kasse"
- **Event:** CartVerifyPersistEvent wird gefeuert
- **Erwartetes Verhalten:**
  - CartValidator prüft kompletten Warenkorb
  - Findet: Gutschein UND reguläres Produkt
  - Fügt BlockingError hinzu mit blockOrder() = true
  - Checkout wird verhindert
  - User wird zu Warenkorb zurückgeleitet
  - Fehlermeldung wird angezeigt
  - User MUSS Warenkorb bereinigen (Sicherheitsnetz)

**TC-PROMO-CHK-005: Mehrere Gutscheine erlaubt**
- **Ausgangssituation:** Warenkorb enthält Gutschein 50€
- **Aktion:** User fügt Gutschein 100€ hinzu
- **Event:** BeforeLineItemAddedEvent wird gefeuert
- **Erwartetes Verhalten:**
  - Prüfung: Neues Item ist Gutschein + Warenkorb enthält nur Gutscheine
  - Gutschein wird erfolgreich hinzugefügt
  - Warenkorb zeigt beide Gutscheine (50€ + 100€)
  - Checkout ist möglich
  - Gesamtpreis: 150€

#### Versandkostenfrei-Promotions

| Test-ID | Name | Priorität | Status | Länder |
|---------|------|-----------|--------|--------|
| TC-PROMO-SHIP-001 | Versandkostenfrei nur Post (DE/AT) | P1 | ○ | AT, DE |
| TC-PROMO-SHIP-002 | Versandkostenfrei nur Post (CH) | P1 | ○ | CH |
| TC-PROMO-SHIP-003 | Versandkostenfrei nur Spedi (DE/AT) | P1 | ○ | AT, DE |
| TC-PROMO-SHIP-004 | Versandkostenfrei nur Spedi (CH) | P1 | ○ | CH |
| TC-PROMO-SHIP-005 | Versandkostenfrei Post ab MBW EUR 50 (DE/AT) | P1 | ○ | AT, DE |
| TC-PROMO-SHIP-006 | Versandkostenfrei Post ab MBW CHF 50 (CH) | P1 | ○ | CH |

**Detaillierte Testbeschreibungen:**

**TC-PROMO-SHIP-001: Versandkostenfrei nur Post (DE/AT)**
- **Beschreibung:** Versandkostenfreie Lieferung nur für Postartikel in DE/AT ohne Mindestbestellwert
- **Bedingungen:**
  - Land = DE, AT
  - Verwendete Versandart = Postversand DE, Postversand AT
  - Shopware-Regel: **GE_Promo_Lieferland-DA_nurPostversand**
- **Promo-Konfiguration:**
  - **Name (FE):** Promohülse
  - **Gültig ab und bis:** [je nach Kampagne]
  - **Gesamtnutzung:** 1
  - **Nutzung je Kunde:** 5
  - **Aktiv:** true
  - **Aktionscodetyp:** je Kampagne
  - **Rabattkonfiguration für Odoo:** je Kampagne IDs und Rabattart
  - **Verkaufskanäle:** AT, DE
  - **Warenkorb-Regel:** GE_Promo_Lieferland-DA_nurPostversand
  - **Rabatt: Anwenden auf:** Versandkosten
  - **Art:** Absolut = 5,95 EUR
- **Testschritte:**
  1. Warenkorb mit Postartikeln befüllen (für DE oder AT)
  2. Promotion-Code eingeben
  3. Prüfen, dass Versandkosten auf 0 reduziert werden
  4. Verifizieren, dass Rabatt absolut 5,95 EUR beträgt
  5. Prüfen, dass nur Postversand-Methode betroffen ist
  6. Nutzungslimits testen (1x global, 5x pro Kunde)
- **Erwartetes Verhalten:**
  - Versandkosten werden auf 0 gesetzt
  - Rabatt von 5,95 EUR wird auf Versandkosten angewendet
  - Funktioniert nur für Postversand DE/AT
  - Speditionsversand ist nicht betroffen
- **Referenzen:**
  - [Shopware-Regel](https://grueneerde.scalecommerce.cloud/admin#/sw/settings/rule/detail/01976f6aee8279dd97dd90c31a120032/base)
  - [Promotion Template](https://grueneerde.scalecommerce.cloud/admin#/sw/promotion/v2/detail/019bec0a3baf723185fbbdfa46d3e7ad/base)

**TC-PROMO-SHIP-002: Versandkostenfrei nur Post (CH)**
- **Beschreibung:** Versandkostenfreie Lieferung nur für Postartikel in CH ohne Mindestbestellwert
- **Bedingungen:**
  - Land = CH
  - Verwendete Versandart = Postversand Schweiz
  - Shopware-Regel: **GE_Promo_LieferlandCH_nurPostversand**
- **Promo-Konfiguration:**
  - **Verkaufskanäle:** CH
  - **Warenkorb-Regel:** GE_Promo_LieferlandCH_nurPostversand
  - **Rabatt: Anwenden auf:** Versandkosten
  - **Art:** Absolut = 6,95 CHF
  - Weitere Konfiguration wie TC-PROMO-SHIP-001
- **Erwartetes Verhalten:**
  - Rabatt von 6,95 CHF wird auf Versandkosten angewendet
  - Funktioniert nur für Postversand CH
- **Referenzen:**
  - [Shopware-Regel](https://grueneerde.scalecommerce.cloud/admin#/sw/settings/rule/detail/0197e57bfea470c9bf7964360934c5e7/base)
  - [Promotion Template](https://grueneerde.scalecommerce.cloud/admin#/sw/promotion/v2/detail/019bec1280c9709b8190c555644401f0/base)

**TC-PROMO-SHIP-003: Versandkostenfrei nur Spedi (DE/AT)**
- **Beschreibung:** Versandkostenfreie Lieferung nur für Speditionsartikel in DE/AT
- **Bedingungen:**
  - Land = DE, AT
  - Verwendete Versandart = Spedi-Versand AT und DE
  - Shopware-Regel: **GE_Promo_MBW50_LieferlandDA_nurSpedi**
- **Promo-Konfiguration:**
  - **Verkaufskanäle:** AT, DE
  - **Warenkorb-Regel:** GE_Promo_MBW50_LieferlandDA_nurSpedi
  - **Rabatt: Anwenden auf:** Versandkosten
  - **Art:** Absolut
- **Testschritte:**
  1. Warenkorb mit Speditionsartikeln befüllen
  2. Promotion-Code eingeben
  3. Prüfen, dass Versandkosten auf 0 reduziert werden
  4. Verifizieren, dass nur Speditionsversand betroffen ist
  5. Prüfen, dass Postversand nicht betroffen ist
- **Erwartetes Verhalten:**
  - Versandkosten für Spedition werden auf 0 gesetzt
  - Funktioniert nur für Speditionsversand
  - Postversand ist nicht betroffen
- **Referenzen:**
  - [Shopware-Regel](https://grueneerde.scalecommerce.cloud/admin#/sw/settings/rule/detail/019974fd6455701b9c6772d9f544f234/base)

**TC-PROMO-SHIP-004: Versandkostenfrei nur Spedi (CH)**
- **Beschreibung:** Versandkostenfreie Lieferung nur für Speditionsartikel in CH
- **Bedingungen:**
  - Land = CH
  - Verwendete Versandart = Spedition Schweiz
  - Shopware-Regel: **GE_Promo_MBW50_LieferlandCH_nurSpedi**
- **Promo-Konfiguration:**
  - **Verkaufskanäle:** CH
  - **Warenkorb-Regel:** GE_Promo_MBW50_LieferlandCH_nurSpedi
  - **Rabatt: Anwenden auf:** Versandkosten
  - **Art:** Absolut
- **Erwartetes Verhalten:**
  - Versandkosten für Spedition CH werden auf 0 gesetzt
  - Funktioniert nur für Speditionsversand CH
- **Referenzen:**
  - [Shopware-Regel](https://grueneerde.scalecommerce.cloud/admin#/sw/settings/rule/detail/019bec0fb87c716489912f1af4a421e9/base)

**TC-PROMO-SHIP-005: Versandkostenfrei Post ab MBW EUR 50 (DE/AT)**
- **Beschreibung:** Versandkostenfreie Postlieferung ab Mindestbestellwert 50 EUR für DE/AT
- **Bedingungen:**
  - Land = DE, AT
  - Verwendete Versandart = Postversand DE, Postversand AT
  - Summe = >50 EUR (Mindestbestellwert)
  - Shopware-Regel: **GE_Promo_MBW50_LieferlandDA_nurPostversand**
- **Promo-Konfiguration:**
  - **Verkaufskanäle:** AT, DE
  - **Warenkorb-Regel:** GE_Promo_MBW50_LieferlandDA_nurPostversand
  - **Rabatt: Anwenden auf:** Versandkosten
  - **Art:** Absolut = 5,95 EUR
- **Testschritte:**
  1. Warenkorb mit Postartikeln befüllen (unter 50 EUR)
  2. Promotion-Code eingeben → sollte nicht funktionieren
  3. Warenkorb auf über 50 EUR erhöhen
  4. Promotion-Code erneut eingeben
  5. Prüfen, dass Versandkosten auf 0 reduziert werden
  6. MBW-Grenze testen (49,99 EUR vs 50,00 EUR)
- **Erwartetes Verhalten:**
  - Promotion funktioniert nur ab 50 EUR Warenwert
  - Versandkosten werden auf 0 gesetzt
  - Rabatt von 5,95 EUR wird angewendet
  - Unter MBW: Fehlermeldung oder keine Anwendung
- **Referenzen:**
  - [Shopware-Regel](https://grueneerde.scalecommerce.cloud/admin#/sw/settings/rule/detail/019bf906150a7042ba5d46f77b009b98/base)
  - [Promotion Template](https://grueneerde.scalecommerce.cloud/admin#/sw/promotion/v2/detail/019beb1f40bf726da2d9e3c10c0c2e5e/conditions)

**TC-PROMO-SHIP-006: Versandkostenfrei Post ab MBW CHF 50 (CH)**
- **Beschreibung:** Versandkostenfreie Postlieferung ab Mindestbestellwert 50 CHF für CH
- **Bedingungen:**
  - Land = CH
  - Verwendete Versandart = Postversand Schweiz
  - Summe = >50 CHF (Mindestbestellwert)
  - Shopware-Regel: **GE_Promo_MBW50_LieferlandCH_nurPostversand**
- **Promo-Konfiguration:**
  - **Verkaufskanäle:** CH
  - **Warenkorb-Regel:** GE_Promo_MBW50_LieferlandCH_nurPostversand
  - **Rabatt: Anwenden auf:** Versandkosten
  - **Art:** Absolut = 6,95 CHF
- **Testschritte:**
  - Analog zu TC-PROMO-SHIP-005, aber mit CHF und CH-spezifischen Werten
- **Erwartetes Verhalten:**
  - Promotion funktioniert nur ab 50 CHF Warenwert
  - Rabatt von 6,95 CHF wird angewendet
- **Referenzen:**
  - [Shopware-Regel](https://grueneerde.scalecommerce.cloud/admin#/sw/settings/rule/detail/019bec0c9ba2724d8f118c3f01db846d/base)
  - [Promotion Template](https://grueneerde.scalecommerce.cloud/admin#/sw/promotion/v2/detail/019bec13f89e7197b69879ce36d3da5c/base)

#### Produktkategorien-Promotions

| Test-ID | Name | Priorität | Status | Länder |
|---------|------|-----------|--------|--------|
| TC-PROMO-CAT-001 | Promo auf Produktkategorie via advertising_material_id | P1 | ○ | AT, DE, CH |
| TC-PROMO-AUTO-001 | Automatisierte Promo auf Werbemittel ID 70 | P1 | ○ | AT, DE, CH |

**Detaillierte Testbeschreibungen:**

**TC-PROMO-AUTO-001: Automatisierte Promo auf Werbemittel ID 70**
- **Beschreibung:** Vorlage für Promohuelse (automatisierte Promo) - prüft automatische Rabattanwendung auf Produkte mit Werbemittel ID 70
- **Bedingung:** Nur Produkte mit Werbemittel ID 70, keine Shopware-Regel notwendig
- **Promo-Konfiguration:**
  - **Aktionscodetyp:** kein Code erforderlich (automatisch)
  - **Rabattkonfiguration für Odoo:** je Kampagne IDs und Rabattart
  - **Odoo Product Tag:** Odoo Product Tag Advertising Material IDs - Automatic Promotion
  - **Verkaufskanäle:** AT, DE, CH
  - **Warenkorb-Regel:** nicht notwendig
  - **Anwenden auf:** Warenkorb
  - **Nur auf ausgewählte Produkte:** true
  - **Anwenden auf:** ausgewählte Produkte
  - **Art:** Prozentual
- **Testschritte:**
  1. Produkt mit advertising_material_id = 70 zum Warenkorb hinzufügen
  2. Zum Warenkorb navigieren
  3. Prüfen, dass automatische Promotion angewendet wurde (kein Code-Eingabe erforderlich)
  4. Prozentuale Rabatt-Berechnung validieren
  5. Test in allen Verkaufskanälen (AT, DE, CH) durchführen
- **Erwartetes Verhalten:**
  - Promotion wird automatisch ohne Code angewendet
  - Rabatt wird nur auf Produkte mit Werbemittel ID 70 angewendet
  - Rabatt ist prozentual und wird korrekt berechnet
  - Funktioniert in allen DACH-Verkaufskanälen
- **Referenz:** [Shopware Promotion Template](https://grueneerde.scalecommerce.cloud/admin#/sw/promotion/v2/detail/019be5f25363722483455ea500fee356/base)

#### Mindestbestellwert-Promotions

| Test-ID | Name | Priorität | Status | Länder |
|---------|------|-----------|--------|--------|
| TC-PROMO-MOV-001 | EUR-Rabatt ab Mindestbestellwert | P1 | ○ | AT, DE, CH |
| TC-PROMO-MOV-002 | MBW nur auf Warenkorb angewendet | P1 | ○ | AT, DE, CH |

#### Mengenrabatt-Promotions

| Test-ID | Name | Priorität | Status | Länder |
|---------|------|-----------|--------|--------|
| TC-PROMO-QTY-001 | % auf teuerstes Produkt | P1 | ○ | AT, DE, CH |
| TC-PROMO-QTY-002 | Mengenrabatt nur auf 1 Produkt | P1 | ○ | AT, DE, CH |
| TC-PROMO-QTY-003 | 3x gleiches Produkt - nur 1x rabattiert | P1 | ○ | AT, DE, CH |

#### Aktionspreis-Promotions

| Test-ID | Name | Priorität | Status | Länder |
|---------|------|-----------|--------|--------|
| TC-PROMO-SALE-001 | Rabatt auf Lieblingsprodukt (Aktionspreis) | P1 | ○ | AT, DE, CH |
| TC-PROMO-SALE-002 | Promo mit Produkt-ID via advertising_material_id | P1 | ○ | AT, DE, CH |
| TC-PROMO-SALE-003 | Promo mit leerer Promo-ID nicht möglich | P1 | ○ | AT, DE, CH |
| TC-PROMO-SALE-004 | SALE-Anzeige bei Aktionspreis korrekt | P1 | ○ | AT, DE, CH |

#### Mitarbeiterrabatt

| Test-ID | Name | Priorität | Status | Länder |
|---------|------|-----------|--------|--------|
| TC-PROMO-EMP-001 | Mitarbeiterrabatt nur auf Basispreis | P1 | ○ | AT, DE, CH |
| TC-PROMO-EMP-002 | Mitarbeiterrabatt nicht auf Aktionspreis | P1 | ○ | AT, DE, CH |

#### Bundle-Promotions

| Test-ID | Name | Priorität | Status | Länder |
|---------|------|-----------|--------|--------|
| TC-PROMO-BUNDLE-001 | Nimm 5 zahl 4 | P1 | ○ | AT, DE, CH |
| TC-PROMO-BUNDLE-002 | Produkt A + Gratisprodukt | P1 | ○ | AT, DE, CH |
| TC-PROMO-BUNDLE-003 | Kissen + Schonbezug gratis | P1 | ○ | AT, DE, CH |
| TC-PROMO-BUNDLE-004 | Pro Kissen ein Schonbezug gratis | P1 | ○ | AT, DE, CH |

#### Promo-Kombinationen

| Test-ID | Name | Priorität | Status | Länder |
|---------|------|-----------|--------|--------|
| TC-PROMO-COMBO-001 | Zwei Promotions kombinierbar | P1 | ○ | AT, DE, CH |
| TC-PROMO-COMBO-002 | 20% Kleidung + 5% Alles | P1 | ○ | AT, DE, CH |
| TC-PROMO-COMBO-003 | Aufeinander aufbauende Promos | P1 | ○ | AT, DE, CH |

---

### 📊 Data Validation Tests

**Priorität:** P1
**Tests:** 0/15 implementiert
**Beschreibung:** Preise, Versandkosten, MwSt., Verfügbarkeit, Produktdaten, Filterbarkeit
**Dauer:** 15-30 Min
**Ausführung:** Täglich (Monitoring), vor Deployments

#### Produktdaten-Validierung

| Test-ID | Name | Priorität | Status | Länder |
|---------|------|-----------|--------|--------|
| TC-DATA-001 | Stichprobe: Produkte haben Produkttyp | P1 | ○ | AT, DE, CH |
| TC-DATA-002 | Stichprobe: Produkte über Grundfarbe findbar | P1 | ○ | AT, DE, CH |
| TC-DATA-003 | Produkttyp nicht leer bei allen Produkten | P1 | ○ | AT, DE, CH |
| TC-DATA-004 | Grundfarbe Filter funktioniert | P1 | ○ | AT, DE, CH |
| TC-DATA-005 | Produkttyp Filter funktioniert | P1 | ○ | AT, DE, CH |

#### Preis-Validierung

| Test-ID | Name | Priorität | Status | Länder |
|---------|------|-----------|--------|--------|
| TC-DATA-006 | Preise korrekt angezeigt | P1 | ○ | AT, DE, CH |
| TC-DATA-007 | MwSt. korrekt berechnet | P1 | ○ | AT, DE, CH |
| TC-DATA-008 | Aktionspreise korrekt dargestellt | P1 | ○ | AT, DE, CH |

#### Versandkosten-Validierung

| Test-ID | Name | Priorität | Status | Länder |
|---------|------|-----------|--------|--------|
| TC-DATA-009 | Versandkosten korrekt berechnet (Post) | P1 | ○ | AT, DE, CH |
| TC-DATA-010 | Versandkosten korrekt berechnet (Spedition) | P1 | ○ | AT, DE, CH |

#### Verfügbarkeits-Validierung

| Test-ID | Name | Priorität | Status | Länder |
|---------|------|-----------|--------|--------|
| TC-DATA-011 | Verfügbarkeitsstatus korrekt angezeigt | P1 | ○ | AT, DE, CH |
| TC-DATA-012 | Nicht verfügbare Produkte nicht bestellbar | P1 | ○ | AT, DE, CH |

#### Cross-Country Daten-Konsistenz

| Test-ID | Name | Priorität | Status | Länder |
|---------|------|-----------|--------|--------|
| TC-DATA-013 | Produkte in allen Ländern verfügbar | P2 | ○ | AT, DE, CH |
| TC-DATA-014 | Produktdaten konsistent über Länder | P2 | ○ | AT, DE, CH |
| TC-DATA-015 | Stichprobe: Produktbilder vorhanden | P1 | ○ | AT, DE, CH |

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
| phase_2 | Phase 2 - Warenkorb | ✅ | 8 | -% |
| phase_3 | Phase 3 - Account | ✅ | 8 | -% |
| phase_4 | Phase 4 - Suche | ✅ | 9 | -% |
| phase_5 | Phase 5 - Versandarten | ✅ | 98 | -% |
| phase_6 | Phase 6 - Promotions | ⏳ | 47 | 60% |
| phase_7 | Phase 7 - Data Validation | ⏳ | 15 | 70% |
| phase_8 | Phase 8 - Regression | ⏳ | 15-20 | 85% |
| phase_9 | Phase 9 - Load Tests | ⏳ | 5 | 90% |

---

## Testdaten

Die folgenden Testdaten werden für die automatisierten Tests verwendet.

### 👤 Registrierte Testkunden

| Land | Name | E-Mail | Kunden-ID |
|------|------|--------|-----------|
| AT | Monika Stadler | ge-at-1@matthias-sax.de | 2921964 |
| DE | Britta Yook | ge-de-1@matthias-sax.de | 199407 |
| CH | Ursula Dold | ge-ch-1@matthias-sax.de | 309348 |

### 📍 Gast-Adresspool

| Land | Stadt | PLZ |
|------|-------|-----|
| AT | Wien | 1010 |
| AT | Linz | 4020 |
| AT | Salzburg | 5020 |
| AT | Graz | 8010 |
| AT | Innsbruck | 6020 |
| DE | München | 80331 |
| DE | Berlin | 10115 |
| DE | Hamburg | 20095 |
| DE | Frankfurt | 60311 |
| DE | Köln | 50667 |
| CH | Zürich | 8001 |
| CH | Bern | 3011 |
| CH | Basel | 4001 |
| CH | Genf | 1201 |
| CH | Luzern | 6003 |

### 📦 Testprodukte

**Postversand (kleine/leichte Artikel):**

| Produkt | Kategorie | Produkt-ID | Verwendung |
|---------|-----------|------------|------------|
| Kurzarmshirt Bio-Baumwolle | Textil | ge-p-862990 | - |
| Blusenshirt Bio-Leinen | Textil | ge-p-863190 | - |
| Duftkissen Lavendel | Accessoires | ge-p-49415 | Gutschein-Checkout-Tests (TC-PROMO-CHK-002) |
| Augen-Entspannungskissen mit Amaranth | Accessoires | ge-p-74157 | - |
| Bademantel Raute | Textil | ge-p-410933 | - |

**Speditionsversand (große/schwere Artikel):**

| Produkt | Kategorie | Produkt-ID | Verwendung |
|---------|-----------|------------|------------|
| Kleiderständer Jukai Pur | Möbel | ge-p-693645 | - |
| Polsterbett Almeno | Möbel/Betten | ge-p-693278 | Gutschein-Checkout-Tests (TC-PROMO-CHK-001) |
| Kleiderschrank (Spedition) | Möbel/Schränke | TBD-schrank-produkt | - |

### 🏷️ Spezielle Testprodukte

**Nicht-rabattierbare Artikel:**

| Artikel-ID | Name | Beschreibung |
|------------|------|--------------|
| 639046 | Nicht-rabattierbarer Artikel | Dieser Artikel darf keinen Rabatt erhalten |

**Produkte mit Aktionspreis:**

| Artikel-ID | Name | Basispreis | Aktionspreis | Status |
|------------|------|------------|--------------|--------|
| TBD | Testprodukt Aktionspreis 1 | TBD | TBD | ❌ Fehlend |
| TBD | Testprodukt Aktionspreis 2 | TBD | TBD | ❌ Fehlend |

**Bundle-Produkte:**

| Artikel-ID | Name | Bundle-Typ | Gratisprodukt | Status |
|------------|------|------------|---------------|--------|
| TBD | Kissen (mit Schonbezug gratis) | A + B gratis | Schonbezug | ❌ Fehlend |
| TBD | Nimm 5 zahl 4 Testprodukt | Mengenrabatt | - | ❌ Fehlend |

**Produkte mit advertising_material_id:**

| Artikel-ID | Name | advertising_material_id | Kategorie | Verwendung | Status |
|------------|------|------------------------|-----------|------------|--------|
| TBD | Testprodukt Werbemittel | 70 | Promo-Werbemittel | TC-PROMO-AUTO-001 (Automatisierte Promo) | ❌ Fehlend |
| TBD | Testprodukt Kategorie 1 | TBD | TBD | Allgemeine Kategorietests | ❌ Fehlend |
| TBD | Testprodukt Kategorie 2 | TBD | TBD | Allgemeine Kategorietests | ❌ Fehlend |

**Produkte für Data Validation Tests:**

| Artikel-ID | Name | Produkttyp | Grundfarbe | Verwendung | Status |
|------------|------|------------|-----------|------------|--------|
| ge-p-862990 | Kurzarmshirt Bio-Baumwolle | Shirt | Weiß/Beige | Stichprobe Produkttyp & Farbe | ✅ Vorhanden |
| ge-p-863190 | Blusenshirt Bio-Leinen | Shirt | Blau | Stichprobe Produkttyp & Farbe | ✅ Vorhanden |
| ge-p-410933 | Bademantel Raute | Bademantel | Grau | Stichprobe Produkttyp & Farbe | ✅ Vorhanden |
| ge-p-49415 | Duftkissen Lavendel | Kissen | Lila | Stichprobe Produkttyp & Farbe | ✅ Vorhanden |
| TBD | Produkt ohne Produkttyp | - | - | Negativtest | ❌ Fehlend |
| TBD | Produkt ohne Grundfarbe | TBD | - | Negativtest | ❌ Fehlend |

### 🎟️ Gutscheine & Rabattcodes

**Kaufgutscheine (für Sicherheitstests & Checkout-Flows):**

| Artikel-ID | Wert | Typ | HC Code | Verwendung | Status |
|------------|------|-----|---------|------------|--------|
| 736675 | 50 EUR | Einkaufsgutschein | 6609 | Checkout-Flow Tests | ✅ Vorhanden |
| TBD | 100 EUR | Einkaufsgutschein | 6609 | Checkout-Flow Tests | ❌ Fehlend |
| TBD | 10 EUR | Kaufgutschein | 6609 | Sicherheitstests | ❌ Fehlend |
| TBD | 25 EUR | Kaufgutschein | 6609 | Sicherheitstests | ❌ Fehlend |

**Wertgutscheine:**

| Code | Wert | Typ | Status |
|------|------|-----|--------|
| TBD | 25 EUR | Wertgutschein | ❌ Fehlend |
| TBD | 50 EUR | Wertgutschein | ❌ Fehlend |

**Rabattcodes:**

| Code | Rabatt | Typ | Bedingungen | Verwendung | Status |
|------|--------|-----|-------------|------------|--------|
| TBD | 10% | Warenkorb | MBW 50 EUR | Allgemein | ❌ Fehlend |
| TBD | 15 EUR | Warenkorb | MBW 100 EUR | Allgemein | ❌ Fehlend |
| TBD | 20% | Warenkorb | Ausschluss nicht-rabattierbar + Gutscheine, 1x global, 5x pro Kunde | TC-PROMO-CART-PERCENT-001 | ❌ Fehlend |
| TBD | Versandkostenfrei (5,95 EUR) | Versand Post | Nur Post DE/AT, 1x global, 5x pro Kunde | TC-PROMO-SHIP-001 | ❌ Fehlend |
| TBD | Versandkostenfrei (6,95 CHF) | Versand Post | Nur Post CH, 1x global, 5x pro Kunde | TC-PROMO-SHIP-002 | ❌ Fehlend |
| TBD | Versandkostenfrei | Versand Spedi | Nur Spedi DE/AT | TC-PROMO-SHIP-003 | ❌ Fehlend |
| TBD | Versandkostenfrei | Versand Spedi | Nur Spedi CH | TC-PROMO-SHIP-004 | ❌ Fehlend |
| TBD | Versandkostenfrei (5,95 EUR) | Versand Post | MBW 50 EUR, Post DE/AT | TC-PROMO-SHIP-005 | ❌ Fehlend |
| TBD | Versandkostenfrei (6,95 CHF) | Versand Post | MBW 50 CHF, Post CH | TC-PROMO-SHIP-006 | ❌ Fehlend |
| TBD | 20% | Produktkategorie | Via advertising_material_id | Allgemein | ❌ Fehlend |
| TBD | % Rabatt | Teuerstes Produkt | Nur 1 Produkt rabattiert | Allgemein | ❌ Fehlend |
| TBD | 20% | Kleidung | Kombinierbar | Allgemein | ❌ Fehlend |
| TBD | 5% | Alles | Kombinierbar | Allgemein | ❌ Fehlend |
| SOMMER20 | 20% | Warenkorb | Gutschein-Checkout-Test | TC-PROMO-CHK-003 | ❌ Fehlend |

### 👥 Mitarbeiter-Accounts

**Test-Mitarbeiter mit Rabatt:**

| Land | Name | E-Mail | Rabatt | Status |
|------|------|--------|--------|--------|
| AT | Mitarbeiter AT | TBD | Nur Basispreis | ❌ Fehlend |
| DE | Mitarbeiter DE | TBD | Nur Basispreis | ❌ Fehlend |
| CH | Mitarbeiter CH | TBD | Nur Basispreis | ❌ Fehlend |

### 💳 Zahlungsarten (Staging)

| Land | Verfügbare Zahlungsarten |
|------|--------------------------|
| AT | Vorkasse, Rechnung |
| DE | Vorkasse, Rechnung |
| CH | Vorkasse, Rechnung |

---


*Generiert am 2026-01-22 08:59 aus test-inventory.yaml und config/config.yaml*
