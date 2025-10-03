"""
Test the exact usage pattern from the problem statement
"""

import sys
import os
import tempfile
import shutil
import pandas as pd

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pricing_enricher import PricingEnricher


def test_problem_statement_usage():
    """Test the exact usage pattern shown in the problem statement"""
    
    # Create temporary directory structure
    test_dir = tempfile.mkdtemp()
    pricing_dir = os.path.join(test_dir, "pricing")
    os.makedirs(pricing_dir)
    
    try:
        # Create test pricing files
        # Pricing grid with band columns
        pricing_grid = pd.DataFrame({
            "country": ["US", "UK", "US", "UK"],
            "sector": ["tech", "finance", "retail", "retail"],
            "risk_band": ["A", "B", "A", "B"],
            "tenor_min": [0, 0, 60, 60],
            "tenor_max": [60, 60, 180, 180],
            "ticket_min": [0, 2000, 5000, 5000],
            "ticket_max": [5000, 10000, 20000, 20000],
            "recommended_rate": [0.05, 0.06, 0.055, 0.065]
        })
        
        # Recommended pricing (higher priority)
        recommended_pricing = pd.DataFrame({
            "country": ["US"],
            "sector": ["tech"],
            "risk_band": ["A"],
            "recommended_rate": [0.045]
        })
        
        pricing_grid.to_csv(os.path.join(pricing_dir, "pricing_grid.csv"), index=False)
        recommended_pricing.to_csv(os.path.join(pricing_dir, "recommended_pricing.csv"), index=False)
        
        # Create test loan data
        loans = pd.DataFrame({
            "loan_id": [1, 2, 3, 4],
            "country": ["US", "UK", "US", "FR"],
            "sector": ["tech", "finance", "retail", "tech"],
            "risk_band": ["A", "B", "A", "A"],
            "tenor_days": [30, 45, 90, 120],
            "ticket_usd": [2000, 5000, 10000, 1000]
        })
        
        # Initialize enricher and test the exact pattern from problem statement
        enricher = PricingEnricher(pricing_paths=[pricing_dir])
        
        # Test the exact method call from problem statement
        enriched = enricher.enrich_loan_data(
            loans,
            join_keys=["country", "sector", "risk_band"],
            band_keys={"tenor_days": ("tenor_min", "tenor_max"), "ticket_usd": ("ticket_min", "ticket_max")},
            recommended_rate_col="recommended_rate"
        )
        
        print("✓ Problem statement usage pattern works correctly")
        print("\nEnriched loans:")
        print(enriched[["loan_id", "country", "sector", "risk_band", "recommended_rate", "has_pricing"]])
        
        # Verify results
        assert "recommended_rate" in enriched.columns, "recommended_rate column missing"
        assert "has_pricing" in enriched.columns, "has_pricing column missing"
        
        # Loan 1 (US/tech/A) should get recommended pricing (0.045)
        assert enriched.loc[0, "recommended_rate"] == 0.045, "Expected 0.045 from recommended_pricing"
        assert enriched.loc[0, "has_pricing"] == True, "Expected has_pricing=True"
        
        # Loan 2 (UK/finance/B) should get grid pricing (0.06)
        # tenor=45 is in [0,60], ticket=5000 is in [2000,10000]
        assert enriched.loc[1, "recommended_rate"] == 0.06, "Expected 0.06 from pricing_grid"
        assert enriched.loc[1, "has_pricing"] == True, "Expected has_pricing=True"
        
        # Loan 3 (US/retail/A) should get grid pricing (0.055)
        # tenor=90 is in [60,180], ticket=10000 is in [5000,20000]
        assert enriched.loc[2, "recommended_rate"] == 0.055, "Expected 0.055 from pricing_grid"
        assert enriched.loc[2, "has_pricing"] == True, "Expected has_pricing=True"
        
        # Loan 4 (FR/tech/A) has no match
        assert pd.isna(enriched.loc[3, "recommended_rate"]), "Expected NaN for unmatched loan"
        assert enriched.loc[3, "has_pricing"] == False, "Expected has_pricing=False"
        
        print("\n✓ All assertions passed!")
        return True
        
    finally:
        # Clean up
        shutil.rmtree(test_dir)


if __name__ == "__main__":
    test_problem_statement_usage()
    print("\n" + "="*80)
    print("SUCCESS: Problem statement usage test completed!")
