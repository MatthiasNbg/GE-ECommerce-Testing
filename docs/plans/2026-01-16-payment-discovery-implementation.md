# Payment Discovery Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Automatische Ermittlung länderspezifischer Zahlungsarten (DE/AT/CH) mit Discovery-Test

**Architecture:** Discovery-Test navigiert zu länderspezifischen Shop-URLs, extrahiert Zahlungsarten-Labels aus dem DOM, generiert englische Aliases und aktualisiert config.yaml. CheckoutPage verwendet Aliases für flexible Label-basierte Selektion.

**Tech Stack:** Python 3.11, Playwright (async), pytest, PyYAML, Pydantic

---

## Task 1: Config-Model erweitern

**Files:**
- Modify: `playwright_tests/config.py:44-93`

**Step 1: Test für erweiterte Config-Felder schreiben**

Create: `playwright_tests/tests/test_config.py`

```python
"""Tests für Konfigurationsmanagement."""
import pytest
from playwright_tests.config import TestConfig


def test_config_has_payment_method_aliases():
    """Config unterstützt payment_method_aliases Dict."""
    config = TestConfig.load()
    assert hasattr(config, "payment_method_aliases")
    assert isinstance(config.payment_method_aliases, dict)


def test_config_has_payment_methods():
    """Config unterstützt payment_methods Dict mit Länder-Keys."""
    config = TestConfig.load()
    assert hasattr(config, "payment_methods")
    assert isinstance(config.payment_methods, dict)


def test_config_has_country_paths():
    """Config hat Standard country_paths für AT/DE/CH."""
    config = TestConfig.load()
    assert hasattr(config, "country_paths")
    assert config.country_paths["AT"] == "/"
    assert config.country_paths["DE"] == "/de-de"
    assert config.country_paths["CH"] == "/de-ch"
```

**Step 2: Test ausführen (erwartet: FAIL)**

```bash
cd .worktrees/feature/payment-discovery
python -m pytest playwright_tests/tests/test_config.py -v
```

Erwartete Ausgabe: `FAILED` - AttributeError: 'TestConfig' object has no attribute 'payment_method_aliases'

**Step 3: Config-Model erweitern**

Modify: `playwright_tests/config.py`

Füge nach Zeile 82 hinzu:

```python
    # Zahlungsarten (länderspezifisch)
    country_paths: dict[str, str] = Field(default_factory=lambda: {
        "AT": "/",
        "DE": "/de-de",
        "CH": "/de-ch"
    })
    payment_methods: dict[str, list[str]] = Field(default_factory=dict)
    payment_method_aliases: dict[str, str] = Field(default_factory=dict)
```

**Step 4: Test ausführen (erwartet: PASS)**

```bash
python -m pytest playwright_tests/tests/test_config.py -v
```

Erwartete Ausgabe: `3 passed`

**Step 5: Commit**

```bash
git add playwright_tests/config.py playwright_tests/tests/test_config.py
git commit -m "feat: add payment method config fields

Add support for country-specific payment methods:
- country_paths: URL paths for AT/DE/CH
- payment_methods: discovered methods per country
- payment_method_aliases: English aliases for German labels

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 2: Alias-Generierung implementieren

**Files:**
- Create: `playwright_tests/utils/__init__.py`
- Create: `playwright_tests/utils/payment_discovery.py`

**Step 1: Test für Alias-Generierung schreiben**

Create: `playwright_tests/tests/test_payment_discovery_utils.py`

```python
"""Tests für Payment Discovery Utilities."""
import pytest
from playwright_tests.utils.payment_discovery import generate_aliases


def test_generate_aliases_known_mappings():
    """Bekannte deutsche Labels werden zu englischen Aliases."""
    discovered = {
        "AT": ["Rechnung", "Kreditkarte", "Vorkasse"]
    }

    aliases = generate_aliases(discovered)

    assert aliases["invoice"] == "Rechnung"
    assert aliases["credit_card"] == "Kreditkarte"
    assert aliases["prepayment"] == "Vorkasse"


def test_generate_aliases_handles_duplicates():
    """Labels aus mehreren Ländern werden dedupliziert."""
    discovered = {
        "AT": ["Rechnung", "Kreditkarte"],
        "DE": ["Rechnung", "PayPal"]
    }

    aliases = generate_aliases(discovered)

    # "Rechnung" sollte nur einmal vorkommen
    assert aliases["invoice"] == "Rechnung"
    assert len([v for v in aliases.values() if v == "Rechnung"]) == 1


def test_generate_aliases_unknown_labels():
    """Unbekannte Labels bekommen generischen Alias."""
    discovered = {
        "AT": ["Sofortüberweisung"]
    }

    aliases = generate_aliases(discovered)

    # Generischer Alias: lowercase, keine Umlaute/Sonderzeichen
    assert aliases["sofortuberweisung"] == "Sofortüberweisung"


def test_generate_aliases_empty_input():
    """Leere discovered_methods liefern leeres Dict."""
    discovered = {}
    aliases = generate_aliases(discovered)
    assert aliases == {}
```

**Step 2: Test ausführen (erwartet: FAIL)**

```bash
python -m pytest playwright_tests/tests/test_payment_discovery_utils.py -v
```

Erwartete Ausgabe: `FAILED` - ModuleNotFoundError: No module named 'playwright_tests.utils'

**Step 3: Alias-Generierung implementieren**

Create: `playwright_tests/utils/__init__.py` (leer)

Create: `playwright_tests/utils/payment_discovery.py`

```python
"""Utilities für automatische Zahlungsarten-Ermittlung."""


def generate_aliases(discovered_methods: dict[str, list[str]]) -> dict[str, str]:
    """
    Generiert englische Aliases für deutsche Zahlungsarten-Labels.

    Args:
        discovered_methods: Dict[country_code, List[label]]

    Returns:
        Dict[alias, label] - Mapping von englischen Aliases zu deutschen Labels

    Examples:
        >>> generate_aliases({"AT": ["Rechnung", "Kreditkarte"]})
        {'invoice': 'Rechnung', 'credit_card': 'Kreditkarte'}
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

    # Sammle alle einzigartigen Labels aus allen Ländern
    for labels in discovered_methods.values():
        all_labels.update(labels)

    # Erstelle Aliases
    for label in all_labels:
        if label in known_mappings:
            alias = known_mappings[label]
        else:
            # Generischer Alias: lowercase, Umlaute ersetzen
            alias = (
                label.lower()
                .replace("ä", "ae")
                .replace("ö", "oe")
                .replace("ü", "ue")
                .replace("ß", "ss")
                .replace(" ", "_")
            )

        aliases[alias] = label

    return aliases
```

**Step 4: Test ausführen (erwartet: PASS)**

```bash
python -m pytest playwright_tests/tests/test_payment_discovery_utils.py -v
```

Erwartete Ausgabe: `4 passed`

**Step 5: Commit**

```bash
git add playwright_tests/utils/ playwright_tests/tests/test_payment_discovery_utils.py
git commit -m "feat: implement payment method alias generation

Generate English aliases for German payment method labels:
- Known mappings for common methods (invoice, credit_card, etc.)
- Generic fallback for unknown labels
- Deduplication across countries

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 3: Config-Update-Funktion implementieren

**Files:**
- Modify: `playwright_tests/utils/payment_discovery.py`

**Step 1: Test für Config-Update schreiben**

Modify: `playwright_tests/tests/test_payment_discovery_utils.py`

Füge am Ende hinzu:

```python
from pathlib import Path
import yaml
import tempfile
import shutil
from playwright_tests.utils.payment_discovery import update_config_with_payment_methods


def test_update_config_adds_payment_methods():
    """Config wird mit discovered payment methods aktualisiert."""
    # Temporäres Config-Verzeichnis
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / "config"
        config_dir.mkdir()
        config_path = config_dir / "config.yaml"

        # Minimale Config erstellen
        initial_config = {
            "profiles": {
                "staging": {
                    "base_url": "https://example.com"
                }
            }
        }
        with open(config_path, "w") as f:
            yaml.dump(initial_config, f)

        # Update ausführen
        discovered = {
            "AT": ["Rechnung", "Kreditkarte"],
            "DE": ["PayPal", "Rechnung"]
        }
        update_config_with_payment_methods("staging", discovered, config_path)

        # Config neu laden
        with open(config_path) as f:
            updated = yaml.safe_load(f)

        # Validierung
        assert "payment_methods" in updated["profiles"]["staging"]
        assert updated["profiles"]["staging"]["payment_methods"]["AT"] == ["Rechnung", "Kreditkarte"]
        assert updated["profiles"]["staging"]["payment_methods"]["DE"] == ["PayPal", "Rechnung"]


def test_update_config_adds_aliases():
    """Config wird mit generierten Aliases aktualisiert."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / "config"
        config_dir.mkdir()
        config_path = config_dir / "config.yaml"

        initial_config = {
            "profiles": {
                "staging": {
                    "base_url": "https://example.com"
                }
            }
        }
        with open(config_path, "w") as f:
            yaml.dump(initial_config, f)

        discovered = {
            "AT": ["Rechnung"]
        }
        update_config_with_payment_methods("staging", discovered, config_path)

        with open(config_path) as f:
            updated = yaml.safe_load(f)

        assert "payment_method_aliases" in updated
        assert updated["payment_method_aliases"]["invoice"] == "Rechnung"


def test_update_config_creates_backup():
    """Backup wird vor Update erstellt."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / "config"
        config_dir.mkdir()
        config_path = config_dir / "config.yaml"
        backup_path = config_dir / "config.yaml.backup"

        initial_config = {"profiles": {"staging": {"base_url": "https://example.com"}}}
        with open(config_path, "w") as f:
            yaml.dump(initial_config, f)

        discovered = {"AT": ["Rechnung"]}
        update_config_with_payment_methods("staging", discovered, config_path)

        assert backup_path.exists()


def test_update_config_adds_country_paths():
    """Country paths werden hinzugefügt falls nicht vorhanden."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir) / "config"
        config_dir.mkdir()
        config_path = config_dir / "config.yaml"

        initial_config = {
            "profiles": {
                "staging": {
                    "base_url": "https://example.com"
                }
            }
        }
        with open(config_path, "w") as f:
            yaml.dump(initial_config, f)

        discovered = {"AT": ["Rechnung"]}
        update_config_with_payment_methods("staging", discovered, config_path)

        with open(config_path) as f:
            updated = yaml.safe_load(f)

        assert "country_paths" in updated["profiles"]["staging"]
        assert updated["profiles"]["staging"]["country_paths"]["AT"] == "/"
        assert updated["profiles"]["staging"]["country_paths"]["DE"] == "/de-de"
        assert updated["profiles"]["staging"]["country_paths"]["CH"] == "/de-ch"
```

**Step 2: Test ausführen (erwartet: FAIL)**

```bash
python -m pytest playwright_tests/tests/test_payment_discovery_utils.py::test_update_config_adds_payment_methods -v
```

Erwartete Ausgabe: `FAILED` - ImportError oder Function not found

**Step 3: Config-Update implementieren**

Modify: `playwright_tests/utils/payment_discovery.py`

Füge am Ende hinzu:

```python
from pathlib import Path
import yaml
import shutil


def update_config_with_payment_methods(
    profile_name: str,
    discovered_methods: dict[str, list[str]],
    config_path: Path | None = None,
) -> None:
    """
    Aktualisiert config.yaml mit ermittelten Zahlungsarten.

    Args:
        profile_name: Name des Profils (staging, production)
        discovered_methods: Dict[country_code, List[label]]
        config_path: Pfad zur config.yaml (optional, default: config/config.yaml)

    Raises:
        FileNotFoundError: Wenn config.yaml nicht existiert
        KeyError: Wenn Profil nicht in Config existiert
    """
    # Standard-Pfad wenn nicht angegeben
    if config_path is None:
        # Projekt-Root finden (zwei Ebenen über diesem File)
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config" / "config.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"Config nicht gefunden: {config_path}")

    # Backup erstellen
    backup_path = config_path.with_suffix(".yaml.backup")
    shutil.copy2(config_path, backup_path)
    print(f"[Discovery] Backup erstellt: {backup_path}")

    # Config laden
    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Validierung
    if "profiles" not in config or profile_name not in config["profiles"]:
        raise KeyError(f"Profil '{profile_name}' nicht in Config gefunden")

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

    # Zurückschreiben mit UTF-8 encoding
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, sort_keys=False)

    print(f"[Discovery] ✓ Config aktualisiert: {config_path}")
```

**Step 4: Test ausführen (erwartet: PASS)**

```bash
python -m pytest playwright_tests/tests/test_payment_discovery_utils.py -v
```

Erwartete Ausgabe: `8 passed`

**Step 5: Commit**

```bash
git add playwright_tests/utils/payment_discovery.py playwright_tests/tests/test_payment_discovery_utils.py
git commit -m "feat: implement config update for payment methods

Update config.yaml with discovered payment methods:
- Creates backup before modification
- Adds payment_methods to profile
- Generates and merges aliases
- Adds country_paths if missing

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 4: Discovery-Test implementieren

**Files:**
- Create: `playwright_tests/tests/test_payment_discovery.py`

**Step 1: Discovery-Test Grundgerüst schreiben**

Create: `playwright_tests/tests/test_payment_discovery.py`

```python
"""
Payment Discovery Test - Ermittelt verfügbare Zahlungsarten.

Dieser Test navigiert zu den länderspezifischen Shop-URLs und
extrahiert die verfügbaren Zahlungsarten aus dem Checkout.
"""
import pytest
from playwright.async_api import Browser, Page

from playwright_tests.config import TestConfig
from playwright_tests.utils.payment_discovery import update_config_with_payment_methods


async def add_test_product_to_cart(page: Page, base_url: str, product_id: str) -> None:
    """
    Fügt ein Testprodukt zum Warenkorb hinzu.

    Args:
        page: Playwright Page
        base_url: Basis-URL des Shops (mit Länder-Pfad)
        product_id: Produkt-ID/Pfad (z.B. "p/produktname/ge-p-123")
    """
    await page.goto(f"{base_url}/{product_id}")
    await page.wait_for_load_state("domcontentloaded")

    # Cookie-Banner schließen falls vorhanden
    cookie_button = page.locator("css=.cookie-notice button, .cookie-consent button, #CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")
    if await cookie_button.count() > 0:
        await cookie_button.first.click()
        await page.wait_for_timeout(500)

    # "In den Warenkorb" Button
    add_to_cart = page.locator("css=.btn-buy, [data-add-to-cart]")
    if await add_to_cart.count() > 0:
        await add_to_cart.first.click()
        await page.wait_for_timeout(2000)  # AJAX abwarten


@pytest.mark.discovery
@pytest.mark.asyncio
async def test_discover_payment_methods(browser: Browser, config: TestConfig):
    """
    Ermittelt verfügbare Zahlungsarten für AT, DE, CH.

    Navigiert zu jedem länderspezifischen Shop, fügt ein Produkt
    zum Warenkorb hinzu, geht zum Checkout und extrahiert die
    Zahlungsarten-Labels.

    Aktualisiert anschließend die config.yaml mit den Ergebnissen.
    """
    print(f"\n[Discovery] Ermittle Zahlungsarten für {config.test_profile}...")

    # Länderspezifische Pfade
    countries = config.country_paths

    # Testprodukt aus Config
    test_product = config.test_products[0] if config.test_products else None
    if not test_product:
        pytest.fail("Kein Testprodukt in Config definiert")

    discovered = {}

    for country_code, path in countries.items():
        country_url = config.base_url.rstrip("/") + path
        print(f"\n[Discovery] {country_code} ({country_url}):")

        # Neuer Browser-Context für jedes Land
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="de-AT",
            # HTTP Basic Auth falls konfiguriert
            http_credentials={
                "username": config.htaccess_user,
                "password": config.htaccess_password
            } if config.htaccess_user else None
        )

        page = await context.new_page()

        try:
            # Produkt zum Warenkorb hinzufügen
            await add_test_product_to_cart(page, country_url, test_product)

            # Zum Checkout navigieren
            checkout_url = f"{country_url}/checkout/confirm"
            await page.goto(checkout_url)
            await page.wait_for_load_state("domcontentloaded")

            # Zahlungsarten extrahieren
            payment_labels = page.locator(".payment-method-label strong")
            count = await payment_labels.count()

            if count == 0:
                print(f"[Discovery]   ⚠ Keine Zahlungsarten gefunden")
                discovered[country_code] = []
            else:
                labels = []
                for i in range(count):
                    label = await payment_labels.nth(i).text_content()
                    label = label.strip()
                    labels.append(label)
                    print(f"[Discovery]   ✓ {label}")

                discovered[country_code] = labels

        except Exception as e:
            print(f"[Discovery]   ✗ Fehler: {e}")
            discovered[country_code] = []

        finally:
            await context.close()

    # Validierung: Mindestens ein Land muss Zahlungsarten haben
    total_methods = sum(len(methods) for methods in discovered.values())
    assert total_methods > 0, (
        "Keine Zahlungsarten gefunden. Mögliche Ursachen:\n"
        "- Falscher DOM-Selektor\n"
        "- Shop-Struktur geändert\n"
        "- Authentifizierung fehlgeschlagen"
    )

    # Config aktualisieren
    print(f"\n[Discovery] Aktualisiere config.yaml...")
    update_config_with_payment_methods(config.test_profile, discovered)
    print(f"[Discovery] ✓ Erfolgreich gespeichert\n")
```

**Step 2: Discovery-Marker registrieren**

Modify: `playwright_tests/conftest.py`

Füge nach Zeile 52 hinzu:

```python
    config.addinivalue_line("markers", "discovery: Discovery-Tests für automatische Ermittlung")
```

**Step 3: Test ausführen (manuell - kein automatischer Test)**

Dieser Test ist ein Discovery-Test und wird manuell ausgeführt.

```bash
python -m pytest playwright_tests/tests/test_payment_discovery.py -m discovery -v -s
```

Erwartete Ausgabe: Test läuft durch, ermittelt Zahlungsarten, aktualisiert config.yaml

**Step 4: Commit**

```bash
git add playwright_tests/tests/test_payment_discovery.py playwright_tests/conftest.py
git commit -m "feat: implement payment method discovery test

Add discovery test that:
- Iterates over country-specific shop URLs (AT/DE/CH)
- Adds test product to cart
- Navigates to checkout
- Extracts payment method labels from DOM
- Updates config.yaml with results

Marker: @pytest.mark.discovery

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 5: CheckoutPage anpassen

**Files:**
- Modify: `playwright_tests/pages/checkout_page.py:141-164`

**Step 1: Test für flexibles select_payment_method schreiben**

Create: `playwright_tests/tests/test_checkout_page_payment.py`

```python
"""Tests für CheckoutPage Zahlungsarten-Selektion."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from playwright_tests.pages.checkout_page import CheckoutPage


@pytest.mark.asyncio
async def test_select_payment_method_with_alias():
    """select_payment_method übersetzt Alias zu Label."""
    # Mock Page
    page = AsyncMock()
    page.locator = MagicMock()

    # Mock Locator
    payment_label_locator = AsyncMock()
    payment_label_locator.count = AsyncMock(return_value=1)

    radio_locator = AsyncMock()
    radio_locator.click = AsyncMock()

    payment_label_locator.locator = MagicMock(return_value=radio_locator)
    radio_locator.locator = MagicMock(return_value=radio_locator)

    page.locator.return_value = payment_label_locator

    # Mock Config mit Alias
    with patch('playwright_tests.pages.checkout_page.get_config') as mock_get_config:
        mock_config = MagicMock()
        mock_config.payment_method_aliases = {"invoice": "Rechnung"}
        mock_get_config.return_value = mock_config

        checkout = CheckoutPage(page, "https://example.com")
        await checkout.select_payment_method("invoice")

        # Sollte nach "Rechnung" suchen (übersetzter Alias)
        page.locator.assert_called_once()
        call_args = page.locator.call_args[0][0]
        assert "Rechnung" in call_args


@pytest.mark.asyncio
async def test_select_payment_method_with_direct_label():
    """select_payment_method funktioniert auch mit direktem Label."""
    page = AsyncMock()
    page.locator = MagicMock()

    payment_label_locator = AsyncMock()
    payment_label_locator.count = AsyncMock(return_value=1)

    radio_locator = AsyncMock()
    radio_locator.click = AsyncMock()

    payment_label_locator.locator = MagicMock(return_value=radio_locator)
    radio_locator.locator = MagicMock(return_value=radio_locator)

    page.locator.return_value = payment_label_locator

    with patch('playwright_tests.pages.checkout_page.get_config') as mock_get_config:
        mock_config = MagicMock()
        mock_config.payment_method_aliases = {}
        mock_get_config.return_value = mock_config

        checkout = CheckoutPage(page, "https://example.com")
        await checkout.select_payment_method("Rechnung")

        # Sollte direkt nach "Rechnung" suchen
        call_args = page.locator.call_args[0][0]
        assert "Rechnung" in call_args


@pytest.mark.asyncio
async def test_select_payment_method_not_found_raises_error():
    """select_payment_method wirft ValueError wenn Zahlungsart nicht gefunden."""
    page = AsyncMock()
    page.locator = MagicMock()

    payment_label_locator = AsyncMock()
    payment_label_locator.count = AsyncMock(return_value=0)
    page.locator.return_value = payment_label_locator

    with patch('playwright_tests.pages.checkout_page.get_config') as mock_get_config:
        mock_config = MagicMock()
        mock_config.payment_method_aliases = {}
        mock_get_config.return_value = mock_config

        checkout = CheckoutPage(page, "https://example.com")

        with pytest.raises(ValueError, match="nicht gefunden"):
            await checkout.select_payment_method("InvalidMethod")
```

**Step 2: Test ausführen (erwartet: FAIL)**

```bash
python -m pytest playwright_tests/tests/test_checkout_page_payment.py -v
```

Erwartete Ausgabe: `FAILED` - Test schlägt fehl weil CheckoutPage noch alte Implementierung hat

**Step 3: CheckoutPage select_payment_method anpassen**

Modify: `playwright_tests/pages/checkout_page.py`

Ersetze die Funktion `select_payment_method` (Zeilen 141-164) mit:

```python
    async def select_payment_method(self, method: str) -> None:
        """
        Wählt eine Zahlungsart aus.

        Unterstützt sowohl englische Aliases ("invoice") als auch
        deutsche Labels ("Rechnung"). Aliases werden automatisch
        aus der Config übersetzt.

        Args:
            method: Englischer Alias (z.B. "invoice") oder deutsches Label ("Rechnung")

        Raises:
            ValueError: Wenn Zahlungsart nicht gefunden wird
        """
        # Lade Config für Alias-Übersetzung
        from playwright_tests.config import get_config
        config = get_config()

        # Übersetze Alias zu Label (falls nötig)
        label = config.payment_method_aliases.get(method, method)

        # Suche nach Label im DOM
        payment_label = self.page.locator(f".payment-method-label:has-text('{label}')")

        if await payment_label.count() == 0:
            raise ValueError(
                f"Zahlungsart '{label}' nicht gefunden. "
                f"Verfügbare Zahlungsarten im DOM prüfen oder Discovery-Test ausführen."
            )

        # Klicke auf zugehöriges Radio-Button
        # Navigiere zum Parent-Container und finde Radio-Button
        radio_button = payment_label.locator("..").locator("input[type='radio']")
        await radio_button.click()
```

**Step 4: Test ausführen (erwartet: PASS)**

```bash
python -m pytest playwright_tests/tests/test_checkout_page_payment.py -v
```

Erwartete Ausgabe: `3 passed`

**Step 5: Commit**

```bash
git add playwright_tests/pages/checkout_page.py playwright_tests/tests/test_checkout_page_payment.py
git commit -m "feat: update CheckoutPage to use flexible payment selection

Update select_payment_method to:
- Accept both English aliases and German labels
- Translate aliases using config.payment_method_aliases
- Use DOM-based label search instead of hardcoded selectors
- Raise clear error if payment method not found

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 6: Discovery ausführen und validieren

**Files:**
- Modify: `config/config.yaml` (automatisch durch Discovery-Test)

**Step 1: Discovery-Test ausführen**

```bash
cd .worktrees/feature/payment-discovery
python -m pytest playwright_tests/tests/test_payment_discovery.py -m discovery -v -s
```

Erwartete Ausgabe:
```
[Discovery] Ermittle Zahlungsarten für staging...

[Discovery] AT (https://grueneerde.scalecommerce.cloud/):
[Discovery]   ✓ Kreditkarte
[Discovery]   ✓ Vorkasse
[Discovery]   ✓ Rechnung

[Discovery] DE (https://grueneerde.scalecommerce.cloud/de-de):
[Discovery]   ✓ Kreditkarte
[Discovery]   ✓ PayPal
[Discovery]   ✓ Rechnung
[Discovery]   ✓ Klarna

[Discovery] CH (https://grueneerde.scalecommerce.cloud/de-ch):
[Discovery]   ✓ Kreditkarte
[Discovery]   ✓ Vorkasse

[Discovery] Aktualisiere config.yaml...
[Discovery] Backup erstellt: config/config.yaml.backup
[Discovery] ✓ Config aktualisiert: config/config.yaml
[Discovery] ✓ Erfolgreich gespeichert

PASSED
```

**Step 2: Config-Änderungen validieren**

```bash
# Prüfe ob payment_methods hinzugefügt wurden
grep -A 10 "payment_methods:" config/config.yaml

# Prüfe ob aliases hinzugefügt wurden
grep -A 10 "payment_method_aliases:" config/config.yaml
```

Erwartete Ausgabe: YAML-Struktur mit payment_methods und payment_method_aliases

**Step 3: Commit der aktualisierten Config**

```bash
git add config/config.yaml
git commit -m "chore: update config with discovered payment methods

Add discovered payment methods for AT/DE/CH:
- AT: Kreditkarte, Vorkasse, Rechnung
- DE: Kreditkarte, PayPal, Rechnung, Klarna
- CH: Kreditkarte, Vorkasse

Add payment method aliases for flexible selection.

Generated by: pytest -m discovery

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 7: Massentests anpassen (optional)

**Files:**
- Modify: `playwright_tests/tests/test_checkout_mass.py:304-333`

**Step 1: Massentest für länderspezifische Zahlungsarten anpassen**

Modify: `playwright_tests/tests/test_checkout_mass.py`

Ersetze `test_mass_orders_payment_matrix` (Zeilen 291-333) mit:

```python
@pytest.mark.massentest
@pytest.mark.asyncio
async def test_mass_orders_payment_matrix(
    browser: Browser,
    shop_config: dict,
    parallel: int,
    products: list[str],
    config: TestConfig,
):
    """
    Testet Massenbestellungen mit länderspezifischen Zahlungsarten.

    Verwendet die per Discovery ermittelten Zahlungsarten aus config.yaml.
    Führt für jede verfügbare Zahlungsart in AT 10 Bestellungen durch.
    """
    # Verwende österreichische Zahlungsarten (Standard-Land)
    country = "AT"

    if not config.payment_methods or country not in config.payment_methods:
        pytest.skip(
            f"Keine Zahlungsarten für {country} in Config gefunden. "
            "Discovery-Test ausführen: pytest -m discovery"
        )

    payment_labels = config.payment_methods[country]

    if not payment_labels:
        pytest.skip(f"Keine Zahlungsarten für {country} ermittelt")

    orders_per_method = 10
    all_results: dict[str, MassTestResult] = {}

    print(f"\n[Payment Matrix] Teste {len(payment_labels)} Zahlungsarten für {country}")

    for payment_label in payment_labels:
        # Finde Alias für dieses Label (falls vorhanden)
        alias = None
        for a, l in config.payment_method_aliases.items():
            if l == payment_label:
                alias = a
                break

        # Verwende Alias falls verfügbar, sonst Label direkt
        payment_method = alias if alias else payment_label

        runner = MassOrderRunner(
            browser=browser,
            base_url=shop_config["base_url"],
            parallel_workers=parallel,
            payment_methods=[payment_method],
        )

        result = await runner.run_mass_orders(
            num_orders=orders_per_method,
            product_ids=products,
        )

        all_results[payment_label] = result

        print(f"\n{payment_label}: "
              f"{result.successful_orders}/{result.total_orders} "
              f"({result.success_rate:.1%})")

    # Alle Zahlungsarten müssen >= 90% Erfolgsrate haben
    for method, result in all_results.items():
        assert result.success_rate >= 0.90, (
            f"Zahlungsart {method}: Erfolgsrate {result.success_rate:.1%} "
            f"unter Schwellwert 90%"
        )
```

**Step 2: Test ausführen (validierung)**

```bash
# Smoke-Test um sicherzustellen dass Änderungen keine Syntax-Fehler haben
python -m pytest playwright_tests/tests/test_checkout_mass.py::test_mass_orders_payment_matrix --collect-only
```

Erwartete Ausgabe: `1 test collected` (kein Fehler)

**Step 3: Commit**

```bash
git add playwright_tests/tests/test_checkout_mass.py
git commit -m "refactor: use discovered payment methods in mass tests

Update payment matrix test to:
- Use country-specific payment methods from config
- Use aliases when available
- Skip if no payment methods discovered
- Clearer error messages

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 8: Dokumentation aktualisieren

**Files:**
- Modify: `README.md`

**Step 1: README mit Discovery-Test-Info erweitern**

Modify: `README.md`

Füge nach dem Abschnitt über Tests einen neuen Abschnitt hinzu:

```markdown
### Payment Discovery

Das Projekt unterstützt automatische Ermittlung länderspezifischer Zahlungsarten:

```bash
# Zahlungsarten für alle Länder ermitteln
pytest -m discovery

# Nur für bestimmtes Profil
pytest -m discovery --profile=production
```

Der Discovery-Test:
1. Navigiert zu AT/DE/CH Shop-URLs
2. Fügt Testprodukt zum Warenkorb hinzu
3. Geht zum Checkout
4. Extrahiert Zahlungsarten-Labels
5. Generiert englische Aliases
6. Aktualisiert `config/config.yaml`

Nach Discovery sind die ermittelten Zahlungsarten in `config.yaml` verfügbar:

```yaml
profiles:
  staging:
    payment_methods:
      AT: ["Kreditkarte", "Vorkasse", "Rechnung"]
      DE: ["Kreditkarte", "PayPal", "Rechnung"]
      CH: ["Kreditkarte", "Vorkasse"]

payment_method_aliases:
  invoice: "Rechnung"
  credit_card: "Kreditkarte"
  prepayment: "Vorkasse"
```

Tests verwenden automatisch die richtigen Zahlungsarten pro Land.
```

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add payment discovery documentation

Document payment discovery feature:
- How to run discovery test
- What it does
- Config structure
- Usage in tests

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 9: Finale Validierung

**Step 1: Alle Tests ausführen**

```bash
# Unit-Tests
python -m pytest playwright_tests/tests/test_config.py -v
python -m pytest playwright_tests/tests/test_payment_discovery_utils.py -v
python -m pytest playwright_tests/tests/test_checkout_page_payment.py -v

# Smoke-Test zur E2E-Validierung
python -m pytest playwright_tests/tests/test_smoke.py::test_homepage_loads -v
```

Erwartete Ausgabe: Alle Tests bestehen

**Step 2: Finale Prüfung der Config**

```bash
cat config/config.yaml | grep -A 20 "staging:"
```

Validiere dass:
- `country_paths` vorhanden
- `payment_methods` mit AT/DE/CH gefüllt
- Root-Level `payment_method_aliases` existiert

**Step 3: Branch-Status prüfen**

```bash
git log --oneline -10
git status
```

Erwartete Ausgabe: 9 Commits, working tree clean

---

## Fertig!

Nach Abschluss aller Tasks ist die Payment Discovery implementiert und einsatzbereit.

**Nächste Schritte (manuell):**
1. Discovery auf Production ausführen
2. Massentests mit echten Zahlungsarten testen
3. Bei Shop-Änderungen Discovery neu ausführen
