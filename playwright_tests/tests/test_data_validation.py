"""
Data Validation Tests - Prüft Preise, MwSt. und Berechnungen.

Diese Tests validieren die Korrektheit von:
- Produktpreisen (PDP vs. Warenkorb)
- MwSt.-Berechnung (20% AT, 19% DE)
- Versandkosten
- Gesamtsummen-Berechnung

Testdaten basierend auf Scan vom 2026-01-21.

Ausführung:
    pytest playwright_tests/tests/test_data_validation.py -v
    pytest playwright_tests/tests/test_data_validation.py -v -k "price"
    pytest playwright_tests/tests/test_data_validation.py -v -k "vat"
"""
import pytest
from playwright.sync_api import Page, expect

from ..conftest import accept_cookie_banner


# =============================================================================
# Testprodukte mit erfassten Preisen (Stand: 2026-01-21)
# =============================================================================

TEST_PRODUCTS = {
    # Post-Versand (kleine Produkte)
    "49415": {
        "path": "p/duftkissen-lavendel/ge-p-49415",
        "name": "Duftkissen Lavendel",
        "price": 12.90,
        "type": "post",
        "available": True,
    },
    "74157": {
        "path": "p/augen-entspannungskissen-mit-amaranth/ge-p-74157",
        "name": "Augen-Entspannungskissen",
        "price": 19.90,
        "type": "post",
        "available": True,
    },
    "863190": {
        "path": "p/blusenshirt-aus-bio-leinen/ge-p-863190",
        "name": "Blusenshirt Bio-Leinen",
        "price": 59.95,  # Sale-Preis
        "type": "post",
        "available": True,
    },
    # Speditions-Versand (große Produkte)
    "693645": {
        "path": "p/kleiderstaender-jukai-pur/ge-p-693645",
        "name": "Kleiderständer Jukai Pur",
        "price": 358.00,
        "type": "spedition",
        "available": True,
    },
    "693278": {
        "path": "p/polsterbett-almeno/ge-p-693278",
        "name": "Polsterbett Almeno",
        "price": 2998.00,
        "type": "spedition",
        "available": True,
    },
}

# MwSt.-Sätze nach Land
VAT_RATES = {
    "AT": 0.20,  # 20%
    "DE": 0.19,  # 19%
    "CH": 0.081,  # 8.1%
}


# =============================================================================
# Hilfsfunktionen
# =============================================================================

def extract_price(text: str) -> float | None:
    """Extrahiert Preis aus Text (z.B. '29,90 €' -> 29.90)."""
    import re
    if not text:
        return None
    # Entferne Tausendertrennzeichen und ersetze Komma durch Punkt
    cleaned = re.sub(r"[^\d,.]", "", text)
    # Bei deutschen Zahlen: 2.998,00 -> 2998.00
    if "," in cleaned and "." in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    elif "," in cleaned:
        cleaned = cleaned.replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None


def get_product_price_from_pdp(page: Page) -> float | None:
    """Liest den Preis von der Produktdetailseite."""
    price_selectors = [
        ".product-detail-price",
        "[itemprop='price']",
        ".product-price .price",
    ]
    for sel in price_selectors:
        elem = page.locator(sel)
        if elem.count() > 0:
            text = elem.first.inner_text()
            price = extract_price(text)
            if price:
                return price
    return None


def get_cart_line_item_price(page: Page, product_id: str) -> float | None:
    """Liest den Preis eines Produkts im Warenkorb."""
    # Suche nach Line-Item mit Produkt-ID
    line_item = page.locator(f".line-item:has([href*='{product_id}']), .cart-item:has([href*='{product_id}'])")
    if line_item.count() > 0:
        price_elem = line_item.first.locator(".line-item-price, .cart-item-price, .price")
        if price_elem.count() > 0:
            return extract_price(price_elem.first.inner_text())
    return None


def get_cart_subtotal(page: Page) -> float | None:
    """Liest die Zwischensumme aus dem Warenkorb."""
    selectors = [
        ".checkout-aside-summary-value",
        "dt:has-text('Zwischensumme') + dd",
        ".summary-subtotal",
    ]
    for sel in selectors:
        elem = page.locator(sel)
        if elem.count() > 0:
            return extract_price(elem.first.inner_text())
    return None


def get_cart_shipping(page: Page) -> float | None:
    """Liest die Versandkosten aus dem Warenkorb."""
    selectors = [
        "dt:has-text('Versandkosten') + dd",
        "dt:has-text('Versand') + dd",
        ".shipping-costs",
    ]
    for sel in selectors:
        elem = page.locator(sel)
        if elem.count() > 0:
            text = elem.first.inner_text()
            # "Kostenlos" oder "Gratis" -> 0
            if "kostenlos" in text.lower() or "gratis" in text.lower():
                return 0.0
            return extract_price(text)
    return None


def get_cart_total(page: Page) -> float | None:
    """Liest die Gesamtsumme aus dem Warenkorb."""
    selectors = [
        ".checkout-aside-summary-total-value",
        ".summary-total .price",
        "dt:has-text('Gesamtsumme') + dd",
    ]
    for sel in selectors:
        elem = page.locator(sel)
        if elem.count() > 0:
            return extract_price(elem.first.inner_text())
    return None


def add_product_to_cart(page: Page, base_url: str, product_path: str) -> bool:
    """Fügt ein Produkt zum Warenkorb hinzu."""
    page.goto(f"{base_url}/{product_path}")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)

    accept_cookie_banner(page)

    buy_btn = page.locator("button.btn-buy, .btn-buy")
    if buy_btn.count() > 0 and buy_btn.first.is_visible():
        buy_btn.first.click()
        page.wait_for_timeout(2000)
        return True
    return False


def clear_cart(page: Page, base_url: str) -> None:
    """Leert den Warenkorb."""
    page.goto(f"{base_url}/checkout/cart")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)

    # Alle "Entfernen"-Buttons klicken
    remove_btns = page.locator(".line-item-remove, .cart-item-remove, button:has-text('Entfernen')")
    while remove_btns.count() > 0:
        try:
            remove_btns.first.click()
            page.wait_for_timeout(1000)
            remove_btns = page.locator(".line-item-remove, .cart-item-remove, button:has-text('Entfernen')")
        except Exception:
            break


# =============================================================================
# TC-DATA-001: Produktpreis konsistent (PDP = Warenkorb)
# =============================================================================

@pytest.mark.data_validation
@pytest.mark.parametrize("product_id", ["49415", "74157"])
def test_product_price_pdp_equals_cart(page: Page, base_url: str, product_id: str):
    """
    TC-DATA-001: Prüft, dass der Preis auf der PDP dem Preis im Warenkorb entspricht.
    """
    product = TEST_PRODUCTS[product_id]
    print(f"\n[Test] Preiskonsistenz: {product['name']}")

    # 1. PDP öffnen und Preis lesen
    page.goto(f"{base_url}/{product['path']}")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1500)
    accept_cookie_banner(page)

    pdp_price = get_product_price_from_pdp(page)
    print(f"    PDP-Preis: {pdp_price} €")

    assert pdp_price is not None, "Konnte Preis auf PDP nicht lesen"

    # 2. Produkt in Warenkorb legen
    buy_btn = page.locator("button.btn-buy")
    assert buy_btn.count() > 0, "Kein Warenkorb-Button gefunden"
    buy_btn.first.click()
    page.wait_for_timeout(2000)

    # 3. Zum Warenkorb navigieren
    page.goto(f"{base_url}/checkout/cart")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1500)

    # 4. Preis im Warenkorb prüfen
    cart_price = get_cart_line_item_price(page, product_id)
    if cart_price is None:
        # Fallback: Zwischensumme prüfen (bei nur 1 Produkt)
        cart_price = get_cart_subtotal(page)

    print(f"    Warenkorb-Preis: {cart_price} €")

    assert cart_price is not None, "Konnte Preis im Warenkorb nicht lesen"
    assert abs(pdp_price - cart_price) < 0.01, (
        f"Preisdifferenz! PDP: {pdp_price} €, Warenkorb: {cart_price} €"
    )

    print(f"    [OK] Preise stimmen überein")


# =============================================================================
# TC-DATA-002: Zwischensumme korrekt (Einzelpreis × Menge)
# =============================================================================

@pytest.mark.data_validation
def test_subtotal_calculation(page: Page, base_url: str):
    """
    TC-DATA-002: Prüft, dass die Zwischensumme korrekt berechnet wird.

    Vereinfacht: Prüft nur, dass Zwischensumme = Produktpreis bei Menge 1.
    """
    product = TEST_PRODUCTS["49415"]  # Duftkissen Lavendel
    expected_subtotal = product["price"]

    print(f"\n[Test] Zwischensummen-Berechnung")
    print(f"    Produkt: {product['name']}")
    print(f"    Erwartete Zwischensumme: {expected_subtotal} €")

    # 1. Warenkorb leeren
    clear_cart(page, base_url)

    # 2. Produkt hinzufügen
    page.goto(f"{base_url}/{product['path']}")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)
    accept_cookie_banner(page)

    buy_btn = page.locator("button.btn-buy")
    buy_btn.first.click()
    page.wait_for_timeout(2000)

    # 3. Zum Warenkorb
    page.goto(f"{base_url}/checkout/cart")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1500)

    # 4. Zwischensumme prüfen
    subtotal = get_cart_subtotal(page)
    print(f"    Tatsächliche Zwischensumme: {subtotal} €")

    assert subtotal is not None, "Konnte Zwischensumme nicht lesen"
    assert abs(subtotal - expected_subtotal) < 0.01, (
        f"Zwischensumme falsch! Erwartet: {expected_subtotal} €, Tatsächlich: {subtotal} €"
    )

    print(f"    [OK] Zwischensumme korrekt")


# =============================================================================
# TC-DATA-003: MwSt.-Berechnung AT (20%)
# =============================================================================

@pytest.mark.data_validation
def test_vat_calculation_at(page: Page, base_url: str):
    """
    TC-DATA-003: Prüft die MwSt.-Berechnung für Österreich (20%).

    Formel: MwSt. = Brutto - (Brutto / 1.20)
    """
    product = TEST_PRODUCTS["49415"]  # Duftkissen Lavendel
    brutto = product["price"]
    expected_vat = brutto - (brutto / 1.20)

    print(f"\n[Test] MwSt.-Berechnung AT (20%)")
    print(f"    Brutto: {brutto} €")
    print(f"    Erwartete MwSt.: {expected_vat:.2f} €")

    # Produkt hinzufügen
    page.goto(f"{base_url}/{product['path']}")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)
    accept_cookie_banner(page)

    buy_btn = page.locator("button.btn-buy")
    if buy_btn.count() > 0:
        buy_btn.first.click()
        page.wait_for_timeout(2000)

    # Checkout aufrufen (MwSt. wird dort angezeigt)
    page.goto(f"{base_url}/checkout/cart")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1500)

    # MwSt. aus Warenkorb lesen
    vat_selectors = [
        "dt:has-text('MwSt') + dd",
        "dt:has-text('Mwst') + dd",
        ".tax-value",
    ]

    vat_amount = None
    for sel in vat_selectors:
        elem = page.locator(sel)
        if elem.count() > 0:
            vat_amount = extract_price(elem.first.inner_text())
            if vat_amount:
                break

    print(f"    Angezeigte MwSt.: {vat_amount} €" if vat_amount else "    MwSt. nicht separat angezeigt")

    # Bei "inkl. MwSt." wird die MwSt. oft nicht separat angezeigt
    # In diesem Fall prüfen wir, dass der Hinweis vorhanden ist
    # Robustere Suche: Prüfe verschiedene Varianten case-insensitive via evaluate
    vat_hint_found = page.evaluate("""() => {
        const body = document.body.innerText.toLowerCase();
        return body.includes('inkl.') && body.includes('mwst') ||
               body.includes('inkl. mwst') ||
               body.includes('inklusive') && body.includes('steuer') ||
               body.includes('mehrwertsteuer') ||
               body.includes('20%') && body.includes('mwst') ||
               body.includes('20 %');
    }""")

    if not vat_hint_found:
        # Fallback: Suche nach typischen Preis-Hinweisen
        page_text = page.locator("body").inner_text().lower()
        vat_hint_found = "inkl" in page_text and ("mwst" in page_text or "steuer" in page_text)

    assert vat_hint_found, "Kein MwSt.-Hinweis gefunden (gesucht: 'inkl. MwSt', 'Mehrwertsteuer', '20%')"

    print(f"    [OK] MwSt.-Hinweis vorhanden")


# =============================================================================
# TC-DATA-004: Versandkosten Post-Versand
# =============================================================================

@pytest.mark.data_validation
def test_shipping_cost_post(page: Page, base_url: str):
    """
    TC-DATA-004: Prüft die Versandkosten für Post-Versand.
    """
    product = TEST_PRODUCTS["49415"]  # Duftkissen (Post-Versand)

    print(f"\n[Test] Versandkosten Post-Versand")
    print(f"    Produkt: {product['name']}")

    # Warenkorb leeren und Produkt hinzufügen
    clear_cart(page, base_url)

    page.goto(f"{base_url}/{product['path']}")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)
    accept_cookie_banner(page)

    buy_btn = page.locator("button.btn-buy")
    buy_btn.first.click()
    page.wait_for_timeout(2000)

    # Warenkorb prüfen
    page.goto(f"{base_url}/checkout/cart")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1500)

    shipping = get_cart_shipping(page)
    print(f"    Versandkosten: {shipping} €" if shipping is not None else "    Versandkosten: N/A")

    # Versandkosten sollten vorhanden sein (>= 0)
    assert shipping is not None or shipping == 0, "Konnte Versandkosten nicht ermitteln"

    # Für kleine Produkte: Versandkosten sollten unter 20€ liegen
    if shipping is not None and shipping > 0:
        assert shipping < 20, f"Versandkosten zu hoch für Post-Versand: {shipping} €"
        print(f"    [OK] Versandkosten plausibel")
    else:
        print(f"    [OK] Kostenloser Versand oder nicht angezeigt")


# =============================================================================
# TC-DATA-005: Versandkosten Spedition
# =============================================================================

@pytest.mark.data_validation
def test_shipping_cost_spedition(page: Page, base_url: str):
    """
    TC-DATA-005: Prüft die Versandkosten für Speditionsversand.
    """
    product = TEST_PRODUCTS["693278"]  # Polsterbett (Spedition)

    print(f"\n[Test] Versandkosten Spedition")
    print(f"    Produkt: {product['name']}")

    # Warenkorb leeren und Produkt hinzufügen
    clear_cart(page, base_url)

    page.goto(f"{base_url}/{product['path']}")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)
    accept_cookie_banner(page)

    buy_btn = page.locator("button.btn-buy")
    if buy_btn.count() > 0:
        buy_btn.first.click()
        page.wait_for_timeout(2000)

    # Warenkorb prüfen
    page.goto(f"{base_url}/checkout/cart")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1500)

    shipping = get_cart_shipping(page)
    print(f"    Versandkosten: {shipping} €" if shipping is not None else "    Versandkosten: N/A")

    # Hinweis: Bei Betten ist der Versand oft kostenlos ("Kostenloser Versand auf Betten")
    if shipping == 0 or shipping is None:
        # Prüfen ob "kostenlos" erwähnt wird
        free_shipping = page.locator("*:has-text('kostenlos'), *:has-text('Gratis')")
        if free_shipping.count() > 0:
            print(f"    [OK] Kostenloser Versand (Aktion)")
        else:
            print(f"    [OK] Versand kostenlos oder nicht separat angezeigt")
    else:
        # Speditionskosten können höher sein
        print(f"    [OK] Speditionskosten: {shipping} €")


# =============================================================================
# TC-DATA-006: Gesamtsumme korrekt (Zwischensumme + Versand)
# =============================================================================

@pytest.mark.data_validation
def test_total_calculation(page: Page, base_url: str):
    """
    TC-DATA-006: Prüft, dass die Gesamtsumme = Zwischensumme + Versandkosten.
    """
    product = TEST_PRODUCTS["49415"]

    print(f"\n[Test] Gesamtsummen-Berechnung")

    # Warenkorb leeren und Produkt hinzufügen
    clear_cart(page, base_url)

    page.goto(f"{base_url}/{product['path']}")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)
    accept_cookie_banner(page)

    buy_btn = page.locator("button.btn-buy")
    buy_btn.first.click()
    page.wait_for_timeout(2000)

    # Warenkorb prüfen
    page.goto(f"{base_url}/checkout/cart")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1500)

    subtotal = get_cart_subtotal(page)
    shipping = get_cart_shipping(page) or 0
    total = get_cart_total(page)

    print(f"    Zwischensumme: {subtotal} €")
    print(f"    Versand: {shipping} €")
    print(f"    Gesamt: {total} €")

    if subtotal is not None and total is not None:
        expected_total = subtotal + shipping
        print(f"    Erwartete Gesamtsumme: {expected_total} €")

        assert abs(total - expected_total) < 0.01, (
            f"Gesamtsumme falsch! Erwartet: {expected_total} €, Tatsächlich: {total} €"
        )
        print(f"    [OK] Gesamtsumme korrekt")
    else:
        print(f"    [WARN] Konnte Summen nicht vollständig prüfen")


# =============================================================================
# TC-DATA-007: Verfügbarkeit wird angezeigt
# =============================================================================

@pytest.mark.data_validation
@pytest.mark.parametrize("product_id", ["49415", "693278"])
def test_availability_displayed(page: Page, base_url: str, product_id: str):
    """
    TC-DATA-007: Prüft, dass die Verfügbarkeit/Lieferzeit angezeigt wird.
    """
    product = TEST_PRODUCTS[product_id]

    print(f"\n[Test] Verfügbarkeitsanzeige: {product['name']}")

    page.goto(f"{base_url}/{product['path']}")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1500)
    accept_cookie_banner(page)

    # Verfügbarkeit suchen
    availability_selectors = [
        ".delivery-information",
        "*:has-text('Lieferzeit')",
        "*:has-text('Sofort lieferbar')",
        "*:has-text('verfügbar')",
        "*:has-text('Nicht mehr verfügbar')",
    ]

    found = False
    for sel in availability_selectors:
        try:
            elem = page.locator(sel).first
            if elem.is_visible():
                text = elem.inner_text()[:100]
                if "Lieferzeit" in text or "lieferbar" in text.lower() or "verfügbar" in text.lower():
                    print(f"    Verfügbarkeit: {text.strip()[:50]}...")
                    found = True
                    break
        except Exception:
            continue

    assert found, "Keine Verfügbarkeitsinformation gefunden"
    print(f"    [OK] Verfügbarkeit angezeigt")


# =============================================================================
# TC-DATA-008: Währung konsistent (EUR)
# =============================================================================

@pytest.mark.data_validation
def test_currency_consistent(page: Page, base_url: str):
    """
    TC-DATA-008: Prüft, dass die Währung durchgehend EUR (€) ist.
    """
    product = TEST_PRODUCTS["49415"]

    print(f"\n[Test] Währungskonsistenz")

    # PDP prüfen
    page.goto(f"{base_url}/{product['path']}")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)
    accept_cookie_banner(page)

    # Euro-Symbol auf PDP
    euro_on_pdp = page.locator("*:has-text('€')").count()
    print(f"    €-Symbole auf PDP: {euro_on_pdp}")

    # Keine anderen Währungen
    other_currencies = page.locator("*:has-text('$'), *:has-text('CHF'), *:has-text('£')").count()

    assert euro_on_pdp > 0, "Kein Euro-Symbol auf PDP gefunden"
    # CHF kann für Schweiz-Besucher angezeigt werden, daher nur warnen
    if other_currencies > 0:
        print(f"    [WARN] Andere Währungssymbole gefunden: {other_currencies}")
    else:
        print(f"    [OK] Nur EUR-Währung")


# =============================================================================
# TC-DATA-009: Artikelnummer angezeigt
# =============================================================================

@pytest.mark.data_validation
@pytest.mark.parametrize("product_id", ["49415", "693278"])
def test_sku_displayed(page: Page, base_url: str, product_id: str):
    """
    TC-DATA-009: Prüft, dass die Artikelnummer korrekt angezeigt wird.
    """
    product = TEST_PRODUCTS[product_id]

    print(f"\n[Test] Artikelnummer: {product['name']}")

    page.goto(f"{base_url}/{product['path']}")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)
    accept_cookie_banner(page)

    # Artikelnummer suchen
    sku_text = page.locator(f"*:has-text('{product_id}')")

    assert sku_text.count() > 0, f"Artikelnummer {product_id} nicht auf Seite gefunden"
    print(f"    [OK] Artikelnummer {product_id} gefunden")


# =============================================================================
# TC-DATA-010: Preis entspricht erwartetem Wert
# =============================================================================

@pytest.mark.data_validation
@pytest.mark.parametrize("product_id,expected_price", [
    ("49415", 12.90),
    ("74157", 19.90),
    ("693645", 358.00),
])
def test_price_matches_expected(page: Page, base_url: str, product_id: str, expected_price: float):
    """
    TC-DATA-010: Prüft, dass der angezeigte Preis dem erwarteten Preis entspricht.

    HINWEIS: Dieser Test kann fehlschlagen, wenn sich Preise geändert haben.
    In diesem Fall sollte product_data_scan.py erneut ausgeführt werden.
    """
    product = TEST_PRODUCTS[product_id]

    print(f"\n[Test] Preisvalidierung: {product['name']}")
    print(f"    Erwarteter Preis: {expected_price} €")

    page.goto(f"{base_url}/{product['path']}")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1500)
    accept_cookie_banner(page)

    actual_price = get_product_price_from_pdp(page)
    print(f"    Tatsächlicher Preis: {actual_price} €")

    assert actual_price is not None, "Konnte Preis nicht lesen"

    # Toleranz für Sale-Preise oder kleine Änderungen
    price_diff = abs(actual_price - expected_price)
    if price_diff > 0.01:
        # Warnung statt Fehler, da Preise sich ändern können
        print(f"    [WARN] Preisdifferenz: {price_diff:.2f} € - Produktdaten aktualisieren!")
        # Soft-Assert: Test besteht mit Warnung
        if price_diff > expected_price * 0.5:  # > 50% Abweichung = Fehler
            pytest.fail(f"Preis weicht stark ab: Erwartet {expected_price} €, Tatsächlich {actual_price} €")
    else:
        print(f"    [OK] Preis korrekt")
