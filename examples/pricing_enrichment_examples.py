"""
Example usage of pricing enrichment functionality.
"""
import pandas as pd
import tempfile
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.pricing_enrichment import enrich_with_pricing


def example_exact_join():
    """Example of exact join on product keys."""
    print("\n=== Example 1: Exact Join on Product Keys ===")
    
    # Create sample loan data
    loans_df = pd.DataFrame({
        'loan_id': [1, 2, 3, 4],
        'product': ['A', 'B', 'C', 'A'],
        'amount': [10000, 20000, 15000, 12000]
    })
    print("\nLoan DataFrame:")
    print(loans_df)
    
    # Create pricing grid
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write('product,apr,eir,recommended_rate\n')
        f.write('A,5.0,4.5,5.0\n')
        f.write('B,6.0,5.5,6.0\n')
        temp_path = f.name
    
    try:
        # Enrich loans with pricing
        enriched = enrich_with_pricing(loans_df, temp_path, join_keys=['product'])
        print("\nEnriched DataFrame:")
        print(enriched)
        print(f"\nAPR-EIR Spread calculated: {enriched['apr_eir_spread'].tolist()}")
        print(f"Has pricing flags: {enriched['has_pricing'].tolist()}")
    finally:
        os.unlink(temp_path)


def example_band_matching():
    """Example of band/interval matching."""
    print("\n\n=== Example 2: Band Matching on Tenor ===")
    
    # Create sample loan data with tenor
    loans_df = pd.DataFrame({
        'loan_id': [1, 2, 3, 4],
        'tenor_days': [30, 90, 180, 365]
    })
    print("\nLoan DataFrame:")
    print(loans_df)
    
    # Create pricing grid with ranges
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write('tenor_min,tenor_max,apr,eir,recommended_rate\n')
        f.write('0,60,5.0,4.5,5.0\n')
        f.write('61,120,6.0,5.5,6.0\n')
        f.write('121,180,7.0,6.5,7.0\n')
        f.write('181,365,8.0,7.5,8.0\n')
        temp_path = f.name
    
    try:
        # Enrich loans with band matching
        enriched = enrich_with_pricing(
            loans_df,
            temp_path,
            band_keys={'tenor_days': ['tenor_min', 'tenor_max']}
        )
        print("\nEnriched DataFrame:")
        print(enriched)
        print(f"\nAPR rates by tenor: {enriched['apr'].tolist()}")
    finally:
        os.unlink(temp_path)


def example_combined():
    """Example combining exact join and band matching."""
    print("\n\n=== Example 3: Combined Exact Join and Band Matching ===")
    
    # Create sample loan data
    loans_df = pd.DataFrame({
        'loan_id': [1, 2, 3, 4],
        'product': ['A', 'A', 'B', 'B'],
        'tenor_days': [30, 90, 180, 365]
    })
    print("\nLoan DataFrame:")
    print(loans_df)
    
    # Create pricing grid
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write('product,tenor_min,tenor_max,apr,eir,recommended_rate\n')
        f.write('A,0,60,5.0,4.5,5.0\n')
        f.write('A,61,120,6.0,5.5,6.0\n')
        f.write('B,121,180,7.0,6.5,7.0\n')
        f.write('B,181,365,8.0,7.5,8.0\n')
        temp_path = f.name
    
    try:
        # Enrich with both exact join and band matching
        enriched = enrich_with_pricing(
            loans_df,
            temp_path,
            join_keys=['product'],
            band_keys={'tenor_days': ['tenor_min', 'tenor_max']}
        )
        print("\nEnriched DataFrame:")
        print(enriched[['loan_id', 'product', 'tenor_days', 'apr', 'eir', 'recommended_rate', 'has_pricing']])
    finally:
        os.unlink(temp_path)


if __name__ == '__main__':
    example_exact_join()
    example_band_matching()
    example_combined()
