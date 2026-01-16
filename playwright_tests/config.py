"""
Konfigurationsmanagement für E2E Tests.

Lädt Einstellungen aus config.yaml und .env mit Profil-Unterstützung.
"""
import os
from pathlib import Path
from typing import Any, Optional

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class ViewportConfig(BaseModel):
    """Browser-Viewport Konfiguration."""
    width: int = 1920
    height: int = 1080


class ReportsConfig(BaseModel):
    """Pfade für Test-Reports."""
    html: str = "reports/html"
    traces: str = "reports/traces"
    screenshots: str = "reports/screenshots"


class MassTestConfig(BaseModel):
    """Massentest-Standardwerte."""
    default_orders: int = 100
    default_parallel: int = 5
    success_rate_threshold: float = 0.95


class ProfileConfig(BaseModel):
    """Konfiguration für ein einzelnes Profil."""
    base_url: str
    timeout: int = 30000
    parallel_workers: int = 5
    headless: bool = True
    slow_mo: int = 0


class TestConfig(BaseSettings):
    """
    Hauptkonfiguration für E2E Tests.

    Lädt Werte aus:
    1. config/config.yaml (Basis)
    2. Umgebungsvariablen (überschreiben YAML)
    3. .env Datei (für Secrets)
    """

    # Profil-Auswahl
    test_profile: str = Field(default="staging", alias="TEST_PROFILE")

    # Aus Profil geladen
    base_url: str = ""
    timeout: int = 30000
    parallel_workers: int = 5
    headless: bool = True
    slow_mo: int = 0

    # Browser
    browser: str = "chromium"
    locale: str = "de-AT"
    viewport: ViewportConfig = Field(default_factory=ViewportConfig)

    # Debugging
    trace_on_failure: bool = True
    screenshot_on_failure: bool = True
    video_on_failure: bool = False

    # Reports
    reports: ReportsConfig = Field(default_factory=ReportsConfig)

    # Massentests
    mass_test: MassTestConfig = Field(default_factory=MassTestConfig)

    # Testdaten
    test_products: list[str] = Field(default_factory=lambda: ["SW-10001"])
    test_search_term: str = "Bett"

    # Zahlungsarten (länderspezifisch)
    country_paths: dict[str, str] = Field(default_factory=lambda: {
        "AT": "/",
        "DE": "/de-de",
        "CH": "/de-ch"
    })
    payment_methods: dict[str, list[str]] = Field(default_factory=dict)
    payment_method_aliases: dict[str, str] = Field(default_factory=dict)

    # Secrets (aus .env)
    test_customer_email: str = Field(default="", alias="TEST_CUSTOMER_EMAIL")
    test_customer_password: str = Field(default="", alias="TEST_CUSTOMER_PASSWORD")
    shop_admin_user: str = Field(default="", alias="SHOP_ADMIN_USER")
    shop_admin_password: str = Field(default="", alias="SHOP_ADMIN_PASSWORD")

    # HTTP Basic Auth (.htaccess Schutz)
    htaccess_user: str = Field(default="", alias="HTACCESS_USER")
    htaccess_password: str = Field(default="", alias="HTACCESS_PASSWORD")

    class Config:
        env_file = "config/.env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "TestConfig":
        """
        Lädt die Konfiguration aus YAML und wendet das aktive Profil an.

        Args:
            config_path: Pfad zur config.yaml (optional)

        Returns:
            TestConfig mit angewendetem Profil
        """
        # Standard-Pfad
        if config_path is None:
            # Projekt-Root finden
            current = Path(__file__).parent.parent
            config_path = current / "config" / "config.yaml"

        # YAML laden
        yaml_config: dict[str, Any] = {}
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                yaml_config = yaml.safe_load(f) or {}

        # Profil ermitteln
        profile_name = os.environ.get(
            "TEST_PROFILE",
            yaml_config.get("default_profile", "staging")
        )

        # Profil-spezifische Werte extrahieren
        profiles = yaml_config.get("profiles", {})
        profile_config = profiles.get(profile_name, {})

        # Basis-Werte aus YAML (ohne Profile)
        base_values = {
            k: v for k, v in yaml_config.items()
            if k not in ["profiles", "default_profile"]
        }

        # Profil-Werte überschreiben Basis-Werte
        merged = {**base_values, **profile_config, "test_profile": profile_name}

        # Pydantic-Instanz erstellen
        return cls(**merged)


def get_config() -> TestConfig:
    """
    Gibt die aktive Testkonfiguration zurück.

    Cached für mehrfache Aufrufe.
    """
    if not hasattr(get_config, "_instance"):
        get_config._instance = TestConfig.load()
    return get_config._instance
