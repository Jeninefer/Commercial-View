"""
Test suite for KPI Analyzer

Tests all functionality of the KPIAnalyzer class including:
- Startup metrics computation
- Fintech metrics computation
- Valuation metrics computation
- Viability index computation
- Safe division utility
- JSON export functionality
"""

import json
import os
import tempfile
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from kpi_analyzer import KPIAnalyzer


class TestKPIAnalyzer:
    """Test cases for the KPIAnalyzer class."""

    @pytest.fixture
    def analyzer(self):
        """Create a KPIAnalyzer instance for testing."""
        return KPIAnalyzer()

    @pytest.fixture
    def sample_revenue_df(self):
        """Create sample revenue DataFrame."""
        return pd.DataFrame({
            "date": ["2023-01", "2023-02", "2023-03"],
            "revenue": [10000, 12000, 15000]
        })

    @pytest.fixture
    def sample_customer_df(self):
        """Create sample customer DataFrame."""
        return pd.DataFrame({
            "date": ["2023-01", "2023-02", "2023-03"],
            "customer_id": [1, 2, 3]
        })

    @pytest.fixture
    def sample_valuation_df(self):
        """Create sample valuation DataFrame."""
        return pd.DataFrame({
            "pre_money_valuation": [1000000],
            "investment_amount": [250000],
            "market_cap": [1500000],
            "total_debt": [100000],
            "cash": [50000],
            "revenue": [100000],
            "ebitda": [20000],
            "marketing_expense": [5000]
        })

    @pytest.fixture
    def sample_loan_df(self):
        """Create sample loan DataFrame."""
        return pd.DataFrame({
            "loan_id": [1, 2, 3, 4, 5],
            "amount": [10000, 20000, 15000, 30000, 25000],
            "dpd": [0, 30, 90, 200, 150],
            "status": ["active", "active", "active", "default", "npl"]
        })

    @pytest.fixture
    def sample_payment_df(self):
        """Create sample payment DataFrame."""
        return pd.DataFrame({
            "payment_id": [1, 2, 3],
            "amount": [5000, 10000, 7500]
        })

    @pytest.fixture
    def sample_user_df(self):
        """Create sample user DataFrame."""
        return pd.DataFrame({
            "user_id": [1, 2, 3, 4, 5],
            "status": ["active", "active", "inactive", "active", "active"]
        })

    def test_safe_division_normal(self, analyzer):
        """Test safe division with normal values."""
        result = analyzer.safe_division(10, 2, 0.0)
        assert result == 5.0

    def test_safe_division_by_zero(self, analyzer):
        """Test safe division by zero returns default."""
        result = analyzer.safe_division(10, 0, 0.0)
        assert result == 0.0

    def test_safe_division_with_nan(self, analyzer):
        """Test safe division with NaN returns default."""
        result = analyzer.safe_division(np.nan, 5, 0.0)
        assert result == 0.0

    def test_safe_division_with_inf(self, analyzer):
        """Test safe division with infinity returns default."""
        result = analyzer.safe_division(np.inf, 5, 0.0)
        assert result == 0.0

    def test_compute_startup_metrics_basic(self, analyzer, sample_revenue_df, sample_customer_df):
        """Test basic startup metrics computation."""
        metrics = analyzer.compute_startup_metrics(sample_revenue_df, sample_customer_df)
        
        assert "total_revenue" in metrics
        assert metrics["total_revenue"] == 37000.0
        assert "total_customers" in metrics
        assert metrics["total_customers"] == 3

    def test_compute_startup_metrics_with_growth(self, analyzer, sample_revenue_df, sample_customer_df):
        """Test startup metrics with growth calculations."""
        metrics = analyzer.compute_startup_metrics(sample_revenue_df, sample_customer_df)
        
        assert "revenue_growth" in metrics
        # Growth from 12000 to 15000 = 3000/12000 = 0.25
        assert abs(metrics["revenue_growth"] - 0.25) < 0.01

    def test_compute_startup_metrics_with_marketing(self, analyzer, sample_revenue_df, sample_customer_df, sample_valuation_df):
        """Test startup metrics with marketing expense."""
        metrics = analyzer.compute_startup_metrics(
            sample_revenue_df, 
            sample_customer_df, 
            sample_valuation_df
        )
        
        assert "marketing_expense" in metrics
        assert metrics["marketing_expense"] == 5000.0
        assert "cac" in metrics

    def test_compute_startup_metrics_empty_dataframes(self, analyzer):
        """Test startup metrics with empty DataFrames."""
        metrics = analyzer.compute_startup_metrics(
            pd.DataFrame(), 
            pd.DataFrame()
        )
        
        assert isinstance(metrics, dict)

    def test_compute_fintech_metrics_basic(self, analyzer, sample_loan_df):
        """Test basic fintech metrics computation."""
        metrics = analyzer.compute_fintech_metrics(sample_loan_df)
        
        assert "total_loans" in metrics
        assert metrics["total_loans"] == 5
        assert "total_loan_amount" in metrics
        assert metrics["total_loan_amount"] == 100000.0

    def test_compute_fintech_metrics_with_defaults(self, analyzer, sample_loan_df):
        """Test fintech metrics with default rate calculation."""
        metrics = analyzer.compute_fintech_metrics(sample_loan_df, default_dpd_threshold=180)
        
        assert "default_rate" in metrics
        # 1 loan with dpd=200 >= 180
        assert metrics["default_rate"] == 0.2

    def test_compute_fintech_metrics_with_payments(self, analyzer, sample_loan_df, sample_payment_df):
        """Test fintech metrics with payment data."""
        metrics = analyzer.compute_fintech_metrics(
            sample_loan_df, 
            payment_df=sample_payment_df
        )
        
        assert "total_payments" in metrics
        assert metrics["total_payments"] == 22500.0
        assert "collection_rate" in metrics

    def test_compute_fintech_metrics_with_users(self, analyzer, sample_loan_df, sample_user_df):
        """Test fintech metrics with user data."""
        metrics = analyzer.compute_fintech_metrics(
            sample_loan_df,
            user_df=sample_user_df
        )
        
        assert "active_users" in metrics
        assert metrics["active_users"] == 4

    def test_compute_fintech_metrics_empty_dataframe(self, analyzer):
        """Test fintech metrics with empty DataFrame."""
        metrics = analyzer.compute_fintech_metrics(pd.DataFrame())
        
        assert isinstance(metrics, dict)
        assert len(metrics) == 0

    def test_compute_viability_index_high_score(self, analyzer):
        """Test viability index with high-performing metrics."""
        startup_metrics = {
            "total_revenue": 100000,
            "revenue_growth": 0.6,
            "total_customers": 1500,
            "ltv_cac_ratio": 4.0
        }
        
        score = analyzer.compute_viability_index(startup_metrics)
        assert score == 100.0

    def test_compute_viability_index_medium_score(self, analyzer):
        """Test viability index with medium-performing metrics."""
        startup_metrics = {
            "total_revenue": 50000,
            "revenue_growth": 0.3,
            "total_customers": 150
        }
        
        score = analyzer.compute_viability_index(startup_metrics)
        assert 50.0 <= score <= 70.0

    def test_compute_viability_index_low_score(self, analyzer):
        """Test viability index with low-performing metrics."""
        startup_metrics = {
            "total_revenue": 0,
            "total_customers": 5
        }
        
        score = analyzer.compute_viability_index(startup_metrics)
        assert score <= 20.0

    def test_compute_viability_index_empty(self, analyzer):
        """Test viability index with empty metrics."""
        score = analyzer.compute_viability_index({})
        assert score == 0.0

    def test_export_json(self, analyzer):
        """Test JSON export functionality."""
        test_data = {"test": "data", "value": 123}
        
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            analyzer._export_json(test_data, "test_export")
            
            assert os.path.exists("test_export.json")
            
            with open("test_export.json", "r") as f:
                loaded_data = json.load(f)
            
            assert loaded_data == test_data

    def test_compute_kpis_full(
        self, 
        analyzer, 
        sample_revenue_df, 
        sample_customer_df, 
        sample_valuation_df,
        sample_loan_df,
        sample_payment_df,
        sample_user_df
    ):
        """Test full KPI computation with all data sources."""
        result = analyzer.compute_kpis(
            revenue_df=sample_revenue_df,
            customer_df=sample_customer_df,
            valuation_df=sample_valuation_df,
            loan_df=sample_loan_df,
            payment_df=sample_payment_df,
            user_df=sample_user_df,
            default_dpd_threshold=180
        )
        
        assert "startup" in result
        assert "fintech" in result
        assert "valuation" in result
        assert "viability_index" in result
        
        # Check startup metrics
        assert isinstance(result["startup"], dict)
        assert "total_revenue" in result["startup"]
        
        # Check fintech metrics
        assert isinstance(result["fintech"], dict)
        assert "total_loans" in result["fintech"]
        
        # Check valuation metrics
        assert isinstance(result["valuation"], dict)
        assert "pre_money_valuation" in result["valuation"]
        assert "post_money_valuation" in result["valuation"]
        assert "enterprise_value" in result["valuation"]
        
        # Check viability index
        assert isinstance(result["viability_index"], float)
        assert 0 <= result["viability_index"] <= 100

    def test_compute_kpis_without_fintech(
        self,
        analyzer,
        sample_revenue_df,
        sample_customer_df,
        sample_valuation_df
    ):
        """Test KPI computation without fintech data."""
        result = analyzer.compute_kpis(
            revenue_df=sample_revenue_df,
            customer_df=sample_customer_df,
            valuation_df=sample_valuation_df
        )
        
        assert "startup" in result
        assert "fintech" in result
        assert result["fintech"] == {}
        assert "valuation" in result
        assert "viability_index" in result

    def test_compute_kpis_valuation_calculations(
        self,
        analyzer,
        sample_revenue_df,
        sample_customer_df,
        sample_valuation_df
    ):
        """Test valuation calculations in KPI computation."""
        result = analyzer.compute_kpis(
            revenue_df=sample_revenue_df,
            customer_df=sample_customer_df,
            valuation_df=sample_valuation_df
        )
        
        valuation = result["valuation"]
        
        # Pre-money valuation
        assert valuation["pre_money_valuation"] == 1000000.0
        
        # Post-money valuation = pre + investment
        assert valuation["post_money_valuation"] == 1250000.0
        
        # Enterprise value = market_cap + debt - cash
        assert valuation["enterprise_value"] == 1550000.0
        
        # Revenue multiple = EV / revenue
        assert valuation["revenue_multiple"] == 15.5
        
        # Dilution = investment / post
        expected_dilution = 250000 / 1250000
        assert abs(valuation["dilution"] - expected_dilution) < 0.001

    def test_compute_kpis_with_export(
        self,
        analyzer,
        sample_revenue_df,
        sample_customer_df,
        sample_valuation_df
    ):
        """Test KPI computation with export enabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            
            result = analyzer.compute_kpis(
                revenue_df=sample_revenue_df,
                customer_df=sample_customer_df,
                valuation_df=sample_valuation_df,
                export=True
            )
            
            assert os.path.exists("kpis.json")
            
            with open("kpis.json", "r") as f:
                exported_data = json.load(f)
            
            assert "startup" in exported_data
            assert "valuation" in exported_data

    def test_compute_kpis_valuation_with_nan(self, analyzer):
        """Test KPI computation with NaN values in valuation."""
        valuation_df = pd.DataFrame({
            "pre_money_valuation": [np.nan],
            "investment_amount": [100000],
            "market_cap": [500000],
            "total_debt": [0],
            "cash": [0],
            "revenue": [0],
            "ebitda": [np.nan]
        })
        
        result = analyzer.compute_kpis(
            revenue_df=pd.DataFrame(),
            customer_df=pd.DataFrame(),
            valuation_df=valuation_df
        )
        
        valuation = result["valuation"]
        assert np.isnan(valuation["post_money_valuation"])
        assert valuation["enterprise_value"] == 500000.0

    def test_compute_kpis_handles_valuation_error(self, analyzer):
        """Test that KPI computation handles valuation errors gracefully."""
        # Create a valuation_df that might cause issues
        valuation_df = pd.DataFrame({})
        
        result = analyzer.compute_kpis(
            revenue_df=pd.DataFrame(),
            customer_df=pd.DataFrame(),
            valuation_df=valuation_df
        )
        
        # Should have valuation dict with default values
        assert "valuation" in result
        assert isinstance(result["valuation"], dict)

    def test_compute_kpis_ebitda_multiple_with_negative_ebitda(self, analyzer):
        """Test that EBITDA multiple is NaN when EBITDA is negative."""
        valuation_df = pd.DataFrame({
            "pre_money_valuation": [1000000],
            "investment_amount": [0],
            "market_cap": [1000000],
            "total_debt": [0],
            "cash": [0],
            "revenue": [100000],
            "ebitda": [-10000]
        })
        
        result = analyzer.compute_kpis(
            revenue_df=pd.DataFrame(),
            customer_df=pd.DataFrame(),
            valuation_df=valuation_df
        )
        
        assert np.isnan(result["valuation"]["ebitda_multiple"])

    def test_compute_kpis_ebitda_multiple_with_zero_ebitda(self, analyzer):
        """Test that EBITDA multiple is NaN when EBITDA is zero."""
        valuation_df = pd.DataFrame({
            "pre_money_valuation": [1000000],
            "investment_amount": [0],
            "market_cap": [1000000],
            "total_debt": [0],
            "cash": [0],
            "revenue": [100000],
            "ebitda": [0]
        })
        
        result = analyzer.compute_kpis(
            revenue_df=pd.DataFrame(),
            customer_df=pd.DataFrame(),
            valuation_df=valuation_df
        )
        
        assert np.isnan(result["valuation"]["ebitda_multiple"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
