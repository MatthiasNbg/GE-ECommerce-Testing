# GE E-Commerce Testing

Automatisiertes Testing-Framework fuer Gruene Erde Onlineshops (AT, DE, CH) auf Basis von Shopware 6 mit Playwright + pytest.

## Projekt-Struktur

- `playwright_tests/` - Testcode (Page Objects, Tests, Daten)
- `schema/examples/` - Test-Contract-JSON-Dateien (maschinenlesbare Testspezifikationen)
- `schema/.cache/test-contract.schema.json` - JSON-Schema fuer Test-Contracts
- `schema/validate.py` - Schema-Validierung
- `schema/generate_shipping_contracts.py` - Generator fuer Shipping-Contracts

## Regel: Automatische Contract-Erzeugung

Bei jeder neuen Testfunktion in `playwright_tests/tests/` MUSS ein zugehoeriger Test-Contract in `schema/examples/` erstellt werden.

**Wichtig:** Auch bei Umbenennungen oder Neuanlage von Test-IDs in `docs/test-concept.md` MUSS ein v3.0-Contract in `schema/examples/` erstellt werden — auch wenn der Test noch nicht implementiert ist (dann `automation.status: "planned"`).

### Dateinamen-Konvention

```
{TEST_ID}_{kurzbeschreibung}.json
```

Beispiele:
- `TC-SMOKE-001_homepage-laden.json`
- `TC-CART-003_menge-aendern.json`
- `TC-SHIP-AT-FINK-MIN-1000_versand-at-fink-1000.json`

### Test-ID-Vergabe

| Praefix | Kategorie | Naechste freie ID |
|---------|-----------|-------------------|
| TC-SMOKE-* | Smoke Tests | TC-SMOKE-007 |
| TC-CART-* | Warenkorb | TC-CART-010 |
| TC-CART-GIFT-* | Einkaufsgutschein/Warenkorb | TC-CART-GIFT-006 |
| TC-CHECKOUT-* | Checkout-Massentests | TC-CHECKOUT-006 |
| TC-CRITICAL-* | Kritischer Pfad | TC-CRITICAL-009 |
| TC-REG-* | Regression | TC-REG-016 |
| TC-SEARCH-* | Suche | TC-SEARCH-011 |
| TC-ACCOUNT-* | Account/Registrierung | TC-ACCOUNT-021 |
| TC-PROMO-* | Promotions/Gutscheine | Kontextabhaengig |
| TC-DATA-* | Datenvalidierung | TC-DATA-016 |
| TC-PERF-* | Performance | TC-PERF-004 |
| TC-PAY-* | Zahlung | TC-PAY-003 |
| TC-SHIP-* | Versand/Spedition | Via generate_shipping_contracts.py |
| TC-SHIP-COST-* | Versandkosten-Validierung | TC-SHIP-COST-AT-003 / TC-SHIP-COST-DE-003 |
| TC-CONTENT-* | Content/Kategorie-Zuordnung | TC-CONTENT-017 |
| TC-NAV-* | Navigation/Menue/Laenderwechsel | TC-NAV-007 |
| TC-PDP-* | Produktdetailseite | TC-PDP-008 |
| TC-LISTING-* | Kategorie/Listing/Filter | TC-LISTING-005 |
| TC-NEWSLETTER-* | Newsletter/Freundeskreis | TC-NEWSLETTER-010 |
| TC-TECH-* | Technisch (Cookie/Responsive/A11y) | TC-TECH-011 |
| TC-E2E-* | E2E Checkout | TC-E2E-004 |
| TC-E2E-CC-* | Click & Collect | TC-E2E-CC-003 |
| TC-WISH-* | Merkliste/Wishlist | TC-WISH-006 |

### Schema-Referenz

Schema: `schema/.cache/test-contract.schema.json`

Pflichtfelder: `test_id`, `name`, `category`, `priority`, `schema_version`, `scope`, `preconditions`, `steps`, `automation`, `orchestration`, `meta`

### `inputs`-Array in Steps

Jeder Step kann ein `inputs`-Array enthalten, das die maschinell ausfuehrbaren Aktionen beschreibt. Die 7 Action-Typen und ihre Playwright-Aequivalente:

| Action | Playwright-Aequivalent | Beschreibung |
|--------|------------------------|--------------|
| `navigate` | `page.goto(value)` | URL aufrufen |
| `fill` | `page.fill(selector, value)` | Textfeld ausfuellen |
| `select` | `page.select_option(selector, value)` | Dropdown auswaehlen |
| `check` | `page.check(selector)` | Checkbox aktivieren |
| `uncheck` | `page.uncheck(selector)` | Checkbox deaktivieren |
| `click` | `page.click(selector)` | Element anklicken |
| `wait` | `page.wait_for_selector(selector)` | Auf Element warten |

### Input-Objekt-Struktur

```json
{
  "action": "fill",
  "selector": "#billingAddressAddressZipcode",
  "value": "4020"
}
```

- `action` (erforderlich): Einer der 7 Action-Typen
- `selector` (optional): CSS-Selektor des Zielelements
- `value` (optional): Wert fuer fill/select/navigate

### Regeln fuer `inputs` vs. `selector_hint`

- `selector_hint`: Bleibt als menschenlesbarer Hinweis bestehen (Legacy)
- `inputs`: Maschinenlesbare Aktionen mit echten CSS-Selektoren aus den Page Objects
- Steps ohne UI-Interaktion (z.B. reine Pruefschritte) haben kein `inputs`-Array
- CSS-Selektoren MUESSEN aus den Page Objects stammen (`checkout_page.py`, `cart_page.py`, `account_page.py`, etc.)

### Beispiel-Contract mit `inputs`

```json
{
  "step": 1,
  "action": "Produktseite aufrufen",
  "expected": "Produktseite laedt korrekt",
  "inputs": [
    { "action": "navigate", "value": "/p/kurzarmshirt-aus-bio-baumwolle/ge-p-862990" }
  ]
}
```

### Validierung

```bash
python schema/validate.py schema/examples/
```

Erwartetes Ergebnis: 309 Dateien, 0 fehlerhaft, Exit-Code 0.
(68 neue Contracts: 6 NAV + 7 PDP + 4 LISTING + 9 NEWSLETTER + 10 ACCOUNT + 6 CONTENT + 10 TECH + 1 CART + 4 SHIP-COST + 1 PROMO-CHK + 4 PROMO-EMP + 1 PROMO-CAT + 2 PROMO-ADVID + 3 E2E)
