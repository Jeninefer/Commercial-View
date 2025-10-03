"""
Example usage of the Pricing Enrichment Module

This script demonstrates how to use the pricing enrichment module
to enrich loan data with pricing information and calculate APR-EIR spreads.
"""

import sys
from pathlib import Path
import pandas as pd

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from pricing_enrichment import enrich_pricing, pricing_enricher


def example_basic_usage():
    """Example 1: Basic usage with APR-EIR spread calculation"""
    print("=" * 60)
    print("Example 1: Basic APR-EIR Spread Calculation")
    print("=" * 60)
    
    # Create sample loan data
    loan_df = pd.DataFrame({
        'loan_id': [1, 2, 3],
        'APR': [0.05, 0.06, 0.07],
        'EIR': [0.04, 0.05, 0.06],
        'amount': [10000, 20000, 30000]
    })
    
    print("\nOriginal Loan Data:")
    print(loan_df)
    
    # Enrich with pricing data
    enriched_df = enrich_pricing(loan_df, autoload=False)
    
    print("\nEnriched Loan Data (with APR-EIR spread):")
    print(enriched_df)
    print()


def example_with_explicit_columns():
    """Example 2: Using explicit column hints"""
    print("=" * 60)
    print("Example 2: Using Explicit Column Hints")
    print("=" * 60)
    
    # Create sample loan data with custom column names
    loan_df = pd.DataFrame({
        'loan_id': [1, 2, 3],
        'annual_percentage_rate': [0.05, 0.06, 0.07],
        'effective_interest_rate': [0.04, 0.05, 0.06],
        'amount': [10000, 20000, 30000]
    })
    
    print("\nOriginal Loan Data:")
    print(loan_df)
    
    # Enrich with explicit column hints
    enriched_df = enrich_pricing(
        loan_df,
        apr_col_hint='annual_percentage_rate',
        eir_col_hint='effective_interest_rate',
        autoload=False
    )
    
    print("\nEnriched Loan Data:")
    print(enriched_df)
    print()


def example_with_join_keys():
    """Example 3: Using join keys for exact matching"""
    print("=" * 60)
    print("Example 3: Using Join Keys for Exact Matching")
    print("=" * 60)
    
    # Create sample loan data
    loan_df = pd.DataFrame({
        'loan_id': [1, 2, 3],
        'product': ['Personal', 'Auto', 'Personal'],
        'APR': [0.05, 0.06, 0.07],
        'EIR': [0.04, 0.05, 0.06]
    })
    
    # Create recommended pricing data
    recommended_pricing = pd.DataFrame({
        'product': ['Personal', 'Auto', 'Mortgage'],
        'recommended_rate': [0.045, 0.055, 0.035]
    })
    
    print("\nOriginal Loan Data:")
    print(loan_df)
    
    print("\nRecommended Pricing Data:")
    print(recommended_pricing)
    
    # Load pricing data into enricher
    pricing_enricher.recommended_pricing = recommended_pricing
    
    # Enrich with join keys
    enriched_df = enrich_pricing(
        loan_df,
        join_keys=['product'],
        autoload=False
    )
    
    print("\nEnriched Loan Data:")
    print(enriched_df)
    print()


def example_with_band_keys():
    """Example 4: Using band keys for interval matching"""
    print("=" * 60)
    print("Example 4: Using Band Keys for Interval Matching")
    print("=" * 60)
    
    # Create sample loan data
    loan_df = pd.DataFrame({
        'loan_id': [1, 2, 3, 4],
        'tenor_days': [30, 90, 180, 360],
        'APR': [0.05, 0.06, 0.07, 0.08],
        'EIR': [0.04, 0.05, 0.06, 0.07]
    })
    
    # Create pricing grid with tenor bands
    pricing_grid = pd.DataFrame({
        'tenor_min': [0, 60, 120, 240],
        'tenor_max': [60, 120, 240, 365],
        'rate_adjustment': [0.01, 0.015, 0.02, 0.025],
        'risk_category': ['Low', 'Medium', 'Medium', 'High']
    })
    
    print("\nOriginal Loan Data:")
    print(loan_df)
    
    print("\nPricing Grid:")
    print(pricing_grid)
    
    # Load pricing data into enricher
    pricing_enricher.pricing_grid = pricing_grid
    
    # Enrich with band keys
    enriched_df = enrich_pricing(
        loan_df,
        band_keys={'tenor_days': ('tenor_min', 'tenor_max')},
        autoload=False
    )
    
    print("\nEnriched Loan Data:")
    print(enriched_df[['loan_id', 'tenor_days', 'APR', 'EIR', 
                       'apr_eir_spread', 'rate_adjustment', 'risk_category']])
    print()


def example_combined():
    """Example 5: Combined usage with both join and band keys"""
    print("=" * 60)
    print("Example 5: Combined Join and Band Key Matching")
    print("=" * 60)
    
    # Create sample loan data
    loan_df = pd.DataFrame({
        'loan_id': [1, 2, 3, 4],
        'product': ['Personal', 'Auto', 'Personal', 'Auto'],
        'tenor_days': [90, 180, 360, 90],
        'APR': [0.05, 0.06, 0.07, 0.08],
        'EIR': [0.04, 0.05, 0.06, 0.07]
    })
    
    # Create recommended pricing by product
    recommended_pricing = pd.DataFrame({
        'product': ['Personal', 'Auto', 'Mortgage'],
        'recommended_rate': [0.045, 0.055, 0.035],
        'base_rate': [0.04, 0.05, 0.03]
    })
    
    # Create pricing grid with tenor bands
    pricing_grid = pd.DataFrame({
        'tenor_min': [0, 120, 240],
        'tenor_max': [120, 240, 365],
        'rate_adjustment': [0.01, 0.015, 0.02],
        'risk_category': ['Low', 'Medium', 'High']
    })
    
    print("\nOriginal Loan Data:")
    print(loan_df)
    
    # Load pricing data
    pricing_enricher.recommended_pricing = recommended_pricing
    pricing_enricher.pricing_grid = pricing_grid
    
    # Enrich with both join and band keys
    enriched_df = enrich_pricing(
        loan_df,
        join_keys=['product'],
        band_keys={'tenor_days': ('tenor_min', 'tenor_max')},
        autoload=False
    )
    
    print("\nEnriched Loan Data:")
    print(enriched_df)
    print()


if __name__ == '__main__':
    example_basic_usage()
    example_with_explicit_columns()
    example_with_join_keys()
    example_with_band_keys()
    example_combined()
    
    print("=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)
