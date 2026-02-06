# Design: Merkliste (Wishlist) E2E Tests

**Datum:** 2026-02-06
**Status:** Genehmigt
**Scope:** AT-Channel, eingeloggter Benutzer

## Zusammenfassung

E2E-Tests fuer die Merklisten-Funktionalitaet (Wishlist) des Gruene Erde Shopware 6 Shops.
Nur AT-Channel, erfordert eingeloggten Benutzer.

## Testfaelle

| Test-ID | Name | Beschreibung |
|---------|------|-------------|
| TC-WISH-001 | Produkt zur Merkliste hinzufuegen | Von Produktseite ueber Herz-Button hinzufuegen, Merklisten-Seite pruefen |
| TC-WISH-002 | Mehrere Produkte hinzufuegen | 3 Produkte hinzufuegen, alle auf Merklisten-Seite sichtbar |
| TC-WISH-003 | Produkt von Merkliste entfernen | Produkt hinzufuegen, dann auf Merklisten-Seite entfernen |
| TC-WISH-004 | Produkt aus Merkliste in Warenkorb | Produkt auf Merkliste, dann "In den Warenkorb" auf der Merklisten-Seite |
| TC-WISH-005 | Leere Merkliste anzeigen | Merklisten-Seite ohne Produkte aufrufen, Leer-Hinweis pruefen |

## Technische Umsetzung

### Neue Dateien

- `playwright_tests/pages/wishlist_page.py` - Page Object
- `playwright_tests/tests/test_wishlist.py` - 5 Tests
- `schema/examples/TC-WISH-001_produkt-zur-merkliste.json`
- `schema/examples/TC-WISH-002_mehrere-produkte-merkliste.json`
- `schema/examples/TC-WISH-003_produkt-von-merkliste-entfernen.json`
- `schema/examples/TC-WISH-004_merkliste-in-warenkorb.json`
- `schema/examples/TC-WISH-005_leere-merkliste.json`

### WishlistPage Page Object

Erbt von `BasePage`, async Pattern wie andere Page Objects.

**Selektoren (Shopware 6):**
- Herz-Button (Produktseite): `[data-add-to-wishlist]`
- Status-Klasse: `.product-wishlist-not-added` / `.product-wishlist-added`
- Merklisten-Seite: `/wishlist`
- Texte: "Zum Merkzettel hinzufuegen" / "Vom Merkzettel entfernen"

**Methoden:**
- `toggle_wishlist_on_product_page()` - Herz klicken
- `is_product_on_wishlist()` - Prueft ob Herz aktiv
- `navigate_to_wishlist()` - `/wishlist` aufrufen
- `get_wishlist_items()` - Alle Produkte auf der Merkliste
- `get_wishlist_count()` - Anzahl Produkte
- `remove_item(index)` - Produkt entfernen
- `add_item_to_cart(index)` - In Warenkorb legen
- `is_wishlist_empty()` - Leer-Zustand pruefen
- `clear_wishlist()` - Alle Produkte entfernen (Cleanup)

### Teststruktur

- Sync Tests (wie `test_cart.py`)
- Marker: `@pytest.mark.wishlist`
- Login via `accept_cookie_banner` + direkte Login-Interaktion
- AT-Testkunde: `ge-at-1@matthias-sax.de` / `scharnsteinAT`
- Testprodukte: 3 Post-Versand-Produkte aus `config.yaml`
- Cleanup: Merkliste am Ende leeren

### Abhaengigkeiten

- Bestehende `AccountPage` fuer Login
- Bestehende `CartPage` fuer Warenkorb-Pruefung (TC-WISH-004)
- Testprodukte aus `config.yaml` (Post-Versand)
- Keine neuen Python-Packages noetig
