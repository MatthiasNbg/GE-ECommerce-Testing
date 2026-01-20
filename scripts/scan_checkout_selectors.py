"""
Scanner für Checkout-Selektoren auf grueneerde.scalecommerce.cloud.

Extrahiert alle relevanten HTML-Elemente für das Page Object Model.
"""
import asyncio
import json
from playwright.async_api import async_playwright


async def scan_page(page, page_name: str) -> dict:
    """Scannt eine Seite und extrahiert relevante Selektoren."""
    url = page.url
    print(f"\n{'='*60}")
    print(f"Scanne: {page_name}")
    print(f"URL: {url}")
    print('='*60)

    await page.wait_for_load_state("domcontentloaded")
    await asyncio.sleep(2)  # Warte auf dynamische Inhalte

    selectors = {
        "page": page_name,
        "url": url,
        "inputs": [],
        "selects": [],
        "buttons": [],
        "checkboxes": [],
        "radios": [],
        "containers": [],
        "links": [],
    }

    # Inputs
    inputs = await page.locator("input:not([type='hidden']):not([type='checkbox']):not([type='radio'])").all()
    for inp in inputs:
        try:
            selectors["inputs"].append({
                "id": await inp.get_attribute("id") or "",
                "name": await inp.get_attribute("name") or "",
                "type": await inp.get_attribute("type") or "text",
                "class": await inp.get_attribute("class") or "",
                "placeholder": await inp.get_attribute("placeholder") or "",
                "data_attrs": {k: v for k, v in (await inp.evaluate("el => Object.fromEntries([...el.attributes].filter(a => a.name.startsWith('data-')).map(a => [a.name, a.value]))")).items()},
            })
        except:
            pass

    # Selects
    selects = await page.locator("select").all()
    for sel in selects:
        try:
            options = await sel.locator("option").all()
            option_texts = []
            for opt in options[:10]:  # Limit
                text = await opt.text_content()
                if text:
                    option_texts.append(text.strip())
            selectors["selects"].append({
                "id": await sel.get_attribute("id") or "",
                "name": await sel.get_attribute("name") or "",
                "class": await sel.get_attribute("class") or "",
                "options": option_texts,
            })
        except:
            pass

    # Buttons
    buttons = await page.locator("button, input[type='submit'], a.btn").all()
    for btn in buttons:
        try:
            text = await btn.text_content()
            selectors["buttons"].append({
                "text": text.strip() if text else "",
                "id": await btn.get_attribute("id") or "",
                "class": await btn.get_attribute("class") or "",
                "type": await btn.get_attribute("type") or "",
                "data_attrs": {k: v for k, v in (await btn.evaluate("el => Object.fromEntries([...el.attributes].filter(a => a.name.startsWith('data-')).map(a => [a.name, a.value]))")).items()},
            })
        except:
            pass

    # Checkboxen
    checkboxes = await page.locator("input[type='checkbox']").all()
    for cb in checkboxes:
        try:
            label = ""
            cb_id = await cb.get_attribute("id")
            if cb_id:
                label_el = page.locator(f"label[for='{cb_id}']")
                if await label_el.count() > 0:
                    label = await label_el.text_content() or ""
            selectors["checkboxes"].append({
                "id": cb_id or "",
                "name": await cb.get_attribute("name") or "",
                "class": await cb.get_attribute("class") or "",
                "label": label.strip()[:100],
            })
        except:
            pass

    # Radio-Buttons
    radios = await page.locator("input[type='radio']").all()
    for radio in radios:
        try:
            label = ""
            radio_id = await radio.get_attribute("id")
            if radio_id:
                label_el = page.locator(f"label[for='{radio_id}']")
                if await label_el.count() > 0:
                    label = await label_el.text_content() or ""
            selectors["radios"].append({
                "id": radio_id or "",
                "name": await radio.get_attribute("name") or "",
                "value": await radio.get_attribute("value") or "",
                "class": await radio.get_attribute("class") or "",
                "label": label.strip()[:100],
            })
        except:
            pass

    # Wichtige Container
    containers = await page.locator("[class*='checkout'], [class*='register'], [class*='payment'], [class*='shipping'], [class*='address'], [class*='cart'], [class*='confirm'], [class*='form-group'], [class*='billing'], [class*='guest']").all()
    seen_classes = set()
    for cont in containers[:80]:  # Limit
        try:
            cls = await cont.get_attribute("class") or ""
            if cls and cls not in seen_classes:
                seen_classes.add(cls)
                selectors["containers"].append({
                    "class": cls,
                    "tag": await cont.evaluate("el => el.tagName.toLowerCase()"),
                })
        except:
            pass

    # Output
    print(f"\nGefunden:")
    print(f"  - {len(selectors['inputs'])} Input-Felder")
    print(f"  - {len(selectors['selects'])} Select-Felder")
    print(f"  - {len(selectors['buttons'])} Buttons")
    print(f"  - {len(selectors['checkboxes'])} Checkboxen")
    print(f"  - {len(selectors['radios'])} Radio-Buttons")
    print(f"  - {len(selectors['containers'])} Container")

    return selectors


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            http_credentials={
                "username": "grueneerde",
                "password": "IlyGn7WfMPElA7mu9iDrF36Q"
            },
            locale="de-AT",
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()

        all_selectors = []
        base_url = "https://grueneerde.scalecommerce.cloud"

        # 1. Zur Produktseite navigieren
        print("Navigiere zur Produktseite...")
        product_url = f"{base_url}/p/kurzarmshirt-aus-bio-baumwolle/ge-p-862990"
        await page.goto(product_url)
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(2)

        # Screenshot Produktseite
        await page.screenshot(path="reports/screenshots/product_page_scan.png", full_page=True)
        print(f"Aktuelle URL: {page.url}")

        # Cookie-Banner akzeptieren
        print("Suche Cookie-Banner...")
        try:
            # Verschiedene Cookie-Banner Selektoren
            cookie_selectors = [
                "button:has-text('Alle akzeptieren')",
                ".js-cookie-accept-all-button",
                "[data-cookie-accept-all]",
                "#uc-btn-accept-banner",
                "button:has-text('Akzeptieren')",
            ]
            for sel in cookie_selectors:
                cookie_btn = page.locator(sel)
                if await cookie_btn.count() > 0:
                    visible = await cookie_btn.first.is_visible(timeout=2000)
                    if visible:
                        print(f"  Cookie-Button gefunden: {sel}")
                        await cookie_btn.first.click()
                        await asyncio.sleep(2)
                        break
        except Exception as e:
            print(f"  Cookie-Banner: {e}")

        # 2. Produkt in den Warenkorb legen
        print("\nSuche 'In den Warenkorb' Button...")
        add_to_cart_selectors = [
            ".btn-buy",
            "button.btn-buy",
            "[data-add-to-cart]",
            "button:has-text('In den Warenkorb')",
            "button:has-text('In den Einkaufswagen')",
            ".product-detail-buy button[type='submit']",
            "form.buy-widget button[type='submit']",
        ]

        added_to_cart = False
        for sel in add_to_cart_selectors:
            btn = page.locator(sel)
            count = await btn.count()
            print(f"  Selektor '{sel}': {count} gefunden")
            if count > 0:
                try:
                    await btn.first.scroll_into_view_if_needed()
                    await asyncio.sleep(0.5)
                    if await btn.first.is_visible():
                        print(f"  -> Klicke auf: {sel}")
                        await btn.first.click()
                        await asyncio.sleep(3)
                        added_to_cart = True
                        break
                except Exception as e:
                    print(f"  -> Fehler: {e}")

        if not added_to_cart:
            print("  WARNUNG: Konnte Produkt nicht in den Warenkorb legen!")
            # Versuche es über die Suche
            print("\nVersuche über Suche...")
            await page.goto(base_url)
            await page.wait_for_load_state("domcontentloaded")

            # Suche öffnen
            search_toggle = page.locator(".search-toggle-btn, [data-bs-target='#searchCollapse']")
            if await search_toggle.count() > 0:
                await search_toggle.first.click()
                await asyncio.sleep(1)

            # Suchfeld finden und füllen
            search_input = page.locator("#header-main-search-input, input[name='search']")
            if await search_input.count() > 0:
                await search_input.first.fill("Shirt")
                await page.keyboard.press("Enter")
                await page.wait_for_load_state("domcontentloaded")
                await asyncio.sleep(2)

                # Erstes Produkt auswählen
                product_link = page.locator(".product-box a.product-image-link, .product-info a").first
                if await product_link.count() > 0:
                    await product_link.click()
                    await page.wait_for_load_state("domcontentloaded")
                    await asyncio.sleep(2)

                    # Nochmal versuchen hinzuzufügen
                    for sel in add_to_cart_selectors:
                        btn = page.locator(sel)
                        if await btn.count() > 0 and await btn.first.is_visible():
                            await btn.first.click()
                            await asyncio.sleep(3)
                            added_to_cart = True
                            break

        # Screenshot nach Warenkorb-Aktion
        await page.screenshot(path="reports/screenshots/after_add_to_cart.png", full_page=True)

        # 3. Zum Checkout navigieren
        print("\nNavigiere zum Checkout...")
        await page.goto(f"{base_url}/checkout/register")
        await page.wait_for_load_state("domcontentloaded")
        await asyncio.sleep(2)

        # Screenshot Checkout-Übersicht
        await page.screenshot(path="reports/screenshots/checkout_register_scan.png", full_page=True)
        print(f"Checkout URL: {page.url}")

        # Scan Checkout-Register Seite
        register_selectors = await scan_page(page, "checkout_register")
        all_selectors.append(register_selectors)

        # 4. Gast-Checkout Button suchen und klicken
        print("\nSuche Gast-Checkout Option...")
        guest_selectors_list = [
            "button:has-text('Als Gast')",
            "button:has-text('Als Gast bestellen')",
            "a:has-text('Als Gast')",
            "[data-toggle='collapse'][href='#collapseGuestCheckout']",
            "#collapseGuestCheckout",
            ".checkout-register-guest",
            "input[value='guest']",
            "label:has-text('Als Gast')",
        ]

        for sel in guest_selectors_list:
            elem = page.locator(sel)
            count = await elem.count()
            print(f"  Selektor '{sel}': {count} gefunden")
            if count > 0:
                try:
                    if await elem.first.is_visible():
                        await elem.first.click()
                        await asyncio.sleep(2)
                        print(f"  -> Gast-Checkout aktiviert mit: {sel}")
                        break
                except:
                    pass

        # Screenshot nach Gast-Auswahl
        await page.screenshot(path="reports/screenshots/checkout_guest_selected.png", full_page=True)

        # Nochmal scannen nach möglichen neuen Feldern
        guest_form_selectors = await scan_page(page, "checkout_guest_form")
        if guest_form_selectors["inputs"] != register_selectors["inputs"]:
            all_selectors.append(guest_form_selectors)

        # 5. Formular ausfüllen und zur Confirm-Seite
        print("\n" + "="*60)
        print("Versuche Formular auszufüllen...")
        print("="*60)

        try:
            # Alle Input-Felder anzeigen
            all_inputs = await page.locator("input:visible").all()
            print(f"\nSichtbare Input-Felder: {len(all_inputs)}")
            for inp in all_inputs[:20]:
                inp_id = await inp.get_attribute("id") or ""
                inp_name = await inp.get_attribute("name") or ""
                inp_type = await inp.get_attribute("type") or ""
                inp_placeholder = await inp.get_attribute("placeholder") or ""
                print(f"  - id='{inp_id}' name='{inp_name}' type='{inp_type}' placeholder='{inp_placeholder}'")

            # Alle Select-Felder anzeigen
            all_selects = await page.locator("select:visible").all()
            print(f"\nSichtbare Select-Felder: {len(all_selects)}")
            for sel in all_selects[:10]:
                sel_id = await sel.get_attribute("id") or ""
                sel_name = await sel.get_attribute("name") or ""
                print(f"  - id='{sel_id}' name='{sel_name}'")

            # Versuche verschiedene Selektoren für die Formularfelder
            field_mappings = {
                "salutation": [
                    "#personalSalutation",
                    "select[name*='salutation']",
                    "select[name='salutationId']",
                    "#billingAddressSalutation",
                ],
                "firstName": [
                    "#billingAddress-personalFirstName",
                    "#personalFirstName",
                    "input[name*='firstName']",
                    "#billingAddressFirstName",
                ],
                "lastName": [
                    "#billingAddress-personalLastName",
                    "#personalLastName",
                    "input[name*='lastName']",
                    "#billingAddressLastName",
                ],
                "email": [
                    "#personalMail",
                    "#email",
                    "input[name='email']",
                    "input[type='email']",
                ],
                "street": [
                    "#billingAddress-AddressStreet",
                    "#billingAddressStreet",
                    "input[name*='street']",
                ],
                "zipcode": [
                    "#billingAddressAddressZipcode",
                    "#billingAddressZipcode",
                    "input[name*='zipcode']",
                ],
                "city": [
                    "#billingAddressAddressCity",
                    "#billingAddressCity",
                    "input[name*='city']",
                ],
                "country": [
                    "#billingAddressAddressCountry",
                    "#billingAddressCountry",
                    "select[name*='country']",
                ],
            }

            found_fields = {}
            for field_name, selectors in field_mappings.items():
                for sel in selectors:
                    elem = page.locator(sel)
                    if await elem.count() > 0 and await elem.first.is_visible():
                        found_fields[field_name] = sel
                        print(f"\nGefunden: {field_name} -> {sel}")
                        break

            # Formular ausfüllen mit gefundenen Selektoren
            if "salutation" in found_fields:
                await page.locator(found_fields["salutation"]).select_option(label="Herr")
            if "firstName" in found_fields:
                await page.fill(found_fields["firstName"], "Test")
            if "lastName" in found_fields:
                await page.fill(found_fields["lastName"], "Scanner")
            if "email" in found_fields:
                import time
                await page.fill(found_fields["email"], f"scan-test-{int(time.time())}@test.local")
            if "street" in found_fields:
                await page.fill(found_fields["street"], "Teststraße 1")
            if "zipcode" in found_fields:
                await page.fill(found_fields["zipcode"], "4020")
            if "city" in found_fields:
                await page.fill(found_fields["city"], "Linz")
            if "country" in found_fields:
                await page.locator(found_fields["country"]).select_option(label="Österreich")

            # Screenshot nach Formular-Ausfüllung
            await page.screenshot(path="reports/screenshots/checkout_form_filled.png", full_page=True)

            # Datenschutz-Checkbox
            privacy_selectors = [
                "#acceptedDataProtection",
                "input[name='acceptedDataProtection']",
                "input[name='tos']",
            ]
            for sel in privacy_selectors:
                cb = page.locator(sel)
                if await cb.count() > 0 and await cb.first.is_visible():
                    if not await cb.first.is_checked():
                        await cb.first.check()
                    print(f"Datenschutz akzeptiert: {sel}")
                    break

            # Weiter-Button
            continue_selectors = [
                "button:has-text('Weiter')",
                "button[type='submit']:has-text('Weiter')",
                ".register-submit button",
                "button:has-text('Zur Kasse')",
            ]
            for sel in continue_selectors:
                btn = page.locator(sel)
                if await btn.count() > 0 and await btn.first.is_visible():
                    print(f"\nKlicke Weiter-Button: {sel}")
                    await btn.first.click()
                    try:
                        await page.wait_for_url("**/checkout/confirm**", timeout=15000)
                        print("Navigation zur Confirm-Seite erfolgreich!")
                    except:
                        print("Timeout - möglicherweise Validierungsfehler")
                    break

            await page.wait_for_load_state("domcontentloaded")
            await asyncio.sleep(2)

            # Screenshot Confirm-Seite
            await page.screenshot(path="reports/screenshots/checkout_confirm_scan.png", full_page=True)

            # 6. Confirm-Seite scannen (falls wir dort angekommen sind)
            if "confirm" in page.url.lower():
                confirm_selectors = await scan_page(page, "checkout_confirm")
                all_selectors.append(confirm_selectors)

        except Exception as e:
            print(f"\nFehler beim Formular-Ausfüllen: {e}")
            import traceback
            traceback.print_exc()

        await browser.close()

        # Ergebnisse speichern
        output_file = "reports/checkout_selectors.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_selectors, f, indent=2, ensure_ascii=False)
        print(f"\n\nErgebnisse gespeichert in: {output_file}")

        # Zusammenfassung ausgeben
        print("\n" + "="*60)
        print("ZUSAMMENFASSUNG - Gefundene Selektoren für Page Object")
        print("="*60)

        for page_data in all_selectors:
            print(f"\n## {page_data['page']}")
            print(f"URL: {page_data['url']}")

            if page_data['inputs']:
                print("\n### Input-Felder:")
                for inp in page_data['inputs']:
                    if inp['id'] or inp['name']:  # Nur relevante
                        selector = f"#{inp['id']}" if inp['id'] else f"input[name='{inp['name']}']"
                        print(f"  {inp['id'] or inp['name']}: '{selector}'")
                        print(f"      type={inp['type']}, placeholder='{inp['placeholder'][:40]}'")

            if page_data['selects']:
                print("\n### Select-Felder:")
                for sel in page_data['selects']:
                    if sel['id'] or sel['name']:
                        selector = f"#{sel['id']}" if sel['id'] else f"select[name='{sel['name']}']"
                        print(f"  {sel['id'] or sel['name']}: '{selector}'")
                        print(f"      options: {sel['options'][:5]}")

            if page_data['checkboxes']:
                print("\n### Checkboxen:")
                for cb in page_data['checkboxes']:
                    if cb['id'] or cb['name']:
                        selector = f"#{cb['id']}" if cb['id'] else f"input[name='{cb['name']}']"
                        print(f"  {cb['id'] or cb['name']}: '{selector}'")
                        print(f"      label: '{cb['label'][:60]}'")

            if page_data['radios']:
                print("\n### Radio-Buttons (Zahlungs-/Versandarten):")
                # Gruppiere nach name
                by_name = {}
                for radio in page_data['radios']:
                    name = radio['name']
                    if name not in by_name:
                        by_name[name] = []
                    by_name[name].append(radio)

                for name, radios in by_name.items():
                    print(f"\n  {name}:")
                    for radio in radios:
                        selector = f"#{radio['id']}" if radio['id'] else f"input[name='{name}'][value='{radio['value']}']"
                        print(f"    - '{selector}' (label: '{radio['label'][:40]}')")


if __name__ == "__main__":
    asyncio.run(main())
