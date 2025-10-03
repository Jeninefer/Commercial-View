"""
Tests for the PricingEnricher class.
"""

import pytest
import pandas as pd
from abaco_core import PricingEnricher


class TestPricingEnricher:
    """Test suite for PricingEnricher class."""
    
    def test_enrich_loan_data_with_matches(self):
        """Test enriching loans when all loans match pricing bands."""
        pricing_bands = pd.DataFrame({
            'term': [12, 24, 36],
            'rate': [0.08, 0.07, 0.06]
        })
        
        loans = pd.DataFrame({
            'loan_id': [1, 2, 3],
            'term': [12, 24, 36],
            'amount': [10000, 20000, 30000]
        })
        
        enricher = PricingEnricher(pricing_bands)
        result = enricher.enrich_loan_data(loans, band_keys=['term'])
        
        # Check that result has original columns
        assert 'loan_id' in result.columns
        assert 'term' in result.columns
        assert 'amount' in result.columns
        
        # Check that grid columns were added
        assert 'term_grid' in result.columns
        assert 'rate_grid' in result.columns
        
        # Check that we have the same number of rows
        assert len(result) == len(loans)
    
    def test_enrich_loan_data_with_non_matches(self):
        """Test enriching loans when some loans don't match any pricing band."""
        pricing_bands = pd.DataFrame({
            'term': [12, 24],
            'rate': [0.08, 0.07]
        })
        
        loans = pd.DataFrame({
            'loan_id': [1, 2, 3],
            'term': [12, 24, 48],  # 48 won't match
            'amount': [10000, 20000, 30000]
        })
        
        enricher = PricingEnricher(pricing_bands)
        result = enricher.enrich_loan_data(loans, band_keys=['term'])
        
        # Check that result has all rows (including non-matching)
        assert len(result) == 3
        
        # Check that non-matching loan (loan_id=3) has NaN in grid columns
        # This is the key fix: None entries are replaced with empty dicts
        assert result.loc[result['loan_id'] == 3, 'rate_grid'].isna().any()
    
    def test_enrich_loan_data_empty_loans(self):
        """Test enriching when loans dataframe is empty."""
        pricing_bands = pd.DataFrame({
            'term': [12, 24],
            'rate': [0.08, 0.07]
        })
        
        loans = pd.DataFrame(columns=['loan_id', 'term', 'amount'])
        
        enricher = PricingEnricher(pricing_bands)
        result = enricher.enrich_loan_data(loans, band_keys=['term'])
        
        # Should return empty dataframe with expected columns
        assert len(result) == 0
        assert 'loan_id' in result.columns
    
    def test_enrich_loan_data_all_non_matches(self):
        """Test enriching when no loans match any pricing band."""
        pricing_bands = pd.DataFrame({
            'term': [12, 24],
            'rate': [0.08, 0.07]
        })
        
        loans = pd.DataFrame({
            'loan_id': [1, 2, 3],
            'term': [36, 48, 60],  # None match
            'amount': [10000, 20000, 30000]
        })
        
        enricher = PricingEnricher(pricing_bands)
        result = enricher.enrich_loan_data(loans, band_keys=['term'])
        
        # All loans should have NaN in grid columns
        assert len(result) == 3
        assert result['rate_grid'].isna().all()
        
        # Original columns should still have data
        assert result['loan_id'].notna().all()
        assert result['amount'].notna().all()
