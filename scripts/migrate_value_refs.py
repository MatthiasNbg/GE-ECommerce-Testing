#!/usr/bin/env python3
"""
migrate_value_refs.py
====================
Migriert Test-Contracts in schema/examples/ von hartcodierten Werten
in step.inputs zu value_ref-Referenzen auf test_data-Eintraege.

Usage:
    python scripts/migrate_value_refs.py              # Alle Dateien migrieren
    python scripts/migrate_value_refs.py --dry-run    # Vorschau ohne Schreiben
    python scripts/migrate_value_refs.py --file X.json # Einzelne Datei
"""

import json
import re
import sys
from pathlib import Path
from collections import defaultdict

EXAMPLES_DIR = Path("schema/examples")

# ============================================================================
# Selector -> (test_data_type, field_name) Mapping
# ============================================================================

SELECTOR_MAP = {
    # Login/Registration - Email
    "#loginMail": ("login", "email"),
    "#personalMail": ("login", "email"),
    "#personalMailConfirmation": ("login", "email"),

    # Login/Registration - Passwort
    "#loginPassword": ("login", "password"),
    "#personalPassword": ("login", "password"),
    "#personalPasswordConfirmation": ("login", "password"),
    "#personalMailPasswordCurrent": ("login", "password"),

    # Persoenliche Daten -> address
    "#personalSalutation": ("address", "salutation"),
    "#personalFirstName": ("address", "first_name"),
    "#personalLastName": ("address", "last_name"),
    "#billingAddress-personalFirstName": ("address", "first_name"),
    "#billingAddress-personalLastName": ("address", "last_name"),
    "#addresspersonalSalutation": ("address", "salutation"),
    "#addresspersonalFirstName": ("address", "first_name"),
    "#addresspersonalLastName": ("address", "last_name"),

    # Rechnungsadresse
    "#billingAddressAddressStreet": ("address", "street"),
    "#billingAddress-AddressStreet": ("address", "street"),
    "#addressAddressStreet": ("address", "street"),
    "#billingAddressAddressZipcode": ("address", "zip"),
    "#addressAddressZipcode": ("address", "zip"),
    "#billingAddressAddressCity": ("address", "city"),
    "#addressAddressCity": ("address", "city"),
    "#billingAddressAddressCountry": ("address", "country"),
    "#addressAddressCountry": ("address", "country"),

    # Firma/B2B
    "#billingAddresscompany": ("address", "company"),
    "#-accountType": ("address", "account_type"),
    "#vatIds": ("address", "vat_id"),

    # Produkt Artikelnummer
    "#addProductInput": ("product", "article_number"),

    # Promo-Code
    "#promotionCode": ("promo", "code"),

    # Suche
    "input#header-main-search-input": ("search", "term"),

    # Bewertung
    "#reviewTitle": ("review", "title"),
    "#reviewContent": ("review", "content"),
    "#reviewRating": ("review", "rating"),
}

# Regex-basierte Selector-Patterns (fuer Compound-Selectors)
SELECTOR_PATTERNS = [
    (re.compile(r"input\[name=['\"]promotionCode['\"]\]"), ("promo", "code")),
    (re.compile(r"input\[type=['\"]email['\"]\]"), ("newsletter", "email")),
    (re.compile(r"input\[name=['\"]quantity['\"]\]"), ("extra", "quantity")),
    (re.compile(r"select\.sorting"), ("extra", "sorting")),
]

# ============================================================================
# Bekannte Daten fuer konsistente Benennung
# ============================================================================

KNOWN_EMAILS = {
    "ge-at-1@matthias-sax.de": {"name": "at_customer", "password": "scharnsteinAT"},
    "ge-de-1@matthias-sax.de": {"name": "de_customer", "password": "scharnsteinDE"},
    "ge-ch-1@matthias-sax.de": {"name": "ch_customer", "password": "scharnsteinCH"},
    "test@example.com": {"name": "guest", "password": "TestPasswort123!"},
    "freundeskreis-test@grueneerde.at": {"name": "freundeskreis", "password": "TestPasswort123!"},
    "gast-test@example.com": {"name": "guest_named", "password": "TestPasswort123!"},
    "b2b-test@example.com": {"name": "b2b_customer", "password": "TestPasswort123!"},
    "duplicate@example.com": {"name": "duplicate", "password": "TestPasswort123!"},
    "nicht-existierend@example.com": {"name": "invalid_user", "password": "FalschesPasswort123!"},
    "test-newsletter@example.com": {"name": "newsletter_test"},
    "ungueltige-email-ohne-at": {"name": "invalid_email"},
    "test-versandkosten-4020@example.com": {"name": "shipping_at"},
    "test-versandkosten-80331@example.com": {"name": "shipping_de"},
}

KNOWN_PASSWORDS = {
    "scharnsteinAT": "at_customer",
    "scharnsteinDE": "de_customer",
    "scharnsteinCH": "ch_customer",
    "TestPasswort123!": None,  # Generisch, wird per Kontext aufgeloest
    "FalschesPasswort123!": "invalid_user",
    "1234": None,  # Schwaches Passwort fuer Negativ-Tests
}

KNOWN_PRODUCTS = {
    "862990": {
        "name": "shirt_bio",
        "product_name": "Kurzarmshirt aus Bio-Baumwolle",
    },
    "693278": {
        "name": "bed_almeno",
        "product_name": "Polsterbett Almeno",
    },
    "410933": {
        "name": "bathrobe_raute",
        "product_name": "Bademantel Raute",
    },
    "21008": {
        "name": "table_vassolo",
        "product_name": "Beistelltisch Vassolo",
    },
    "49415": {
        "name": "cushion_lavender",
        "product_name": "Duftkissen Lavendel",
    },
    "60780": {
        "name": "lip_balm",
        "product_name": "Lippenbalsam mit Bio-Bienenwachs",
    },
    "GUTSCHEIN": {
        "name": "gift_voucher",
        "product_name": "Einkaufsgutschein",
    },
    "BUNDLE": {
        "name": "bundle_product",
        "product_name": "Bundle-Produkt",
    },
    "UPDATETHIS": {
        "name": "placeholder",
        "product_name": "Platzhalter-Produkt (UPDATETHIS)",
    },
}

KNOWN_PROMOS = {
    "TEST20": {"name": "test_discount", "description": "Test-Rabattcode 20%"},
    "MA-KOSMETIK50": {"name": "employee_kosmetik", "description": "Mitarbeiterrabatt 50% Kosmetik"},
    "MA-ALLES20": {"name": "employee_alles", "description": "Mitarbeiterrabatt 20% alle Produkte"},
    "FK-BONUS-TESTCODE": {"name": "freundeskreis_bonus", "description": "Freundeskreis Bonusgutschein"},
    "CHF10AB50": {"name": "chf_mbw_rabatt", "description": "CHF 10 Rabatt ab 50 CHF"},
    "MBW50TEST": {"name": "mbw_test", "description": "Mindestbestellwert-Test"},
    "SPEDIFREI": {"name": "spedition_frei", "description": "Spedition versandkostenfrei"},
    "VERSANDFREI": {"name": "versand_frei", "description": "Versandkostenfrei"},
    "TESTRABATT10": {"name": "test_rabatt_10", "description": "Testrabatt 10%"},
    "UNGUELTIG123": {"name": "ungueltig", "description": "Ungueltiger Gutscheincode"},
    "UPDATETHISCODE": {"name": "update_placeholder", "description": "Platzhalter-Code"},
}

KNOWN_SEARCH_TERMS = {
    "862990": {"name": "article_number"},
    "Baumwolle": {"name": "material"},
    "bett": {"name": "category_term"},
    "wildrose": {"name": "product_name"},
    "xyznonexistent123": {"name": "no_results"},
    "be": {"name": "autocomplete_prefix"},
    "test": {"name": "generic"},
}

# Hinweis: is_constant_url() behandelt jetzt alle nicht-Produkt-URLs als Konstanten.
# Diese Liste wird nicht mehr direkt verwendet, bleibt als Dokumentation.


# ============================================================================
# Hilfsfunktionen
# ============================================================================

def is_constant_url(url):
    """Pruefen ob URL eine Konstante ist (bleibt als value).

    Alle nicht-Produkt-URLs sind Konstanten (Kategorie-Seiten, Suchseiten, etc.).
    Nur Produkt-URLs (/p/...) werden zu value_ref migriert.
    """
    # Volle URLs (https://...) sind Konstanten
    if url.startswith("http://") or url.startswith("https://"):
        return True
    # Produkt-URLs sind KEINE Konstanten (werden migriert)
    if "/p/" in url:
        return False
    # Alles andere (Kategorie-URLs, Suchseiten, etc.) sind Konstanten
    return True


def is_product_url(url):
    """Pruefen ob URL eine Produktseite ist."""
    return "/p/" in url


def extract_product_id(url):
    """Produkt-ID aus URL extrahieren: /p/name/ge-p-123456 -> 123456"""
    match = re.search(r"ge-p-([A-Za-z0-9_]+)", url)
    return match.group(1) if match else None


def get_selector_mapping(selector):
    """(type, field) Mapping fuer einen Selector zurueckgeben."""
    if not selector:
        return None
    # Direkter Match
    if selector in SELECTOR_MAP:
        return SELECTOR_MAP[selector]
    # Regex-Pattern Match
    for pattern, mapping in SELECTOR_PATTERNS:
        if pattern.search(selector):
            return mapping
    return None


def find_td_entry(test_data, td_type, name=None, **match_fields):
    """test_data-Eintrag nach Typ und optionalen Feldern finden."""
    for entry in test_data:
        if entry.get("type") != td_type:
            continue
        if name is not None and entry.get("name") != name:
            continue
        if match_fields:
            if all(entry.get(k) == v for k, v in match_fields.items()):
                return entry
        else:
            return entry
    return None


def find_td_by_field_value(test_data, td_type, field, value):
    """test_data-Eintrag finden der einen bestimmten Feldwert hat."""
    for entry in test_data:
        if entry.get("type") != td_type:
            continue
        if entry.get(field) == value:
            return entry
    return None


def ensure_td_entry(test_data, td_type, name, **fields):
    """test_data-Eintrag finden oder erstellen."""
    entry = find_td_entry(test_data, td_type, name)
    if entry:
        for k, v in fields.items():
            if k not in entry:
                entry[k] = v
        return entry
    entry = {"type": td_type, "name": name}
    entry.update(fields)
    test_data.append(entry)
    return entry


# ============================================================================
# Haupt-Migrationslogik
# ============================================================================

def migrate_contract(filepath, dry_run=False):
    """Einzelne Contract-Datei migrieren. Returns (changed, refs_created, reason)."""
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return False, 0, "invalid JSON"

    steps = data.get("steps", [])
    test_data = data.get("test_data", [])

    if not steps:
        return False, 0, "no steps"

    # Pruefen ob ueberhaupt Arbeit noetig ist
    has_work = False
    for step in steps:
        for inp in step.get("inputs", []):
            if "value_ref" in inp:
                continue
            if "value" not in inp:
                continue
            action = inp.get("action", "")
            if action in ("click", "check", "uncheck", "wait"):
                continue
            if action == "navigate" and is_constant_url(inp["value"]):
                continue
            has_work = True
            break
        if has_work:
            break

    if not has_work:
        return False, 0, "already clean"

    # ===== PHASE 1: Alle hartcodierten Werte sammeln =====

    # Pro Step email+passwort Paare sammeln
    email_password_map = {}   # email -> password
    all_emails = set()
    all_passwords = set()
    orphan_passwords = []
    address_values = {}       # field -> value (letzter Wert gewinnt)
    products_by_id = {}       # product_id -> url
    promos = set()
    search_terms = set()
    review_values = {}
    newsletter_emails = set()
    extra_values = {}         # field -> value

    for step in steps:
        step_emails = []
        step_passwords = []

        for inp in step.get("inputs", []):
            if "value_ref" in inp or "value" not in inp:
                continue
            value = inp["value"]
            selector = inp.get("selector", "")
            action = inp.get("action", "")

            # Navigate -> Produkt-URL
            if action == "navigate" and is_product_url(value):
                pid = extract_product_id(value)
                if pid:
                    products_by_id[pid] = value
                continue

            if action in ("click", "check", "uncheck", "wait", "navigate"):
                continue

            mapping = get_selector_mapping(selector)
            if not mapping:
                continue

            td_type, field = mapping

            if td_type == "login":
                if field == "email":
                    step_emails.append(value)
                    all_emails.add(value)
                elif field == "password":
                    step_passwords.append(value)
                    all_passwords.add(value)
            elif td_type == "address":
                address_values[field] = value
            elif td_type == "promo":
                promos.add(value)
            elif td_type == "search":
                search_terms.add(value)
            elif td_type == "review":
                review_values[field] = value
            elif td_type == "newsletter":
                newsletter_emails.add(value)
            elif td_type == "product":
                if field == "article_number":
                    products_by_id[value] = None
            elif td_type == "extra":
                extra_values[field] = value

        # Email-Passwort Paare innerhalb desselben Steps
        for email in step_emails:
            for pwd in step_passwords:
                email_password_map[email] = pwd

        # Verwaiste Passwoerter (kein Email im selben Step)
        if step_passwords and not step_emails:
            orphan_passwords.extend(step_passwords)

    # Fuer Emails ohne Passwort-Paar: aus KNOWN_EMAILS ergaenzen
    for email in all_emails:
        if email not in email_password_map:
            known = KNOWN_EMAILS.get(email, {})
            if "password" in known:
                email_password_map[email] = known["password"]

    # ===== PHASE 2: test_data-Eintraege sicherstellen =====

    # --- Login-Eintraege ---
    login_map = {}  # email -> entry
    for email in all_emails:
        known = KNOWN_EMAILS.get(email, {})
        login_name = known.get("name", f"user_{len(login_map)+1}")

        # Vorhandenen Eintrag suchen (login ODER account)
        existing = None
        for entry in test_data:
            if entry.get("type") in ("login", "account") and entry.get("email") == email:
                existing = entry
                break

        password = email_password_map.get(email)

        if existing:
            login_name = existing["name"]
            if password and "password" not in existing:
                existing["password"] = password
            login_map[email] = existing
        else:
            fields = {"email": email}
            if password:
                fields["password"] = password
            entry = ensure_td_entry(test_data, "login", login_name, **fields)
            login_map[email] = entry

    # Passwort -> Login-Eintrag Zuordnung
    pwd_to_login = {}
    for email, entry in login_map.items():
        if "password" in entry:
            pwd_to_login[entry["password"]] = entry

    # Verwaiste Passwoerter zuordnen
    for pwd in orphan_passwords:
        if pwd not in pwd_to_login:
            # In bekannten Emails suchen
            for known_email, known_info in KNOWN_EMAILS.items():
                if known_info.get("password") == pwd and known_email in login_map:
                    pwd_to_login[pwd] = login_map[known_email]
                    break
            # In vorhandenen test_data suchen
            if pwd not in pwd_to_login:
                for entry in test_data:
                    if entry.get("type") in ("login", "account") and entry.get("password") == pwd:
                        pwd_to_login[pwd] = entry
                        break
            # Passwort ohne zugehoerige Email -> generischen Login erstellen
            if pwd not in pwd_to_login and all_emails:
                # Dem ersten Email zuordnen
                first_email = list(all_emails)[0]
                if first_email in login_map:
                    entry = login_map[first_email]
                    if "password" not in entry:
                        entry["password"] = pwd
                    pwd_to_login[pwd] = entry

    # Alleinige Passwoerter ohne Email (z.B. Passwort-only Tests)
    for pwd in all_passwords:
        if pwd not in pwd_to_login:
            # Bekanntes Passwort -> bekannter Login-Name
            known_name = KNOWN_PASSWORDS.get(pwd)
            if known_name:
                existing = find_td_entry(test_data, "login", known_name)
                if not existing:
                    existing = find_td_entry(test_data, "account", known_name)
                if existing:
                    pwd_to_login[pwd] = existing

    # --- Adress-Eintraege ---
    if address_values:
        existing_addr = find_td_entry(test_data, "address")
        addr_name = "billing"
        if existing_addr:
            addr_name = existing_addr["name"]
            # "default" -> "billing" umbenennen
            if addr_name == "default":
                existing_addr["name"] = "billing"
                addr_name = "billing"
            # Fehlende Felder ergaenzen
            for k, v in address_values.items():
                if k not in existing_addr:
                    existing_addr[k] = v
        else:
            ensure_td_entry(test_data, "address", addr_name, **address_values)

    # --- Produkt-Eintraege ---
    product_map = {}  # product_id -> entry
    for pid, url in products_by_id.items():
        known = KNOWN_PRODUCTS.get(pid, {})
        prod_name = known.get("name", f"product_{pid}")

        # Vorhandenen Eintrag suchen
        existing = None
        for entry in test_data:
            if entry.get("type") == "product":
                entry_pid = entry.get("article_number") or ""
                entry_product_id = entry.get("product_id", "").replace("ge-p-", "")
                entry_path = entry.get("path", "")
                if entry_pid == pid or entry_product_id == pid or f"ge-p-{pid}" in entry_path:
                    existing = entry
                    break

        if existing:
            prod_name = existing["name"]
            if url and "path" not in existing:
                existing["path"] = url
            if pid.isdigit() and "article_number" not in existing:
                existing["article_number"] = pid
            product_map[pid] = existing
        else:
            fields = {}
            if url:
                fields["path"] = url
            if known.get("product_name"):
                fields["product_name"] = known["product_name"]
            if pid.isdigit():
                fields["article_number"] = pid
            entry = ensure_td_entry(test_data, "product", prod_name, **fields)
            product_map[pid] = entry

    # --- Promo-Eintraege ---
    promo_map = {}  # code -> entry
    for code in promos:
        known = KNOWN_PROMOS.get(code, {})
        promo_name = known.get("name", code.lower().replace("-", "_"))

        existing = find_td_by_field_value(test_data, "promo", "code", code)
        if existing:
            promo_map[code] = existing
        else:
            fields = {"code": code}
            if known.get("description"):
                fields["description"] = known["description"]
            entry = ensure_td_entry(test_data, "promo", promo_name, **fields)
            promo_map[code] = entry

    # --- Such-Eintraege ---
    search_map = {}
    for term in search_terms:
        known = KNOWN_SEARCH_TERMS.get(term, {})
        search_name = known.get("name", f"term_{len(search_map)+1}")

        existing = find_td_by_field_value(test_data, "search", "term", term)
        if existing:
            search_map[term] = existing
        else:
            entry = ensure_td_entry(test_data, "search", search_name, term=term)
            search_map[term] = entry

    # --- Bewertungs-Eintraege ---
    if review_values:
        ensure_td_entry(test_data, "review", "default", **review_values)

    # --- Newsletter-Eintraege ---
    for email in newsletter_emails:
        known = KNOWN_EMAILS.get(email, {})
        nl_name = known.get("name", "default")
        ensure_td_entry(test_data, "newsletter", nl_name, email=email)

    # --- Extra-Eintraege (Quantity, Sorting etc.) ---
    if extra_values:
        ensure_td_entry(test_data, "extra", "config", **extra_values)

    # ===== PHASE 3: Hartcodierte Werte durch value_ref ersetzen =====
    refs_created = 0

    for step in steps:
        for inp in step.get("inputs", []):
            if "value_ref" in inp or "value" not in inp:
                continue

            value = inp["value"]
            selector = inp.get("selector", "")
            action = inp.get("action", "")

            # Aktionen ohne Wert ueberspringen
            if action in ("click", "check", "uncheck", "wait"):
                continue

            # Navigate-Aktion
            if action == "navigate":
                if is_constant_url(value):
                    continue
                if is_product_url(value):
                    pid = extract_product_id(value)
                    if pid and pid in product_map:
                        entry = product_map[pid]
                        inp["value_ref"] = f"product:{entry['name']}.path"
                        del inp["value"]
                        refs_created += 1
                continue

            # Selector-basiertes Mapping
            mapping = get_selector_mapping(selector)
            if not mapping:
                continue

            td_type, field = mapping

            if td_type == "login":
                if field == "email":
                    if value in login_map:
                        entry = login_map[value]
                        entry_type = entry.get("type", "login")
                        inp["value_ref"] = f"{entry_type}:{entry['name']}.email"
                        del inp["value"]
                        refs_created += 1
                elif field == "password":
                    if value in pwd_to_login:
                        entry = pwd_to_login[value]
                        entry_type = entry.get("type", "login")
                        inp["value_ref"] = f"{entry_type}:{entry['name']}.password"
                        del inp["value"]
                        refs_created += 1

            elif td_type == "address":
                addr_entry = find_td_entry(test_data, "address")
                if addr_entry:
                    inp["value_ref"] = f"address:{addr_entry['name']}.{field}"
                    del inp["value"]
                    refs_created += 1

            elif td_type == "promo":
                if value in promo_map:
                    entry = promo_map[value]
                    inp["value_ref"] = f"promo:{entry['name']}.code"
                    del inp["value"]
                    refs_created += 1

            elif td_type == "search":
                if value in search_map:
                    entry = search_map[value]
                    inp["value_ref"] = f"search:{entry['name']}.term"
                    del inp["value"]
                    refs_created += 1

            elif td_type == "review":
                inp["value_ref"] = f"review:default.{field}"
                del inp["value"]
                refs_created += 1

            elif td_type == "newsletter":
                known = KNOWN_EMAILS.get(value, {})
                nl_name = known.get("name", "default")
                inp["value_ref"] = f"newsletter:{nl_name}.email"
                del inp["value"]
                refs_created += 1

            elif td_type == "product":
                if field == "article_number" and value in product_map:
                    entry = product_map[value]
                    inp["value_ref"] = f"product:{entry['name']}.article_number"
                    del inp["value"]
                    refs_created += 1

            elif td_type == "extra":
                extra_entry = find_td_entry(test_data, "extra", "config")
                if extra_entry:
                    inp["value_ref"] = f"extra:config.{field}"
                    del inp["value"]
                    refs_created += 1

    # ===== PHASE 4: Aufraumen =====

    # "extra" Eintraege die nur noch password hatten -> entfernen
    cleaned_td = []
    for entry in test_data:
        if entry.get("type") == "extra" and entry.get("name") == "default":
            remaining = {k: v for k, v in entry.items()
                         if k not in ("type", "name", "password")}
            if not remaining:
                continue  # Leeren Extra-Eintrag entfernen
            if "password" in entry:
                del entry["password"]
        cleaned_td.append(entry)
    data["test_data"] = cleaned_td

    # Datei schreiben
    if refs_created > 0 and not dry_run:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")

    return refs_created > 0, refs_created, "ok"


# ============================================================================
# Main
# ============================================================================

def main():
    dry_run = "--dry-run" in sys.argv
    single_file = None
    for arg in sys.argv[1:]:
        if arg.startswith("--file="):
            single_file = arg.split("=", 1)[1]
        elif arg.endswith(".json") and not arg.startswith("--"):
            single_file = arg

    examples_dir = EXAMPLES_DIR
    if single_file:
        files = [examples_dir / single_file]
    else:
        files = sorted(examples_dir.glob("*.json"))

    total = len(files)
    changed_count = 0
    skipped_count = 0
    error_count = 0
    total_refs = 0
    remaining_hardcoded = 0

    for filepath in files:
        if not filepath.exists():
            print(f"  FEHLT  {filepath.name}")
            error_count += 1
            continue

        changed, refs, reason = migrate_contract(filepath, dry_run)
        if reason == "invalid JSON":
            print(f"  ERROR  {filepath.name}: {reason}")
            error_count += 1
        elif changed:
            print(f"  OK     {filepath.name}: {refs} refs")
            changed_count += 1
            total_refs += refs
        else:
            if reason == "already clean":
                pass  # Still clean
            else:
                skipped_count += 1

    # Abschlussbericht
    mode = " (DRY RUN)" if dry_run else ""
    print(f"\n{'='*60}")
    print(f"Migration{mode}")
    print(f"  Dateien gesamt:     {total}")
    print(f"  Geaendert:          {changed_count}")
    print(f"  Uebersprungen:      {skipped_count}")
    print(f"  Fehler:             {error_count}")
    print(f"  value_refs erstellt: {total_refs}")

    # Verbleibende hartcodierte Werte zaehlen
    if not dry_run:
        print(f"\nPruefe verbleibende hartcodierte Werte...")
        remaining = 0
        remaining_files = []
        for filepath in files:
            if not filepath.exists():
                continue
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                continue
            for step in data.get("steps", []):
                for inp in step.get("inputs", []):
                    if "value" in inp and "value_ref" not in inp:
                        action = inp.get("action", "")
                        if action in ("click", "check", "uncheck", "wait"):
                            continue
                        if action == "navigate" and is_constant_url(inp["value"]):
                            continue
                        remaining += 1
                        if filepath.name not in remaining_files:
                            remaining_files.append(filepath.name)

        print(f"  Verbleibend:        {remaining} Werte in {len(remaining_files)} Dateien")
        if remaining_files:
            print(f"  Betroffene Dateien:")
            for fn in remaining_files[:20]:
                print(f"    - {fn}")
            if len(remaining_files) > 20:
                print(f"    ... und {len(remaining_files)-20} weitere")


if __name__ == "__main__":
    main()
