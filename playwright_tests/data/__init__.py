"""
Testdaten fuer Playwright E2E Tests.
"""
from .shipping_rules import (
    PLZRule,
    AT_SPEDITION_RULES,
    DE_SPEDITION_RULES,
    CH_SPEDITION_RULES,
    ALL_SPEDITION_RULES,
    SHIPPING_TEST_CASES,
    get_test_plz_for_rule,
    get_city_for_plz,
)

__all__ = [
    "PLZRule",
    "AT_SPEDITION_RULES",
    "DE_SPEDITION_RULES",
    "CH_SPEDITION_RULES",
    "ALL_SPEDITION_RULES",
    "SHIPPING_TEST_CASES",
    "get_test_plz_for_rule",
    "get_city_for_plz",
]
