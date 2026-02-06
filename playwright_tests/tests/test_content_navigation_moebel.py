"""
Content-Navigation-Test: Moebel-Kategoriebaum (TC-NAV-006).

Validiert den Kategoriebaum unter "Moebel" im Mega-Menue gegen eine
Soll-Struktur. Prueft korrekte Titel, korrekte URLs, fehlende und
zusaetzliche Kategorien.

url=None in der Soll-Struktur = Filter-URL (nur Titel wird geprueft).

Ausfuehrung:
    pytest playwright_tests/tests/test_content_navigation_moebel.py -v -s
"""
from urllib.parse import unquote, urlparse

import pytest
from playwright.sync_api import Page

from ..conftest import accept_cookie_banner


# =============================================================================
# Soll-Kategoriebaum: Moebel
# url=None = Filter-URL (kein eigener Pfad, nur Name wird geprueft)
# =============================================================================

EXPECTED_MOEBEL_TREE = [
    {
        "name": "Betten",
        "url": "/betten",
        "subcategories": [
            {"name": "Betten und Nachttische", "url": "/betten-und-nachttische"},
            {"name": "Nachttische", "url": "/nachttische"},
            {"name": "Bettzubehör", "url": "/bettzubehoer"},
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


# =============================================================================
# Test
# =============================================================================

def test_content_navigation_moebel(page: Page, base_url: str):
    """
    Validiert den Moebel-Kategoriebaum im Mega-Menue.

    Oeffnet das Mega-Menue unter "Moebel" und prueft:
    1. Sind alle erwarteten UK1- und UK2-Kategorien vorhanden?
    2. Stimmen die URLs?
    3. Gibt es zusaetzliche Kategorien, die nicht in der Soll-Liste stehen?
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

    # 2. "Moebel"-Link in der Hauptnavigation finden und hovern
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
        "Moebel-Link in der Hauptnavigation nicht gefunden. "
        f"Gefundene Links: {[nav_links.nth(i).inner_text().strip() for i in range(nav_links.count()) if nav_links.nth(i).is_visible()]}"
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
                    print(f"    Flyout gefunden: {sel}")
                    break
            except Exception:
                continue

    assert flyout is not None, "Mega-Menue-Flyout nicht gefunden nach Hover ueber Moebel"

    # Alle Links im Flyout sammeln
    anchors = flyout.locator("a")
    all_links = []
    anchor_count = anchors.count()

    skip_names = {"möbel", "alle anzeigen", "alle produkte", ""}
    for i in range(anchor_count):
        a = anchors.nth(i)
        try:
            name = a.inner_text(timeout=1000).strip()
            href = a.get_attribute("href") or ""
            if name and normalize_name(name) not in skip_names:
                path = extract_path(href)
                all_links.append({"name": name, "path": path})
        except Exception:
            continue

    print(f"    {len(all_links)} Links gefunden im Moebel-Flyout:")
    for link in all_links:
        print(f"      - {link['name']}: {link['path']}")
    print()

    # 4. Vergleich: Soll vs. Ist
    print("[4] Kategorien vergleichen...\n")

    correct = []
    missing_critical = []  # UK1 + UK2 mit bekannter URL
    missing_filter = []    # UK2 mit Filter-URL (informativ)
    url_mismatches = []
    matched_names = set()

    for uk1 in EXPECTED_MOEBEL_TREE:
        # UK1 pruefen
        uk1_match = find_link_by_name(all_links, uk1["name"])

        if uk1_match:
            matched_names.add(normalize_name(uk1["name"]))
            if path_matches(uk1_match["path"], uk1["url"]):
                correct.append(f"UK1 {uk1['name']}: {uk1['url']}")
            else:
                url_mismatches.append(
                    f"UK1 {uk1['name']}: erwartet '{uk1['url']}', "
                    f"gefunden '{uk1_match['path']}'"
                )
        else:
            missing_critical.append(f"UK1 {uk1['name']} ({uk1['url']})")

        # UK2 pruefen
        for uk2 in uk1.get("subcategories", []):
            uk2_match = find_link_by_name(all_links, uk2["name"])

            if uk2_match:
                matched_names.add(normalize_name(uk2["name"]))
                if uk2["url"]:
                    if path_matches(uk2_match["path"], uk2["url"]):
                        correct.append(
                            f"  UK2 {uk2['name']}: {uk2['url']}"
                        )
                    else:
                        url_mismatches.append(
                            f"  UK2 {uk2['name']} (unter {uk1['name']}): "
                            f"erwartet '{uk2['url']}', gefunden '{uk2_match['path']}'"
                        )
                else:
                    correct.append(f"  UK2 {uk2['name']}: (Filter-URL)")
            else:
                if uk2["url"]:
                    missing_critical.append(
                        f"  UK2 {uk2['name']} ({uk2['url']}) unter {uk1['name']}"
                    )
                else:
                    missing_filter.append(
                        f"  UK2 {uk2['name']} (Filter) unter {uk1['name']}"
                    )

    # 5. Extras finden (im Flyout vorhanden, aber nicht in Soll-Liste)
    extras = []
    for link in all_links:
        if normalize_name(link["name"]) not in matched_names:
            extras.append(f"{link['name']}: {link['path']}")

    # 6. Report
    print("=" * 60)
    print("ERGEBNIS: Moebel-Kategoriebaum")
    print("=" * 60)

    print(f"\nKORREKT ({len(correct)}):")
    for item in correct:
        print(f"  [OK] {item}")

    if url_mismatches:
        print(f"\nURL-ABWEICHUNGEN ({len(url_mismatches)}):")
        for item in url_mismatches:
            print(f"  [!!] {item}")

    if missing_critical:
        print(f"\nFEHLEND - kritisch ({len(missing_critical)}):")
        for item in missing_critical:
            print(f"  [FEHLT] {item}")

    if missing_filter:
        print(
            f"\nFILTER-KATEGORIEN NICHT IM MEGA-MENUE "
            f"({len(missing_filter)}):"
        )
        for item in missing_filter:
            print(f"  [FILTER] {item}")

    if extras:
        print(f"\nZUSAETZLICH - nicht in Soll-Liste ({len(extras)}):")
        for item in extras:
            print(f"  [EXTRA] {item}")

    total_expected = sum(
        1 + len(uk1.get("subcategories", []))
        for uk1 in EXPECTED_MOEBEL_TREE
    )
    print(f"\nZusammenfassung:")
    print(f"  Soll-Kategorien:        {total_expected}")
    print(f"  Korrekt:                {len(correct)}")
    print(f"  URL-Abweichungen:       {len(url_mismatches)}")
    print(f"  Fehlend (kritisch):     {len(missing_critical)}")
    print(f"  Filter nicht im Menue:  {len(missing_filter)}")
    print(f"  Zusaetzlich:            {len(extras)}")

    # Screenshot bei Problemen
    if missing_critical or url_mismatches:
        page.screenshot(path="error_navigation_moebel.png")

    # Assertions - nur kritische Fehler (fehlende Kategorien + falsche URLs)
    errors = []
    if missing_critical:
        errors.append(
            f"Fehlende Kategorien:\n"
            + "\n".join(f"  - {m}" for m in missing_critical)
        )
    if url_mismatches:
        errors.append(
            f"URL-Abweichungen:\n"
            + "\n".join(f"  - {m}" for m in url_mismatches)
        )

    assert not errors, "\n\n".join(errors)
