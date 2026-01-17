"""
Performance-Test für Staging: 150 Bestellungen in kürzester Zeit.

Dieser Test erstellt 150 echte Bestellungen mit verschiedenen Szenarien:
- Gast-Checkout mit Postversand
- Gast-Checkout mit Speditionsversand
- Registrierte Kunden mit Postversand
- Registrierte Kunden mit Speditionsversand
- Multi-Produkt-Bestellungen
"""
import asyncio
import json
import random
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

import pytest
from playwright.async_api import Browser, BrowserContext

from playwright_tests.config import TestConfig, TestCustomer, get_config
from playwright_tests.pages.checkout_page import Address, CheckoutPage, CheckoutResult


class OrderType(Enum):
    """Bestellungstypen für den Performance-Test."""
    GUEST_POST = "guest_post"
    GUEST_SPEDITION = "guest_spedition"
    REGISTERED_POST = "registered_post"
    REGISTERED_SPEDITION = "registered_spedition"
    MULTI_PRODUCT = "multi_product"


@dataclass
class PerformanceOrderResult(CheckoutResult):
    """Erweitertes Ergebnis mit Performance-Metriken."""
    order_type: OrderType = OrderType.GUEST_POST
    product_ids: list[str] = field(default_factory=list)
    shipping_type: str = "post"
    customer_type: str = "guest"


@dataclass
class PerformanceTestResult:
    """Aggregiertes Ergebnis des Performance-Tests."""
    total_orders: int = 0
    successful_orders: int = 0
    failed_orders: int = 0
    success_rate: float = 0.0

    # Timing
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    total_duration_seconds: float = 0.0
    avg_duration_seconds: float = 0.0
    min_duration_seconds: float = 0.0
    max_duration_seconds: float = 0.0
    orders_per_minute: float = 0.0

    # Aufschlüsselung nach Typ
    results_by_type: dict[str, dict] = field(default_factory=dict)

    # Einzelergebnisse
    order_results: list[PerformanceOrderResult] = field(default_factory=list)
    errors: list[dict] = field(default_factory=list)

    def calculate_stats(self) -> None:
        """Berechnet alle Statistiken aus den Einzelergebnissen."""
        if not self.order_results:
            return

        self.total_orders = len(self.order_results)
        self.successful_orders = len([r for r in self.order_results if r.success])
        self.failed_orders = self.total_orders - self.successful_orders

        if self.total_orders > 0:
            self.success_rate = self.successful_orders / self.total_orders

        # Timing-Statistiken
        durations = [r.duration_seconds for r in self.order_results if r.success]
        if durations:
            self.avg_duration_seconds = sum(durations) / len(durations)
            self.min_duration_seconds = min(durations)
            self.max_duration_seconds = max(durations)

        # Orders pro Minute
        if self.total_duration_seconds > 0:
            self.orders_per_minute = (self.successful_orders / self.total_duration_seconds) * 60

        # Aufschlüsselung nach Typ
        for order_type in OrderType:
            type_results = [r for r in self.order_results if r.order_type == order_type]
            if type_results:
                successful = len([r for r in type_results if r.success])
                self.results_by_type[order_type.value] = {
                    "total": len(type_results),
                    "successful": successful,
                    "failed": len(type_results) - successful,
                    "success_rate": successful / len(type_results) if type_results else 0,
                }

        # Fehler sammeln
        self.errors = [
            {
                "order_num": i,
                "order_type": r.order_type.value,
                "error": r.error_message
            }
            for i, r in enumerate(self.order_results)
            if not r.success
        ]

    def to_dict(self) -> dict:
        """Konvertiert das Ergebnis in ein Dictionary für JSON-Export."""
        return {
            "summary": {
                "total_orders": self.total_orders,
                "successful_orders": self.successful_orders,
                "failed_orders": self.failed_orders,
                "success_rate": round(self.success_rate * 100, 2),
                "success_rate_percent": f"{self.success_rate:.1%}",
            },
            "timing": {
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": self.end_time.isoformat() if self.end_time else None,
                "total_duration_seconds": round(self.total_duration_seconds, 2),
                "avg_duration_seconds": round(self.avg_duration_seconds, 2),
                "min_duration_seconds": round(self.min_duration_seconds, 2),
                "max_duration_seconds": round(self.max_duration_seconds, 2),
                "orders_per_minute": round(self.orders_per_minute, 2),
            },
            "by_type": self.results_by_type,
            "errors": self.errors[:20],  # Max 20 Fehler im Report
            "error_count": len(self.errors),
        }


class PerformanceTestRunner:
    """
    Runner für den Performance-Test mit 150 Bestellungen.

    Unterstützt verschiedene Bestellungstypen und sammelt detaillierte Metriken.
    """

    def __init__(
        self,
        browser: Browser,
        config: TestConfig,
        parallel_workers: int = 15,
    ):
        self.browser = browser
        self.config = config
        self.base_url = config.base_url
        self.parallel_workers = parallel_workers

        self.semaphore = asyncio.Semaphore(parallel_workers)
        self.results: list[PerformanceOrderResult] = []
        self.results_lock = asyncio.Lock()

        # Produkte laden
        self.post_products = config.get_post_products()
        self.spedition_products = config.get_spedition_products()
        self.all_products = config.get_all_products()

        # Fallback falls keine Produkte konfiguriert
        if not self.post_products:
            self.post_products = self.all_products[:2] if len(self.all_products) >= 2 else self.all_products
        if not self.spedition_products:
            self.spedition_products = self.all_products[2:] if len(self.all_products) > 2 else self.all_products[-1:]

    def _generate_guest_address(self, order_num: int, country: str = "AT") -> Address:
        """Generiert eine Gast-Adresse aus dem konfigurierten Pool."""
        timestamp = int(time.time() * 1000)

        # Stadt aus Pool wählen
        cities_config = self.config.test_customers.guest_address_pool.cities
        cities = cities_config.get(country, [])

        if cities:
            city_data = random.choice(cities)
            city = city_data.city if hasattr(city_data, 'city') else city_data.get('city', 'Wien')
            zip_code = city_data.zip if hasattr(city_data, 'zip') else city_data.get('zip', '1010')
        else:
            # Fallback
            city = random.choice(["Wien", "Linz", "Salzburg", "Graz"])
            zip_code = random.choice(["1010", "4020", "5020", "8010"])

        return Address(
            salutation=random.choice(["mr", "mrs"]),
            first_name="Perf",
            last_name=f"Test-{order_num}",
            street=f"Teststraße {order_num}",
            zip_code=zip_code,
            city=city,
            country=country,
            email=f"perf-{timestamp}-{order_num}@gruene-erde-test.com",
        )

    async def _add_products_to_cart(
        self,
        context: BrowserContext,
        product_ids: list[str],
    ) -> None:
        """Fügt Produkte zum Warenkorb hinzu."""
        page = await context.new_page()

        try:
            for product_id in product_ids:
                # Zur Produktseite navigieren
                product_url = f"{self.base_url}/{product_id}" if not product_id.startswith("/") else f"{self.base_url}{product_id}"
                await page.goto(product_url)
                await page.wait_for_load_state("networkidle")

                # Zum Warenkorb hinzufügen
                add_to_cart = page.locator("css=.btn-buy, [data-add-to-cart], .product-detail-buy button")
                if await add_to_cart.count() > 0:
                    await add_to_cart.first.click()
                    await page.wait_for_timeout(1500)  # Warten auf AJAX
        finally:
            await page.close()

    async def _run_guest_order(
        self,
        order_num: int,
        product_ids: list[str],
        order_type: OrderType,
    ) -> PerformanceOrderResult:
        """Führt eine Gast-Bestellung durch."""
        async with self.semaphore:
            context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080}
            )

            start_time = time.time()

            try:
                # Produkte zum Warenkorb
                await self._add_products_to_cart(context, product_ids)

                # Checkout
                page = await context.new_page()
                checkout = CheckoutPage(page, self.base_url)
                await checkout.goto_checkout()

                # Adresse generieren
                address = self._generate_guest_address(order_num)

                # Zahlungsart wählen
                payment_methods = self.config.payment_methods.get("AT", ["Rechnung"])
                payment_method = random.choice(payment_methods) if payment_methods else "Rechnung"

                # Checkout durchführen
                result = await checkout.execute_guest_checkout(
                    address=address,
                    payment_method=payment_method
                )

                return PerformanceOrderResult(
                    success=result.success,
                    order_id=result.order_id,
                    order_number=result.order_number,
                    error_message=result.error_message,
                    duration_seconds=time.time() - start_time,
                    order_type=order_type,
                    product_ids=product_ids,
                    shipping_type="post" if order_type == OrderType.GUEST_POST else "spedition",
                    customer_type="guest",
                )

            except Exception as e:
                return PerformanceOrderResult(
                    success=False,
                    error_message=f"Fehler: {str(e)}",
                    duration_seconds=time.time() - start_time,
                    order_type=order_type,
                    product_ids=product_ids,
                    customer_type="guest",
                )
            finally:
                await context.close()

    async def _run_registered_order(
        self,
        order_num: int,
        customer: TestCustomer,
        product_ids: list[str],
        order_type: OrderType,
    ) -> PerformanceOrderResult:
        """Führt eine Bestellung mit registriertem Kunden durch."""
        async with self.semaphore:
            context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080}
            )

            start_time = time.time()

            try:
                # Login
                page = await context.new_page()
                await page.goto(f"{self.base_url}/account/login")
                await page.wait_for_load_state("networkidle")

                # Login-Formular ausfüllen
                await page.fill("css=#loginMail, input[name='email']", customer.email)
                password = self.config.get_customer_password(customer)
                await page.fill("css=#loginPassword, input[name='password']", password)
                await page.click("css=.login-submit button, button[type='submit']")
                await page.wait_for_load_state("networkidle")

                # Prüfen ob Login erfolgreich
                if "/account" not in page.url:
                    return PerformanceOrderResult(
                        success=False,
                        error_message=f"Login fehlgeschlagen für {customer.email}",
                        duration_seconds=time.time() - start_time,
                        order_type=order_type,
                        product_ids=product_ids,
                        customer_type="registered",
                    )

                await page.close()

                # Produkte zum Warenkorb
                await self._add_products_to_cart(context, product_ids)

                # Checkout
                page = await context.new_page()
                checkout = CheckoutPage(page, self.base_url)
                await checkout.goto_checkout()

                # Zahlungsart wählen
                payment_methods = self.config.payment_methods.get(customer.country, ["Rechnung"])
                payment_method = random.choice(payment_methods) if payment_methods else "Rechnung"

                await checkout.select_payment_method(payment_method)
                await checkout.accept_terms()
                await checkout.place_order()
                await checkout.wait_for_confirmation()

                order_number = await checkout.get_order_number()
                order_id = await checkout.get_order_id_from_url()

                return PerformanceOrderResult(
                    success=True,
                    order_id=order_id,
                    order_number=order_number,
                    duration_seconds=time.time() - start_time,
                    order_type=order_type,
                    product_ids=product_ids,
                    shipping_type="post" if order_type == OrderType.REGISTERED_POST else "spedition",
                    customer_type="registered",
                )

            except Exception as e:
                return PerformanceOrderResult(
                    success=False,
                    error_message=f"Fehler: {str(e)}",
                    duration_seconds=time.time() - start_time,
                    order_type=order_type,
                    product_ids=product_ids,
                    customer_type="registered",
                )
            finally:
                await context.close()

    def _create_order_tasks(self) -> list:
        """Erstellt die Order-Tasks basierend auf der konfigurierten Verteilung."""
        distribution = self.config.performance_test.distribution
        tasks = []
        order_num = 0

        # Registrierte Kunden laden
        registered_customers = self.config.test_customers.registered

        # 1. Gast + Postversand
        for _ in range(distribution.guest_post):
            product = random.choice(self.post_products) if self.post_products else self.all_products[0]
            tasks.append(self._run_guest_order(
                order_num=order_num,
                product_ids=[product],
                order_type=OrderType.GUEST_POST,
            ))
            order_num += 1

        # 2. Gast + Spedition
        for _ in range(distribution.guest_spedition):
            product = random.choice(self.spedition_products) if self.spedition_products else self.all_products[-1]
            tasks.append(self._run_guest_order(
                order_num=order_num,
                product_ids=[product],
                order_type=OrderType.GUEST_SPEDITION,
            ))
            order_num += 1

        # 3. Registriert + Postversand
        for i in range(distribution.registered_post):
            if registered_customers:
                customer = registered_customers[i % len(registered_customers)]
                product = random.choice(self.post_products) if self.post_products else self.all_products[0]
                tasks.append(self._run_registered_order(
                    order_num=order_num,
                    customer=customer,
                    product_ids=[product],
                    order_type=OrderType.REGISTERED_POST,
                ))
            else:
                # Fallback auf Gast wenn keine Kunden konfiguriert
                product = random.choice(self.post_products) if self.post_products else self.all_products[0]
                tasks.append(self._run_guest_order(
                    order_num=order_num,
                    product_ids=[product],
                    order_type=OrderType.GUEST_POST,
                ))
            order_num += 1

        # 4. Registriert + Spedition
        for i in range(distribution.registered_spedition):
            if registered_customers:
                customer = registered_customers[i % len(registered_customers)]
                product = random.choice(self.spedition_products) if self.spedition_products else self.all_products[-1]
                tasks.append(self._run_registered_order(
                    order_num=order_num,
                    customer=customer,
                    product_ids=[product],
                    order_type=OrderType.REGISTERED_SPEDITION,
                ))
            else:
                product = random.choice(self.spedition_products) if self.spedition_products else self.all_products[-1]
                tasks.append(self._run_guest_order(
                    order_num=order_num,
                    product_ids=[product],
                    order_type=OrderType.GUEST_SPEDITION,
                ))
            order_num += 1

        # 5. Multi-Produkt (1 Post + 1 Spedition)
        for _ in range(distribution.multi_product):
            products = []
            if self.post_products:
                products.append(random.choice(self.post_products))
            if self.spedition_products:
                products.append(random.choice(self.spedition_products))
            if not products:
                products = self.all_products[:2]

            tasks.append(self._run_guest_order(
                order_num=order_num,
                product_ids=products,
                order_type=OrderType.MULTI_PRODUCT,
            ))
            order_num += 1

        return tasks

    async def run(self) -> PerformanceTestResult:
        """Führt den kompletten Performance-Test durch."""
        result = PerformanceTestResult(start_time=datetime.now())

        # Tasks erstellen
        tasks = self._create_order_tasks()

        print(f"\n{'='*70}")
        print(f"PERFORMANCE-TEST GESTARTET")
        print(f"{'='*70}")
        print(f"Ziel:              {len(tasks)} Bestellungen")
        print(f"Parallelität:      {self.parallel_workers} Worker")
        print(f"Post-Produkte:     {len(self.post_products)}")
        print(f"Speditions-Produkte: {len(self.spedition_products)}")
        print(f"{'='*70}\n")

        # Alle Tasks parallel ausführen
        order_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Ergebnisse verarbeiten
        for i, res in enumerate(order_results):
            if isinstance(res, Exception):
                result.order_results.append(PerformanceOrderResult(
                    success=False,
                    error_message=str(res),
                    order_type=OrderType.GUEST_POST,
                ))
            else:
                result.order_results.append(res)

        result.end_time = datetime.now()
        result.total_duration_seconds = (result.end_time - result.start_time).total_seconds()
        result.calculate_stats()

        return result


def print_performance_report(result: PerformanceTestResult) -> None:
    """Gibt einen formatierten Report aus."""
    print(f"\n{'='*70}")
    print(f"PERFORMANCE-TEST ERGEBNIS")
    print(f"{'='*70}")
    print(f"Bestellungen gesamt:    {result.total_orders}")
    print(f"Erfolgreich:            {result.successful_orders}")
    print(f"Fehlgeschlagen:         {result.failed_orders}")
    print(f"Erfolgsrate:            {result.success_rate:.1%}")
    print(f"{'='*70}")
    print(f"Gesamtdauer:            {result.total_duration_seconds:.1f}s ({result.total_duration_seconds/60:.1f} min)")
    print(f"Ø pro Bestellung:       {result.avg_duration_seconds:.1f}s")
    print(f"Min:                    {result.min_duration_seconds:.1f}s")
    print(f"Max:                    {result.max_duration_seconds:.1f}s")
    print(f"Orders/Minute:          {result.orders_per_minute:.1f}")
    print(f"{'='*70}")

    if result.results_by_type:
        print(f"\nAUFSCHLÜSSELUNG NACH TYP:")
        print(f"{'-'*70}")
        for order_type, stats in result.results_by_type.items():
            print(f"  {order_type:25} {stats['successful']:3}/{stats['total']:3} ({stats['success_rate']:.1%})")

    if result.errors:
        print(f"\n{'='*70}")
        print(f"FEHLER ({len(result.errors)}):")
        print(f"{'-'*70}")
        for err in result.errors[:10]:
            print(f"  [{err['order_type']}] Order {err['order_num']}: {err['error'][:60]}...")
        if len(result.errors) > 10:
            print(f"  ... und {len(result.errors) - 10} weitere Fehler")

    print(f"{'='*70}\n")


def save_json_report(result: PerformanceTestResult, path: Path) -> None:
    """Speichert das Ergebnis als JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
    print(f"JSON-Report gespeichert: {path}")


# =============================================================================
# Pytest Tests
# =============================================================================

@pytest.mark.performance
@pytest.mark.asyncio
async def test_staging_performance_150_orders(browser: Browser, config: TestConfig):
    """
    Performance-Test: 150 Bestellungen auf Staging.

    Testet die Shop-Performance unter realistischer Last mit verschiedenen
    Bestellungstypen (Gast/Registriert, Post/Spedition).

    Erfolgskriterien:
    - Mindestens 95% Erfolgsrate
    - Maximale Gesamtdauer: 15 Minuten
    """
    perf_config = config.performance_test

    runner = PerformanceTestRunner(
        browser=browser,
        config=config,
        parallel_workers=perf_config.parallel_workers,
    )

    result = await runner.run()

    # Report ausgeben
    print_performance_report(result)

    # JSON-Report speichern
    report_path = Path("reports/performance") / f"performance-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    save_json_report(result, report_path)

    # Assertions
    assert result.success_rate >= perf_config.success_rate_threshold, (
        f"Erfolgsrate {result.success_rate:.1%} unter Schwellwert "
        f"{perf_config.success_rate_threshold:.1%}. "
        f"Fehlgeschlagen: {result.failed_orders}/{result.total_orders}"
    )

    max_duration = perf_config.max_duration_minutes * 60
    assert result.total_duration_seconds <= max_duration, (
        f"Gesamtdauer {result.total_duration_seconds:.0f}s überschreitet "
        f"Maximum von {max_duration}s ({perf_config.max_duration_minutes} min)"
    )


@pytest.mark.performance
@pytest.mark.asyncio
async def test_staging_performance_quick(browser: Browser, config: TestConfig):
    """
    Schneller Performance-Test: 30 Bestellungen (Smoke-Test für Performance).

    Reduzierte Version für schnelle Validierung der Performance-Test-Infrastruktur.
    """
    # Temporär Konfiguration anpassen
    config.performance_test.distribution.guest_post = 15
    config.performance_test.distribution.guest_spedition = 5
    config.performance_test.distribution.registered_post = 5
    config.performance_test.distribution.registered_spedition = 3
    config.performance_test.distribution.multi_product = 2

    runner = PerformanceTestRunner(
        browser=browser,
        config=config,
        parallel_workers=10,
    )

    result = await runner.run()
    print_performance_report(result)

    # Lockerere Kriterien für Quick-Test
    assert result.success_rate >= 0.90, (
        f"Erfolgsrate {result.success_rate:.1%} unter 90%"
    )


@pytest.mark.performance
@pytest.mark.asyncio
async def test_staging_performance_stress(browser: Browser, config: TestConfig):
    """
    Stress-Test: 300 Bestellungen mit hoher Parallelität.

    Testet die Grenzen der Shop-Performance.
    Markiert als 'slow' - nur bei expliziter Anforderung ausführen.
    """
    # Verdoppelte Last
    config.performance_test.distribution.guest_post = 120
    config.performance_test.distribution.guest_spedition = 60
    config.performance_test.distribution.registered_post = 60
    config.performance_test.distribution.registered_spedition = 30
    config.performance_test.distribution.multi_product = 30

    runner = PerformanceTestRunner(
        browser=browser,
        config=config,
        parallel_workers=25,  # Sehr hohe Parallelität
    )

    result = await runner.run()
    print_performance_report(result)

    # Report speichern
    report_path = Path("reports/performance") / f"stress-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    save_json_report(result, report_path)

    # Niedrigere Schwelle für Stress-Test
    assert result.success_rate >= 0.85, (
        f"Stress-Test: Erfolgsrate {result.success_rate:.1%} unter 85%"
    )
