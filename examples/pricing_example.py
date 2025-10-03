"""
Example usage of the PricingEnricher class.

This script demonstrates how to use the PricingEnricher to:
1. Load pricing data from CSV files
2. Enrich loan data with pricing information
3. Calculate APR-EIR spreads
"""

import pandas as pd
import os
import sys
import tempfile
import shutil

# Add parent directory to path to import abaco_core
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from abaco_core.pricing import PricingEnricher


def main():
    # Create a temporary directory for the example
    temp_dir = tempfile.mkdtemp()
    exports_dir = os.path.join(temp_dir, "exports")
    os.makedirs(exports_dir, exist_ok=True)
    
    try:
        print("=" * 60)
        print("PricingEnricher Example Usage")
        print("=" * 60)
        
        # Create sample pricing data
        print("\n1. Creating sample pricing data...")
        
        # Create pricing grid
        grid_data = pd.DataFrame({
            "segment": ["A", "B", "C"],
            "term": [12, 24, 36],
            "base_rate": [0.05, 0.06, 0.07],
            "margin": [0.01, 0.015, 0.02]
        })
        grid_file = os.path.join(exports_dir, "pricing_grid.csv")
        grid_data.to_csv(grid_file, index=False)
        print(f"   Created pricing grid: {grid_file}")
        print(grid_data.to_string(index=False))
        
        # Create recommended pricing
        rec_data = pd.DataFrame({
            "segment": ["A", "B"],
            "term": [12, 24],
            "recommended_rate": [0.045, 0.055]
        })
        rec_file = os.path.join(exports_dir, "recommended_pricing.csv")
        rec_data.to_csv(rec_file, index=False)
        print(f"\n   Created recommended pricing: {rec_file}")
        print(rec_data.to_string(index=False))
        
        # Create sample loan data
        print("\n2. Creating sample loan data...")
        loan_data = pd.DataFrame({
            "loan_id": [1001, 1002, 1003, 1004],
            "segment": ["A", "B", "C", "A"],
            "term": [12, 24, 36, 12],
            "loan_amount": [10000, 25000, 50000, 15000],
            "APR": [0.055, 0.065, 0.080, 0.060],
            "EIR": [0.050, 0.058, 0.072, 0.054]
        })
        print(loan_data.to_string(index=False))
        
        # Initialize PricingEnricher
        print("\n3. Initializing PricingEnricher...")
        enricher = PricingEnricher(pricing_paths=[exports_dir])
        
        # Find and load pricing files
        print("\n4. Finding pricing files...")
        found_files = enricher.find_pricing_files()
        for key, path in found_files.items():
            print(f"   {key}: {path}")
        
        print("\n5. Loading pricing data...")
        loaded = enricher.load_pricing_data()
        print(f"   Loaded successfully: {loaded}")
        
        # Enrich loan data
        print("\n6. Enriching loan data...")
        enriched = enricher.enrich_loan_data(loan_data, autoload=False)
        print("\nEnriched loan data:")
        print(enriched.to_string(index=False))
        
        # Show what columns were added
        new_cols = set(enriched.columns) - set(loan_data.columns)
        print(f"\n   New columns added: {sorted(new_cols)}")
        
        # Demonstrate interval matching with band keys
        print("\n7. Demonstrating interval matching...")
        grid_with_ranges = pd.DataFrame({
            "amount_min": [0, 10000, 30000],
            "amount_max": [9999, 29999, 100000],
            "tier": ["Bronze", "Silver", "Gold"],
            "discount_rate": [0.00, 0.005, 0.010]
        })
        grid_range_file = os.path.join(exports_dir, "pricing_grid_ranges.csv")
        grid_with_ranges.to_csv(grid_range_file, index=False)
        
        # Reload with the new grid
        enricher2 = PricingEnricher(pricing_paths=[exports_dir])
        enricher2.pricing_grid = pd.read_csv(grid_range_file)
        
        band_keys = {"loan_amount": ("amount_min", "amount_max")}
        enriched_with_bands = enricher2.enrich_loan_data(
            loan_data, 
            band_keys=band_keys, 
            autoload=False
        )
        print("\nLoan data with interval matching:")
        cols_to_show = ["loan_id", "loan_amount", "tier_grid", "discount_rate_grid"]
        available_cols = [c for c in cols_to_show if c in enriched_with_bands.columns]
        if available_cols:
            print(enriched_with_bands[available_cols].to_string(index=False))
        else:
            print(enriched_with_bands.to_string(index=False))
        
        print("\n" + "=" * 60)
        print("Example completed successfully!")
        print("=" * 60)
        
    finally:
        # Clean up
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    main()
