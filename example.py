"""
Example usage of the PricingEnricher class

This script demonstrates how to use the PricingEnricher to discover pricing files,
load pricing data, and enrich loan data with pricing information.
"""

import sys
import os
import pandas as pd
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.pricing_enricher import PricingEnricher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Run example enrichment workflow"""
    
    # Create sample loan data
    loans = pd.DataFrame({
        "loan_id": [1, 2, 3, 4, 5],
        "country": ["US", "UK", "US", "DE", "FR"],
        "sector": ["tech", "finance", "retail", "tech", "finance"],
        "risk_band": ["A", "B", "A", "C", "B"],
        "tenor_days": [30, 60, 90, 120, 180],
        "ticket_usd": [1000, 5000, 10000, 2500, 7500],
        "apr": [0.10, 0.12, 0.11, 0.15, 0.13],
        "eir": [0.08, 0.10, 0.09, 0.12, 0.11]
    })
    
    print("Sample Loan Data:")
    print(loans)
    print("\n" + "="*80 + "\n")
    
    # Initialize enricher
    # By default, it looks in ./data/pricing, ./pricing, and ./data directories
    enricher = PricingEnricher()
    
    # Or specify custom paths:
    # enricher = PricingEnricher(pricing_paths=["./custom/pricing/path"])
    
    # Discover pricing files
    print("Discovering pricing files...")
    pricing_files = enricher.find_pricing_files()
    
    if pricing_files:
        print(f"Found {len(pricing_files)} pricing file(s):")
        for kind, path in pricing_files.items():
            print(f"  - {kind}: {path}")
    else:
        print("No pricing files found. Creating sample pricing data...")
        
        # Create sample pricing data for demonstration
        pricing_grid = pd.DataFrame({
            "country": ["US", "UK", "DE"],
            "sector": ["tech", "finance", "retail"],
            "risk_band": ["A", "B", "A"],
            "recommended_rate": [0.05, 0.06, 0.055]
        })
        
        recommended_pricing = pd.DataFrame({
            "country": ["US", "UK"],
            "sector": ["tech", "finance"],
            "risk_band": ["A", "B"],
            "recommended_rate": [0.045, 0.055]
        })
        
        enricher.pricing_grid = pricing_grid
        enricher.recommended_pricing = recommended_pricing
        print("Sample pricing data loaded.")
    
    print("\n" + "="*80 + "\n")
    
    # Enrich loan data
    print("Enriching loan data...")
    enriched_loans = enricher.enrich_loan_data(
        loans,
        join_keys=["country", "sector", "risk_band"],
        recommended_rate_col="recommended_rate"
    )
    
    print("\nEnriched Loan Data:")
    print(enriched_loans)
    
    # Show enrichment statistics
    print("\n" + "="*80 + "\n")
    print("Enrichment Statistics:")
    
    if "has_pricing" in enriched_loans.columns:
        total_loans = len(enriched_loans)
        loans_with_pricing = enriched_loans["has_pricing"].sum()
        print(f"  Total loans: {total_loans}")
        print(f"  Loans with pricing: {loans_with_pricing}")
        print(f"  Coverage: {loans_with_pricing/total_loans*100:.1f}%")
    
    if "apr_eir_spread" in enriched_loans.columns:
        avg_spread = enriched_loans["apr_eir_spread"].mean()
        print(f"  Average APR-EIR spread: {avg_spread:.4f}")
        
        extreme_spreads = (enriched_loans["apr_eir_spread"].abs() > 0.5).sum()
        if extreme_spreads > 0:
            print(f"  WARNING: {extreme_spreads} loan(s) with extreme APR-EIR spread (>50pp)")
    
    print("\n" + "="*80 + "\n")
    print("Example completed successfully!")


if __name__ == "__main__":
    main()
