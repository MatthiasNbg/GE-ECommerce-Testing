# Design: Automatische Zahlungsarten-Ermittlung

**Datum**: 2026-01-16
**Status**: Design validiert, bereit für Implementierung

## Überblick

Ein Discovery-Test ermittelt automatisch die verfügbaren Zahlungsarten für Deutschland, Österreich und Schweiz pro Profil und aktualisiert die `config.yaml`. Dies macht die Tests datengetrieben und robust gegenüber Shop-Änderungen.

## Problem

Aktuell sind Zahlungsarten hardcodiert:
- Test verwendet: `["invoice", "credit_card", "paypal"]`
- CheckoutPage hat statisches Mapping zu CSS-Selektoren
- Keine Berücksichtigung von länderspezifischen Unterschieden
- Zahlungsarten unterscheiden sich zwischen DE, AT, CH

## Lösung

### Workflow

```bash
# Discovery-Test ausführen
pytest -m discovery --profile=staging

# Aktualisiert automatisch config.yaml mit:
# - payment_methods pro Land und Profil
# - payment_method_aliases (englisch → deutsch)
```

### Komponenten

**Neuer Test**: `playwright_tests/tests/test_payment_discovery.py`
- Marker: `@pytest.mark.discovery`
- Iteriert über Länder: AT, DE, CH
- Navigiert zu länderspezifischen Shop-URLs
- Extrahiert Zahlungsarten-Labels aus DOM
- Generiert Aliases automatisch
- Aktualisiert `config.yaml`

**Config-Struktur nach Discovery**:
```yaml
profiles:
  staging:
    base_url: "https://grueneerde.scalecommerce.cloud"
    country_paths:
      AT: "/"
      DE: "/de-de"
      CH: "/de-ch"
    payment_methods:
      AT: ["Kreditkarte", "Vorkasse", "Rechnung"]
      DE: ["Kreditkarte", "PayPal", "Rechnung", "Klarna"]
      CH: ["Kreditkarte", "Vorkasse"]

payment_method_aliases:
  "invoice": "Rechnung"
  "credit_card": "Kreditkarte"
  "prepayment": "Vorkasse"
  "paypal": "PayPal"
  "klarna": "Klarna"
```

## Implementierungsdetails

### 1. Discovery-Test

**Datei**: `playwright_tests/tests/test_payment_discovery.py`

```python
@pytest.mark.discovery
async def test_discover_payment_methods(browser, config):
    """Ermittelt verfügbare Zahlungsarten für alle Länder."""

    countries = {
        "AT": "/",
        "DE": "/de-de",
        "CH": "/de-ch"
    }

    discovered = {}

    for country_code, path in countries.items():
        url = config.base_url + path

        # Neuen Browser-Context für jedes Land
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # Produkt zum Warenkorb hinzufügen
            await add_test_product_to_cart(page, url)

            # Zu Checkout navigieren
            await page.goto(f"{url}/checkout/confirm")
            await page.wait_for_load_state("domcontentloaded")

            # Zahlungsarten extrahieren
            labels = await page.locator(".payment-method-label strong").all_text_contents()
            discovered[country_code] = labels

        except Exception as e:
            print(f"Warning: Konnte {country_code} nicht ermitteln: {e}")
            discovered[country_code] = []

        finally:
            await context.close()

    # Config aktualisieren
    update_config_with_payment_methods(config.profile, discovered)
```

**Extraktion aus DOM**:
Basierend auf der HTML-Struktur:
```html
<div class="payment-method-label">
    <strong>Kreditkarte</strong>
    <p>Beschreibung...</p>
</div>
```

Selektor: `.payment-method-label strong`

### 2. Config-Aktualisierung

**Funktion**: `update_config_with_payment_methods(profile_name, discovered_methods)`

```python
import yaml
from pathlib import Path

def update_config_with_payment_methods(profile_name, discovered_methods):
    """
    Aktualisiert config.yaml mit ermittelten Zahlungsarten.

    Args:
        profile_name: Name des Profils (staging, production)
        discovered_methods: Dict[country_code, List[label]]
    """
    config_path = Path("config/config.yaml")

    # Backup erstellen
    backup_path = config_path.with_suffix(".yaml.backup")
    config_path.replace(backup_path)

    # Config laden
    with open(backup_path) as f:
        config = yaml.safe_load(f)

    # Country paths hinzufügen (falls nicht vorhanden)
    if "country_paths" not in config["profiles"][profile_name]:
        config["profiles"][profile_name]["country_paths"] = {
            "AT": "/",
            "DE": "/de-de",
            "CH": "/de-ch"
        }

    # Payment methods hinzufügen
    config["profiles"][profile_name]["payment_methods"] = discovered_methods

    # Aliases generieren und mergen
    new_aliases = generate_aliases(discovered_methods)
    if "payment_method_aliases" not in config:
        config["payment_method_aliases"] = {}
    config["payment_method_aliases"].update(new_aliases)

    # Zurückschreiben
    with open(config_path, "w") as f:
        yaml.dump(config, f, allow_unicode=True, sort_keys=False)

    print(f"✓ Config aktualisiert: {config_path}")
```

### 3. Alias-Generierung

**Funktion**: `generate_aliases(discovered_methods)`

```python
def generate_aliases(discovered_methods):
    """
    Generiert englische Aliases für deutsche Zahlungsarten-Labels.

    Returns:
        Dict[alias, label]
    """
    known_mappings = {
        "Rechnung": "invoice",
        "Kreditkarte": "credit_card",
        "Vorkasse": "prepayment",
        "PayPal": "paypal",
        "Klarna": "klarna",
        "Sofortüberweisung": "sofort",
    }

    aliases = {}
    all_labels = set()

    # Sammle alle einzigartigen Labels
    for labels in discovered_methods.values():
        all_labels.update(labels)

    # Erstelle Aliases
    for label in all_labels:
        if label in known_mappings:
            alias = known_mappings[label]
        else:
            # Generischer Alias: lowercase, keine Umlaute
            alias = label.lower()\
                .replace("ä", "ae")\
                .replace("ö", "oe")\
                .replace("ü", "ue")\
                .replace("ß", "ss")\
                .replace(" ", "_")

        aliases[alias] = label

    return aliases
```

### 4. CheckoutPage Integration

**Anpassung**: `checkout_page.py` - `select_payment_method()`

```python
async def select_payment_method(self, method: str) -> None:
    """
    Wählt eine Zahlungsart aus.

    Args:
        method: Englischer Alias (z.B. "invoice") oder deutsches Label ("Rechnung")
    """
    # Lade Aliases aus Config
    from playwright_tests.config import get_config
    config = get_config()

    # Übersetze Alias zu Label (falls nötig)
    label = config.payment_method_aliases.get(method, method)

    # Suche nach Label im DOM
    payment_label = self.page.locator(f".payment-method-label:has-text('{label}')")

    if await payment_label.count() == 0:
        raise ValueError(f"Zahlungsart '{label}' nicht gefunden")

    # Klicke auf zugehöriges Radio-Button
    radio_button = payment_label.locator("..").locator("input[type='radio']")
    await radio_button.click()
```

**Vorteil**: Tests können weiterhin `select_payment_method("invoice")` verwenden, während die Implementierung flexibel mit den tatsächlichen Shop-Labels arbeitet.

### 5. Config-Model Erweiterung

**Datei**: `playwright_tests/config.py`

```python
from typing import Dict, List

class TestConfig(BaseSettings):
    # ... bestehende Felder ...

    country_paths: Dict[str, str] = {
        "AT": "/",
        "DE": "/de-de",
        "CH": "/de-ch"
    }

    payment_methods: Dict[str, List[str]] = {}
    payment_method_aliases: Dict[str, str] = {}
```

## Fehlerbehandlung

### 1. Land nicht erreichbar
- Warning ausgeben, Test fortsetzen
- Leere Liste für das Land speichern

### 2. Keine Zahlungsarten gefunden
- Test schlägt fehl mit klarer Fehlermeldung
- Vermutlich strukturelles Problem (falscher Selektor, Shop-Änderung)

### 3. YAML-Schreibfehler
- Backup wird automatisch erstellt (`.yaml.backup`)
- Bei Fehler: Original bleibt als Backup erhalten

### 4. Unbekannte Zahlungsart
- Generischer Alias wird erstellt
- Warning im Log für manuelle Review

## Logging-Ausgabe

```
[Discovery] Ermittle Zahlungsarten für staging...
[Discovery]
[Discovery] AT (https://grueneerde.scalecommerce.cloud/):
[Discovery]   ✓ Kreditkarte → credit_card
[Discovery]   ✓ Vorkasse → prepayment
[Discovery]   ✓ Rechnung → invoice
[Discovery]
[Discovery] DE (https://grueneerde.scalecommerce.cloud/de-de):
[Discovery]   ✓ Kreditkarte → credit_card
[Discovery]   ✓ PayPal → paypal
[Discovery]   ✓ Rechnung → invoice
[Discovery]   ✓ Klarna → klarna
[Discovery]
[Discovery] CH (https://grueneerde.scalecommerce.cloud/de-ch):
[Discovery]   ✓ Kreditkarte → credit_card
[Discovery]   ✓ Vorkasse → prepayment
[Discovery]
[Discovery] Erstelle Backup: config/config.yaml.backup
[Discovery] Aktualisiere config/config.yaml...
[Discovery] ✓ Erfolgreich gespeichert
```

## Integration mit Massentests

**Vorher** (hardcodiert):
```python
payment_methods = ["invoice", "credit_card", "paypal"]
```

**Nachher** (datengetrieben):
```python
# Wähle Zahlungsarten basierend auf Land
country = "AT"  # oder aus Config
payment_methods = config.payment_methods[country]
# ["Kreditkarte", "Vorkasse", "Rechnung"]

# Tests verwenden Aliases
for method in ["invoice", "credit_card", "prepayment"]:
    await checkout_page.select_payment_method(method)
    # Wird automatisch zu "Rechnung", "Kreditkarte", "Vorkasse" übersetzt
```

## Vorteile

1. **Datengetrieben**: Keine hardcodierten Zahlungsarten mehr
2. **Länderspezifisch**: Testet nur verfügbare Zahlungsarten pro Land
3. **Wartbar**: Bei Shop-Änderungen nur Discovery neu laufen lassen
4. **Flexibel**: Funktioniert für staging und production
5. **Lesbar**: Tests verwenden englische Aliases, Config hat deutsche Labels
6. **Sicher**: Backup wird automatisch erstellt

## Nächste Schritte

1. Discovery-Test implementieren (`test_payment_discovery.py`)
2. Config-Update-Funktion implementieren
3. Alias-Generierung implementieren
4. CheckoutPage anpassen (`select_payment_method`)
5. Config-Model erweitern
6. Discovery auf staging ausführen
7. Massentests anpassen (länderspezifische Zahlungsarten)
8. Dokumentation aktualisieren

## Offene Fragen

Keine - Design vollständig validiert.
