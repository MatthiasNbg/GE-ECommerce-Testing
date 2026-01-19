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


class PerformanceTestDistribution(BaseModel):
    """Verteilung der Bestellungen im Performance-Test."""
    guest_post: int = 60
    guest_spedition: int = 30
    registered_post: int = 30
    registered_spedition: int = 15
    multi_product: int = 15


class PerformanceTestConfig(BaseModel):
    """Performance-Test Konfiguration (150 Bestellungen)."""
    target_orders: int = 150
    parallel_workers: int = 15
    success_rate_threshold: float = 0.95
    max_duration_minutes: int = 15
    distribution: PerformanceTestDistribution = Field(default_factory=PerformanceTestDistribution)


class TestCustomer(BaseModel):
    """Konfiguration für einen Testkunden."""
    email: str
    password: str = ""  # Direktes Passwort
    password_env: str = ""  # Oder aus Umgebungsvariable
    name: str = ""
    customer_type: str = "private"
    country: str = "AT"
    customer_id: str = ""  # Shopware Kunden-ID


class CityZip(BaseModel):
    """Stadt mit PLZ."""
    city: str
    zip: str


class GuestAddressPool(BaseModel):
    """Pool für Gast-Adressen."""
    countries: list[str] = Field(default_factory=lambda: ["AT", "DE", "CH"])
    cities: dict[str, list[CityZip]] = Field(default_factory=dict)


class TestCustomersConfig(BaseModel):
    """Testkunden-Konfiguration."""
    registered: list[TestCustomer] = Field(default_factory=list)
    guest_address_pool: GuestAddressPool = Field(default_factory=GuestAddressPool)


class TestProduct(BaseModel):
    """Produkt mit Metadaten."""
    id: str
    name: str = ""
    min_stock: int = 100
    category: str = ""


class TestProductsConfig(BaseModel):
    """Produkte nach Versandart."""
    default: list[str] = Field(default_factory=list)
    post_shipping: list[TestProduct] = Field(default_factory=list)
    spedition_shipping: list[TestProduct] = Field(default_factory=list)
    mixed_ratio: dict[str, int] = Field(default_factory=lambda: {"post_percent": 70, "spedition_percent": 30})


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

    # Performance-Test (150 Bestellungen)
    performance_test: PerformanceTestConfig = Field(default_factory=PerformanceTestConfig)

    # Testkunden
    test_customers: TestCustomersConfig = Field(default_factory=TestCustomersConfig)

    # Testdaten - Legacy (einfache Liste für Abwärtskompatibilität)
    test_products: TestProductsConfig | list[str] = Field(default_factory=lambda: ["SW-10001"])
    test_search_term: str = "Bett"

    # Zahlungsarten (länderspezifisch)
    country_paths: dict[str, str] = Field(default_factory=lambda: {
        "AT": "/",
        "DE": "/de-de",
        "CH": "/de-ch"
    })
    payment_methods: dict[str, list[str]] = Field(default_factory=dict)
    payment_method_aliases: dict[str, str] = Field(default_factory=dict)

    def get_post_products(self) -> list[str]:
        """Gibt Produkt-IDs für Postversand zurück."""
        if isinstance(self.test_products, TestProductsConfig):
            return [p.id for p in self.test_products.post_shipping if not p.id.startswith("TBD")]
        return self.test_products if isinstance(self.test_products, list) else []

    def get_spedition_products(self) -> list[str]:
        """Gibt Produkt-IDs für Speditionsversand zurück."""
        if isinstance(self.test_products, TestProductsConfig):
            return [p.id for p in self.test_products.spedition_shipping if not p.id.startswith("TBD")]
        return []

    def get_all_products(self) -> list[str]:
        """Gibt alle konfigurierten Produkt-IDs zurück."""
        if isinstance(self.test_products, TestProductsConfig):
            return self.test_products.default or (self.get_post_products() + self.get_spedition_products())
        return self.test_products if isinstance(self.test_products, list) else []

    def get_registered_customer(self, index: int = 0) -> TestCustomer | None:
        """Gibt einen registrierten Testkunden zurück."""
        customers = self.test_customers.registered
        if customers and index < len(customers):
            return customers[index]
        return None

    def get_customer_password(self, customer: TestCustomer) -> str:
        """Lädt das Passwort eines Kunden (direkt oder aus Umgebungsvariable)."""
        # Direktes Passwort hat Vorrang
        if customer.password:
            return customer.password
        # Fallback auf Umgebungsvariable
        if customer.password_env:
            return os.environ.get(customer.password_env, "")
        return ""

    def get_customer_by_country(self, country: str) -> TestCustomer | None:
        """Gibt einen Testkunden nach Land zurück."""
        for customer in self.test_customers.registered:
            if customer.country == country:
                return customer
        return None

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
