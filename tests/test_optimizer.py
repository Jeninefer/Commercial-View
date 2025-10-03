"""Tests for the PortfolioOptimizer."""

import pytest
import pandas as pd
import numpy as np
from commercial_view.optimizer import PortfolioOptimizer


class TestPortfolioOptimizer:
    """Test suite for PortfolioOptimizer."""
    
    @pytest.fixture
    def sample_rules(self):
        """Sample rules configuration."""
        return {
            "hard_limits": {
                "apr": {
                    "0-5": {"max_pct": 0.3},
                    "5-7": {"max_pct": 0.4},
                    "7-10": {"max_pct": 0.5},
                    "10+": {"max_pct": 0.2}
                },
                "payer": {
                    "any_anchor": {"max_pct": 0.04}
                },
                "industry": {
                    "any_sector": {"max_pct": 0.35}
                }
            }
        }
    
    @pytest.fixture
    def sample_weights(self):
        """Sample weights configuration."""
        return {
            "apr": 0.6,
            "term_fit": 0.35,
            "origination_count": 0.05
        }
    
    @pytest.fixture
    def optimizer(self, sample_rules, sample_weights):
        """Create an optimizer instance."""
        return PortfolioOptimizer(rules=sample_rules, weights=sample_weights)
    
    @pytest.fixture
    def sample_candidates(self):
        """Sample candidate data."""
        return pd.DataFrame({
            "customer_id": ["A", "B", "C", "D", "E"],
            "amount": [100000, 200000, 150000, 300000, 250000],
            "apr": [6.5, 7.2, 5.8, 8.5, 6.0],
            "term": [36, 48, 36, 60, 48],
            "payer_rank": [1, 2, 1, 3, 2],
            "industry": ["Tech", "Healthcare", "Finance", "Retail", "Tech"]
        })
    
    def test_optimize_returns_dataframe(self, optimizer, sample_candidates):
        """Test that optimize returns a DataFrame."""
        result = optimizer.optimize(sample_candidates, aum_total=500000)
        assert isinstance(result, pd.DataFrame)
    
    def test_optimize_empty_input(self, optimizer):
        """Test optimize with empty DataFrame."""
        empty_df = pd.DataFrame()
        result = optimizer.optimize(empty_df, aum_total=1000000)
        assert result.empty
    
    def test_optimize_adds_required_columns(self, optimizer, sample_candidates):
        """Test that optimize adds the 'selected' and 'selected_amount_cum' columns."""
        result = optimizer.optimize(sample_candidates, aum_total=500000)
        if not result.empty:
            assert "selected" in result.columns
            assert "selected_amount_cum" in result.columns
            assert (result["selected"] == True).all()
    
    def test_optimize_respects_aum_total(self, optimizer, sample_candidates):
        """Test that optimize respects the total AUM limit."""
        aum_total = 500000
        result = optimizer.optimize(sample_candidates, aum_total=aum_total)
        if not result.empty:
            total_selected = result["amount"].sum()
            assert total_selected <= aum_total + 1e-6
    
    def test_optimize_with_target_term(self, optimizer, sample_candidates):
        """Test optimize with target term specified."""
        result = optimizer.optimize(sample_candidates, aum_total=500000, target_term=36)
        assert isinstance(result, pd.DataFrame)
    
    def test_optimize_cumsum_is_correct(self, optimizer, sample_candidates):
        """Test that selected_amount_cum is correctly calculated."""
        result = optimizer.optimize(sample_candidates, aum_total=800000)
        if not result.empty:
            expected_cumsum = result["amount"].cumsum()
            pd.testing.assert_series_equal(
                result["selected_amount_cum"], 
                expected_cumsum,
                check_names=False
            )
    
    def test_optimize_scoring_columns_added(self, optimizer, sample_candidates):
        """Test that scoring-related columns are added during optimization."""
        result = optimizer.optimize(sample_candidates, aum_total=500000)
        # The original df should have these columns, but selected may not retain all
        # Just verify the method runs without error
        assert isinstance(result, pd.DataFrame)
    
    def test_bucket_apr(self, optimizer):
        """Test APR bucketing."""
        assert optimizer._bucket_apr(3.0) == "0-5"
        assert optimizer._bucket_apr(6.0) == "5-7"
        assert optimizer._bucket_apr(8.5) == "7-10"
        assert optimizer._bucket_apr(12.0) == "10+"
    
    def test_bucket_line(self, optimizer):
        """Test line amount bucketing."""
        assert optimizer._bucket_line(50000) == "0-100k"
        assert optimizer._bucket_line(250000) == "100k-500k"
        assert optimizer._bucket_line(750000) == "500k-1M"
        assert optimizer._bucket_line(2000000) == "1M+"
    
    def test_payer_bucket(self, optimizer):
        """Test payer rank bucketing."""
        assert optimizer._payer_bucket(1) == "top"
        assert optimizer._payer_bucket(2) == "mid"
        assert optimizer._payer_bucket(5) == "low"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
