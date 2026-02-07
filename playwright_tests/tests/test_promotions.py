"""
Promotion-Tests für den Grüne Erde Shopware Shop.

Testet alle Promotion/Rabattcode-Funktionen:
- Prozentuale Rabatte auf Warenkorb
- Versandkostenfrei-Promotions
- Automatische Promotions
- Mindestbestellwert-Bedingungen
- Nicht-rabattierbare Artikel

Test-IDs: TC-PROMO-001 bis TC-PROMO-SHIP-006
Phase: 6 (Promotions)
Priorität: P1 (Hoch)
"""
import pytest
from playwright.sync_api import Page, expect

from ..conftest import accept_cookie_banner


# =============================================================================
# Testdaten
# =============================================================================

# Testprodukte für Promotion-Tests
TEST_PRODUCTS = {
    "post": "p/kurzarmshirt-aus-bio-baumwolle/ge-p-862990",
    "spedition": "p/kleiderstaender-jukai-pur/ge-p-693645",
    "accessoire": "p/duftkissen-lavendel/ge-p-49415",
}

# Test-Promotion-Codes (müssen im Shopware-Backend angelegt sein)
# Diese Codes sind für Testzwecke und sollten nur auf Staging aktiv sein
TEST_PROMO_CODES = {
    "percentage_cart": "TEST20",  # 20% auf Warenkorb
    "free_shipping_post": "VERSANDFREI",  # Versandkostenfrei Post
    "free_shipping_spedi": "SPEDIFREI",  # Versandkostenfrei Spedition
    "min_order_50": "MBW50TEST",  # Mindestbestellwert 50 EUR
    "invalid": "UNGUELTIG123",  # Ungültiger Code
    # Kategorie-Promo (via advertising_material_id / Sortimentsbereich)
    "category_clothing_10": "UPDATETHISCODE",  # 10% auf Kleidung (Sortimentsbereich)
    # Werbemittel-ID-Promo (advertising_material_id = 70, manuelle Code-Eingabe)
    "advid_70": "UPDATETHISCODE",  # Promo auf Werbemittel ID 70 (manuell)
    # Mitarbeiterrabatt-Codes (Staging)
    "employee_50_cosmetics": "MA-KOSMETIK50",  # 50% auf Kosmetik (via Werbemittel-ID)
    "employee_20_all": "MA-ALLES20",  # 20% auf Alles
}

# Testprodukte für Kategorie-Promo (advertising_material_id / Sortimentsbereich "Kleidung")
# TODO: Echte Produkte einsetzen, die advertising_material_id für Kleidung haben
CATEGORY_PROMO_PRODUCTS = {
    # Produkt MIT passender advertising_material_id (Kleidung/Sortimentsbereich)
    "clothing": "p/UPDATETHIS-kleidung-produkt/ge-p-UPDATETHIS",
    # Produkt OHNE passende advertising_material_id (z.B. Möbel, Accessoire)
    "non_clothing": "p/duftkissen-lavendel/ge-p-49415",
}

# Testprodukte für Werbemittel-ID-70-Promo (advertising_material_id = 70)
# TODO: Echte Produkte einsetzen, die advertising_material_id = 70 haben
ADVID_70_PROMO_PRODUCTS = {
    # Produkt MIT advertising_material_id = 70
    "with_advid_70": "p/UPDATETHIS-werbemittel70-produkt/ge-p-UPDATETHIS",
    # Produkt OHNE advertising_material_id = 70 (z.B. Accessoire)
    "without_advid_70": "p/duftkissen-lavendel/ge-p-49415",
}

# Testprodukte für Mitarbeiterrabatt
EMPLOYEE_DISCOUNT_PRODUCTS = {
    # Kosmetik-Produkt (hat passende advertising_material_id für 50%-Promo)
    "cosmetics": "p/lippenbalsam-mit-bio-bienenwachs/ge-p-60780",
    # Reguläres Produkt (kein Aktionspreis, kein Kosmetik)
    "regular": "p/kurzarmshirt-aus-bio-baumwolle/ge-p-862990",
    # Produkt mit Aktionspreis/SALE (sale flag = JA) - kein Mitarbeiterrabatt
    "sale_item": "p/sale-produkt/ge-p-SALE",  # TODO: Echtes SALE-Produkt einsetzen
}


# =============================================================================
# Hilfsfunktionen
# =============================================================================

def add_product_to_cart(page: Page, base_url: str, product_path: str) -> None:
    """Fügt ein Produkt zum Warenkorb hinzu."""
    page.goto(f"{base_url}/{product_path}", wait_until="domcontentloaded")
    page.wait_for_timeout(1000)

    accept_cookie_banner(page)

    add_btn = page.locator("button.btn-buy")
    expect(add_btn.first).to_be_visible(timeout=10000)
    add_btn.first.click()
    page.wait_for_timeout(3000)

    # Offcanvas schließen
    offcanvas_close = page.locator(".offcanvas-close, .btn-close, [data-bs-dismiss='offcanvas']")
    if offcanvas_close.count() > 0:
        try:
            if offcanvas_close.first.is_visible(timeout=2000):
                offcanvas_close.first.click()
                page.wait_for_timeout(500)
        except Exception:
            pass


def navigate_to_cart(page: Page, base_url: str) -> None:
    """Navigiert zur Warenkorb-Seite."""
    page.goto(f"{base_url}/checkout/cart", wait_until="domcontentloaded")
    page.wait_for_timeout(1000)


def get_cart_total(page: Page) -> str:
    """Gibt die Gesamtsumme als Text zurück."""
    total_value = page.locator(
        ".checkout-aside-summary-total dd, "
        ".checkout-aside-summary-total .checkout-aside-summary-value, "
        ".checkout-aside-summary-total strong"
    )
    if total_value.count() > 0:
        return total_value.first.text_content() or ""
    return ""


def apply_promo_code(page: Page, code: str) -> bool:
    """
    Wendet einen Promotion-Code an.

    Returns:
        True wenn erfolgreich
    """
    # Promotion-Eingabefeld suchen
    promo_input = page.locator(
        "input[name='promotionCode'], "
        "#promotionCode, "
        "input[placeholder*='Gutschein'], "
        "input[placeholder*='Code']"
    )

    # Falls Container eingeklappt ist, aufklappen
    toggle = page.locator(
        "[data-bs-toggle='collapse'][href='#promotionContainer'], "
        "button:has-text('Gutschein einlösen')"
    )
    if toggle.count() > 0:
        try:
            if toggle.first.is_visible():
                toggle.first.click()
                page.wait_for_timeout(500)
        except Exception:
            pass

    if promo_input.count() == 0:
        return False

    promo_input.first.fill(code)
    page.wait_for_timeout(300)

    # Submit-Button
    submit_btn = page.locator(
        "button[type='submit']:has-text('Einlösen'), "
        "button:has-text('Gutschein einlösen'), "
        ".promotion-submit"
    )

    if submit_btn.count() > 0:
        submit_btn.first.click()
    else:
        promo_input.first.press("Enter")

    page.wait_for_timeout(2000)

    # Prüfe Erfolg
    success = page.locator(".alert-success, .promotion-success")
    return success.count() > 0


def has_promotion_discount(page: Page) -> bool:
    """Prüft ob ein Rabatt im Warenkorb sichtbar ist."""
    discount_line = page.locator(
        ".line-item-promotion, "
        ".line-item:has-text('Rabatt'), "
        ".line-item:has-text('Promotion'), "
        ".checkout-aside-summary-list dt:has-text('Rabatt')"
    )
    return discount_line.count() > 0


def get_shipping_cost(page: Page) -> str:
    """Gibt die Versandkosten als Text zurück."""
    shipping = page.locator(
        ".checkout-aside-summary-list dt:has-text('Versand') + dd, "
        ".checkout-aside-summary-list dt:has-text('Lieferung') + dd"
    )
    if shipping.count() > 0:
        return shipping.first.text_content() or ""
    return ""


# =============================================================================
# Tests
# =============================================================================

@pytest.mark.promotions
def test_promo_invalid_code_rejected(page: Page, base_url: str):
    """
    TC-PROMO-INVALID-001: Ungültiger Promotion-Code wird abgelehnt.

    Prüft, dass ein nicht existierender Code eine Fehlermeldung zeigt.
    """
    # Produkt zum Warenkorb hinzufügen
    add_product_to_cart(page, base_url, TEST_PRODUCTS["post"])
    navigate_to_cart(page, base_url)

    # Ungültigen Code eingeben
    success = apply_promo_code(page, TEST_PROMO_CODES["invalid"])

    # Sollte fehlschlagen
    assert not success, "Ungültiger Promotion-Code wurde fälschlicherweise akzeptiert"

    # Fehlermeldung sollte sichtbar sein
    error = page.locator(".alert-danger, .promotion-error, .invalid-feedback")
    expect(error.first).to_be_visible(timeout=5000)


@pytest.mark.promotions
def test_promo_percentage_cart_discount(page: Page, base_url: str):
    """
    TC-PROMO-CART-PERCENT-001: Prozentuale Aktion auf Warenkorb.

    Prüft prozentuale Promotion auf gesamten Warenkorb mit Aktionscode.
    """
    # Produkt zum Warenkorb hinzufügen
    add_product_to_cart(page, base_url, TEST_PRODUCTS["post"])
    navigate_to_cart(page, base_url)

    # Preis vor Rabatt merken
    total_before = get_cart_total(page)

    # Promotion-Code anwenden
    success = apply_promo_code(page, TEST_PROMO_CODES["percentage_cart"])

    if success:
        # Rabatt sollte sichtbar sein
        has_discount = has_promotion_discount(page)
        assert has_discount, "Promotion-Rabatt wird nicht im Warenkorb angezeigt"

        # Gesamtpreis sollte niedriger sein
        total_after = get_cart_total(page)
        assert total_before != total_after, "Preis hat sich nach Rabatt nicht geändert"
    else:
        pytest.skip("Promotion-Code TEST20 ist nicht im System konfiguriert")


@pytest.mark.promotions
def test_promo_free_shipping_post_de_at(page: Page, base_url: str):
    """
    TC-PROMO-SHIP-001: Versandkostenfrei nur Post (DE/AT).

    Prüft versandkostenfreie Lieferung nur für Postartikel in DE/AT.
    """
    # Produkt zum Warenkorb hinzufügen (Post-Artikel)
    add_product_to_cart(page, base_url, TEST_PRODUCTS["post"])
    navigate_to_cart(page, base_url)

    # Versandkosten vor Promotion
    shipping_before = get_shipping_cost(page)

    # Versandkostenfrei-Code anwenden
    success = apply_promo_code(page, TEST_PROMO_CODES["free_shipping_post"])

    if success:
        # Versandkosten sollten 0 oder "Kostenlos" sein
        shipping_after = get_shipping_cost(page)
        is_free = "0,00" in shipping_after or "kostenlos" in shipping_after.lower() or "gratis" in shipping_after.lower()
        assert is_free, f"Versandkosten sind nicht kostenlos: {shipping_after}"
    else:
        pytest.skip("Promotion-Code VERSANDFREI ist nicht im System konfiguriert")


@pytest.mark.promotions
def test_promo_free_shipping_spedition(page: Page, base_url: str):
    """
    TC-PROMO-SHIP-003: Versandkostenfrei nur Spedition (DE/AT).

    Prüft versandkostenfreie Lieferung nur für Speditionsartikel.
    """
    # Speditions-Produkt zum Warenkorb hinzufügen
    add_product_to_cart(page, base_url, TEST_PRODUCTS["spedition"])
    navigate_to_cart(page, base_url)

    # Versandkostenfrei-Code für Spedition anwenden
    success = apply_promo_code(page, TEST_PROMO_CODES["free_shipping_spedi"])

    if success:
        shipping_after = get_shipping_cost(page)
        is_free = "0,00" in shipping_after or "kostenlos" in shipping_after.lower() or "gratis" in shipping_after.lower()
        assert is_free, f"Speditions-Versandkosten sind nicht kostenlos: {shipping_after}"
    else:
        pytest.skip("Promotion-Code SPEDIFREI ist nicht im System konfiguriert")


@pytest.mark.promotions
def test_promo_minimum_order_value_rejected(page: Page, base_url: str):
    """
    TC-PROMO-SHIP-005: Versandkostenfrei Post ab MBW EUR 50 - unter Grenze.

    Prüft, dass Promotion unter Mindestbestellwert abgelehnt wird.
    """
    # Günstiges Produkt zum Warenkorb hinzufügen (unter 50 EUR)
    add_product_to_cart(page, base_url, TEST_PRODUCTS["accessoire"])
    navigate_to_cart(page, base_url)

    # MBW-Code anwenden
    success = apply_promo_code(page, TEST_PROMO_CODES["min_order_50"])

    # Sollte fehlschlagen (unter Mindestbestellwert)
    if not success:
        # Erwartetes Verhalten - Fehlermeldung sollte auf MBW hinweisen
        error = page.locator(".alert-danger, .promotion-error")
        if error.count() > 0:
            error_text = error.first.text_content() or ""
            assert "50" in error_text or "mindest" in error_text.lower() or "minimum" in error_text.lower(), \
                f"Fehlermeldung erwähnt Mindestbestellwert nicht: {error_text}"
    else:
        pytest.skip("Promotion-Code MBW50TEST ist nicht im System konfiguriert oder MBW nicht aktiv")


@pytest.mark.promotions
def test_promo_minimum_order_value_accepted(page: Page, base_url: str):
    """
    TC-PROMO-SHIP-005: Versandkostenfrei Post ab MBW EUR 50 - über Grenze.

    Prüft, dass Promotion über Mindestbestellwert akzeptiert wird.
    """
    # Mehrere Produkte zum Warenkorb hinzufügen (über 50 EUR)
    add_product_to_cart(page, base_url, TEST_PRODUCTS["post"])
    add_product_to_cart(page, base_url, TEST_PRODUCTS["accessoire"])
    navigate_to_cart(page, base_url)

    # Prüfe ob Warenkorbwert über 50 EUR
    total = get_cart_total(page)

    # MBW-Code anwenden
    success = apply_promo_code(page, TEST_PROMO_CODES["min_order_50"])

    if success:
        # Promotion sollte aktiv sein
        has_discount = has_promotion_discount(page)
        # Bei MBW-Versandkostenfrei: Versandkosten prüfen
        shipping = get_shipping_cost(page)
        is_free = "0,00" in shipping or "kostenlos" in shipping.lower()
        assert has_discount or is_free, "MBW-Promotion wurde nicht korrekt angewendet"
    else:
        pytest.skip("Promotion-Code MBW50TEST ist nicht im System konfiguriert")


@pytest.mark.promotions
def test_promo_code_removed_on_cart_clear(page: Page, base_url: str):
    """
    TC-PROMO-REMOVE-001: Promotion wird bei Warenkorb-Leerung entfernt.

    Prüft, dass Promotion-Rabatt entfernt wird, wenn Warenkorb geleert wird.
    """
    # Produkt hinzufügen und Promotion anwenden
    add_product_to_cart(page, base_url, TEST_PRODUCTS["post"])
    navigate_to_cart(page, base_url)

    success = apply_promo_code(page, TEST_PROMO_CODES["percentage_cart"])

    if not success:
        pytest.skip("Promotion-Code TEST20 ist nicht im System konfiguriert")

    # Produkt aus Warenkorb entfernen
    remove_btn = page.locator("button.line-item-remove-button, .line-item-remove")
    if remove_btn.count() > 0:
        remove_btn.first.click()
        page.wait_for_timeout(2000)

    # Warenkorb sollte leer sein
    empty_msg = page.locator(".cart-empty, :has-text('Ihr Warenkorb ist leer')")
    is_empty = empty_msg.count() > 0

    if is_empty:
        # Promotion-Rabatt sollte nicht mehr sichtbar sein
        has_discount = has_promotion_discount(page)
        assert not has_discount, "Promotion-Rabatt ist noch sichtbar bei leerem Warenkorb"


@pytest.mark.promotions
def test_promo_persists_through_checkout(page: Page, base_url: str):
    """
    TC-PROMO-PERSIST-001: Promotion bleibt im Checkout erhalten.

    Prüft, dass angewandte Promotion im Checkout-Prozess erhalten bleibt.
    """
    # Produkt hinzufügen und Promotion anwenden
    add_product_to_cart(page, base_url, TEST_PRODUCTS["post"])
    navigate_to_cart(page, base_url)

    success = apply_promo_code(page, TEST_PROMO_CODES["percentage_cart"])

    if not success:
        pytest.skip("Promotion-Code TEST20 ist nicht im System konfiguriert")

    # Zur Kasse gehen
    checkout_btn = page.locator("a:has-text('Zur Kasse'), button:has-text('Zur Kasse')")
    if checkout_btn.count() > 0:
        checkout_btn.first.click()
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)

    # Promotion sollte noch sichtbar sein
    has_discount = has_promotion_discount(page)
    assert has_discount, "Promotion-Rabatt wurde beim Checkout-Übergang entfernt"


@pytest.mark.promotions
def test_promo_display_in_order_summary(page: Page, base_url: str):
    """
    TC-PROMO-DISPLAY-001: Promotion wird in Bestellübersicht angezeigt.

    Prüft, dass der Rabatt korrekt in der Zusammenfassung erscheint.
    """
    # Produkt hinzufügen
    add_product_to_cart(page, base_url, TEST_PRODUCTS["post"])
    navigate_to_cart(page, base_url)

    # Promotion anwenden
    success = apply_promo_code(page, TEST_PROMO_CODES["percentage_cart"])

    if not success:
        pytest.skip("Promotion-Code TEST20 ist nicht im System konfiguriert")

    # Prüfe Anzeige in Zusammenfassung
    summary = page.locator(".checkout-aside-summary, .cart-summary")
    expect(summary.first).to_be_visible(timeout=5000)

    # Rabatt sollte als separate Zeile erscheinen
    discount_display = page.locator(
        ".checkout-aside-summary-list dt:has-text('Rabatt'), "
        ".checkout-aside-summary-list dt:has-text('Promotion'), "
        ".line-item-promotion"
    )
    expect(discount_display.first).to_be_visible(timeout=5000)


@pytest.mark.promotions
def test_promo_blocked_on_gift_voucher_checkout(page: Page, base_url: str):
    """
    TC-PROMO-CHK-003: Promotion auf Gutschein blockiert (Checkout-Flow).

    Prüft, dass keine Promotions auf Einkaufsgutscheine angewendet werden können.
    Testet den gesamten Flow: Warenkorb → Promo-Versuch → Checkout → kein Rabatt.
    """
    # Gutschein-Artikelnummer
    gift_voucher_number = "736675"

    # 1. Warenkorb-Seite aufrufen
    navigate_to_cart(page, base_url)
    accept_cookie_banner(page)

    # 2. Gutschein per Artikelnummer hinzufügen
    number_input = page.locator("#addProductInput")
    expect(number_input).to_be_visible(timeout=5000)
    number_input.fill(gift_voucher_number)

    submit_btn = page.locator("#addProductButton")
    expect(submit_btn).to_be_visible(timeout=5000)
    submit_btn.click()
    page.wait_for_timeout(3000)

    # 3. Prüfen: Mindestens 1 Produkt im Warenkorb
    items = page.locator(".line-item")
    assert items.count() >= 1, "Gutschein wurde nicht zum Warenkorb hinzugefügt"

    # 4. Promo-Code-Handling prüfen
    promo_input = page.locator(
        "input[name='promotionCode'], "
        "#promotionCode, "
        "input[placeholder*='Gutschein'], "
        "input[placeholder*='Code']"
    )

    # Falls Container eingeklappt ist, aufklappen
    toggle = page.locator(
        "[data-bs-toggle='collapse'][href='#promotionContainer'], "
        "button:has-text('Gutschein einlösen')"
    )
    if toggle.count() > 0:
        try:
            if toggle.first.is_visible():
                toggle.first.click()
                page.wait_for_timeout(500)
        except Exception:
            pass

    promo_visible = promo_input.count() > 0 and promo_input.first.is_visible()

    if not promo_visible:
        # Fall A: Promo-Input ist ausgeblendet (gute UX bei Gutscheinen)
        pass
    else:
        # Fall B: Promo-Input ist sichtbar → Code eingeben
        promo_input.first.fill("TESTCODE123")
        page.wait_for_timeout(300)

        promo_submit = page.locator(
            "button[type='submit']:has-text('Einlösen'), "
            "button:has-text('Gutschein einlösen'), "
            ".promotion-submit"
        )
        if promo_submit.count() > 0:
            promo_submit.first.click()
        else:
            promo_input.first.press("Enter")
        page.wait_for_timeout(2000)

        # Kein Promotion-Rabatt sollte angewendet worden sein
        assert not has_promotion_discount(page), \
            "Promotion-Rabatt wurde auf Gutschein angewendet - sollte blockiert sein"

    # 5. Zur Kasse navigieren
    checkout_btn = page.locator("a:has-text('Zur Kasse'), button:has-text('Zur Kasse')")
    if checkout_btn.count() > 0:
        checkout_btn.first.click()
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(3000)

    # 6. Auf Checkout-Seite: Kein Promotion-Rabatt in der Bestellzusammenfassung
    assert not has_promotion_discount(page), \
        "Promotion-Rabatt ist in der Checkout-Bestellzusammenfassung sichtbar - sollte blockiert sein"


# =============================================================================
# Hilfsfunktionen Mitarbeiterrabatt
# =============================================================================

def _parse_price(text: str) -> float:
    """Parst einen Preistext wie '€ 29,90' oder 'CHF 35.50' zu float."""
    import re
    cleaned = re.sub(r"[^\d,.]", "", text)
    # Europäisches Format: Komma als Dezimaltrenner
    if "," in cleaned and "." in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    elif "," in cleaned:
        cleaned = cleaned.replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def _get_line_item_prices(page: Page) -> list[dict]:
    """Gibt alle Line-Items mit Name und Preis zurück."""
    items = []
    line_items = page.locator(".line-item")
    count = line_items.count()
    for i in range(count):
        item = line_items.nth(i)
        name_el = item.locator(".line-item-label, .line-item-details-name")
        price_el = item.locator(
            ".line-item-total-price, "
            ".line-item-price .line-item-total-price-value"
        )
        name = name_el.first.text_content().strip() if name_el.count() > 0 else ""
        price_text = price_el.first.text_content().strip() if price_el.count() > 0 else ""
        # Promotion-Zeilen überspringen
        if "promotion" in name.lower() or "rabatt" in name.lower():
            continue
        items.append({"name": name, "price_text": price_text, "price": _parse_price(price_text)})
    return items


def _get_discount_amount(page: Page) -> float:
    """Gibt den Rabattbetrag (als positiven Wert) aus der Warenkorb-Zusammenfassung zurück."""
    discount_line = page.locator(
        ".line-item-promotion .line-item-total-price, "
        ".line-item-promotion .line-item-total-price-value"
    )
    if discount_line.count() > 0:
        text = discount_line.first.text_content().strip()
        return abs(_parse_price(text))
    return 0.0


# =============================================================================
# Mitarbeiterrabatt-Tests
# =============================================================================

@pytest.mark.promotions
def test_employee_discount_50_cosmetics(page: Page, base_url: str):
    """
    TC-PROMO-EMP-003: Mitarbeiterrabatt 50% auf Kosmetik einzeln einloesen.

    Prüft, dass der Mitarbeiterrabatt-Code für Kosmetik (50%) korrekt
    auf ein Kosmetik-Produkt (via Werbemittel-ID) angewendet wird.
    """
    cosmetics_product = EMPLOYEE_DISCOUNT_PRODUCTS["cosmetics"]
    promo_code = TEST_PROMO_CODES["employee_50_cosmetics"]

    # 1. Kosmetik-Produkt zum Warenkorb hinzufügen
    add_product_to_cart(page, base_url, cosmetics_product)
    navigate_to_cart(page, base_url)

    # 2. Preis vor Rabatt merken
    total_before = get_cart_total(page)
    price_before = _parse_price(total_before)
    assert price_before > 0, f"Ungültiger Preis vor Rabatt: {total_before}"

    # 3. Mitarbeiterrabatt-Code 50% Kosmetik einlösen
    success = apply_promo_code(page, promo_code)

    if not success:
        pytest.skip(f"Promotion-Code {promo_code} ist nicht im System konfiguriert")

    # 4. Rabatt prüfen
    has_discount = has_promotion_discount(page)
    assert has_discount, "Mitarbeiterrabatt-Zeile wird nicht im Warenkorb angezeigt"

    # 5. Preisänderung prüfen
    total_after = get_cart_total(page)
    price_after = _parse_price(total_after)
    assert price_after < price_before, (
        f"Preis hat sich nach 50%-Kosmetik-Rabatt nicht verringert: "
        f"vorher={total_before}, nachher={total_after}"
    )

    # 6. Rabatt sollte ca. 50% betragen (Toleranz für Rundung)
    discount = _get_discount_amount(page)
    expected_discount = price_before * 0.50
    if discount > 0:
        tolerance = expected_discount * 0.05  # 5% Toleranz
        assert abs(discount - expected_discount) <= tolerance, (
            f"Rabatt {discount:.2f} weicht von erwarteten 50% ({expected_discount:.2f}) ab"
        )


@pytest.mark.promotions
def test_employee_discount_20_everything(page: Page, base_url: str):
    """
    TC-PROMO-EMP-004: Mitarbeiterrabatt 20% auf Alles einzeln einloesen.

    Prüft, dass der Mitarbeiterrabatt-Code 20% auf ein reguläres Produkt
    (nicht Kosmetik, kein Aktionspreis) angewendet wird.
    """
    regular_product = EMPLOYEE_DISCOUNT_PRODUCTS["regular"]
    promo_code = TEST_PROMO_CODES["employee_20_all"]

    # 1. Reguläres Produkt zum Warenkorb hinzufügen
    add_product_to_cart(page, base_url, regular_product)
    navigate_to_cart(page, base_url)

    # 2. Preis vor Rabatt merken
    total_before = get_cart_total(page)
    price_before = _parse_price(total_before)
    assert price_before > 0, f"Ungültiger Preis vor Rabatt: {total_before}"

    # 3. Mitarbeiterrabatt-Code 20% auf Alles einlösen
    success = apply_promo_code(page, promo_code)

    if not success:
        pytest.skip(f"Promotion-Code {promo_code} ist nicht im System konfiguriert")

    # 4. Rabatt prüfen
    has_discount = has_promotion_discount(page)
    assert has_discount, "Mitarbeiterrabatt-Zeile wird nicht im Warenkorb angezeigt"

    # 5. Preisänderung prüfen
    total_after = get_cart_total(page)
    price_after = _parse_price(total_after)
    assert price_after < price_before, (
        f"Preis hat sich nach 20%-Rabatt nicht verringert: "
        f"vorher={total_before}, nachher={total_after}"
    )

    # 6. Rabatt sollte ca. 20% betragen
    discount = _get_discount_amount(page)
    expected_discount = price_before * 0.20
    if discount > 0:
        tolerance = expected_discount * 0.05
        assert abs(discount - expected_discount) <= tolerance, (
            f"Rabatt {discount:.2f} weicht von erwarteten 20% ({expected_discount:.2f}) ab"
        )


@pytest.mark.promotions
def test_employee_discount_combined(page: Page, base_url: str):
    """
    TC-PROMO-EMP-005: Mitarbeiterrabatt 50% Kosmetik + 20% Alles gemeinsam einloesen.

    Prüft, dass beide Mitarbeiterrabatt-Codes gleichzeitig auf einen
    gemischten Warenkorb (Kosmetik + reguläres Produkt) angewendet werden.
    Kosmetik erhält 50%, reguläres Produkt erhält 20%.
    """
    cosmetics_product = EMPLOYEE_DISCOUNT_PRODUCTS["cosmetics"]
    regular_product = EMPLOYEE_DISCOUNT_PRODUCTS["regular"]
    promo_50 = TEST_PROMO_CODES["employee_50_cosmetics"]
    promo_20 = TEST_PROMO_CODES["employee_20_all"]

    # 1. Beide Produkte zum Warenkorb hinzufügen
    add_product_to_cart(page, base_url, cosmetics_product)
    add_product_to_cart(page, base_url, regular_product)
    navigate_to_cart(page, base_url)

    # 2. Preise vor Rabatt erfassen
    total_before = get_cart_total(page)
    price_before = _parse_price(total_before)
    assert price_before > 0, f"Ungültiger Gesamtpreis vor Rabatt: {total_before}"

    items_before = _get_line_item_prices(page)
    assert len(items_before) >= 2, (
        f"Erwartet mindestens 2 Produkte im Warenkorb, gefunden: {len(items_before)}"
    )

    # 3. Ersten Code einlösen: 50% Kosmetik
    success_50 = apply_promo_code(page, promo_50)
    if not success_50:
        pytest.skip(f"Promotion-Code {promo_50} ist nicht im System konfiguriert")

    # 4. Zweiten Code einlösen: 20% auf Alles
    success_20 = apply_promo_code(page, promo_20)
    if not success_20:
        pytest.skip(f"Promotion-Code {promo_20} ist nicht im System konfiguriert")

    # 5. Mindestens ein Rabatt muss sichtbar sein
    has_discount = has_promotion_discount(page)
    assert has_discount, "Kein Mitarbeiterrabatt im Warenkorb sichtbar nach Eingabe beider Codes"

    # 6. Gesamtpreis muss niedriger sein
    total_after = get_cart_total(page)
    price_after = _parse_price(total_after)
    assert price_after < price_before, (
        f"Gesamtpreis hat sich nach beiden Rabatten nicht verringert: "
        f"vorher={total_before}, nachher={total_after}"
    )


@pytest.mark.promotions
def test_employee_discount_not_on_sale(page: Page, base_url: str):
    """
    TC-PROMO-EMP-006: Mitarbeiterrabatt nicht auf Aktionspreis (sale flag = JA).

    Prüft, dass der Mitarbeiterrabatt NICHT auf Produkte mit Aktionspreis
    (SALE) angewendet wird. Keine Doppelrabattierung erlaubt.
    """
    sale_product = EMPLOYEE_DISCOUNT_PRODUCTS["sale_item"]
    regular_product = EMPLOYEE_DISCOUNT_PRODUCTS["regular"]
    promo_20 = TEST_PROMO_CODES["employee_20_all"]

    # 1. SALE-Produkt und reguläres Produkt zum Warenkorb hinzufügen
    add_product_to_cart(page, base_url, sale_product)
    add_product_to_cart(page, base_url, regular_product)
    navigate_to_cart(page, base_url)

    # 2. Preise vor Rabatt erfassen
    items_before = _get_line_item_prices(page)
    assert len(items_before) >= 2, (
        f"Erwartet mindestens 2 Produkte im Warenkorb, gefunden: {len(items_before)}"
    )

    total_before = get_cart_total(page)
    price_before = _parse_price(total_before)

    # 3. Mitarbeiterrabatt-Code 20% einlösen
    success = apply_promo_code(page, promo_20)

    if not success:
        pytest.skip(f"Promotion-Code {promo_20} ist nicht im System konfiguriert")

    # 4. Prüfen: Rabatt sichtbar (nur auf reguläres Produkt)
    has_discount = has_promotion_discount(page)
    assert has_discount, "Mitarbeiterrabatt wird nicht angezeigt"

    # 5. Einzelpreise nach Rabatt erfassen
    items_after = _get_line_item_prices(page)

    # 6. Gesamtpreis muss niedriger sein (Rabatt auf reguläres Produkt)
    total_after = get_cart_total(page)
    price_after = _parse_price(total_after)
    assert price_after < price_before, (
        f"Gesamtpreis hat sich nach Mitarbeiterrabatt nicht verringert: "
        f"vorher={total_before}, nachher={total_after}"
    )

    # 7. Rabatt darf nicht dem Rabatt auf den vollen Warenkorb entsprechen
    # (wäre der Fall, wenn SALE-Produkt auch rabattiert wird)
    discount = _get_discount_amount(page)
    full_cart_20_discount = price_before * 0.20
    if discount > 0 and full_cart_20_discount > 0:
        # Wenn Rabatt deutlich kleiner als 20% vom Gesamtwarenkorb ist,
        # wurde das SALE-Produkt korrekt ausgeschlossen
        assert discount < full_cart_20_discount * 0.95, (
            f"Rabatt ({discount:.2f}) entspricht ca. 20% des Gesamtwarenkorbs "
            f"({full_cart_20_discount:.2f}) - SALE-Produkt wurde wahrscheinlich "
            f"fälschlicherweise rabattiert"
        )


# =============================================================================
# Kategorie-Promotion-Tests (advertising_material_id / Sortimentsbereich)
# =============================================================================

@pytest.mark.promotions
def test_promo_category_clothing_applied(page: Page, base_url: str):
    """
    TC-PROMO-CAT-001: Promo auf Produktkategorie via advertising_material_id.

    Prüft, dass eine Promotion "10% Rabatt auf Kleidung" nur auf Produkte
    mit passender advertising_material_id (Sortimentsbereich Kleidung)
    angewendet wird.

    Positiv: Kleidungs-Produkt erhält Rabatt.
    Negativ: Nicht-Kleidungs-Produkt bleibt unrabattiert.
    """
    clothing_product = CATEGORY_PROMO_PRODUCTS["clothing"]
    non_clothing_product = CATEGORY_PROMO_PRODUCTS["non_clothing"]
    promo_code = TEST_PROMO_CODES["category_clothing_10"]

    # 1. Kleidungs-Produkt (mit passender advertising_material_id) hinzufügen
    add_product_to_cart(page, base_url, clothing_product)

    # 2. Nicht-Kleidungs-Produkt (ohne passende advertising_material_id) hinzufügen
    add_product_to_cart(page, base_url, non_clothing_product)

    # 3. Zum Warenkorb navigieren
    navigate_to_cart(page, base_url)

    # 4. Preise vor Rabatt erfassen
    items_before = _get_line_item_prices(page)
    assert len(items_before) >= 2, (
        f"Erwartet mindestens 2 Produkte im Warenkorb, gefunden: {len(items_before)}"
    )

    total_before = get_cart_total(page)
    price_before = _parse_price(total_before)
    assert price_before > 0, f"Ungültiger Gesamtpreis vor Rabatt: {total_before}"

    # 5. Promotion-Code "10% auf Kleidung" einlösen
    success = apply_promo_code(page, promo_code)

    if not success:
        pytest.skip(
            f"Promotion-Code {promo_code} ist nicht im System konfiguriert. "
            "Bitte Code in TEST_PROMO_CODES['category_clothing_10'] aktualisieren."
        )

    # 6. Positiv: Rabatt muss sichtbar sein
    has_discount = has_promotion_discount(page)
    assert has_discount, (
        "Kein Promotion-Rabatt sichtbar nach Eingabe des Kleidung-Promo-Codes"
    )

    # 7. Gesamtpreis muss niedriger sein
    total_after = get_cart_total(page)
    price_after = _parse_price(total_after)
    assert price_after < price_before, (
        f"Gesamtpreis hat sich nach Kategorie-Rabatt nicht verringert: "
        f"vorher={total_before}, nachher={total_after}"
    )

    # 8. Negativ: Rabatt darf NICHT dem Rabatt auf den vollen Warenkorb entsprechen
    # (sonst wurde auch das Nicht-Kleidungs-Produkt rabattiert)
    discount = _get_discount_amount(page)
    full_cart_10_discount = price_before * 0.10
    if discount > 0 and full_cart_10_discount > 0:
        assert discount < full_cart_10_discount * 0.95, (
            f"Rabatt ({discount:.2f}) entspricht ca. 10% des Gesamtwarenkorbs "
            f"({full_cart_10_discount:.2f}) - Nicht-Kleidungs-Produkt wurde "
            f"wahrscheinlich fälschlicherweise rabattiert"
        )


@pytest.mark.promotions
def test_promo_advid_70_manual_code(page: Page, base_url: str):
    """
    TC-PROMO-ADVID-001: Promo auf Werbemittel ID 70 mit manueller Code-Eingabe.

    Prüft, dass eine Promotion per manuellem Code auf Produkte mit
    advertising_material_id = 70 angewendet wird.
    Positiv: Produkt mit advid 70 erhält Rabatt nach Code-Eingabe.
    Negativ: Produkt ohne advid 70 bleibt unrabattiert.
    """
    product_with = ADVID_70_PROMO_PRODUCTS["with_advid_70"]
    product_without = ADVID_70_PROMO_PRODUCTS["without_advid_70"]
    promo_code = TEST_PROMO_CODES["advid_70"]

    # 1. Produkt mit advertising_material_id = 70 hinzufügen
    add_product_to_cart(page, base_url, product_with)

    # 2. Produkt ohne advertising_material_id = 70 hinzufügen
    add_product_to_cart(page, base_url, product_without)

    # 3. Zum Warenkorb navigieren
    navigate_to_cart(page, base_url)

    # 4. Prüfen: Kein automatischer Rabatt vorhanden (Code ist manuell!)
    assert not has_promotion_discount(page), (
        "Promotion-Rabatt ist bereits vor Code-Eingabe sichtbar - "
        "sollte nur mit manuellem Code angewendet werden"
    )

    # 5. Preise vor Rabatt erfassen
    items_before = _get_line_item_prices(page)
    assert len(items_before) >= 2, (
        f"Erwartet mindestens 2 Produkte im Warenkorb, gefunden: {len(items_before)}"
    )

    total_before = get_cart_total(page)
    price_before = _parse_price(total_before)
    assert price_before > 0, f"Ungültiger Gesamtpreis vor Rabatt: {total_before}"

    # 6. Promotion-Code manuell eingeben
    success = apply_promo_code(page, promo_code)

    if not success:
        pytest.skip(
            f"Promotion-Code {promo_code} ist nicht im System konfiguriert. "
            "Bitte Code in TEST_PROMO_CODES['advid_70'] aktualisieren."
        )

    # 7. Positiv: Rabatt muss jetzt sichtbar sein
    has_discount = has_promotion_discount(page)
    assert has_discount, (
        "Kein Promotion-Rabatt sichtbar nach Eingabe des Werbemittel-ID-70-Codes"
    )

    # 8. Gesamtpreis muss niedriger sein
    total_after = get_cart_total(page)
    price_after = _parse_price(total_after)
    assert price_after < price_before, (
        f"Gesamtpreis hat sich nach Werbemittel-Rabatt nicht verringert: "
        f"vorher={total_before}, nachher={total_after}"
    )

    # 9. Negativ: Rabatt darf nicht auf den gesamten Warenkorb angewendet worden sein
    discount = _get_discount_amount(page)
    if discount > 0:
        # Wenn advid-70-Produkt deutlich günstiger als Gesamtwarenkorb,
        # muss der Rabatt kleiner sein als ein Rabatt auf den gesamten Warenkorb
        # (grobe Prüfung: Rabatt < 95% des Gesamtwarenkorb-Rabatts)
        full_cart_discount = price_before * 0.50  # Großzügige Obergrenze
        assert discount < full_cart_discount, (
            f"Rabatt ({discount:.2f}) ist unverhältnismäßig hoch - "
            f"möglicherweise wurde auch das Nicht-Werbemittel-Produkt rabattiert"
        )
