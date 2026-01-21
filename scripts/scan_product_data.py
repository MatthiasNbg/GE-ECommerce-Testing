#!/usr/bin/env python
"""
Scannt Testprodukte und erfasst den Ist-Stand für Data Validation Tests.

Erfasste Daten:
- Produktname
- Preis (brutto)
- MwSt.-Satz
- Verfügbarkeit/Lieferzeit
- Versandart (Post/Spedition)

Ausführung:
    python scripts/scan_product_data.py
"""
import json
import re
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright


# Testprodukte aus config.yaml
TEST_PRODUCTS = {
    "post_shipping": [
        {
            "id": "862990",
            "path": "p/kurzarmshirt-aus-bio-baumwolle/ge-p-862990",
            "name": "Kurzarmshirt Bio-Baumwolle",
            "type": "post",
        },
        {
            "id": "863190",
            "path": "p/blusenshirt-aus-bio-leinen/ge-p-863190",
            "name": "Blusenshirt Bio-Leinen",
            "type": "post",
        },
        {
            "id": "49415",
            "path": "p/duftkissen-lavendel/ge-p-49415",
            "name": "Duftkissen Lavendel",
            "type": "post",
        },
        {
            "id": "74157",
            "path": "p/augen-entspannungskissen-mit-amaranth/ge-p-74157",
            "name": "Augen-Entspannungskissen",
            "type": "post",
        },
    ],
    "spedition_shipping": [
        {
            "id": "693645",
            "path": "p/kleiderstaender-jukai-pur/ge-p-693645",
            "name": "Kleiderständer Jukai Pur",
            "type": "spedition",
        },
        {
            "id": "693278",
            "path": "p/polsterbett-almeno/ge-p-693278",
            "name": "Polsterbett Almeno",
            "type": "spedition",
        },
    ],
}

# Staging-Umgebung (Shop noch nicht gerelaunched!)
BASE_URL = "https://grueneerde.scalecommerce.cloud"
HTACCESS_USER = "grueneerde"
HTACCESS_PASSWORD = "IlyGn7WfMPElA7mu9iDrF36Q"


def accept_cookies(page):
    """Akzeptiert Cookie-Banner falls vorhanden."""
    try:
        # Usercentrics Shadow DOM
        uc_root = page.locator("#usercentrics-root")
        if uc_root.count() > 0:
            shadow = uc_root.evaluate_handle("el => el.shadowRoot")
            if shadow:
                accept_btn = page.evaluate(
                    """() => {
                    const root = document.querySelector('#usercentrics-root');
                    if (!root || !root.shadowRoot) return null;
                    const btn = root.shadowRoot.querySelector('button[data-testid="uc-accept-all-button"]');
                    if (btn) { btn.click(); return true; }
                    return null;
                }"""
                )
                if accept_btn:
                    page.wait_for_timeout(1000)
                    return True
    except Exception:
        pass
    return False


def extract_price(text: str) -> float | None:
    """Extrahiert Preis aus Text (z.B. '29,90 €' -> 29.90)."""
    if not text:
        return None
    # Entferne Tausendertrennzeichen und ersetze Komma durch Punkt
    cleaned = re.sub(r"[^\d,.]", "", text)
    cleaned = cleaned.replace(".", "").replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None


def scan_product(page, product: dict) -> dict:
    """Scannt ein einzelnes Produkt und erfasst die Daten."""
    url = f"{BASE_URL}/{product['path']}"
    print(f"\n[Scan] {product['name']} ({product['id']})")
    print(f"       URL: {url}")

    result = {
        "id": product["id"],
        "path": product["path"],
        "name": product["name"],
        "type": product["type"],
        "url": url,
        "scanned_at": datetime.now().isoformat(),
        "data": {},
        "errors": [],
    }

    try:
        page.goto(url, timeout=30000)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)

        # Cookie-Banner
        accept_cookies(page)

        # === Produktname ===
        name_selectors = [
            "h1.product-detail-name",
            ".product-detail-name",
            "h1[itemprop='name']",
            ".product-name h1",
        ]
        for sel in name_selectors:
            elem = page.locator(sel)
            if elem.count() > 0:
                result["data"]["displayed_name"] = elem.first.inner_text().strip()
                break

        # === Preis ===
        price_selectors = [
            ".product-detail-price",
            "[itemprop='price']",
            ".product-price",
            ".price",
        ]
        for sel in price_selectors:
            elem = page.locator(sel)
            if elem.count() > 0:
                price_text = elem.first.inner_text().strip()
                result["data"]["price_text"] = price_text
                result["data"]["price"] = extract_price(price_text)
                break

        # === MwSt.-Hinweis ===
        vat_selectors = [
            ".product-detail-tax",
            "*:has-text('inkl. MwSt')",
            "*:has-text('inkl. Mwst')",
            "*:has-text('zzgl.')",
        ]
        for sel in vat_selectors:
            try:
                elem = page.locator(sel).first
                if elem.count() > 0 and elem.is_visible():
                    vat_text = elem.inner_text().strip()
                    if "MwSt" in vat_text or "Mwst" in vat_text:
                        result["data"]["vat_info"] = vat_text
                        # MwSt-Satz extrahieren
                        vat_match = re.search(r"(\d+)[,.]?(\d*)\s*%", vat_text)
                        if vat_match:
                            vat_rate = float(
                                f"{vat_match.group(1)}.{vat_match.group(2) or '0'}"
                            )
                            result["data"]["vat_rate"] = vat_rate
                        break
            except Exception:
                continue

        # === Verfügbarkeit / Lieferzeit ===
        availability_selectors = [
            ".delivery-information",
            ".product-detail-delivery-information",
            "*:has-text('Lieferzeit')",
            "*:has-text('verfügbar')",
            "*:has-text('Auf Lager')",
        ]
        for sel in availability_selectors:
            try:
                elem = page.locator(sel).first
                if elem.count() > 0 and elem.is_visible():
                    avail_text = elem.inner_text().strip()
                    if (
                        "Lieferzeit" in avail_text
                        or "verfügbar" in avail_text.lower()
                        or "lager" in avail_text.lower()
                    ):
                        result["data"]["availability"] = avail_text
                        break
            except Exception:
                continue

        # === Versandkosten-Hinweis ===
        shipping_selectors = [
            ".shipping-costs",
            "*:has-text('Versandkosten')",
            "*:has-text('Versand')",
        ]
        for sel in shipping_selectors:
            try:
                elem = page.locator(sel).first
                if elem.count() > 0 and elem.is_visible():
                    ship_text = elem.inner_text().strip()
                    if "Versand" in ship_text:
                        result["data"]["shipping_info"] = ship_text
                        break
            except Exception:
                continue

        # === Artikelnummer ===
        sku_selectors = [
            ".product-detail-ordernumber",
            "[itemprop='sku']",
            "*:has-text('Artikel-Nr')",
            "*:has-text('Produkt-Nr')",
        ]
        for sel in sku_selectors:
            try:
                elem = page.locator(sel).first
                if elem.count() > 0 and elem.is_visible():
                    sku_text = elem.inner_text().strip()
                    result["data"]["sku_display"] = sku_text
                    # Nummer extrahieren
                    sku_match = re.search(r"(\d{5,})", sku_text)
                    if sku_match:
                        result["data"]["sku"] = sku_match.group(1)
                    break
            except Exception:
                continue

        # === In Warenkorb Button vorhanden? ===
        buy_btn = page.locator("button.btn-buy, .btn-buy, button:has-text('In den Warenkorb')")
        result["data"]["can_add_to_cart"] = buy_btn.count() > 0 and buy_btn.first.is_visible()

        print(f"       Preis: {result['data'].get('price_text', 'N/A')}")
        print(f"       Verfügbarkeit: {result['data'].get('availability', 'N/A')[:50]}...")

    except Exception as e:
        result["errors"].append(str(e))
        print(f"       FEHLER: {e}")

    return result


def scan_cart_calculation(page, products: list[dict]) -> dict:
    """Testet die Warenkorb-Berechnung mit mehreren Produkten."""
    print("\n" + "=" * 60)
    print("WARENKORB-BERECHNUNG TESTEN")
    print("=" * 60)

    result = {
        "scanned_at": datetime.now().isoformat(),
        "products_added": [],
        "cart_data": {},
        "errors": [],
    }

    try:
        # Warenkorb leeren (zur Startseite und neu beginnen)
        page.goto(f"{BASE_URL}/checkout/cart", timeout=30000)
        page.wait_for_load_state("domcontentloaded")
        accept_cookies(page)

        # Ein Post-Produkt hinzufügen
        post_product = products[0]  # Kurzarmshirt
        print(f"\n[1] Füge hinzu: {post_product['name']}")
        page.goto(f"{BASE_URL}/{post_product['path']}", timeout=30000)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(1000)

        buy_btn = page.locator("button.btn-buy")
        if buy_btn.count() > 0 and buy_btn.first.is_visible():
            buy_btn.first.click()
            page.wait_for_timeout(3000)
            result["products_added"].append(post_product["id"])

        # Zum Warenkorb
        page.goto(f"{BASE_URL}/checkout/cart", timeout=30000)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)

        # Warenkorb-Daten extrahieren
        # Zwischensumme
        subtotal_sel = page.locator(".checkout-aside-summary-value").first
        if subtotal_sel.count() > 0:
            result["cart_data"]["subtotal_text"] = subtotal_sel.inner_text().strip()
            result["cart_data"]["subtotal"] = extract_price(result["cart_data"]["subtotal_text"])

        # Versandkosten
        shipping_sel = page.locator("dt:has-text('Versandkosten') + dd, dt:has-text('Versand') + dd")
        if shipping_sel.count() > 0:
            result["cart_data"]["shipping_text"] = shipping_sel.first.inner_text().strip()
            result["cart_data"]["shipping"] = extract_price(result["cart_data"]["shipping_text"])

        # Gesamtsumme
        total_sel = page.locator(".checkout-aside-summary-total-value, .summary-total")
        if total_sel.count() > 0:
            result["cart_data"]["total_text"] = total_sel.first.inner_text().strip()
            result["cart_data"]["total"] = extract_price(result["cart_data"]["total_text"])

        # MwSt
        vat_sel = page.locator("dt:has-text('MwSt') + dd, dt:has-text('Mwst') + dd")
        if vat_sel.count() > 0:
            result["cart_data"]["vat_text"] = vat_sel.first.inner_text().strip()
            result["cart_data"]["vat_amount"] = extract_price(result["cart_data"]["vat_text"])

        print(f"       Zwischensumme: {result['cart_data'].get('subtotal_text', 'N/A')}")
        print(f"       Versand: {result['cart_data'].get('shipping_text', 'N/A')}")
        print(f"       Gesamt: {result['cart_data'].get('total_text', 'N/A')}")

    except Exception as e:
        result["errors"].append(str(e))
        print(f"       FEHLER: {e}")

    return result


def main():
    """Hauptfunktion zum Scannen aller Testprodukte."""
    print("=" * 60)
    print("TESTPRODUKT-SCAN FÜR DATA VALIDATION")
    print(f"Zeitpunkt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}")
    print("=" * 60)

    all_results = {
        "scan_timestamp": datetime.now().isoformat(),
        "base_url": BASE_URL,
        "products": [],
        "cart_test": None,
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="de-AT",
            ignore_https_errors=True,
            http_credentials={"username": HTACCESS_USER, "password": HTACCESS_PASSWORD},
        )
        page = context.new_page()

        # Alle Produkte scannen
        all_products = (
            TEST_PRODUCTS["post_shipping"] + TEST_PRODUCTS["spedition_shipping"]
        )

        for product in all_products:
            result = scan_product(page, product)
            all_results["products"].append(result)

        # Warenkorb-Berechnung testen
        all_results["cart_test"] = scan_cart_calculation(
            page, TEST_PRODUCTS["post_shipping"]
        )

        browser.close()

    # Ergebnisse speichern
    output_path = Path("reports/product_data_scan.json")
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print(f"SCAN ABGESCHLOSSEN")
    print(f"Ergebnisse gespeichert in: {output_path}")
    print("=" * 60)

    # Zusammenfassung
    print("\n=== ZUSAMMENFASSUNG ===")
    for prod in all_results["products"]:
        status = "[OK]" if not prod["errors"] else "[FEHLER]"
        price = prod["data"].get("price_text", "N/A")
        print(f"{status} {prod['name']}: {price}")

    return all_results


if __name__ == "__main__":
    main()
