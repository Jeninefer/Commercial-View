"""Test suite for PricingEnricher JSON-safe conversion."""

import pytest
import pandas as pd
import numpy as np
import json
from src.pricing_enricher import PricingEnricher


class TestPricingEnricherJSONSafe:
    """Test class for PricingEnricher JSON-safe functionality."""
    
    def test_pricing_enricher_to_json_safe(self):
        """Test PricingEnricher.to_json_safe method."""
        enricher = PricingEnricher()
        
        df = pd.DataFrame({
            'loan_id': ['L001', 'L002'],
            'amount': [np.int64(10000), np.int64(20000)],
            'rate': [np.float64(0.05), np.float64(0.06)],
            'date': pd.to_datetime(['2024-01-01', '2024-01-02'])
        })
        
        result = enricher.to_json_safe(df)
        
        assert len(result) == 2
        assert isinstance(result[0]['amount'], int)
        assert isinstance(result[0]['rate'], float)
        assert isinstance(result[0]['date'], str)
        
        # Verify JSON serialization works
        json_str = json.dumps(result)
        assert json_str is not None
    
    def test_pricing_enricher_to_json_safe_with_nan(self):
        """Test PricingEnricher.to_json_safe with NaN values."""
        enricher = PricingEnricher()
        
        df = pd.DataFrame({
            'loan_id': ['L001', 'L002'],
            'rate': [0.05, np.nan]
        })
        
        result = enricher.to_json_safe(df)
        
        assert len(result) == 2
        assert result[0]['rate'] == 0.05
        assert result[1]['rate'] is None
        
        # Verify JSON serialization works
        json_str = json.dumps(result)
        assert json_str is not None
    
    def test_pricing_enricher_to_json_safe_empty(self):
        """Test PricingEnricher.to_json_safe with empty DataFrame."""
        enricher = PricingEnricher()
        
        df = pd.DataFrame()
        result = enricher.to_json_safe(df)
        
        assert result == []
        
        # Verify JSON serialization works
        json_str = json.dumps(result)
        assert json_str == '[]'
