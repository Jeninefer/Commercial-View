"""
Tests for CustomerAnalytics class.
"""

import logging
import pandas as pd
import pytest
from commercial_view.analytics import CustomerAnalytics


# Configure logging for tests
logging.basicConfig(level=logging.INFO)


class TestCustomerAnalytics:
    """Test suite for CustomerAnalytics class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analytics = CustomerAnalytics()

    def test_calculate_customer_dpd_stats_basic(self):
        """Test basic DPD stats calculation."""
        # Create sample DPD data
        dpd_df = pd.DataFrame({
            "loan_id": ["L1", "L2", "L3", "L4", "L5"],
            "days_past_due": [0, 15, 30, 10, 20]
        })
        
        # Create sample loan data
        loan_df = pd.DataFrame({
            "loan_id": ["L1", "L2", "L3", "L4", "L5"],
            "customer_id": ["C1", "C1", "C2", "C2", "C3"]
        })
        
        result = self.analytics.calculate_customer_dpd_stats(
            dpd_df, loan_df, "customer_id", "loan_id"
        )
        
        # Verify the result structure
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3  # 3 unique customers
        assert list(result.columns) == ["customer_id", "dpd_mean", "dpd_median", "dpd_max", "dpd_min", "dpd_count"]
        
        # Verify customer C1 stats
        c1_stats = result[result["customer_id"] == "C1"].iloc[0]
        assert c1_stats["dpd_mean"] == 7.5  # (0 + 15) / 2
        assert c1_stats["dpd_median"] == 7.5
        assert c1_stats["dpd_max"] == 15
        assert c1_stats["dpd_min"] == 0
        assert c1_stats["dpd_count"] == 2

    def test_calculate_customer_dpd_stats_missing_columns(self):
        """Test handling of missing required columns."""
        # Missing days_past_due column
        dpd_df = pd.DataFrame({
            "loan_id": ["L1", "L2"],
            "some_other_column": [1, 2]
        })
        
        loan_df = pd.DataFrame({
            "loan_id": ["L1", "L2"],
            "customer_id": ["C1", "C2"]
        })
        
        result = self.analytics.calculate_customer_dpd_stats(
            dpd_df, loan_df, "customer_id", "loan_id"
        )
        
        # Should return empty DataFrame
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    def test_calculate_customer_dpd_stats_with_nulls(self):
        """Test DPD stats calculation with null values."""
        # Create sample DPD data with nulls
        dpd_df = pd.DataFrame({
            "loan_id": ["L1", "L2", "L3", "L4"],
            "days_past_due": [10, None, 20, 30]
        })
        
        # Create sample loan data
        loan_df = pd.DataFrame({
            "loan_id": ["L1", "L2", "L3", "L4"],
            "customer_id": ["C1", "C1", "C2", "C2"]
        })
        
        result = self.analytics.calculate_customer_dpd_stats(
            dpd_df, loan_df, "customer_id", "loan_id"
        )
        
        # L2 should be dropped due to null DPD
        assert len(result) == 2  # 2 customers
        
        # Verify customer C1 stats (only L1 counted, L2 dropped)
        c1_stats = result[result["customer_id"] == "C1"].iloc[0]
        assert c1_stats["dpd_count"] == 1
        assert c1_stats["dpd_mean"] == 10

    def test_calculate_customer_dpd_stats_custom_fields(self):
        """Test with custom field names."""
        # Create sample DPD data
        dpd_df = pd.DataFrame({
            "account_num": ["A1", "A2", "A3"],
            "days_past_due": [5, 15, 25]
        })
        
        # Create sample loan data
        loan_df = pd.DataFrame({
            "account_num": ["A1", "A2", "A3"],
            "client_id": ["CL1", "CL1", "CL2"]
        })
        
        result = self.analytics.calculate_customer_dpd_stats(
            dpd_df, loan_df, "client_id", "account_num"
        )
        
        # Verify the result
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert "client_id" in result.columns
        assert list(result.columns) == ["client_id", "dpd_mean", "dpd_median", "dpd_max", "dpd_min", "dpd_count"]

    def test_calculate_customer_dpd_stats_single_customer(self):
        """Test with a single customer."""
        dpd_df = pd.DataFrame({
            "loan_id": ["L1", "L2", "L3"],
            "days_past_due": [10, 20, 30]
        })
        
        loan_df = pd.DataFrame({
            "loan_id": ["L1", "L2", "L3"],
            "customer_id": ["C1", "C1", "C1"]
        })
        
        result = self.analytics.calculate_customer_dpd_stats(
            dpd_df, loan_df, "customer_id", "loan_id"
        )
        
        assert len(result) == 1
        stats = result.iloc[0]
        assert stats["customer_id"] == "C1"
        assert stats["dpd_mean"] == 20  # (10 + 20 + 30) / 3
        assert stats["dpd_median"] == 20
        assert stats["dpd_max"] == 30
        assert stats["dpd_min"] == 10
        assert stats["dpd_count"] == 3
