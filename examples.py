"""
Example usage of the Commercial View pricing enrichment functionality.
"""

import pandas as pd
from commercial_view import enrich_with_pricing


def example_exact_keys():
    """Example 1: Exact key joins with Parquet file."""
    print("=" * 60)
    print("Example 1: Exact Key Joins (Parquet)")
    print("=" * 60)
    
    # Sample loans data
    loans_df = pd.DataFrame({
        'loan_id': [1, 2, 3, 4, 5],
        'country': ['USA', 'USA', 'UK', 'UK', 'USA'],
        'sector': ['tech', 'retail', 'tech', 'retail', 'finance'],
        'risk_band': ['A', 'A', 'A', 'A', 'A'],
        'amount': [100000, 50000, 75000, 120000, 90000]
    })
    
    print("\nOriginal Loans DataFrame:")
    print(loans_df)
    
    # Enrich with pricing using exact key joins
    enriched_loans = enrich_with_pricing(
        loans_df,
        "configs/pricing_grid.parquet",
        join_keys=["country", "sector", "risk_band"]
    )
    
    print("\nEnriched Loans DataFrame:")
    print(enriched_loans)
    print("\n")


def example_interval_keys():
    """Example 2: Interval/band joins with YAML file."""
    print("=" * 60)
    print("Example 2: Interval + Exact Key Joins (YAML)")
    print("=" * 60)
    
    # Sample loans data with interval columns
    loans_df = pd.DataFrame({
        'loan_id': [101, 102, 103, 104, 105],
        'country': ['USA', 'USA', 'UK', 'UK', 'USA'],
        'risk_band': ['A', 'A', 'A', 'B', 'B'],
        'tenor_days': [90, 200, 60, 365, 100],
        'ticket_usd': [50000, 75000, 80000, 150000, 120000],
        'amount': [50000, 75000, 80000, 150000, 120000]
    })
    
    print("\nOriginal Loans DataFrame:")
    print(loans_df)
    
    # Enrich with pricing using interval + exact key joins
    enriched_loans = enrich_with_pricing(
        loans_df,
        "configs/pricing_grid.yaml",
        join_keys=["country", "risk_band"],
        band_keys={
            "tenor_days": ["tenor_min", "tenor_max"],
            "ticket_usd": ["ticket_min", "ticket_max"]
        },
        rate_cols=("apr", "eir"),
        recommended_col="recommended_rate"
    )
    
    print("\nEnriched Loans DataFrame:")
    print(enriched_loans)
    print("\n")


def example_interval_keys_all_columns():
    """Example 3: Interval joins without filtering columns."""
    print("=" * 60)
    print("Example 3: Interval Joins (All Columns)")
    print("=" * 60)
    
    # Sample loans data
    loans_df = pd.DataFrame({
        'loan_id': [201, 202, 203],
        'country': ['USA', 'UK', 'USA'],
        'risk_band': ['A', 'A', 'B'],
        'tenor_days': [45, 90, 200],
        'ticket_usd': [25000, 50000, 100000]
    })
    
    print("\nOriginal Loans DataFrame:")
    print(loans_df)
    
    # Enrich with pricing, keeping all pricing columns
    enriched_loans = enrich_with_pricing(
        loans_df,
        "configs/pricing_grid.yaml",
        join_keys=["country", "risk_band"],
        band_keys={
            "tenor_days": ["tenor_min", "tenor_max"],
            "ticket_usd": ["ticket_min", "ticket_max"]
        }
    )
    
    print("\nEnriched Loans DataFrame (with interval bounds):")
    print(enriched_loans)
    print("\n")


if __name__ == "__main__":
    # Run all examples
    example_exact_keys()
    example_interval_keys()
    example_interval_keys_all_columns()
    
    print("=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)
