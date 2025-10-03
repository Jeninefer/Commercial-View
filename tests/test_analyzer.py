"""Tests for PaymentAnalyzer class."""

import pytest
import pandas as pd
import numpy as np
from src.commercial_view import PaymentAnalyzer


class TestPaymentAnalyzer:
    """Test suite for PaymentAnalyzer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = PaymentAnalyzer(dpd_threshold=90)
    
    def test_get_dpd_buckets_default(self):
        """Test DPD bucketing with default configuration."""
        df = pd.DataFrame({
            "loan_id": [1, 2, 3, 4, 5],
            "days_past_due": [0, 15, 45, 75, 120]
        })
        
        result = self.analyzer.get_dpd_buckets(df)
        
        assert "dpd_bucket" in result.columns
        assert "default_flag" in result.columns
        assert result["dpd_bucket"].iloc[0] == "Current"
        assert result["dpd_bucket"].iloc[1] == "1-29"
        assert result["dpd_bucket"].iloc[2] == "30-59"
        assert result["default_flag"].iloc[4] == 1  # 120 >= 90
    
    def test_get_dpd_buckets_custom_config(self):
        """Test DPD bucketing with custom configuration."""
        config = {
            "dpd_buckets": [
                (0, 0, "Current"),
                (1, 30, "1-30"),
                (31, None, "31+")
            ]
        }
        analyzer = PaymentAnalyzer(config=config, dpd_threshold=90)
        
        df = pd.DataFrame({
            "loan_id": [1, 2, 3],
            "days_past_due": [0, 15, 100]
        })
        
        result = analyzer.get_dpd_buckets(df)
        
        assert result["dpd_bucket"].iloc[0] == "Current"
        assert result["dpd_bucket"].iloc[1] == "1-30"
        assert result["dpd_bucket"].iloc[2] == "31+"
    
    def test_get_dpd_buckets_missing_column(self):
        """Test that ValueError is raised when days_past_due is missing."""
        df = pd.DataFrame({"loan_id": [1, 2, 3]})
        
        with pytest.raises(ValueError, match="days_past_due"):
            self.analyzer.get_dpd_buckets(df)
    
    def test_calculate_customer_segments(self):
        """Test customer segmentation."""
        df = pd.DataFrame({
            "loan_id": [1, 2, 3, 4, 5, 6, 7, 8],
            "customer_id": ["A", "B", "C", "D", "E", "F", "G", "H"],
            "outstanding_balance": [1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000]
        })
        
        result = self.analyzer.calculate_customer_segments(df)
        
        assert "segment" in result.columns
        assert len(result) == len(df)
        # Highest exposure should be segment A
        max_exposure_row = result.loc[result["outstanding_balance"].idxmax()]
        assert max_exposure_row["segment"] == "A"
    
    def test_calculate_customer_segments_few_customers(self):
        """Test customer segmentation with few customers."""
        df = pd.DataFrame({
            "loan_id": [1, 2, 3],
            "customer_id": ["A", "B", "C"],
            "outstanding_balance": [1000, 2000, 3000]
        })
        
        result = self.analyzer.calculate_customer_segments(df)
        
        assert "segment" in result.columns
        # With less than 6 unique exposures, all should be F
        assert all(result["segment"] == "F")
    
    def test_determine_customer_type(self):
        """Test customer type determination."""
        loans_df = pd.DataFrame({
            "loan_id": [1, 2, 3, 4],
            "customer_id": ["A", "A", "B", "B"],
            "origination_date": pd.to_datetime(["2023-01-01", "2023-02-15", "2023-01-01", "2023-06-01"])
        })
        dpd_df = pd.DataFrame({
            "loan_id": [1, 2, 3, 4],
            "days_past_due": [0, 0, 0, 0]
        })
        
        result = self.analyzer.determine_customer_type(loans_df, dpd_df)
        
        assert "customer_type" in result.columns
        # First loan for each customer should be New
        assert result.iloc[0]["customer_type"] == "New"
        assert result.iloc[2]["customer_type"] == "New"
        # Second loan for customer A is within 90 days
        assert result.iloc[1]["customer_type"] == "Recurring"
        # Second loan for customer B is beyond 90 days
        assert result.iloc[3]["customer_type"] == "Recovered"
    
    def test_calculate_weighted_stats(self):
        """Test weighted statistics calculation."""
        df = pd.DataFrame({
            "loan_id": [1, 2, 3],
            "apr": [10.0, 15.0, 20.0],
            "outstanding_balance": [1000, 2000, 1000]
        })
        
        result = self.analyzer.calculate_weighted_stats(df)
        
        assert "weighted_apr" in result
        # Weighted average: (10*1000 + 15*2000 + 20*1000) / 4000 = 15.0
        expected = (10*1000 + 15*2000 + 20*1000) / 4000
        assert np.isclose(result["weighted_apr"], expected)
    
    def test_calculate_hhi(self):
        """Test HHI calculation."""
        df = pd.DataFrame({
            "customer_id": ["A", "B", "C"],
            "outstanding_balance": [5000, 3000, 2000]
        })
        
        result = self.analyzer.calculate_hhi(df)
        
        # HHI = (0.5^2 + 0.3^2 + 0.2^2) * 10000 = (0.25 + 0.09 + 0.04) * 10000 = 3800
        expected = 3800
        assert np.isclose(result, expected)
    
    def test_detect_loan_ids(self):
        """Test loan ID detection."""
        df = pd.DataFrame({
            "loan_id": [1, 2, 3],
            "amount": [1000, 2000, 3000]
        })
        
        col1, col2 = self.analyzer.detect_loan_ids(df)
        assert col1 == "loan_id"
        assert col2 == "loan_id"
    
    def test_detect_loan_ids_missing(self):
        """Test that ValueError is raised when loan ID is missing."""
        df = pd.DataFrame({
            "amount": [1000, 2000, 3000]
        })
        
        with pytest.raises(ValueError, match="Loan ID column not found"):
            self.analyzer.detect_loan_ids(df)


def test_calculate_revenue_metrics():
    """Test revenue metrics calculation."""
    from src.commercial_view.analyzer import calculate_revenue_metrics
    
    df = pd.DataFrame({
        "loan_id": [1, 2, 3],
        "principal": [10000, 20000, 30000],
        "interest_rate": [10.0, 15.0, 20.0],  # percentage
        "term": [12, 24, 36]  # months
    })
    
    result = calculate_revenue_metrics(df)
    
    assert "expected_revenue" in result.columns
    # For loan 1: 10000 * 0.10 * 1 = 1000
    assert np.isclose(result.iloc[0]["expected_revenue"], 1000)
    # For loan 2: 20000 * 0.15 * 2 = 6000
    assert np.isclose(result.iloc[1]["expected_revenue"], 6000)


def test_calculate_line_utilization():
    """Test line utilization calculation."""
    from src.commercial_view.analyzer import calculate_line_utilization
    
    df = pd.DataFrame({
        "loan_id": [1, 2, 3],
        "credit_line": [10000, 20000, 30000],
        "outstanding": [5000, 15000, 30000]
    })
    
    result = calculate_line_utilization(df)
    
    assert "line_utilization" in result.columns
    assert np.isclose(result.iloc[0]["line_utilization"], 0.5)
    assert np.isclose(result.iloc[1]["line_utilization"], 0.75)
    assert np.isclose(result.iloc[2]["line_utilization"], 1.0)


def test_calculate_customer_dpd_stats():
    """Test customer DPD statistics calculation."""
    from src.commercial_view.analyzer import calculate_customer_dpd_stats
    
    loans_df = pd.DataFrame({
        "loan_id": [1, 2, 3],
        "customer_id": ["A", "A", "B"]
    })
    
    dpd_df = pd.DataFrame({
        "loan_id": [1, 2, 3],
        "days_past_due": [0, 30, 60]
    })
    
    result = calculate_customer_dpd_stats(loans_df, dpd_df)
    
    assert "dpd_mean" in result.columns
    assert "dpd_median" in result.columns
    assert "dpd_max" in result.columns
    assert "dpd_min" in result.columns
    # Customer A has loans 1 and 2 with DPD 0 and 30
    customer_a_rows = result[result["customer_id"] == "A"]
    assert np.isclose(customer_a_rows.iloc[0]["dpd_mean"], 15.0)  # (0+30)/2
    assert np.isclose(customer_a_rows.iloc[0]["dpd_max"], 30.0)
