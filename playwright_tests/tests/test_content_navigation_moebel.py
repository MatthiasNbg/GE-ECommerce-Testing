"""
Content-Navigation-Test: Moebel-Kategoriebaum (TC-NAV-006).

Validiert den Kategoriebaum unter "Moebel" im Mega-Menue gegen eine
Soll-Struktur mit 3 Ebenen (UK1 / UK2 / UK3).

Prueft:
- Korrekte Titel und URLs auf allen 3 Ebenen
- Fehlende Kategorien
- Zusaetzliche Kategorien (nicht in Soll-Liste)
- Duplikate (gleicher Name mehrfach im Menue) => FEHLER
- Leere Eintraege ("empty") => FEHLER

Ausfuehrung:
    pytest playwright_tests/tests/test_content_navigation_moebel.py -v -s
"""
from urllib.parse import unquote, urlparse

import pytest
from playwright.sync_api import Page

from ..conftest import accept_cookie_banner


# =============================================================================
# Soll-Kategoriebaum: Moebel (3 Ebenen: UK1 > UK2 > UK3)
#
# Struktur:
#   UK1 = Hauptkategorie (z.B. Betten, Sofas)
#   UK2 = Unterkategorie (z.B. Betten und Nachttische, Schlafsofas)
#   UK3 = Sub-Unterkategorie (z.B. Nachttische, Bettzubehoer)
#
# "subcategories" auf UK2-Ebene = UK3-Eintraege (sofern vorhanden)
# =============================================================================

EXPECTED_MOEBEL_TREE = [
    {
        "name": "Betten",
        "url": "/betten",
        "subcategories": [
            {
                "name": "Betten und Nachttische",
                "url": "/betten-und-nachttische",
                "subcategories": [
                    {"name": "Nachttische", "url": "/nachttische"},
                    {"name": "Bettzubehör", "url": "/bettzubehoer"},
                ],
            },
        ],
    },
    {
        "name": "Sofas",
        "url": "/sofas",
        "subcategories": [
            {"name": "Schlafsofas", "url": "/schlafsofas"},
            {"name": "Hocker", "url": "/hocker"},
            {"name": "Sofakissen", "url": "/sofakissen"},
            {"name": "Ecksofas", "url": "/ecksofas"},
            {"name": "Einzelsofas", "url": "/einzelsofas"},
            {"name": "Sofatische", "url": "/sofatische"},
        ],
    },
    {
        "name": "Wohnschränke & Vitrinen",
        "url": "/wohnschraenke-vitrinen",
        "subcategories": [
            {"name": "Wohnschränke", "url": "/wohnschraenke"},
            {"name": "Vitrinen", "url": "/vitrinen"},
        ],
    },
    {
        "name": "Schränke",
        "url": "/schraenke",
        "subcategories": [
            {"name": "Sideboards & Kommoden", "url": "/sideboards-kommoden"},
            {"name": "Schrankzubehör", "url": "/schrankzubehoer"},
            {"name": "Kleiderschränke", "url": "/kleiderschraenke"},
        ],
    },
    {
        "name": "Regale",
        "url": "/regale",
        "subcategories": [
            {"name": "Regalsysteme", "url": "/regalsysteme"},
            {"name": "Regalzubehör", "url": "/regalzubehoer"},
        ],
    },
    {
        "name": "Tische",
        "url": "/tische",
        "subcategories": [
            {"name": "Esstische & Ausziehtische", "url": "/esstische-ausziehtische"},
            {"name": "Schreibtische", "url": "/schreibtische"},
        ],
    },
    {
        "name": "Stühle & Bänke",
        "url": "/stuehle-baenke",
        "subcategories": [
            {"name": "Sitzbänke", "url": "/sitzbaenke"},
            {"name": "Stühle", "url": "/stuehle"},
        ],
    },
    {
        "name": "Polstersessel",
        "url": "/polstersessel",
        "subcategories": [],
    },
    {
        "name": "Lampen & Leuchten",
        "url": "/lampen-leuchten",
        "subcategories": [
            {"name": "Hängeleuchten", "url": "/haengeleuchten"},
            {"name": "Stehleuchten", "url": "/stehleuchten"},
            {"name": "Tischleuchten", "url": "/tischleuchten"},
            {"name": "Bodenleuchten", "url": "/bodenleuchten"},
            {"name": "Leuchtmittel", "url": "/leuchtmittel"},
        ],
    },
    {
        "name": "Teppiche",
        "url": "/teppiche",
        "subcategories": [],
    },
]


# =============================================================================
# Hilfsfunktionen
# =============================================================================

def normalize_name(name: str) -> str:
    """Normalisiert Kategorienamen fuer Vergleich (lowercase, Whitespace)."""
    return " ".join(name.strip().lower().split())


def extract_path(href: str) -> str:
    """Extrahiert und normalisiert den URL-Pfad."""
    if not href:
        return ""
    parsed = urlparse(href)
    return unquote(parsed.path).rstrip("/")


def find_link_by_name(links: list[dict], name: str) -> dict | None:
    """Findet einen Link per normalisiertem Namen. Gibt ersten Treffer zurueck."""
    target = normalize_name(name)
    for link in links:
        if normalize_name(link["name"]) == target:
            return link
    return None


def path_matches(actual_path: str, expected_suffix: str) -> bool:
    """Prueft ob der tatsaechliche Pfad mit dem erwarteten Suffix endet."""
    actual = unquote(actual_path).rstrip("/")
    expected = expected_suffix.rstrip("/")
    return actual.endswith(expected)


def count_expected(tree: list[dict]) -> dict:
    """Zaehlt erwartete Kategorien auf allen 3 Ebenen."""
    counts = {"uk1": 0, "uk2": 0, "uk3": 0, "total": 0}
    for uk1 in tree:
        counts["uk1"] += 1
        counts["total"] += 1
        for uk2 in uk1.get("subcategories", []):
            counts["uk2"] += 1
            counts["total"] += 1
            for _uk3 in uk2.get("subcategories", []):
                counts["uk3"] += 1
                counts["total"] += 1
    return counts


# =============================================================================
# Test
# =============================================================================

def test_content_navigation_moebel(page: Page, base_url: str):
    """
    Validiert den Moebel-Kategoriebaum im Mega-Menue (UK1/UK2/UK3).

    Prueft:
    1. Sind alle erwarteten UK1-, UK2- und UK3-Kategorien vorhanden?
    2. Stimmen die URLs?
    3. Gibt es Duplikate (gleicher Name mehrfach)?
    4. Gibt es leere Eintraege ("empty")?
    5. Gibt es zusaetzliche Kategorien?
    """
    print("\n" + "=" * 60)
    print("TC-NAV-006: Content-Navigation Moebel")
    print("=" * 60)

    # 1. Homepage laden
    print("\n[1] Homepage laden...")
    page.goto(base_url)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1500)
    accept_cookie_banner(page)
    page.wait_for_timeout(500)

    # 2. "Moebel"-Link finden und hovern
    print("[2] Moebel-Navigation oeffnen...")
    nav_links = page.locator(
        ".main-navigation-link, .nav-link.main-navigation-link, "
        ".main-navigation a"
    )
    assert nav_links.count() > 0, "Keine Navigations-Links gefunden"

    moebel_link = None
    for i in range(nav_links.count()):
        link = nav_links.nth(i)
        if link.is_visible():
            text = link.inner_text().strip()
            if normalize_name(text) == "möbel":
                moebel_link = link
                break

    assert moebel_link is not None, (
        "Moebel-Link in der Hauptnavigation nicht gefunden."
    )

    moebel_link.hover()
    page.wait_for_timeout(1500)

    # 3. Flyout-Links auslesen
    print("[3] Mega-Menue auswerten...")
    flyout_selectors = [
        ".navigation-flyout",
        ".navigation-flyout-content",
        ".main-navigation-flyout",
        ".mega-menu",
    ]

    flyout = None
    for sel in flyout_selectors:
        loc = page.locator(sel)
        if loc.count() > 0:
            try:
                if loc.first.is_visible(timeout=3000):
                    flyout = loc.first
                    break
            except Exception:
                continue

    assert flyout is not None, "Mega-Menue-Flyout nicht gefunden nach Hover ueber Moebel"

    # Alle Links im Flyout sammeln mit CSS-Klassen-Info
    anchors = flyout.locator("a")
    all_links = []
    name_occurrences = {}  # name -> list of paths (fuer Duplikat-Erkennung)

    skip_names = {"möbel", "alle anzeigen", "alle produkte"}
    for i in range(anchors.count()):
        a = anchors.nth(i)
        try:
            name = a.inner_text(timeout=1000).strip()
            href = a.get_attribute("href") or ""
            if not name or normalize_name(name) in skip_names:
                continue
            classes = a.get_attribute("class") or ""
            path = extract_path(href)
            is_header = "navigation-flyout-link" in classes
            all_links.append({
                "name": name,
                "path": path,
                "is_header": is_header,
            })
            # Duplikat-Tracking
            norm = normalize_name(name)
            if norm not in name_occurrences:
                name_occurrences[norm] = []
            name_occurrences[norm].append(path)
        except Exception:
            continue

    print(f"    {len(all_links)} Links gefunden im Moebel-Flyout:")
    for link in all_links:
        level = "H" if link["is_header"] else " "
        print(f"      [{level}] {link['name']}: {link['path']}")
    print()

    # 4. Duplikate erkennen
    duplicates = []
    for norm_name, paths in name_occurrences.items():
        if len(paths) > 1:
            display_name = next(
                l["name"] for l in all_links
                if normalize_name(l["name"]) == norm_name
            )
            duplicates.append({
                "name": display_name,
                "count": len(paths),
                "paths": paths,
            })

    # 5. Leere Eintraege ("empty") erkennen
    empty_entries = [
        l for l in all_links
        if normalize_name(l["name"]) == "empty"
    ]

    # 6. Vergleich: Soll vs. Ist (3 Ebenen: UK1 > UK2 > UK3)
    print("[4] Kategorien vergleichen (UK1 / UK2 / UK3)...\n")

    correct = []
    missing = []
    url_mismatches = []
    matched_names = set()

    for uk1 in EXPECTED_MOEBEL_TREE:
        # UK1 pruefen
        uk1_match = find_link_by_name(all_links, uk1["name"])

        if uk1_match:
            matched_names.add(normalize_name(uk1["name"]))
            if path_matches(uk1_match["path"], uk1["url"]):
                correct.append({
                    "level": "UK1", "name": uk1["name"],
                    "expected_url": uk1["url"], "actual_url": uk1_match["path"],
                    "status": "OK",
                })
            else:
                url_mismatches.append({
                    "level": "UK1", "name": uk1["name"],
                    "expected_url": uk1["url"], "actual_url": uk1_match["path"],
                })
        else:
            missing.append({
                "level": "UK1", "name": uk1["name"],
                "expected_url": uk1["url"], "parent": "",
            })

        # UK2 pruefen
        for uk2 in uk1.get("subcategories", []):
            uk2_match = find_link_by_name(all_links, uk2["name"])

            if uk2_match:
                matched_names.add(normalize_name(uk2["name"]))
                if uk2.get("url"):
                    if path_matches(uk2_match["path"], uk2["url"]):
                        correct.append({
                            "level": "UK2", "name": uk2["name"],
                            "expected_url": uk2["url"],
                            "actual_url": uk2_match["path"],
                            "status": "OK", "parent": uk1["name"],
                        })
                    else:
                        url_mismatches.append({
                            "level": "UK2", "name": uk2["name"],
                            "expected_url": uk2["url"],
                            "actual_url": uk2_match["path"],
                            "parent": uk1["name"],
                        })
            else:
                missing.append({
                    "level": "UK2", "name": uk2["name"],
                    "expected_url": uk2.get("url", ""),
                    "parent": uk1["name"],
                })

            # UK3 pruefen
            for uk3 in uk2.get("subcategories", []):
                uk3_match = find_link_by_name(all_links, uk3["name"])

                if uk3_match:
                    matched_names.add(normalize_name(uk3["name"]))
                    if uk3.get("url"):
                        if path_matches(uk3_match["path"], uk3["url"]):
                            correct.append({
                                "level": "UK3", "name": uk3["name"],
                                "expected_url": uk3["url"],
                                "actual_url": uk3_match["path"],
                                "status": "OK",
                                "parent": f"{uk1['name']} > {uk2['name']}",
                            })
                        else:
                            url_mismatches.append({
                                "level": "UK3", "name": uk3["name"],
                                "expected_url": uk3["url"],
                                "actual_url": uk3_match["path"],
                                "parent": f"{uk1['name']} > {uk2['name']}",
                            })
                else:
                    missing.append({
                        "level": "UK3", "name": uk3["name"],
                        "expected_url": uk3.get("url", ""),
                        "parent": f"{uk1['name']} > {uk2['name']}",
                    })

    # 7. Extras (im Flyout vorhanden, nicht in Soll-Liste)
    extras = []
    seen_extra_names = set()
    for link in all_links:
        norm = normalize_name(link["name"])
        if norm not in matched_names and norm != "empty" and norm not in seen_extra_names:
            extras.append({"name": link["name"], "path": link["path"]})
            seen_extra_names.add(norm)

    # =================================================================
    # 8. Report
    # =================================================================
    expected_counts = count_expected(EXPECTED_MOEBEL_TREE)

    print("=" * 60)
    print("ERGEBNIS: Moebel-Kategoriebaum (UK1 / UK2 / UK3)")
    print("=" * 60)

    # --- Korrekte Kategorien ---
    print(f"\nKORREKT ({len(correct)}):")
    print(f"  {'Ebene':<5} {'Kategorie':<35} {'URL (Soll)':<30} {'URL (Ist)'}")
    print(f"  {'-'*5:<5} {'-'*35:<35} {'-'*30:<30} {'-'*40}")
    for item in correct:
        print(
            f"  {item['level']:<5} {item['name']:<35} "
            f"{item['expected_url']:<30} {item['actual_url']}"
        )

    # --- URL-Abweichungen ---
    if url_mismatches:
        print(f"\nURL-ABWEICHUNGEN ({len(url_mismatches)}):")
        print(f"  {'Ebene':<5} {'Kategorie':<35} {'URL (Soll)':<30} {'URL (Ist)'}")
        print(f"  {'-'*5:<5} {'-'*35:<35} {'-'*30:<30} {'-'*40}")
        for item in url_mismatches:
            print(
                f"  {item['level']:<5} {item['name']:<35} "
                f"{item['expected_url']:<30} {item['actual_url']}"
            )

    # --- Fehlende Kategorien ---
    if missing:
        print(f"\nFEHLEND ({len(missing)}):")
        print(f"  {'Ebene':<5} {'Kategorie':<35} {'URL (Soll)':<30} {'Eltern'}")
        print(f"  {'-'*5:<5} {'-'*35:<35} {'-'*30:<30} {'-'*30}")
        for item in missing:
            print(
                f"  {item['level']:<5} {item['name']:<35} "
                f"{item['expected_url']:<30} {item.get('parent', '')}"
            )

    # --- Duplikate (FEHLER) ---
    if duplicates:
        print(f"\nDUPLIKATE - FEHLER ({len(duplicates)}):")
        for dup in duplicates:
            print(f"  [DUPLIKAT] \"{dup['name']}\" kommt {dup['count']}x vor:")
            for p in dup["paths"]:
                print(f"             - {p}")

    # --- Leere Eintraege (FEHLER) ---
    if empty_entries:
        print(f"\nLEERE EINTRAEGE - FEHLER ({len(empty_entries)}):")
        for entry in empty_entries:
            print(f"  [LEER] \"{entry['name']}\": {entry['path']}")

    # --- Extras ---
    if extras:
        print(f"\nZUSAETZLICH - nicht in Soll-Liste ({len(extras)}):")
        for item in extras:
            print(f"  [EXTRA] {item['name']}: {item['path']}")

    # --- Zusammenfassung ---
    print(f"\n{'=' * 60}")
    print("ZUSAMMENFASSUNG")
    print(f"{'=' * 60}")
    print(f"  Soll-Kategorien gesamt:  {expected_counts['total']}")
    print(f"    davon UK1:             {expected_counts['uk1']}")
    print(f"    davon UK2:             {expected_counts['uk2']}")
    print(f"    davon UK3:             {expected_counts['uk3']}")
    print(f"  Korrekt:                 {len(correct)}")
    print(f"  URL-Abweichungen:        {len(url_mismatches)}")
    print(f"  Fehlend:                 {len(missing)}")
    print(f"  Duplikate:               {len(duplicates)}")
    print(f"  Leere Eintraege:         {len(empty_entries)}")
    print(f"  Zusaetzlich:             {len(extras)}")

    # Screenshot bei Problemen
    if missing or url_mismatches or duplicates or empty_entries:
        page.screenshot(path="error_navigation_moebel.png")

    # Assertions - Test schlaegt fehl bei:
    # fehlende Kategorien, URL-Abweichungen, Duplikate, leere Eintraege
    errors = []
    if missing:
        errors.append(
            f"Fehlende Kategorien ({len(missing)}):\n"
            + "\n".join(
                f"  - {m['level']} {m['name']} ({m['expected_url']})"
                + (f" unter {m['parent']}" if m.get("parent") else "")
                for m in missing
            )
        )
    if url_mismatches:
        errors.append(
            f"URL-Abweichungen ({len(url_mismatches)}):\n"
            + "\n".join(
                f"  - {m['level']} {m['name']}: "
                f"erwartet '{m['expected_url']}', gefunden '{m['actual_url']}'"
                for m in url_mismatches
            )
        )
    if duplicates:
        errors.append(
            f"Duplikate im Mega-Menue ({len(duplicates)}):\n"
            + "\n".join(
                f"  - \"{d['name']}\" {d['count']}x: {', '.join(d['paths'])}"
                for d in duplicates
            )
        )
    if empty_entries:
        errors.append(
            f"Leere Eintraege im Mega-Menue ({len(empty_entries)}):\n"
            + "\n".join(
                f"  - \"{e['name']}\" ({e['path']})"
                for e in empty_entries
            )
        )

    assert not errors, "\n\n".join(errors)
