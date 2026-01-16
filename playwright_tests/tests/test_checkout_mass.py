"""
Massentests für den Shopware Checkout.

Führt eine konfigurierbare Anzahl von Bestellungen parallel aus
und wertet die Ergebnisse statistisch aus.
"""
import asyncio
import random
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import pytest
from playwright.async_api import Browser, BrowserContext

from playwright_tests.pages.checkout_page import Address, CheckoutPage, CheckoutResult


@dataclass
class MassTestResult:
    """Aggregiertes Ergebnis eines Massentests."""
    total_orders: int = 0
    successful_orders: int = 0
    failed_orders: int = 0
    success_rate: float = 0.0
    
    avg_duration_seconds: float = 0.0
    min_duration_seconds: float = 0.0
    max_duration_seconds: float = 0.0
    
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    total_duration_seconds: float = 0.0
    
    order_results: list[CheckoutResult] = field(default_factory=list)
    errors: list[dict] = field(default_factory=list)
    
    def calculate_stats(self) -> None:
        """Berechnet Statistiken aus den Einzelergebnissen."""
        if not self.order_results:
            return
        
        self.total_orders = len(self.order_results)
        self.successful_orders = len([r for r in self.order_results if r.success])
        self.failed_orders = self.total_orders - self.successful_orders
        
        if self.total_orders > 0:
            self.success_rate = self.successful_orders / self.total_orders
        
        durations = [r.duration_seconds for r in self.order_results if r.success]
        if durations:
            self.avg_duration_seconds = sum(durations) / len(durations)
            self.min_duration_seconds = min(durations)
            self.max_duration_seconds = max(durations)
        
        self.errors = [
            {"order_num": i, "error": r.error_message}
            for i, r in enumerate(self.order_results)
            if not r.success
        ]


def generate_test_address(order_num: int) -> Address:
    """
    Generiert eine eindeutige Testadresse für jede Bestellung.
    
    Args:
        order_num: Laufende Nummer der Bestellung für Eindeutigkeit
    """
    timestamp = int(time.time() * 1000)
    
    return Address(
        salutation=random.choice(["mr", "mrs"]),
        first_name="Test",
        last_name=f"Bestellung-{order_num}",
        street=f"Teststraße {order_num}",
        zip_code=random.choice(["4020", "1010", "5020", "6020", "8010"]),
        city=random.choice(["Linz", "Wien", "Salzburg", "Innsbruck", "Graz"]),
        country="AT",
        email=f"test-{timestamp}-{order_num}@gruene-erde-test.com",
    )


class MassOrderRunner:
    """
    Führt Massentests für Bestellungen durch.
    
    Verwaltet parallele Browser-Kontexte und sammelt Ergebnisse.
    """
    
    def __init__(
        self,
        browser: Browser,
        base_url: str,
        parallel_workers: int = 5,
        payment_methods: Optional[list[str]] = None,
    ):
        self.browser = browser
        self.base_url = base_url
        self.parallel_workers = parallel_workers
        self.payment_methods = payment_methods or ["invoice"]
        
        self.semaphore = asyncio.Semaphore(parallel_workers)
        self.results: list[CheckoutResult] = []
        self.results_lock = asyncio.Lock()
    
    async def _add_product_to_cart(self, context: BrowserContext, product_id: str) -> None:
        """
        Fügt ein Produkt zum Warenkorb hinzu.
        
        Args:
            context: Browser-Kontext
            product_id: Shopware Produkt-ID oder -nummer
        """
        page = await context.new_page()
        
        try:
            # Zur Produktseite navigieren
            await page.goto(f"{self.base_url}/detail/{product_id}")
            await page.wait_for_load_state("networkidle")
            
            # Zum Warenkorb hinzufügen
            add_to_cart = page.locator("css=.btn-buy, [data-add-to-cart]")
            await add_to_cart.click()
            
            # Warten bis Warenkorb aktualisiert
            await page.wait_for_timeout(1000)  # Mini-Wartezeit für AJAX
            
        finally:
            await page.close()
    
    async def _run_single_order(
        self,
        order_num: int,
        product_id: str,
    ) -> CheckoutResult:
        """
        Führt eine einzelne Bestellung durch.
        
        Args:
            order_num: Laufende Nummer für Logging und Testdaten
            product_id: Zu bestellendes Produkt
            
        Returns:
            CheckoutResult mit Erfolg/Misserfolg
        """
        async with self.semaphore:
            context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080}
            )
            
            try:
                # Produkt zum Warenkorb hinzufügen
                await self._add_product_to_cart(context, product_id)
                
                # Neue Seite für Checkout
                page = await context.new_page()
                checkout = CheckoutPage(page, self.base_url)
                
                # Zum Checkout navigieren
                await checkout.goto_checkout()
                
                # Testadresse generieren
                address = generate_test_address(order_num)
                
                # Zahlungsart wählen
                payment_method = random.choice(self.payment_methods)
                
                # Checkout durchführen
                result = await checkout.execute_guest_checkout(
                    address=address,
                    payment_method=payment_method
                )
                
                return result
                
            except Exception as e:
                return CheckoutResult(
                    success=False,
                    error_message=f"Unerwarteter Fehler: {str(e)}"
                )
                
            finally:
                await context.close()
    
    async def run_mass_orders(
        self,
        num_orders: int,
        product_ids: list[str],
    ) -> MassTestResult:
        """
        Führt mehrere Bestellungen parallel aus.
        
        Args:
            num_orders: Anzahl der Bestellungen
            product_ids: Liste der zu bestellenden Produkte (zufällige Auswahl)
            
        Returns:
            MassTestResult mit aggregierten Statistiken
        """
        result = MassTestResult(start_time=datetime.now())
        
        # Alle Orders als Tasks erstellen
        tasks = [
            self._run_single_order(
                order_num=i,
                product_id=random.choice(product_ids),
            )
            for i in range(num_orders)
        ]
        
        # Parallel ausführen
        order_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Ergebnisse verarbeiten
        for i, res in enumerate(order_results):
            if isinstance(res, Exception):
                result.order_results.append(CheckoutResult(
                    success=False,
                    error_message=str(res)
                ))
            else:
                result.order_results.append(res)
        
        result.end_time = datetime.now()
        result.total_duration_seconds = (result.end_time - result.start_time).total_seconds()
        result.calculate_stats()
        
        return result


# =============================================================================
# Pytest Tests
# =============================================================================

@pytest.mark.massentest
@pytest.mark.asyncio
async def test_mass_orders_basic(
    browser: Browser,
    shop_config: dict,
    mass_orders: int,
    parallel: int,
    products: list[str],
):
    """
    Basis-Massentest: Führt n Bestellungen parallel aus.
    
    Erfolgskriterium: Mindestens 95% Erfolgsrate.
    """
    runner = MassOrderRunner(
        browser=browser,
        base_url=shop_config["base_url"],
        parallel_workers=parallel,
    )
    
    result = await runner.run_mass_orders(
        num_orders=mass_orders,
        product_ids=products,
    )
    
    # Reporting
    print(f"\n{'='*60}")
    print(f"MASSENTEST ERGEBNIS")
    print(f"{'='*60}")
    print(f"Bestellungen:    {result.total_orders}")
    print(f"Erfolgreich:     {result.successful_orders}")
    print(f"Fehlgeschlagen:  {result.failed_orders}")
    print(f"Erfolgsrate:     {result.success_rate:.1%}")
    print(f"{'='*60}")
    print(f"Dauer gesamt:    {result.total_duration_seconds:.1f}s")
    print(f"Ø pro Bestellung: {result.avg_duration_seconds:.1f}s")
    print(f"Min:             {result.min_duration_seconds:.1f}s")
    print(f"Max:             {result.max_duration_seconds:.1f}s")
    print(f"{'='*60}")
    
    if result.errors:
        print(f"\nFEHLER ({len(result.errors)}):")
        for err in result.errors[:10]:  # Max 10 Fehler anzeigen
            print(f"  Order {err['order_num']}: {err['error']}")
        if len(result.errors) > 10:
            print(f"  ... und {len(result.errors) - 10} weitere")
    
    # Assertion
    assert result.success_rate >= 0.95, (
        f"Erfolgsrate {result.success_rate:.1%} unter Schwellwert 95%. "
        f"Fehlgeschlagen: {result.failed_orders}/{result.total_orders}"
    )


@pytest.mark.massentest
@pytest.mark.asyncio
async def test_mass_orders_payment_matrix(
    browser: Browser,
    shop_config: dict,
    parallel: int,
    products: list[str],
):
    """
    Testet Massenbestellungen mit verschiedenen Zahlungsarten.

    Verwendet die für das Land (Standard: AT) konfigurierten Zahlungsarten
    aus config.yaml und führt für jede 10 Bestellungen durch.

    Überspringt den Test, falls keine Zahlungsarten ermittelt wurden.
    """
    # Land aus Config (default: AT)
    country = shop_config.get("country", "AT")

    # Zahlungsarten für das Land abrufen
    payment_methods_config = shop_config.get("payment_methods", {})
    country_payment_methods = payment_methods_config.get(country, [])

    # Test überspringen falls keine Payment Methods
    if not country_payment_methods:
        pytest.skip(
            f"Keine Zahlungsarten für Land {country} konfiguriert. "
            f"Führe 'pytest -m discovery' aus, um sie zu ermitteln."
        )

    # Aliases für bessere Lesbarkeit
    aliases = shop_config.get("payment_method_aliases", {})

    orders_per_method = 10
    all_results: dict[str, MassTestResult] = {}

    for payment_method in country_payment_methods:
        # Alias für Logging verwenden falls verfügbar
        display_name = next(
            (alias for alias, label in aliases.items() if label == payment_method),
            payment_method
        )

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

        all_results[payment_method] = result

        print(f"\n{display_name.upper()}: "
              f"{result.successful_orders}/{result.total_orders} "
              f"({result.success_rate:.1%})")

    # Alle Zahlungsarten müssen >= 90% Erfolgsrate haben
    for method, result in all_results.items():
        display_name = next(
            (alias for alias, label in aliases.items() if label == method),
            method
        )
        assert result.success_rate >= 0.90, (
            f"Zahlungsart {display_name}: Erfolgsrate {result.success_rate:.1%} "
            f"unter Schwellwert 90%"
        )


@pytest.mark.massentest
@pytest.mark.slow
@pytest.mark.asyncio
async def test_mass_orders_stress(
    browser: Browser,
    shop_config: dict,
    products: list[str],
):
    """
    Stresstest: 200 Bestellungen mit hoher Parallelität.
    
    Dieser Test ist als "slow" markiert und läuft nur bei expliziter Anforderung.
    """
    runner = MassOrderRunner(
        browser=browser,
        base_url=shop_config["base_url"],
        parallel_workers=20,  # Hohe Parallelität
    )
    
    result = await runner.run_mass_orders(
        num_orders=200,
        product_ids=products,
    )
    
    print(f"\nSTRESSTEST: {result.successful_orders}/{result.total_orders} "
          f"({result.success_rate:.1%}) in {result.total_duration_seconds:.1f}s")
    
    # Etwas niedrigere Schwelle für Stresstest
    assert result.success_rate >= 0.90, (
        f"Stresstest: Erfolgsrate {result.success_rate:.1%} unter 90%"
    )
