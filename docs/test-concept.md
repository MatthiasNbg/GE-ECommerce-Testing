# Test-Konzept: Grüne Erde E-Commerce Shop

**Projekt:** GE-ECommerce-Testing
**Datum:** 2026-02-04
**Version:** 1.06
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

<details>
<summary><strong>Detaillierte Testbeschreibungen</strong></summary>

Die 8 Warenkorb-Tests prüfen alle wesentlichen Funktionen des Warenkorbs: Hinzufügen, Entfernen, Mengenänderung, Preisberechnung und Persistenz. Alle Tests laufen in allen 3 Verkaufskanälen (AT, DE, CH).

#### Produkte verwalten (4 Tests)

**TC-CART-001: Produkt zum Warenkorb hinzufügen**
- **Schritte:** Produktdetailseite aufrufen → „In den Warenkorb" klicken → Warenkorb öffnen → Produktname und Preis prüfen
- **Erwartet:** Produkt wird im Warenkorb angezeigt, Name und Preis stimmen mit der Produktseite überein, Menge ist 1

**TC-CART-004: Produkt entfernen aktualisiert Warenkorb**
- **Schritte:** Zwei Produkte hinzufügen → Warenkorb öffnen → erstes Produkt entfernen → Inhalt und Gesamtpreis prüfen
- **Erwartet:** Nur noch ein Produkt im Warenkorb, Gesamtpreis und Zähler aktualisiert

**TC-CART-005: Leerer Warenkorb zeigt Meldung**
- **Schritte:** Sicherstellen dass Warenkorb leer ist → Warenkorb-Seite aufrufen → Meldung prüfen
- **Erwartet:** Hinweismeldung (z.B. „Ihr Warenkorb ist leer"), Weiter-Einkaufen-Link vorhanden

**TC-CART-007: Mehrere Produkte hinzufügen**
- **Schritte:** Drei verschiedene Produkte nacheinander hinzufügen → Warenkorb öffnen → alle Produkte und Gesamtpreis prüfen
- **Erwartet:** Alle drei Produkte mit korrekten Einzelpreisen, Gesamtpreis ist die Summe

#### Preisberechnung (2 Tests)

**TC-CART-003: Menge ändern aktualisiert Gesamtpreis**
- **Schritte:** Produkt hinzufügen → Warenkorb öffnen, Einzelpreis notieren → Menge auf 2 erhöhen → Gesamtpreis prüfen
- **Erwartet:** Gesamtpreis ist doppelter Einzelpreis, Zwischensumme wird ebenfalls aktualisiert

**TC-CART-008: Preisberechnung korrekt**
- **Schritte:** Mehrere Produkte mit unterschiedlichen Mengen hinzufügen → Einzelpreise prüfen → Zeilenpreise prüfen (Einzelpreis × Menge) → Gesamtpreis prüfen
- **Erwartet:** Einzelpreise stimmen mit Produktseiten überein, Zeilenpreise und Gesamtsumme mathematisch korrekt

#### Zähler & Persistenz (2 Tests)

**TC-CART-002: Warenkorb-Zähler aktualisiert sich**
- **Schritte:** Zähler im Header prüfen (0/leer) → Produkt hinzufügen → Zähler prüfen (1) → weiteres Produkt hinzufügen → Zähler prüfen (2)
- **Erwartet:** Zähler aktualisiert sich nach jedem Hinzufügen und zeigt korrekte Anzahl

**TC-CART-006: Warenkorb bleibt zwischen Seiten erhalten**
- **Schritte:** Produkt hinzufügen → zu Kategorie-Seite navigieren → Zähler prüfen → zur Homepage navigieren → Warenkorb öffnen
- **Erwartet:** Warenkorb-Inhalt und Zähler bleiben bei Navigation zwischen Seiten erhalten

**Automation:**
- **Playwright-Testdatei:** `playwright_tests/tests/test_cart.py`
- **Testdaten:** `playwright_tests/data/tests_basis.json` (TC-CART-001 bis TC-CART-008)
- **Cleanup:** Warenkorb wird nach jedem Test geleert

</details>

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

<details>
<summary><strong>Detaillierte Testbeschreibungen</strong></summary>

Die 9 Suchtests validieren die Shopware-Suchfunktion in drei Bereichen: Autocomplete-Dropdown, Suchergebnisseite und Negativtests. Alle Tests laufen in allen 3 Verkaufskanälen (AT, DE, CH).

#### Autocomplete / Suchvorschläge (6 Tests)

**TC-SEARCH-001: Autocomplete zeigt korrektes Produkt**
- **Schritte:** Suchfeld anklicken → bekannten Produktnamen eingeben (mind. 3 Zeichen) → Autocomplete-Dropdown prüfen
- **Erwartet:** Das gesuchte Produkt erscheint in den Vorschlägen

**TC-SEARCH-002: Autocomplete-Klick navigiert zu Produkt**
- **Schritte:** Suchbegriff eingeben → auf Produktvorschlag im Dropdown klicken → Produktdetailseite prüfen
- **Erwartet:** Navigation zur korrekten Produktseite

**TC-SEARCH-006: Suchvorschläge erscheinen bei Eingabe**
- **Schritte:** Suchfeld anklicken → langsam Buchstabe für Buchstabe eingeben → Dropdown prüfen
- **Erwartet:** Suchvorschläge erscheinen automatisch nach wenigen Zeichen

**TC-SEARCH-007: Suchvorschläge zeigen Kategorien**
- **Schritte:** Generischen Suchbegriff eingeben (z.B. „Bett", „Decke") → Dropdown prüfen
- **Erwartet:** Neben Produkten werden auch Kategorien angezeigt, visuell unterscheidbar

**TC-SEARCH-008: Autocomplete zeigt Produktbilder**
- **Schritte:** Suchbegriff eingeben → Produktvorschläge im Dropdown prüfen → Bildladung prüfen
- **Erwartet:** Jeder Produktvorschlag enthält ein korrekt geladenes Produktbild

**TC-SEARCH-009: Autocomplete Produktinfo vollständig**
- **Schritte:** Suchbegriff eingeben → Produktname, Preis und Bild in jedem Vorschlag prüfen
- **Erwartet:** Alle drei Informationen (Name, Preis, Bild) sind sichtbar und korrekt

#### Suchergebnisseite (2 Tests)

**TC-SEARCH-003: Suchergebnisseite zeigt korrektes Produkt**
- **Schritte:** Bekannten Produktnamen eingeben → Suche absenden (Enter) → Ergebnisse prüfen
- **Erwartet:** Suchergebnisseite wird geladen, das korrekte Produkt erscheint mit Name und Preis

**TC-SEARCH-004: Suchergebnis-Klick navigiert zu Produkt**
- **Schritte:** Suche durchführen → auf ein Suchergebnis klicken → Produktdetailseite prüfen
- **Erwartet:** Navigation zur korrekten Produktseite mit Name und Preis

#### Negativtest (1 Test)

**TC-SEARCH-005: Keine Ergebnisse bei ungültigem Artikel**
- **Schritte:** Nicht existierenden Suchbegriff eingeben (z.B. „xyzabc123") → Suche absenden → Ergebnisseite prüfen
- **Erwartet:** Keine Suchergebnisse, passende Hinweismeldung (z.B. „Keine Ergebnisse gefunden")

**Automation:**
- **Playwright-Testdatei:** `playwright_tests/tests/test_search.py`
- **Testdaten:** `playwright_tests/data/tests_basis.json` (TC-SEARCH-001 bis TC-SEARCH-009)
- **Hinweis:** Suchtests sind abhängig von aktuellen Produktdaten im Staging-Katalog

</details>

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

<details>
<summary><strong>Detaillierte Testbeschreibungen</strong></summary>

Die 8 Account-Tests decken den gesamten Benutzerlebenszyklus ab: Registrierung, Login und Profilverwaltung. Die Tests laufen in allen 3 Verkaufskanälen (AT, DE, CH) und sind in zwei funktionale Gruppen unterteilt.

#### Registrierung (4 Tests)

**TC-ACCOUNT-001: Registrierung erfolgreich**
- **Ziel:** Neue Kundenregistrierung mit gültigen Daten durchführen
- **Schritte:** Registrierungsseite aufrufen → Anrede, Vorname, Nachname eingeben → gültige E-Mail → sicheres Passwort → absenden → Bestätigung prüfen
- **Erwartet:** Registrierung erfolgreich, Benutzer wird eingeloggt oder erhält Bestätigung

**TC-ACCOUNT-002: Registrierung mit existierender E-Mail schlägt fehl**
- **Ziel:** Doppelte Registrierung wird verhindert
- **Schritte:** Registrierungsformular mit bereits registrierter E-Mail ausfüllen → absenden
- **Erwartet:** Fehlermeldung, kein doppelter Account wird angelegt

**TC-ACCOUNT-003: Registrierung mit ungültiger E-Mail zeigt Fehler**
- **Ziel:** Formular-Validierung erkennt ungültige E-Mail-Formate
- **Schritte:** Ungültige E-Mail eingeben (z.B. „test@", „test.de", „@domain.com") → absenden
- **Erwartet:** Validierungsfehler beim E-Mail-Feld, Registrierung wird nicht abgeschickt

**TC-ACCOUNT-004: Schwaches Passwort wird abgelehnt**
- **Ziel:** Passwort-Richtlinien werden durchgesetzt
- **Schritte:** Gültige Daten mit schwachem Passwort (z.B. „123") eingeben → absenden
- **Erwartet:** Fehlermeldung mit Passwort-Anforderungen, Registrierung wird nicht abgeschlossen

#### Login (2 Tests)

**TC-ACCOUNT-005: Login erfolgreich**
- **Vorbedingung:** Bestehender Kundenaccount mit bekannten Zugangsdaten
- **Schritte:** Login-Seite aufrufen → E-Mail und Passwort eingeben → absenden → Dashboard prüfen
- **Erwartet:** Benutzer ist eingeloggt, Dashboard wird angezeigt, Name/Anrede im Header sichtbar

**TC-ACCOUNT-006: Login mit falschen Daten schlägt fehl**
- **Schritte:** Login-Seite aufrufen → gültige E-Mail + falsches Passwort → absenden
- **Erwartet:** Fehlermeldung, Benutzer bleibt auf der Login-Seite

#### Profilverwaltung (2 Tests)

**TC-ACCOUNT-007: Profil anzeigen und bearbeiten**
- **Vorbedingung:** Bestehender Kundenaccount, eingeloggt
- **Schritte:** Zur Profilseite navigieren → Daten prüfen (Name, E-Mail) → Wert ändern (z.B. Vorname) → speichern → Seite neu laden → Änderung prüfen
- **Erwartet:** Daten werden korrekt angezeigt, Änderungen werden gespeichert und persistiert

**TC-ACCOUNT-008: Adressverwaltung**
- **Vorbedingung:** Bestehender Kundenaccount, eingeloggt
- **Schritte:** Adressverwaltung aufrufen → Übersicht prüfen → neue Adresse hinzufügen → speichern → in der Liste prüfen
- **Erwartet:** Adressübersicht zeigt alle Adressen, Hinzufügen/Bearbeiten/Löschen funktioniert

**Automation:**
- **Playwright-Testdatei:** `playwright_tests/tests/test_account.py`
- **Testdaten:** `playwright_tests/data/tests_basis.json` (TC-ACCOUNT-001 bis TC-ACCOUNT-008)
- **Hinweis:** Registrierungstests erzeugen Testaccounts – nach Testlauf ggf. bereinigen

</details>

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

<details>
<summary><strong>Detaillierte Testbeschreibungen</strong></summary>

Die 98 Versandarten-Tests validieren die korrekte Zuordnung von Logistikpartnern zu PLZ-Bereichen im Checkout. Jeder Test prüft für eine bestimmte PLZ, ob der erwartete Versandpartner und das korrekte Versandart-Label angezeigt werden. Pro PLZ-Bereich werden jeweils Minimum- und Maximum-PLZ getestet (Grenzwertanalyse).

**Teststrategie:**
- **Grenzwertanalyse:** Für jeden PLZ-Bereich wird die niedrigste (Min) und höchste (Max) PLZ getestet
- **Vollständige Abdeckung:** Alle Logistikpartner in allen 3 Ländern (AT, DE, CH) werden abgedeckt
- **Identischer Testablauf:** Jeder Test folgt demselben 4-Schritt-Ablauf

**Testablauf (alle 98 Tests identisch):**
1. **Speditionsprodukt zum Warenkorb hinzufügen** → Produkt ist im Warenkorb
2. **Zur Kasse navigieren** → Checkout-Seite wird geladen
3. **PLZ als Lieferadresse eingeben** → PLZ wird akzeptiert
4. **Versandart-Anzeige prüfen** → Korrekter Versandpartner und Label werden angezeigt

**Vorbedingungen:**
- Shop ist erreichbar
- Speditionsprodukt im Warenkorb
- Lieferadresse im jeweiligen Land

#### Österreich (AT) — 26 Tests, 5 Logistikpartner

**Post AT** — 2 Tests
- PLZ-Bereich: 0000–9999 (ganz Österreich)
- Label: „Postversand"
- Tests: TC-SHIP-AT-POST-001 (Min: 0000), TC-SHIP-AT-POST-002 (Max: 9999)

**Wetsch AT** — 2 Tests
- PLZ-Bereich: 6000–6999 (Tirol/Vorarlberg)
- Label: „Spedition Wetsch"
- Tests: TC-SHIP-AT-WETSCH-001 (Min: 6000), TC-SHIP-AT-WETSCH-002 (Max: 6999)

**Thurner AT** — 2 Tests
- PLZ-Bereich: 4700–5799 (Oberösterreich/Salzburg)
- Label: „Spedition Thurner"
- Tests: TC-SHIP-AT-THURNER-001 (Min: 4700), TC-SHIP-AT-THURNER-002 (Max: 5799)

**Fink AT** — 10 Tests
- PLZ-Bereiche: 1000–1199, 3000–3399, 3600–3699, 4000–4699, 8000–9999
- Label: „Spedition Fink"
- Tests: TC-SHIP-AT-FINK-001 bis TC-SHIP-AT-FINK-010 (je Min/Max pro Bereich)

**Cargoe AT** — 10 Tests
- PLZ-Bereiche: 1200–1399, 2000–2999, 3400–3599, 3700–3999, 7000–7999
- Label: „Spedition Cargoe"
- Tests: TC-SHIP-AT-CARGOE-001 bis TC-SHIP-AT-CARGOE-010 (je Min/Max pro Bereich)

#### Deutschland (DE) — 68 Tests, 6 Logistikpartner

**Post DE** — 2 Tests
- PLZ-Bereich: 00000–99999 (ganz Deutschland)
- Label: „Postversand"
- Tests: TC-SHIP-DE-POST-001 (Min: 00000), TC-SHIP-DE-POST-002 (Max: 99999)

**Logsens Nord** — 18 Tests
- PLZ-Bereiche: 19000–29999, 30000–32999, 34000–37139, 37140–37199, 37200–37399, 37400–39174, 39326–39499, 39500–39699, 49000–49999
- Label: „Spedition Logsens Nord"
- Tests: TC-SHIP-DE-LNORD-001 bis TC-SHIP-DE-LNORD-018 (je Min/Max pro Bereich)

**Logsens Ost** — 12 Tests
- PLZ-Bereiche: 00000–09999, 10000–15999, 16000–18999, 39175–39319, 95000–96999, 98000–99999
- Label: „Spedition Logsens Ost"
- Tests: TC-SHIP-DE-LOST-001 bis TC-SHIP-DE-LOST-012 (je Min/Max pro Bereich)

**Logsens Sued** — 12 Tests
- PLZ-Bereiche: 54000–54999, 56000–56999, 66000–67999, 72000–72999, 75000–79999, 80000–89999
- Label: „Spedition Logsens Sued"
- Tests: TC-SHIP-DE-LSUED-001 bis TC-SHIP-DE-LSUED-012 (je Min/Max pro Bereich)

**Logsens West** — 12 Tests
- PLZ-Bereiche: 33000–33999, 41000–41999, 42000–48999, 50000–53999, 57000–57999, 58000–59999
- Label: „Spedition Logsens West"
- Tests: TC-SHIP-DE-LWEST-001 bis TC-SHIP-DE-LWEST-012 (je Min/Max pro Bereich)

**Thurner DE** — 12 Tests
- PLZ-Bereiche: 55000–55999, 60000–65999, 68000–71999, 73000–74999, 90000–94999, 97000–97999
- Label: „Spedition Thurner"
- Tests: TC-SHIP-DE-THURNER-001 bis TC-SHIP-DE-THURNER-012 (je Min/Max pro Bereich)

#### Schweiz (CH) — 4 Tests, 2 Logistikpartner

**Post CH** — 2 Tests
- PLZ-Bereich: 1000–9658 (ganze Schweiz)
- Label: „Postversand"
- Tests: TC-SHIP-CH-001 (Min: 1000), TC-SHIP-CH-002 (Max: 9658)

**Kuoni CH** — 2 Tests
- PLZ-Bereich: 1000–9658 (ganze Schweiz)
- Label: „Spedition Kuoni"
- Tests: TC-SHIP-CH-003 (Min: 1000), TC-SHIP-CH-004 (Max: 9658)

**Automation:**
- **Playwright-Testdatei:** `playwright_tests/tests/test_shipping_plz.py`
- **Testdaten:** `playwright_tests/data/tests_versandarten.json`
- **Parametrisiert:** Alle 98 Tests laufen datengetrieben aus der JSON-Datei
- **CI/CD:** Automatische Ausführung vor Feature-Releases

</details>

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

**TC-PROMO-001: Nicht-rabattierbarer Artikel (639046)**
- **Beschreibung:** Prüft, dass Artikel mit nicht_rabattierbar = true von prozentualen und absoluten Warenkorb-Promotions ausgeschlossen werden
- **Bedingung:**
  - Produkt mit Odoo-Eigenschaft nicht_rabattierbar = true (Variante 639046)
  - Aktive Warenkorb-Promotion (prozentual oder absolut)
- **Testschritte:**
  1. Nicht-rabattierbares Produkt (639046) zum Warenkorb hinzufügen
  2. Optional: Weiteres rabattierbares Produkt hinzufügen
  3. Promotion-Code eingeben
  4. Prüfen, dass Rabatt NICHT auf das nicht-rabattierbare Produkt angewendet wird
  5. Prüfen, dass Rabatt korrekt nur auf rabattierbare Produkte berechnet wird
  6. Gesamtsumme validieren
- **Erwartetes Verhalten:**
  - Nicht-rabattierbarer Artikel bleibt zum vollen Preis im Warenkorb
  - Rabatt wird nur auf rabattierbare Artikel angewendet
  - Gesamtsumme = voller Preis nicht-rabattierbar + rabattierter Preis der übrigen Artikel
  - Keine Fehlermeldung – Promotion wird akzeptiert, aber nicht auf ausgeschlossene Produkte angewendet

**TC-PROMO-002: Ausschluss Kauf rabattierter Artikel**
- **Beschreibung:** Prüft, dass bereits reduzierte Artikel (Aktionspreis/SALE) von zusätzlichen Promotions ausgeschlossen werden
- **Bedingung:**
  - Produkt mit Aktionspreis (SALE-Preis aktiv)
  - Aktive Warenkorb-Promotion mit Ausschluss von Aktionspreisen
- **Testschritte:**
  1. Produkt mit Aktionspreis zum Warenkorb hinzufügen
  2. Reguläres Produkt (ohne Aktionspreis) zum Warenkorb hinzufügen
  3. Promotion-Code eingeben
  4. Prüfen, dass Rabatt nur auf das reguläre Produkt angewendet wird
  5. Prüfen, dass das SALE-Produkt zum Aktionspreis bleibt
- **Erwartetes Verhalten:**
  - Artikel mit Aktionspreis werden vom Promotion-Rabatt ausgeschlossen
  - Rabatt wird nur auf reguläre Artikel angewendet
  - Doppelrabattierung wird verhindert
  - Aktionspreis bleibt unverändert

**TC-PROMO-003: Ausschluss Kaufgutscheine mit Rabatten**
- **Beschreibung:** Prüft, dass Einkaufsgutscheine im Warenkorb von Promotion-Rabatten ausgeschlossen werden
- **Bedingung:**
  - Einkaufsgutschein im Warenkorb (z.B. 50€ Gutschein, HC Code 6609)
  - Aktive Warenkorb-Promotion
  - Shopware-Regel: [GE-Template-Warenkorb] mit Gutschein-Ausschluss
- **Testschritte:**
  1. Einkaufsgutschein zum Warenkorb hinzufügen
  2. Promotion-Code eingeben
  3. Prüfen, dass Rabatt NICHT auf den Gutschein angewendet wird
  4. Gutscheinpreis bleibt unverändert
- **Erwartetes Verhalten:**
  - Einkaufsgutscheine werden vom Promotion-Rabatt ausgeschlossen
  - Gutscheinpreis bleibt beim Nennwert (z.B. 50€)
  - Promotion wird ggf. auf andere rabattierbare Artikel angewendet
  - Kein Rabatt auf den Gutschein selbst

**TC-PROMO-004: Kein Rabatt auf Wertgutschein**
- **Beschreibung:** Prüft, dass Wertgutscheine (Geschenkgutscheine) grundsätzlich von allen Rabattaktionen ausgeschlossen sind
- **Bedingung:**
  - Wertgutschein im Warenkorb
  - Beliebige aktive Promotion (prozentual, absolut, automatisch)
- **Testschritte:**
  1. Wertgutschein zum Warenkorb hinzufügen
  2. Verschiedene Promotion-Codes eingeben (prozentual, absolut)
  3. Prüfen, dass kein Rabatt auf den Wertgutschein angewendet wird
  4. Automatische Promotions prüfen – ebenfalls kein Rabatt
- **Erwartetes Verhalten:**
  - Wertgutscheine sind von ALLEN Rabattaktionen ausgeschlossen
  - Kein Rabatt wird angewendet, weder manuell noch automatisch
  - Gutschein-Nennwert bleibt unverändert
  - Promotion-Code kann eingegeben werden, aber Rabatt greift nicht auf den Gutschein

#### Gutschein-Sicherheit (Brute-Force Tests)

| Test-ID | Name | Priorität | Status | Länder |
|---------|------|-----------|--------|--------|
| TC-PROMO-SEC-001 | Ausnutzungsmöglichkeiten Kaufgutscheine | P0 | ○ | AT, DE, CH |
| TC-PROMO-SEC-002 | Gutschein-Kombination für kostenlosen Warenkorb | P0 | ○ | AT, DE, CH |
| TC-PROMO-SEC-003 | Gutscheine zum Erreichen von MBW | P1 | ○ | AT, DE, CH |
| TC-PROMO-SEC-004 | Alle Gutschein-Kombinationen (Brute-Force) | P1 | ○ | AT, DE, CH |

**Detaillierte Testbeschreibungen:**

**TC-PROMO-SEC-001: Ausnutzungsmöglichkeiten Kaufgutscheine**
- **Beschreibung:** Prüft potenzielle Ausnutzungsmöglichkeiten beim Kauf von Einkaufsgutscheinen (z.B. Rabatt auf Gutschein anwenden, dann vollen Wert einlösen)
- **Bedingung:**
  - Einkaufsgutscheine verfügbar (verschiedene Nennwerte)
  - Verschiedene aktive Promotions vorhanden
- **Testschritte:**
  1. Einkaufsgutschein zum Warenkorb hinzufügen
  2. Versuchen, Promotion-Code auf Gutschein-Kauf anzuwenden
  3. Versuchen, automatische Promotions auf Gutschein anzuwenden
  4. Prüfen, ob rabattiert gekaufter Gutschein vollen Nennwert behält
  5. Verschiedene Gutschein-Nennwerte testen
- **Erwartetes Verhalten:**
  - Keine Promotion kann auf Gutschein-Kauf angewendet werden
  - Gutscheine können nicht unter Nennwert erworben werden
  - System verhindert Arbitrage-Möglichkeiten
  - Alle Schutzmechanismen greifen unabhängig vom Gutschein-Nennwert

**TC-PROMO-SEC-002: Gutschein-Kombination für kostenlosen Warenkorb**
- **Beschreibung:** Prüft, ob durch Kombination von Einlösegutscheinen und Promotions ein kostenloser Warenkorb erreicht werden kann
- **Bedingung:**
  - Einlösegutschein mit Guthaben vorhanden
  - Aktive Warenkorb-Promotion
- **Testschritte:**
  1. Günstiges Produkt zum Warenkorb hinzufügen
  2. Einlösegutschein eingeben (Guthaben > Warenwert)
  3. Zusätzlich Promotion-Code eingeben
  4. Prüfen, dass Endsumme nicht negativ wird
  5. Prüfen, dass kein Guthaben über den Warenwert hinaus erstattet wird
- **Erwartetes Verhalten:**
  - Warenkorb kann maximal auf 0 EUR reduziert werden
  - Kein negativer Warenkorbwert möglich
  - Überschüssiges Guthaben bleibt auf dem Gutschein
  - Promotion und Gutschein werden korrekt verrechnet

**TC-PROMO-SEC-003: Gutscheine zum Erreichen von MBW**
- **Beschreibung:** Prüft, ob Einlösegutscheine fälschlicherweise zum Mindestbestellwert (MBW) gezählt werden
- **Bedingung:**
  - Promotion mit Mindestbestellwert-Bedingung
  - Warenkorb unter MBW
  - Einlösegutschein verfügbar
- **Testschritte:**
  1. Produkte unter MBW-Grenze zum Warenkorb hinzufügen
  2. Einlösegutschein eingeben
  3. Prüfen, ob MBW-Promotion nun verfügbar ist
  4. MBW-Code eingeben
  5. Validieren, dass Gutschein-Guthaben NICHT zum MBW gezählt wird
- **Erwartetes Verhalten:**
  - Gutschein-Guthaben wird NICHT zum Warenwert für MBW-Berechnung addiert
  - MBW wird nur aus tatsächlichen Produktpreisen berechnet
  - Promotion wird weiterhin abgelehnt, wenn Produktwert unter MBW liegt

**TC-PROMO-SEC-004: Alle Gutschein-Kombinationen (Brute-Force)**
- **Beschreibung:** Systematischer Test aller möglichen Gutschein-Promotion-Kombinationen
- **Bedingung:**
  - Alle verfügbaren Gutschein-Typen (Einkaufsgutschein, Einlösegutschein, Wertgutschein)
  - Alle verfügbaren Promotion-Typen (prozentual, absolut, Versandkostenfrei, automatisch)
- **Testschritte:**
  1. Matrix aufbauen: Gutschein-Typen x Promotion-Typen
  2. Jede Kombination einzeln testen
  3. Mehrfach-Kombinationen testen (2+ Gutscheine + Promotion)
  4. Reihenfolge variieren (erst Gutschein, dann Promotion und umgekehrt)
  5. Ergebnisse dokumentieren
- **Erwartetes Verhalten:**
  - Keine Kombination führt zu negativem Warenwert
  - Alle Ausschlussregeln greifen konsistent
  - Reihenfolge der Eingabe hat keinen Einfluss auf das Ergebnis
  - Fehlermeldungen sind eindeutig und korrekt

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
| TC-PROMO-SHIP-007 | Versandkostenfrei gemischter Warenkorb (Post + Spedi) DE | P1 | ○ | DE |
| TC-PROMO-SHIP-008 | Versandkostenfrei gemischter Warenkorb (Post + Spedi) AT | P1 | ○ | AT |
| TC-PROMO-SHIP-009 | Versandkostenfrei gemischter Warenkorb (Post + Spedi) CH | P1 | ○ | CH |

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

**TC-PROMO-SHIP-007: Versandkostenfrei gemischter Warenkorb (Post + Spedi) DE**
- **Beschreibung:** Prüft Versandkostenfrei-Promotion bei gemischtem Warenkorb mit Post- und Speditionsartikeln für Deutschland
- **Bedingungen:**
  - Land = DE
  - Warenkorb enthält sowohl Postartikel als auch Speditionsartikel
  - Beide Versandarten werden im Checkout angezeigt
- **Testschritte:**
  1. Postartikel zum Warenkorb hinzufügen (z.B. Textil, kleines Produkt)
  2. Speditionsartikel zum Warenkorb hinzufügen (z.B. Möbel, großes Produkt)
  3. Prüfen, dass beide Versandarten im Checkout erscheinen
  4. Versandkostenfrei-Promocode für Post eingeben (TC-PROMO-SHIP-001)
  5. Prüfen, dass nur Postversandkosten auf 0 reduziert werden
  6. Prüfen, dass Speditionskosten unverändert bleiben
  7. Alternativ: Versandkostenfrei-Promocode für Spedi eingeben (TC-PROMO-SHIP-003)
  8. Prüfen, dass nur Speditionskosten auf 0 reduziert werden
- **Erwartetes Verhalten:**
  - Post-Promotion reduziert nur Postversandkosten
  - Spedi-Promotion reduziert nur Speditionskosten
  - Beide Versandarten werden separat berechnet und angezeigt
  - Korrekte Berechnung der Gesamtversandkosten

**TC-PROMO-SHIP-008: Versandkostenfrei gemischter Warenkorb (Post + Spedi) AT**
- **Beschreibung:** Prüft Versandkostenfrei-Promotion bei gemischtem Warenkorb mit Post- und Speditionsartikeln für Österreich
- **Bedingungen:**
  - Land = AT
  - Warenkorb enthält sowohl Postartikel als auch Speditionsartikel
  - Beide Versandarten werden im Checkout angezeigt
- **Testschritte:**
  1. Postartikel zum Warenkorb hinzufügen
  2. Speditionsartikel zum Warenkorb hinzufügen
  3. Prüfen, dass beide Versandarten im Checkout erscheinen
  4. Versandkostenfrei-Promocode für Post eingeben (TC-PROMO-SHIP-001)
  5. Prüfen, dass nur Postversandkosten (5,95 EUR) auf 0 reduziert werden
  6. Prüfen, dass Speditionskosten unverändert bleiben
  7. Alternativ: Versandkostenfrei-Promocode für Spedi eingeben (TC-PROMO-SHIP-003)
  8. Prüfen, dass nur Speditionskosten auf 0 reduziert werden
- **Erwartetes Verhalten:**
  - Analog zu TC-PROMO-SHIP-007, aber für AT-Kanal
  - Postversand AT und Spedi-Versand AT separat behandelt

**TC-PROMO-SHIP-009: Versandkostenfrei gemischter Warenkorb (Post + Spedi) CH**
- **Beschreibung:** Prüft Versandkostenfrei-Promotion bei gemischtem Warenkorb mit Post- und Speditionsartikeln für Schweiz
- **Bedingungen:**
  - Land = CH
  - Warenkorb enthält sowohl Postartikel als auch Speditionsartikel
  - Beide Versandarten werden im Checkout angezeigt
  - Preise in CHF
- **Testschritte:**
  1. Postartikel zum Warenkorb hinzufügen
  2. Speditionsartikel zum Warenkorb hinzufügen
  3. Prüfen, dass beide Versandarten im Checkout erscheinen
  4. Versandkostenfrei-Promocode für Post eingeben (TC-PROMO-SHIP-002)
  5. Prüfen, dass nur Postversandkosten (6,95 CHF) auf 0 reduziert werden
  6. Prüfen, dass Speditionskosten unverändert bleiben
  7. Alternativ: Versandkostenfrei-Promocode für Spedi eingeben (TC-PROMO-SHIP-004)
  8. Prüfen, dass nur Speditionskosten auf 0 reduziert werden
- **Erwartetes Verhalten:**
  - Post-Promotion reduziert nur Postversandkosten (6,95 CHF)
  - Spedi-Promotion reduziert nur Speditionskosten
  - Korrekte CHF-Berechnung der Gesamtversandkosten

#### Produktkategorien-Promotions

| Test-ID | Name | Priorität | Status | Länder |
|---------|------|-----------|--------|--------|
| TC-PROMO-CAT-001 | Promo auf Produktkategorie via advertising_material_id | P1 | ○ | AT, DE, CH |
| TC-PROMO-AUTO-001 | Automatisierte Promo auf Werbemittel ID 70 | P1 | ○ | AT, DE, CH |

**Detaillierte Testbeschreibungen:**

**TC-PROMO-CAT-001: Promo auf Produktkategorie via advertising_material_id**
- **Beschreibung:** Prüft, dass eine Promotion nur auf Produkte einer bestimmten Kategorie angewendet wird, identifiziert über advertising_material_id
- **Bedingung:**
  - Promotion mit Produktfilter auf bestimmte advertising_material_id
  - Produkte mit und ohne passende advertising_material_id vorhanden
- **Testschritte:**
  1. Produkt mit passender advertising_material_id zum Warenkorb hinzufügen
  2. Produkt OHNE passende advertising_material_id zum Warenkorb hinzufügen
  3. Promotion-Code eingeben
  4. Prüfen, dass Rabatt nur auf das Produkt mit passender ID angewendet wird
  5. Prüfen, dass das andere Produkt zum vollen Preis bleibt
  6. Test in allen Verkaufskanälen (AT, DE, CH) durchführen
- **Erwartetes Verhalten:**
  - Rabatt wird nur auf Produkte mit passender advertising_material_id angewendet
  - Produkte ohne passende ID bleiben unrabattiert
  - Prozentuale oder absolute Berechnung ist korrekt
  - Funktioniert in allen DACH-Verkaufskanälen

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

**Detaillierte Testbeschreibungen:**

**TC-PROMO-MOV-001: EUR-Rabatt ab Mindestbestellwert**
- **Beschreibung:** Prüft absolute EUR-Rabatte, die erst ab einem bestimmten Mindestbestellwert (MBW) greifen
- **Bedingung:**
  - Promotion mit absolutem EUR-Rabatt (z.B. 10 EUR Rabatt)
  - Mindestbestellwert-Bedingung (z.B. ab 50 EUR)
  - Shopware-Regel mit MBW-Bedingung
- **Testschritte:**
  1. Warenkorb mit Produkten unter MBW befüllen (z.B. 40 EUR)
  2. Promotion-Code eingeben → sollte abgelehnt werden
  3. Warenkorb auf über MBW erhöhen (z.B. 55 EUR)
  4. Promotion-Code erneut eingeben → sollte akzeptiert werden
  5. Prüfen, dass absoluter Rabatt korrekt abgezogen wird
  6. MBW-Grenzwert testen (exakt MBW-Betrag)
  7. Test in AT, DE, CH durchführen
- **Erwartetes Verhalten:**
  - Unter MBW: Promotion wird abgelehnt mit Hinweis auf MBW
  - Ab MBW: Promotion wird akzeptiert
  - Absoluter Rabatt wird korrekt abgezogen (Endsumme = Warenwert - Rabatt + Versand)
  - MBW wird nur auf Produktwert berechnet (ohne Versandkosten)

**TC-PROMO-MOV-002: MBW nur auf Warenkorb angewendet**
- **Beschreibung:** Prüft, dass der Mindestbestellwert nur auf den Warenkorb-Produktwert berechnet wird, nicht auf Versandkosten oder Gutscheine
- **Bedingung:**
  - Promotion mit MBW-Bedingung
  - Warenkorb mit Produkten + Versandkosten
- **Testschritte:**
  1. Produkte knapp unter MBW in den Warenkorb legen
  2. Prüfen, dass Versandkosten NICHT zum MBW gezählt werden
  3. Prüfen, dass Einlösegutscheine NICHT den Warenwert für MBW reduzieren
  4. Prüfen, dass nur Netto-Produktwerte für MBW zählen
  5. Produkt hinzufügen, bis MBW erreicht
  6. Promotion-Code eingeben → sollte akzeptiert werden
- **Erwartetes Verhalten:**
  - MBW wird ausschließlich aus Produktpreisen berechnet
  - Versandkosten, Gutschein-Guthaben und Rabatte fließen nicht in MBW-Berechnung ein
  - Korrekte Berechnung auch bei gemischtem Warenkorb (Post + Spedition)

#### Mengenrabatt-Promotions

| Test-ID | Name | Priorität | Status | Länder |
|---------|------|-----------|--------|--------|
| TC-PROMO-QTY-001 | % auf teuerstes Produkt | P1 | ○ | AT, DE, CH |

**Detaillierte Testbeschreibungen:**

**TC-PROMO-QTY-001: % auf teuerstes Produkt**
- **Beschreibung:** Prüft prozentuale Promotion, die nur auf das teuerste Produkt im Warenkorb angewendet wird
- **Bedingung:**
  - Promotion mit Rabatt-Anwendung auf "teuersten Artikel"
  - Warenkorb mit mehreren Produkten unterschiedlicher Preise
- **Testschritte:**
  1. Mehrere Produkte mit unterschiedlichen Preisen zum Warenkorb hinzufügen (z.B. 30€, 50€, 80€)
  2. Promotion-Code eingeben
  3. Prüfen, dass Rabatt nur auf das teuerste Produkt (80€) angewendet wird
  4. Prüfen, dass die günstigeren Produkte zum vollen Preis bleiben
  5. Prozentuale Berechnung validieren (z.B. 20% von 80€ = 16€ Rabatt)
  6. Gesamtsumme validieren
- **Erwartetes Verhalten:**
  - Rabatt wird nur auf das teuerste Produkt angewendet
  - Bei gleich teuren Produkten: Rabatt auf eines davon
  - Prozentuale Berechnung ist korrekt
  - Andere Produkte bleiben unverändert

#### Aktionspreis-Promotions

| Test-ID | Name | Priorität | Status | Länder |
|---------|------|-----------|--------|--------|
| TC-PROMO-SALE-001 | Rabatt auf Lieblingsprodukt (Aktionspreis) | P1 | ○ | AT, DE, CH |
| TC-PROMO-SALE-002 | Promo mit Produkt-ID via advertising_material_id | P1 | ○ | AT, DE, CH |
| TC-PROMO-SALE-003 | Promo mit leerer Promo-ID nicht möglich | P1 | ○ | AT, DE, CH |
| TC-PROMO-SALE-004 | SALE-Anzeige bei Aktionspreis korrekt | P1 | ○ | AT, DE, CH |

**Detaillierte Testbeschreibungen:**

**TC-PROMO-SALE-001: Rabatt auf Lieblingsprodukt (Aktionspreis)**
- **Beschreibung:** Prüft die "Lieblingsprodukt"-Promotion, bei der ein prozentualer Rabatt auf ein einzelnes, vom Kunden gewähltes Produkt angewendet wird (z.B. Code "Liebling20" für 20% auf teuerstes Produkt)
- **Bedingung:**
  - Promotion-Code: Liebling20 (oder je nach Kampagne)
  - Rabatt: Prozentual auf teuerstes Produkt
  - Aktive Kampagne mit gültigem Zeitraum
- **Testschritte:**
  1. Mehrere Produkte zum Warenkorb hinzufügen
  2. Promotion-Code "Liebling20" eingeben
  3. Prüfen, dass Rabatt auf das teuerste Produkt angewendet wird
  4. Aktionspreis-Berechnung validieren (20% von Einzelpreis)
  5. Prüfen, dass durchgestrichener Originalpreis angezeigt wird
  6. Test in allen Verkaufskanälen (AT, DE, CH) durchführen
- **Erwartetes Verhalten:**
  - 20% Rabatt wird auf das teuerste Produkt angewendet
  - Originalpreis wird durchgestrichen angezeigt
  - Aktionspreis wird korrekt berechnet
  - Andere Produkte bleiben unverändert

**TC-PROMO-SALE-002: Promo mit Produkt-ID via advertising_material_id**
- **Beschreibung:** Prüft, dass eine Promotion über die advertising_material_id gezielt auf bestimmte Produkte angewendet wird
- **Bedingung:**
  - Promotion mit Produktfilter über advertising_material_id
  - Produkte mit und ohne passende advertising_material_id
- **Testschritte:**
  1. Produkt mit passender advertising_material_id zum Warenkorb hinzufügen
  2. Produkt ohne passende ID hinzufügen
  3. Promotion-Code eingeben
  4. Prüfen, dass Rabatt nur auf Produkt mit passender ID angewendet wird
  5. Rabattberechnung validieren
- **Erwartetes Verhalten:**
  - Rabatt wird nur auf Produkte mit passender advertising_material_id angewendet
  - Andere Produkte bleiben unverändert
  - Filterung über advertising_material_id funktioniert korrekt

**TC-PROMO-SALE-003: Promo mit leerer Promo-ID nicht möglich**
- **Beschreibung:** Prüft, dass eine Promotion mit leerer oder fehlender advertising_material_id nicht angewendet werden kann (Schutz vor Fehlkonfiguration)
- **Bedingung:**
  - Promotion ohne advertising_material_id oder mit leerer ID
  - Beliebige Produkte im Warenkorb
- **Testschritte:**
  1. Produkt zum Warenkorb hinzufügen
  2. Promotion ohne gültige advertising_material_id versuchen anzuwenden
  3. Prüfen, dass keine Fehlkonfiguration zu unbeabsichtigten Rabatten führt
- **Erwartetes Verhalten:**
  - Promotion mit leerer ID wird nicht angewendet
  - Fehlermeldung oder stille Ablehnung
  - Kein unbeabsichtigter Rabatt auf alle Produkte

**TC-PROMO-SALE-004: SALE-Anzeige bei Aktionspreis korrekt**
- **Beschreibung:** Prüft die korrekte Frontend-Darstellung von SALE/Aktionspreisen (durchgestrichener Originalpreis, SALE-Badge, Rabatt-Prozent)
- **Bedingung:**
  - Produkt mit aktivem Aktionspreis (SALE)
  - Aktionspreis in Shopware konfiguriert
- **Testschritte:**
  1. Produktseite mit Aktionspreis aufrufen
  2. Prüfen, dass Originalpreis durchgestrichen angezeigt wird
  3. Prüfen, dass Aktionspreis prominent angezeigt wird
  4. Prüfen, dass SALE-Badge/Label vorhanden ist
  5. Prüfen, dass Preise in Listing/Kategorie-Übersicht korrekt angezeigt werden
  6. Prüfen, dass Aktionspreis im Warenkorb und Checkout korrekt übernommen wird
  7. Test in allen Verkaufskanälen (AT: EUR, DE: EUR, CH: CHF) durchführen
- **Erwartetes Verhalten:**
  - Originalpreis wird durchgestrichen angezeigt
  - Aktionspreis ist hervorgehoben (andere Farbe/Größe)
  - SALE-Badge ist auf PDP und in Listings sichtbar
  - Preise sind in Warenkorb und Checkout konsistent
  - Währungsformatierung ist je Verkaufskanal korrekt (EUR/CHF)

#### Mitarbeiterrabatt

| Test-ID | Name | Priorität | Status | Länder |
|---------|------|-----------|--------|--------|
| TC-PROMO-EMP-001 | Mitarbeiterrabatt nur auf Basispreis | P1 | ○ | AT, DE, CH |
| TC-PROMO-EMP-002 | Mitarbeiterrabatt nicht auf Aktionspreis | P1 | ○ | AT, DE, CH |

**Detaillierte Testbeschreibungen:**

**TC-PROMO-EMP-001: Mitarbeiterrabatt nur auf Basispreis**
- **Beschreibung:** Prüft, dass der Mitarbeiterrabatt auf den regulären Basispreis berechnet wird, nicht auf bereits reduzierte Preise
- **Bedingung:**
  - Eingeloggter Mitarbeiter-Account (spezielle Kundengruppe)
  - Automatische Mitarbeiter-Promotion aktiv
  - Produkte mit regulärem Preis im Warenkorb
- **Testschritte:**
  1. Mit Mitarbeiter-Account einloggen
  2. Reguläres Produkt (ohne Aktionspreis) zum Warenkorb hinzufügen
  3. Prüfen, dass Mitarbeiterrabatt automatisch angewendet wird
  4. Rabatt-Berechnung validieren (% vom Basispreis)
  5. Verschiedene Produktkategorien testen (Kleidung, Kosmetik, Möbel)
  6. Test in AT, DE und CH durchführen
- **Erwartetes Verhalten:**
  - Mitarbeiterrabatt wird automatisch auf Basispreis angewendet
  - Rabatt-Prozentsatz ist je Kategorie korrekt
  - Anzeige im Warenkorb: Originalpreis + Mitarbeiterrabatt-Zeile
  - Kein manueller Code erforderlich

**TC-PROMO-EMP-002: Mitarbeiterrabatt nicht auf Aktionspreis**
- **Beschreibung:** Prüft, dass der Mitarbeiterrabatt NICHT auf bereits reduzierte Aktionspreise (SALE) angewendet wird – keine Doppelrabattierung
- **Bedingung:**
  - Eingeloggter Mitarbeiter-Account
  - Produkt mit aktivem Aktionspreis (SALE)
- **Testschritte:**
  1. Mit Mitarbeiter-Account einloggen
  2. Produkt mit Aktionspreis zum Warenkorb hinzufügen
  3. Prüfen, dass KEIN zusätzlicher Mitarbeiterrabatt auf den Aktionspreis angewendet wird
  4. Prüfen, ob der Aktionspreis oder der Mitarbeiterrabatt günstiger ist
  5. Gemischter Warenkorb: Aktionspreis-Produkt + reguläres Produkt → Mitarbeiterrabatt nur auf reguläres
- **Erwartetes Verhalten:**
  - Kein Mitarbeiterrabatt auf Aktionspreise (keine Doppelrabattierung)
  - Produkt wird zum Aktionspreis berechnet
  - Bei gemischtem Warenkorb: Mitarbeiterrabatt nur auf reguläre Produkte
  - Alternativ: Der günstigere Preis (Aktionspreis vs. Mitarbeiterrabatt) wird angewendet

#### Bundle-Promotions

| Test-ID | Name | Priorität | Status | Länder |
|---------|------|-----------|--------|--------|
| TC-PROMO-BUNDLE-001 | Nimm 3 zahl 2 | P1 | ○ | AT, DE, CH |
| TC-PROMO-BUNDLE-003 | Kissen + Schonbezug gratis | P1 | ○ | AT, DE, CH |
| TC-PROMO-BUNDLE-004 | Pro Kissen ein Schonbezug gratis bei allen im Artikel | P1 | ○ | AT, DE, CH |

**Detaillierte Testbeschreibungen:**

**TC-PROMO-BUNDLE-001: Nimm 3 zahl 2**
- **Beschreibung:** Prüft die "Nimm 5, zahl 4"-Aktion – bei 5 gleichen Produkten wird das günstigste kostenlos
- **Bedingung:**
  - Promotion mit Regel "5 kaufen, 4 bezahlen"
  - Mindestmenge: 5 gleiche Produkte
  - Automatisch oder per Code
- **Testschritte:**
  1. 5x gleiches Produkt zum Warenkorb hinzufügen
  2. Prüfen, dass automatisch 1 Stück als Gratis markiert wird (oder Code eingeben)
  3. Gesamtpreis validieren (= 4x Einzelpreis)
  4. Mit 4 Stück testen → kein Rabatt
  5. Mit 6 Stück testen → weiterhin nur 1x gratis (oder 2x bei 10 Stück)
  6. Rabatt-Anzeige im Warenkorb prüfen
- **Erwartetes Verhalten:**
  - Bei 5 Stück: 1 Stück wird als 100% rabattiert angezeigt
  - Gesamtpreis = 4 × Einzelpreis
  - Unter 5 Stück: Kein Rabatt
  - Rabatt wird als separate Promotion-Zeile angezeigt

**TC-PROMO-BUNDLE-003: Kissen + Schonbezug gratis**
- **Beschreibung:** Prüft spezifische Bundle-Aktion: Beim Kauf eines Kissens wird ein passender Schonbezug gratis hinzugefügt
- **Bedingung:**
  - Promotion: Kissen-Kauf → Schonbezug gratis
  - Kissen und Schonbezug als Bundle konfiguriert
- **Testschritte:**
  1. Kissen zum Warenkorb hinzufügen
  2. Prüfen, ob Schonbezug automatisch als Gratisartikel erscheint
  3. Prüfen, dass Schonbezug mit 0 EUR/CHF angezeigt wird
  4. Prüfen, dass nur der passende Schonbezug hinzugefügt wird
  5. Anderes Kissen testen → anderer Schonbezug
  6. Kissen entfernen → Schonbezug wird ebenfalls entfernt
- **Erwartetes Verhalten:**
  - Passender Schonbezug wird automatisch gratis hinzugefügt
  - Schonbezug mit Preis 0 im Warenkorb
  - Korrekte Zuordnung Kissen → Schonbezug
  - Entfernung des Kissens entfernt auch den Schonbezug

**TC-PROMO-BUNDLE-004: Pro Kissen ein Schonbezug gratis bei allen im Artikel**
- **Beschreibung:** Prüft die Mengenstaffelung bei Bundle-Aktionen: Pro gekauftem Kissen wird jeweils ein Schonbezug gratis hinzugefügt
- **Bedingung:**
  - Promotion: Pro Kissen 1x Schonbezug gratis (Mengenstaffelung)
  - Mehrere Kissen im Warenkorb
- **Testschritte:**
  1. 1x Kissen zum Warenkorb hinzufügen → 1x Schonbezug gratis
  2. 2x Kissen hinzufügen → 2x Schonbezug gratis
  3. 3x Kissen hinzufügen → 3x Schonbezug gratis
  4. Kissen-Menge reduzieren → Schonbezug-Menge passt sich an
  5. Gesamtpreis validieren (nur Kissen-Preise, keine Schonbezug-Kosten)
  6. Verschiedene Kissen-Varianten testen
- **Erwartetes Verhalten:**
  - Anzahl Gratis-Schonbezüge = Anzahl Kissen
  - Mengenstaffelung funktioniert korrekt in beide Richtungen (erhöhen/reduzieren)
  - Gesamtpreis enthält nur Kissen-Preise
  - Bei Mischung verschiedener Kissen: jeweils passender Schonbezug

#### Promo-Kombinationen

| Test-ID | Name | Priorität | Status | Länder |
|---------|------|-----------|--------|--------|
| TC-PROMO-COMBO-001 | Zwei Promotions kombinierbar | P1 | ○ | AT, DE, CH |
| TC-PROMO-COMBO-002 | 20% Kleidung + 5% Alles | P1 | ○ | AT, DE, CH |

**Detaillierte Testbeschreibungen:**

**TC-PROMO-COMBO-001: Zwei Promotions kombinierbar**
- **Beschreibung:** Prüft, ob zwei unabhängige Promotions gleichzeitig auf denselben Warenkorb angewendet werden können
- **Bedingung:**
  - Zwei aktive, kombinierbare Promotions
  - Shopware-Promotion-Einstellung: "Kombination erlaubt" = true
- **Testschritte:**
  1. Produkte zum Warenkorb hinzufügen
  2. Ersten Promotion-Code eingeben → wird akzeptiert
  3. Zweiten Promotion-Code eingeben → wird akzeptiert
  4. Prüfen, dass beide Rabatte im Warenkorb angezeigt werden
  5. Prüfen, dass beide Rabatte korrekt berechnet werden
  6. Gesamtpreis validieren (beide Rabatte abgezogen)
  7. Reihenfolge umkehren und erneut testen
- **Erwartetes Verhalten:**
  - Beide Promotions werden gleichzeitig angewendet
  - Beide Rabatte erscheinen als separate Zeilen
  - Gesamtpreis ist korrekt (beide Rabatte berücksichtigt)
  - Reihenfolge der Eingabe hat keinen Einfluss auf Ergebnis

**TC-PROMO-COMBO-002: 20% Kleidung + 5% Alles**
- **Beschreibung:** Prüft die Kombination einer kategoriespezifischen Promotion (20% auf Kleidung) mit einer allgemeinen Promotion (5% auf alles)
- **Bedingung:**
  - Promotion 1: 20% auf Kleidung (automatisch oder per Code)
  - Promotion 2: 5% auf gesamten Warenkorb
  - Warenkorb mit Kleidung + Nicht-Kleidung
- **Testschritte:**
  1. Kleidungsprodukt zum Warenkorb hinzufügen
  2. Nicht-Kleidungsprodukt hinzufügen (z.B. Kosmetik)
  3. Beide Promotions aktivieren
  4. Kleidungsprodukt: Prüfen ob 20% + 5% = 25% oder sequenziell (20% dann 5% auf Rest)
  5. Nicht-Kleidungsprodukt: Nur 5% Rabatt
  6. Rabattberechnung validieren (additiv vs. sequenziell)
  7. Gesamtpreis prüfen
- **Erwartetes Verhalten:**
  - Kleidung erhält beide Rabatte (20% + 5%)
  - Nicht-Kleidung erhält nur 5%
  - Berechnung ist je nach Shopware-Konfiguration additiv oder sequenziell
  - Gesamtpreis ist korrekt berechnet

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
| TBD | Nimm 3 zahl 2 Testprodukt | Mengenrabatt | - | ❌ Fehlend |

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

<details>
<summary><strong>Detaillierte Testbeschreibungen</strong></summary>

Die Gutscheine und Rabattcodes werden in den Promotion-Testfällen (Abschnitt „Feature Tests – Promotions") verwendet. Hier ist dokumentiert, welche konkreten Codes für welche Testfälle benötigt werden, welcher Typ jeweils vorliegt und welche Sicherheitsmechanismen getestet werden.

#### Kaufgutscheine (Einkaufsgutscheine)

Kaufgutscheine sind Artikel, die im Shop erworben werden. Sie haben einen festen Nennwert und werden nach Kauf als Einlösegutschein aktiviert.

**Artikel 736675 – Einkaufsgutschein 50 EUR (HC Code 6609)**
- **Verwendung:** Checkout-Flow Tests (TC-PROMO-CHK-001 bis TC-PROMO-CHK-004)
- **Status:** Vorhanden
- **Testszenarien:**
  - Gutschein zu regulärem Warenkorb hinzufügen → muss blockiert werden (TC-PROMO-CHK-001)
  - Reguläres Produkt zu Gutschein-Warenkorb hinzufügen → muss blockiert werden (TC-PROMO-CHK-002)
  - Promotion auf Gutschein-Kauf anwenden → muss verhindert werden (TC-PROMO-CHK-003)
  - Gemischter Warenkorb im Checkout → muss durch CartValidator blockiert werden (TC-PROMO-CHK-004)

**Weitere Kaufgutscheine (noch anzulegen):**
- **100 EUR Einkaufsgutschein:** Für Checkout-Flow Tests mit höherem Nennwert
- **10 EUR / 25 EUR Kaufgutscheine:** Für Sicherheitstests – prüfen, dass Promotions nicht auf Gutschein-Käufe angewendet werden können (TC-PROMO-SEC-001: Arbitrage-Verhinderung)

#### Wertgutscheine (Einlösegutscheine)

Wertgutscheine haben ein Guthaben, das beim Checkout als Zahlungsmittel eingelöst wird. Sie sind keine Produkte, sondern werden als Zahlungsabzug verrechnet.

**Benötigte Wertgutscheine (noch anzulegen):**
- **25 EUR Wertgutschein:** Für Tests unter Mindestbestellwert-Grenze (TC-PROMO-SEC-003: Gutschein darf nicht zum MBW gezählt werden)
- **50 EUR Wertgutschein:** Für Kombinations-Tests (TC-PROMO-SEC-002: Gutschein + Promotion darf Warenkorb nicht unter 0 bringen)

**Sicherheitsrelevante Testfälle:**
- **TC-PROMO-SEC-002:** Einlösegutschein (Guthaben > Warenwert) + Promotion → Endsumme darf nicht negativ werden
- **TC-PROMO-SEC-003:** Einlösegutschein darf nicht zum Mindestbestellwert gezählt werden → MBW basiert nur auf Produktpreisen

#### Rabattcodes (Promotion-Codes)

Rabattcodes werden im Warenkorb oder Checkout eingegeben und aktivieren eine Shopware-Promotion. Die Codes sind an Regeln gebunden (Mindestbestellwert, Produktausschlüsse, Länderbeschränkung).

**Warenkorb-Rabatte:**
- **10% auf Warenkorb (MBW 50 EUR):** Allgemeiner Testcode für prozentuale Warenkorb-Promotions
- **15 EUR auf Warenkorb (MBW 100 EUR):** Allgemeiner Testcode für absolute Warenkorb-Promotions
- **20% auf Warenkorb:** Template-Test (TC-PROMO-CART-PERCENT-001) – mit Ausschluss nicht-rabattierbarer Artikel + Einkaufsgutscheine, 1x global / 5x pro Kunde

**Versandkostenfrei-Codes:**
- **Post DE/AT frei (5,95 EUR absolut):** TC-PROMO-SHIP-001 – nur Postversand, keine Spedition
- **Post CH frei (6,95 CHF absolut):** TC-PROMO-SHIP-002 – nur Postversand CH
- **Spedition DE/AT frei:** TC-PROMO-SHIP-003
- **Spedition CH frei:** TC-PROMO-SHIP-004
- **Post DE/AT frei ab MBW 50 EUR:** TC-PROMO-SHIP-005 – mit Mindestbestellwert-Bedingung
- **Post CH frei ab MBW 50 CHF:** TC-PROMO-SHIP-006 – mit Mindestbestellwert-Bedingung

**Spezial-Codes:**
- **20% auf Produktkategorie:** Über advertising_material_id gefiltert – nur bestimmte Produkte rabattiert
- **% auf teuerstes Produkt:** Nur 1 Artikel im Warenkorb wird rabattiert
- **20% auf Kleidung (kombinierbar):** Kann mit anderen Codes gestapelt werden
- **5% auf alles (kombinierbar):** Niedrigster Rabatt, kombinierbar mit kategoriespezifischen Codes
- **SOMMER20:** Testcode für TC-PROMO-CHK-003 (Promotion auf Gutschein-Warenkorb muss blockiert werden)

**Hinweise zur Einrichtung:**
- Alle Codes mit „TBD" müssen noch im Shopware-Admin angelegt werden
- Codes sollten auf der Staging-Umgebung eingerichtet werden, nicht auf Production
- Nutzungslimits beachten: Nach Testdurchläufen ggf. Zähler zurücksetzen
- Shopware-Regeln (z.B. GE_Promo_Lieferland-DA_nurPostversand) müssen vor den Promotions existieren

</details>

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
