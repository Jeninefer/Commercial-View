"""Unit tests for the KPI calculation system"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config import KPIConfig
from src.comprehensive_kpi_calculator import ComprehensiveKPICalculator
from src.kpi_calculator import KPICalculator
from src.enhanced_kpi_calculator import EnhancedKPICalculator


class TestKPIConfig(unittest.TestCase):
    """Test cases for KPIConfig"""

    def test_default_config(self):
        """Test default configuration values"""
        config = KPIConfig()
        self.assertEqual(config.risk_threshold_high, 0.7)
        self.assertEqual(config.risk_threshold_medium, 0.4)
        self.assertEqual(config.default_interest_rate, 0.05)
        self.assertEqual(config.default_ltv_ratio, 0.8)
        self.assertTrue(config.enable_advanced_metrics)
        self.assertTrue(config.enable_validation)

    def test_custom_config(self):
        """Test custom configuration values"""
        config = KPIConfig(
            risk_threshold_high=0.9,
            risk_threshold_medium=0.5,
            default_interest_rate=0.06,
            enable_advanced_metrics=False
        )
        self.assertEqual(config.risk_threshold_high, 0.9)
        self.assertEqual(config.risk_threshold_medium, 0.5)
        self.assertEqual(config.default_interest_rate, 0.06)
        self.assertFalse(config.enable_advanced_metrics)

    def test_invalid_thresholds(self):
        """Test that invalid thresholds raise ValueError"""
        with self.assertRaises(ValueError):
            KPIConfig(risk_threshold_high=0.3, risk_threshold_medium=0.5)

    def test_invalid_ltv_ratio(self):
        """Test that invalid LTV ratio raises ValueError"""
        with self.assertRaises(ValueError):
            KPIConfig(default_ltv_ratio=1.5)
        with self.assertRaises(ValueError):
            KPIConfig(default_ltv_ratio=-0.1)


class TestComprehensiveKPICalculator(unittest.TestCase):
    """Test cases for ComprehensiveKPICalculator"""

    def setUp(self):
        """Set up test fixtures"""
        self.calculator = ComprehensiveKPICalculator()

    def test_empty_dataframe_raises_error(self):
        """Test that empty DataFrame raises ValueError"""
        empty_df = pd.DataFrame()
        with self.assertRaises(ValueError):
            self.calculator.calculate_all_kpis(empty_df)

    def test_non_dataframe_raises_error(self):
        """Test that non-DataFrame input raises ValueError"""
        with self.assertRaises(ValueError):
            self.calculator.calculate_all_kpis([])

    def test_basic_loan_data(self):
        """Test calculation with basic loan data"""
        loan_df = pd.DataFrame({
            "loan_id": [1, 2, 3],
            "principal": [10000, 20000, 15000],
            "balance": [8000, 18000, 14000],
        })
        result = self.calculator.calculate_all_kpis(loan_df)
        
        self.assertIn("total_loans", result)
        self.assertEqual(result["total_loans"], 3)
        self.assertIn("portfolio_metrics", result)
        self.assertEqual(result["portfolio_metrics"]["count"], 3)
        self.assertEqual(result["portfolio_metrics"]["total_principal"], 45000)

    def test_loan_data_with_status(self):
        """Test calculation with loan status data"""
        loan_df = pd.DataFrame({
            "loan_id": [1, 2, 3, 4],
            "principal": [10000, 20000, 15000, 12000],
            "status": ["active", "active", "default", "charged_off"],
        })
        result = self.calculator.calculate_all_kpis(loan_df)
        
        self.assertIn("risk_metrics", result)
        self.assertEqual(result["risk_metrics"]["default_count"], 2)
        self.assertEqual(result["risk_metrics"]["default_rate"], 0.5)

    def test_loan_data_with_ltv(self):
        """Test calculation with LTV data"""
        loan_df = pd.DataFrame({
            "loan_id": [1, 2, 3],
            "loan_amount": [80000, 150000, 120000],
            "collateral_value": [100000, 200000, 150000],
        })
        result = self.calculator.calculate_all_kpis(loan_df)
        
        self.assertIn("risk_metrics", result)
        self.assertIn("average_ltv", result["risk_metrics"])
        # Average LTV: (0.8 + 0.75 + 0.8) / 3 = 0.7833...
        self.assertAlmostEqual(result["risk_metrics"]["average_ltv"], 0.7833, places=2)


class TestKPICalculator(unittest.TestCase):
    """Test cases for KPICalculator"""

    def setUp(self):
        """Set up test fixtures"""
        self.calculator = KPICalculator()

    def test_startup_metrics_basic(self):
        """Test basic startup metrics calculation"""
        revenue_df = pd.DataFrame({
            "amount": [1000, 2000, 1500],
            "period": ["monthly", "monthly", "one-time"],
        })
        customer_df = pd.DataFrame({
            "customer_id": [1, 2, 3],
            "acquisition_cost": [100, 150, 120],
        })
        
        result = self.calculator.compute_startup_metrics(revenue_df, customer_df)
        
        self.assertEqual(result["total_customers"], 3)
        self.assertEqual(result["total_revenue"], 4500)
        self.assertEqual(result["mrr"], 3000)
        self.assertAlmostEqual(result["average_cac"], 123.33, places=2)

    def test_fintech_metrics_basic(self):
        """Test basic fintech metrics calculation"""
        transaction_df = pd.DataFrame({
            "transaction_id": [1, 2, 3, 4],
            "amount": [100, 200, 150, 300],
            "status": ["success", "success", "failed", "completed"],
            "payment_method": ["card", "card", "bank", "card"],
        })
        
        result = self.calculator.compute_fintech_metrics(transaction_df)
        
        self.assertEqual(result["total_transactions"], 4)
        self.assertEqual(result["total_transaction_volume"], 750)
        self.assertEqual(result["transaction_success_rate"], 0.75)
        self.assertIn("payment_method_distribution", result)

    def test_valuation_metrics_basic(self):
        """Test basic valuation metrics calculation"""
        revenue_df = pd.DataFrame({
            "amount": [1000, 2000, 1500],
            "period": ["monthly", "monthly", "monthly"],
        })
        customer_df = pd.DataFrame({
            "customer_id": [1, 2, 3],
            "status": ["active", "active", "churned"],
        })
        transaction_df = pd.DataFrame({
            "transaction_id": [1, 2, 3],
            "amount": [100, 200, 150],
        })
        
        result = self.calculator.compute_valuation_metrics(revenue_df, customer_df, transaction_df)
        
        self.assertIn("average_cltv", result)
        self.assertEqual(result["average_cltv"], 1500)
        self.assertIn("arr", result)
        self.assertEqual(result["arr"], 54000)  # (1000 + 2000 + 1500) * 12
        self.assertIn("churn_rate", result)
        self.assertAlmostEqual(result["churn_rate"], 1/3, places=2)

    def test_empty_dataframes(self):
        """Test handling of empty DataFrames"""
        empty_df = pd.DataFrame()
        
        result = self.calculator.compute_startup_metrics(empty_df, empty_df)
        self.assertEqual(result["total_customers"], 0)
        
        result = self.calculator.compute_fintech_metrics(empty_df)
        self.assertEqual(result["total_transactions"], 0)


class TestEnhancedKPICalculator(unittest.TestCase):
    """Test cases for EnhancedKPICalculator"""

    def setUp(self):
        """Set up test fixtures"""
        self.calculator = EnhancedKPICalculator()
        self.loan_df = pd.DataFrame({
            "loan_id": [1, 2, 3],
            "principal": [10000, 20000, 15000],
            "balance": [8000, 18000, 14000],
        })
        self.revenue_df = pd.DataFrame({
            "amount": [1000, 2000],
            "period": ["monthly", "monthly"],
        })
        self.customer_df = pd.DataFrame({
            "customer_id": [1, 2],
        })
        self.transaction_df = pd.DataFrame({
            "transaction_id": [1, 2],
            "amount": [100, 200],
        })

    def test_calculate_portfolio_kpis(self):
        """Test portfolio KPI calculation"""
        result = self.calculator.calculate_portfolio_kpis(self.loan_df)
        
        self.assertIn("total_loans", result)
        self.assertEqual(result["total_loans"], 3)
        self.assertIn("portfolio_metrics", result)

    def test_calculate_portfolio_kpis_empty_dataframe(self):
        """Test that empty DataFrame raises ValueError"""
        with self.assertRaises(ValueError):
            self.calculator.calculate_portfolio_kpis(pd.DataFrame())

    def test_calculate_business_metrics(self):
        """Test business metrics calculation"""
        result = self.calculator.calculate_business_metrics(
            self.revenue_df, self.customer_df, self.transaction_df
        )
        
        self.assertIn("startup_metrics", result)
        self.assertIn("fintech_metrics", result)
        self.assertIn("valuation_metrics", result)

    def test_calculate_business_metrics_invalid_input(self):
        """Test that non-DataFrame input raises ValueError"""
        with self.assertRaises(ValueError):
            self.calculator.calculate_business_metrics([], self.customer_df, self.transaction_df)

    def test_calculate_all_metrics_with_all_data(self):
        """Test calculation of all metrics when all data is provided"""
        result = self.calculator.calculate_all_metrics(
            self.loan_df,
            self.revenue_df,
            self.customer_df,
            self.transaction_df
        )
        
        self.assertIn("calculation_timestamp", result)
        self.assertIn("data_summary", result)
        self.assertIn("portfolio_kpis", result)
        self.assertIn("business_metrics", result)
        
        # Check data summary
        self.assertEqual(result["data_summary"]["loans_count"], 3)
        self.assertTrue(result["data_summary"]["revenue_available"])
        self.assertTrue(result["data_summary"]["customer_data_available"])
        self.assertTrue(result["data_summary"]["transaction_data_available"])
        
        # Business metrics should be calculated
        self.assertIn("startup_metrics", result["business_metrics"])

    def test_calculate_all_metrics_without_business_data(self):
        """Test calculation when business data is not provided"""
        result = self.calculator.calculate_all_metrics(self.loan_df)
        
        self.assertIn("portfolio_kpis", result)
        self.assertIn("business_metrics", result)
        
        # Business metrics should be skipped
        self.assertEqual(result["business_metrics"]["status"], "skipped")
        self.assertEqual(result["business_metrics"]["reason"], "missing or empty inputs")
        
        # Data summary should reflect missing data
        self.assertFalse(result["data_summary"]["revenue_available"])
        self.assertFalse(result["data_summary"]["customer_data_available"])
        self.assertFalse(result["data_summary"]["transaction_data_available"])

    def test_calculate_all_metrics_with_partial_business_data(self):
        """Test calculation when only some business data is provided"""
        result = self.calculator.calculate_all_metrics(
            self.loan_df,
            revenue_df=self.revenue_df,
            customer_df=None,
            transaction_df=None
        )
        
        # Business metrics should be skipped
        self.assertEqual(result["business_metrics"]["status"], "skipped")

    def test_calculate_all_metrics_with_empty_business_data(self):
        """Test calculation when business DataFrames are empty"""
        empty_df = pd.DataFrame()
        result = self.calculator.calculate_all_metrics(
            self.loan_df,
            revenue_df=empty_df,
            customer_df=empty_df,
            transaction_df=empty_df
        )
        
        # Business metrics should be skipped
        self.assertEqual(result["business_metrics"]["status"], "skipped")

    def test_calculate_all_metrics_invalid_loan_df(self):
        """Test that invalid loan_df raises ValueError"""
        with self.assertRaises(ValueError):
            self.calculator.calculate_all_metrics(pd.DataFrame())
        
        with self.assertRaises(ValueError):
            self.calculator.calculate_all_metrics([])


if __name__ == "__main__":
    unittest.main()
