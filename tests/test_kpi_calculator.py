"""Tests for Commercial View KPI Calculator."""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

import sys
sys.path.insert(0, '/home/runner/work/Commercial-View/Commercial-View/src')

from commercial_view.kpi_calculator import (
    KPIConfig,
    ComprehensiveKPICalculator,
    _require_df,
    calculate_comprehensive_kpis,
    calculate_exposure_metrics,
    calculate_yield_metrics,
    calculate_delinquency_metrics,
    calculate_utilization_metrics,
    calculate_segment_mix_metrics,
    calculate_vintage_metrics,
)


class TestRequireDF(unittest.TestCase):
    """Test the _require_df validation function."""
    
    def test_valid_dataframe(self):
        """Test that valid non-empty DataFrame passes validation."""
        df = pd.DataFrame({'col1': [1, 2, 3]})
        # Should not raise an exception
        _require_df(df, "test_df")
    
    def test_empty_dataframe(self):
        """Test that empty DataFrame raises ValueError."""
        df = pd.DataFrame()
        with self.assertRaises(ValueError) as context:
            _require_df(df, "test_df")
        self.assertIn("test_df must be a non-empty pandas DataFrame", str(context.exception))
    
    def test_non_dataframe(self):
        """Test that non-DataFrame raises ValueError."""
        not_df = [1, 2, 3]
        with self.assertRaises(ValueError) as context:
            _require_df(not_df, "test_df")
        self.assertIn("test_df must be a non-empty pandas DataFrame", str(context.exception))


class TestKPIConfig(unittest.TestCase):
    """Test KPIConfig dataclass."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = KPIConfig()
        self.assertTrue(config.include_exposure_metrics)
        self.assertTrue(config.include_yield_metrics)
        self.assertTrue(config.include_delinquency_metrics)
        self.assertEqual(config.delinquency_days_threshold, 30)
        self.assertEqual(config.precision, 2)
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = KPIConfig(
            include_exposure_metrics=False,
            delinquency_days_threshold=60,
            precision=4
        )
        self.assertFalse(config.include_exposure_metrics)
        self.assertEqual(config.delinquency_days_threshold, 60)
        self.assertEqual(config.precision, 4)


class TestExposureMetrics(unittest.TestCase):
    """Test exposure metrics calculation."""
    
    def setUp(self):
        """Set up test data."""
        self.loan_df = pd.DataFrame({
            'balance': [1000.0, 2000.0, 3000.0, 4000.0],
            'principal': [900.0, 1800.0, 2700.0, 3600.0],
            'outstanding_amount': [100.0, 200.0, 300.0, 400.0]
        })
    
    def test_exposure_metrics(self):
        """Test basic exposure metrics calculation."""
        metrics = calculate_exposure_metrics(self.loan_df)
        
        self.assertEqual(metrics['total_balance'], 10000.0)
        self.assertEqual(metrics['average_balance'], 2500.0)
        self.assertEqual(metrics['median_balance'], 2500.0)
        self.assertEqual(metrics['max_balance'], 4000.0)
        self.assertEqual(metrics['min_balance'], 1000.0)
        self.assertEqual(metrics['total_principal'], 9000.0)
        self.assertEqual(metrics['total_outstanding'], 1000.0)
    
    def test_exposure_metrics_empty_df(self):
        """Test that empty DataFrame raises ValueError."""
        empty_df = pd.DataFrame()
        with self.assertRaises(ValueError):
            calculate_exposure_metrics(empty_df)


class TestYieldMetrics(unittest.TestCase):
    """Test yield metrics calculation."""
    
    def setUp(self):
        """Set up test data."""
        self.loan_df = pd.DataFrame({
            'balance': [1000.0, 2000.0, 3000.0, 4000.0],
            'interest_rate': [5.0, 6.0, 7.0, 8.0],
            'interest_income': [50.0, 120.0, 210.0, 320.0]
        })
    
    def test_yield_metrics(self):
        """Test basic yield metrics calculation."""
        metrics = calculate_yield_metrics(self.loan_df)
        
        self.assertEqual(metrics['average_interest_rate'], 6.5)
        self.assertAlmostEqual(metrics['weighted_average_rate'], 7.0, places=1)
        self.assertEqual(metrics['total_interest_income'], 700.0)
        self.assertEqual(metrics['average_interest_income'], 175.0)
        self.assertAlmostEqual(metrics['portfolio_yield'], 7.0, places=1)


class TestDelinquencyMetrics(unittest.TestCase):
    """Test delinquency metrics calculation."""
    
    def setUp(self):
        """Set up test data."""
        self.loan_df = pd.DataFrame({
            'balance': [1000.0, 2000.0, 3000.0, 4000.0],
            'delinquent': [0, 1, 0, 1],
            'days_past_due': [0, 45, 10, 120]
        })
    
    def test_delinquency_metrics(self):
        """Test basic delinquency metrics calculation."""
        metrics = calculate_delinquency_metrics(self.loan_df)
        
        self.assertEqual(metrics['delinquency_rate'], 50.0)
        self.assertEqual(metrics['delinquent_count'], 2)
        self.assertEqual(metrics['current_count'], 2)
        self.assertAlmostEqual(metrics['average_days_past_due'], 43.75)
        self.assertEqual(metrics['max_days_past_due'], 120.0)
        self.assertEqual(metrics['delinquent_balance'], 6000.0)
        self.assertEqual(metrics['delinquent_balance_rate'], 60.0)
    
    def test_delinquency_buckets(self):
        """Test delinquency bucket calculations."""
        metrics = calculate_delinquency_metrics(self.loan_df)
        
        self.assertEqual(metrics['dpd_0_30'], 2)
        self.assertEqual(metrics['dpd_31_60'], 1)
        self.assertEqual(metrics['dpd_61_90'], 0)
        self.assertEqual(metrics['dpd_90_plus'], 1)


class TestUtilizationMetrics(unittest.TestCase):
    """Test utilization metrics calculation."""
    
    def setUp(self):
        """Set up test data."""
        self.loan_df = pd.DataFrame({
            'balance': [500.0, 1500.0, 3000.0, 4000.0],
            'credit_limit': [1000.0, 2000.0, 4000.0, 5000.0]
        })
    
    def test_utilization_metrics(self):
        """Test basic utilization metrics calculation."""
        metrics = calculate_utilization_metrics(self.loan_df)
        
        self.assertAlmostEqual(metrics['average_utilization_rate'], 70.0, places=1)
        self.assertEqual(metrics['portfolio_utilization_rate'], 75.0)
        self.assertEqual(metrics['total_available_credit'], 3000.0)
    
    def test_utilization_buckets(self):
        """Test utilization bucket calculations."""
        metrics = calculate_utilization_metrics(self.loan_df)
        
        self.assertEqual(metrics['utilization_0_25'], 0)
        self.assertEqual(metrics['utilization_25_50'], 1)
        self.assertEqual(metrics['utilization_50_75'], 2)
        self.assertEqual(metrics['utilization_75_100'], 1)


class TestSegmentMixMetrics(unittest.TestCase):
    """Test segment mix metrics calculation."""
    
    def setUp(self):
        """Set up test data."""
        self.loan_df = pd.DataFrame({
            'balance': [1000.0, 2000.0, 3000.0, 4000.0],
            'segment': ['retail', 'commercial', 'retail', 'commercial'],
            'product_type': ['term_loan', 'line_of_credit', 'term_loan', 'term_loan']
        })
    
    def test_segment_distribution(self):
        """Test segment distribution calculations."""
        metrics = calculate_segment_mix_metrics(self.loan_df)
        
        self.assertEqual(metrics['segment_retail_count'], 2)
        self.assertEqual(metrics['segment_commercial_count'], 2)
        self.assertEqual(metrics['segment_retail_pct'], 50.0)
        self.assertEqual(metrics['segment_commercial_pct'], 50.0)
        self.assertEqual(metrics['segment_retail_balance'], 4000.0)
        self.assertEqual(metrics['segment_commercial_balance'], 6000.0)
    
    def test_product_distribution(self):
        """Test product type distribution calculations."""
        metrics = calculate_segment_mix_metrics(self.loan_df)
        
        self.assertEqual(metrics['product_term_loan_count'], 3)
        self.assertEqual(metrics['product_line_of_credit_count'], 1)


class TestVintageMetrics(unittest.TestCase):
    """Test vintage metrics calculation."""
    
    def setUp(self):
        """Set up test data."""
        base_date = datetime(2020, 1, 1)
        self.loan_df = pd.DataFrame({
            'balance': [1000.0, 2000.0, 3000.0, 4000.0],
            'loan_age': [365, 730, 1095, 1460],
            'origination_date': [
                base_date,
                base_date + timedelta(days=365),
                base_date + timedelta(days=730),
                base_date + timedelta(days=1095)
            ],
            'maturity_date': [
                base_date + timedelta(days=1825),
                base_date + timedelta(days=2190),
                base_date + timedelta(days=2555),
                base_date + timedelta(days=2920)
            ]
        })
    
    def test_vintage_age_metrics(self):
        """Test loan age metrics calculation."""
        metrics = calculate_vintage_metrics(self.loan_df)
        
        self.assertEqual(metrics['average_loan_age'], 912.5)
        self.assertEqual(metrics['median_loan_age'], 912.5)
        self.assertEqual(metrics['max_loan_age'], 1460.0)
        self.assertEqual(metrics['min_loan_age'], 365.0)
    
    def test_vintage_date_metrics(self):
        """Test origination date metrics."""
        metrics = calculate_vintage_metrics(self.loan_df)
        
        self.assertIn('earliest_origination', metrics)
        self.assertIn('latest_origination', metrics)


class TestComprehensiveKPICalculator(unittest.TestCase):
    """Test ComprehensiveKPICalculator class."""
    
    def setUp(self):
        """Set up test data."""
        self.loan_df = pd.DataFrame({
            'balance': [1000.0, 2000.0, 3000.0, 4000.0],
            'principal': [900.0, 1800.0, 2700.0, 3600.0],
            'interest_rate': [5.0, 6.0, 7.0, 8.0],
            'delinquent': [0, 1, 0, 1],
            'days_past_due': [0, 45, 10, 120],
            'credit_limit': [2000.0, 3000.0, 4000.0, 5000.0],
            'segment': ['retail', 'commercial', 'retail', 'commercial'],
            'loan_age': [365, 730, 1095, 1460]
        })
    
    def test_calculate_all_kpis(self):
        """Test comprehensive KPI calculation."""
        calculator = ComprehensiveKPICalculator()
        results = calculator.calculate_all_kpis(self.loan_df)
        
        self.assertIn('exposure_metrics', results)
        self.assertIn('yield_metrics', results)
        self.assertIn('delinquency_metrics', results)
        self.assertIn('utilization_metrics', results)
        self.assertIn('segment_mix_metrics', results)
        self.assertIn('vintage_metrics', results)
        self.assertIn('metadata', results)
    
    def test_calculate_all_kpis_with_config(self):
        """Test comprehensive KPI calculation with custom config."""
        config = KPIConfig(
            include_exposure_metrics=True,
            include_yield_metrics=False,
            include_metadata=False
        )
        calculator = ComprehensiveKPICalculator(config)
        results = calculator.calculate_all_kpis(self.loan_df)
        
        self.assertIn('exposure_metrics', results)
        self.assertNotIn('yield_metrics', results)
        self.assertNotIn('metadata', results)
    
    def test_public_api_function(self):
        """Test public API function."""
        results = calculate_comprehensive_kpis(self.loan_df)
        
        self.assertIn('exposure_metrics', results)
        self.assertIn('yield_metrics', results)
        self.assertIn('metadata', results)


if __name__ == '__main__':
    unittest.main()
