"""
Page Object Models für Shopware 6.

Jede Seite wird als Klasse mit Selektoren und Interaktionsmethoden abgebildet.
"""
from .base_page import BasePage
from .checkout_page import Address, CheckoutPage, CheckoutResult

__all__ = ["BasePage", "CheckoutPage", "Address", "CheckoutResult"]
