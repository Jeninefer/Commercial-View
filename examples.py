"""
Example usage of the abaco_core library.

This script demonstrates the three main components:
1. PricingEnricher - for enriching loans with pricing data
2. PaymentProcessor - for detecting defaults
3. KPICalculator - for computing viability metrics
"""

import pandas as pd
from abaco_core import PricingEnricher, PaymentProcessor, KPICalculator


def example_pricing_enricher():
    """Demonstrate PricingEnricher functionality."""
    print("=" * 60)
    print("PricingEnricher Example")
    print("=" * 60)
    
    # Create pricing bands
    pricing_bands = pd.DataFrame({
        'term': [12, 24, 36],
        'rate': [0.08, 0.07, 0.06],
        'fee': [100, 150, 200]
    })
    print("\nPricing Bands:")
    print(pricing_bands)
    
    # Create loan data (note: loan 4 has term=48 which won't match)
    loans = pd.DataFrame({
        'loan_id': [1, 2, 3, 4],
        'term': [12, 24, 36, 48],
        'amount': [10000, 20000, 30000, 15000]
    })
    print("\nOriginal Loans:")
    print(loans)
    
    # Enrich loans with pricing data
    enricher = PricingEnricher(pricing_bands)
    enriched = enricher.enrich_loan_data(loans, band_keys=['term'])
    print("\nEnriched Loans (note loan 4 has NaN for grid columns):")
    print(enriched)
    print()


def example_payment_processor():
    """Demonstrate PaymentProcessor functionality."""
    print("=" * 60)
    print("PaymentProcessor Example")
    print("=" * 60)
    
    # Create payment data
    payments = pd.DataFrame({
        'loan_id': [1, 2, 3, 4, 5],
        'amount': [1000, 1500, 2000, 1200, 800],
        'days_past_due': [0, 45, 90, 180, 200]
    })
    print("\nPayment Data:")
    print(payments)
    
    # Process with default 180-day threshold
    processor_180 = PaymentProcessor(default_threshold=180)
    processed_180 = processor_180.process_payments(payments)
    print("\nProcessed with 180-day threshold (write-off):")
    print(processed_180)
    print(f"Default rate: {processor_180.calculate_default_rate(payments):.2%}")
    
    # Process with 90-day threshold (technical default)
    processor_90 = PaymentProcessor(default_threshold=90)
    processed_90 = processor_90.process_payments(payments)
    print("\nProcessed with 90-day threshold (technical default):")
    print(processed_90)
    print(f"Default rate: {processor_90.calculate_default_rate(payments):.2%}")
    print()


def example_kpi_calculator():
    """Demonstrate KPICalculator functionality."""
    print("=" * 60)
    print("KPICalculator Example")
    print("=" * 60)
    
    calculator = KPICalculator()
    
    # Example 1: With startup metrics
    print("\nExample 1: Startup with good metrics")
    good_startup = {
        'runway_months': 18,
        'burn_rate': 50000,
        'revenue_growth': 0.20,
        'revenue': 100000
    }
    viability = calculator.compute_viability_index(startup_metrics=good_startup)
    print(f"Startup metrics: {good_startup}")
    print(f"Viability index: {viability:.2f}")
    
    # Example 2: With poor startup metrics
    print("\nExample 2: Startup with poor metrics")
    poor_startup = {
        'runway_months': 6,
        'burn_rate': 150000,
        'revenue_growth': 0.02,
        'revenue': 30000
    }
    viability = calculator.compute_viability_index(startup_metrics=poor_startup)
    print(f"Startup metrics: {poor_startup}")
    print(f"Viability index: {viability:.2f}")
    
    # Example 3: Pure fintech (no startup metrics)
    print("\nExample 3: Pure fintech with only loan data (no startup metrics)")
    viability = calculator.compute_viability_index(startup_metrics=None)
    print(f"Startup metrics: None")
    print(f"Viability index: {viability:.2f} (N/A - not applicable)")
    
    # Example 4: Portfolio KPIs
    print("\nExample 4: Portfolio KPIs")
    loans = pd.DataFrame({
        'loan_id': [1, 2, 3, 4, 5],
        'principal': [10000, 20000, 15000, 25000, 30000],
        'interest_rate': [0.08, 0.07, 0.09, 0.06, 0.08],
        'days_past_due': [0, 30, 15, 0, 45]
    })
    kpis = calculator.calculate_portfolio_kpis(loans)
    print("Portfolio KPIs:")
    for key, value in kpis.items():
        if isinstance(value, float):
            print(f"  {key}: {value:,.2f}")
        else:
            print(f"  {key}: {value}")
    print()


if __name__ == "__main__":
    example_pricing_enricher()
    example_payment_processor()
    example_kpi_calculator()
    
    print("=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)
