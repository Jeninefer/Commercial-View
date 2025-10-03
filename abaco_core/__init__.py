"""
abaco_core - A library for financial calculations and KPI analysis.

This library provides tools for:
- Loan pricing enrichment with interval matching
- KPI calculations for financial viability
- Payment processing with configurable default thresholds
"""

__version__ = "0.1.0"

from .pricing_enricher import PricingEnricher
from .kpi_calculator import KPICalculator
from .payment_processor import PaymentProcessor

__all__ = [
    "PricingEnricher",
    "KPICalculator",
    "PaymentProcessor",
]
