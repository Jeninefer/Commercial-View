"""
Unit tests for MetricsCalculator
"""
import unittest
import pandas as pd
import numpy as np
from src.metrics_calculator import MetricsCalculator


class TestMetricsCalculator(unittest.TestCase):
    """Test cases for MetricsCalculator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.calculator = MetricsCalculator()
    
    def test_safe_division_normal(self):
        """Test safe_division with normal values"""
        result = self.calculator.safe_division(10, 2, 0.0)
        self.assertEqual(result, 5.0)
    
    def test_safe_division_zero_denominator(self):
        """Test safe_division with zero denominator"""
        result = self.calculator.safe_division(10, 0, 0.0)
        self.assertEqual(result, 0.0)
        
        result = self.calculator.safe_division(10, 0, np.inf)
        self.assertEqual(result, np.inf)
    
    def test_safe_division_nan_denominator(self):
        """Test safe_division with NaN denominator"""
        result = self.calculator.safe_division(10, np.nan, -1.0)
        self.assertEqual(result, -1.0)
    
    def test_mrr_arr_calculation(self):
        """Test MRR and ARR calculation"""
        revenue_df = pd.DataFrame({
            'date': ['2023-01-01', '2023-02-01', '2023-03-01'],
            'recurring_revenue': [10000, 12000, 15000]
        })
        customer_df = pd.DataFrame({'customer_id': [1, 2, 3]})
        
        metrics = self.calculator.compute_startup_metrics(revenue_df, customer_df)
        
        self.assertIn('mrr', metrics)
        self.assertIn('arr', metrics)
        self.assertEqual(metrics['mrr'], 15000)  # Latest value
        self.assertEqual(metrics['arr'], 15000 * 12)
    
    def test_churn_rate_with_counts(self):
        """Test churn rate calculation using churn_count and start_count"""
        revenue_df = pd.DataFrame({'date': ['2023-01-01']})
        customer_df = pd.DataFrame({
            'churn_count': [5, 10, 8],
            'start_count': [100, 150, 120]
        })
        
        metrics = self.calculator.compute_startup_metrics(revenue_df, customer_df)
        
        self.assertIn('churn_rate', metrics)
        # (5+10+8) / (100+150+120) = 23/370
        expected_churn = 23.0 / 370.0
        self.assertAlmostEqual(metrics['churn_rate'], expected_churn, places=6)
    
    def test_churn_rate_with_is_churned(self):
        """Test churn rate calculation using is_churned column"""
        revenue_df = pd.DataFrame({'date': ['2023-01-01']})
        customer_df = pd.DataFrame({
            'is_churned': [1, 0, 1, 0, 0, 1, 0, 0, 0, 0]  # 3 churned out of 10
        })
        
        metrics = self.calculator.compute_startup_metrics(revenue_df, customer_df)
        
        self.assertIn('churn_rate', metrics)
        self.assertAlmostEqual(metrics['churn_rate'], 0.3, places=6)
    
    def test_nrr_calculation(self):
        """Test Net Revenue Retention calculation"""
        revenue_df = pd.DataFrame({
            'date': ['2023-01-01', '2023-02-01'],
            'start_revenue': [100000, 120000],
            'end_revenue': [110000, 135000]
        })
        customer_df = pd.DataFrame({'customer_id': [1, 2]})
        
        metrics = self.calculator.compute_startup_metrics(revenue_df, customer_df)
        
        self.assertIn('nrr', metrics)
        # (110000 + 135000) / (100000 + 120000) = 245000 / 220000
        expected_nrr = 245000.0 / 220000.0
        self.assertAlmostEqual(metrics['nrr'], expected_nrr, places=6)
    
    def test_cac_calculation(self):
        """Test Customer Acquisition Cost calculation"""
        revenue_df = pd.DataFrame({'date': ['2023-01-01']})
        customer_df = pd.DataFrame({
            'new_customers': [10, 15, 20]
        })
        expense_df = pd.DataFrame({
            'marketing_expense': [5000, 7500, 10000]
        })
        
        metrics = self.calculator.compute_startup_metrics(revenue_df, customer_df, expense_df)
        
        self.assertIn('cac', metrics)
        # (5000 + 7500 + 10000) / (10 + 15 + 20) = 22500 / 45 = 500
        self.assertAlmostEqual(metrics['cac'], 500.0, places=2)
    
    def test_arpu_calculation(self):
        """Test Average Revenue Per User calculation"""
        revenue_df = pd.DataFrame({
            'date': ['2023-01-01', '2023-02-01'],
            'revenue': [10000, 15000],
            'customer_count': [100, 120]
        })
        customer_df = pd.DataFrame({
            'new_customers': [10, 15]
        })
        expense_df = pd.DataFrame({
            'marketing_expense': [1000, 1500]
        })
        
        metrics = self.calculator.compute_startup_metrics(revenue_df, customer_df, expense_df)
        
        self.assertIn('arpu', metrics)
        # (10000 + 15000) / (100 + 120) = 25000 / 220
        expected_arpu = 25000.0 / 220.0
        self.assertAlmostEqual(metrics['arpu'], expected_arpu, places=2)
    
    def test_ltv_calculation(self):
        """Test Lifetime Value calculation"""
        revenue_df = pd.DataFrame({
            'date': ['2023-01-01'],
            'revenue': [10000],
            'customer_count': [100]
        })
        customer_df = pd.DataFrame({
            'new_customers': [10],
            'churn_count': [5],
            'start_count': [100]
        })
        expense_df = pd.DataFrame({
            'marketing_expense': [1000]
        })
        
        metrics = self.calculator.compute_startup_metrics(revenue_df, customer_df, expense_df)
        
        self.assertIn('ltv', metrics)
        self.assertIn('arpu', metrics)
        self.assertIn('churn_rate', metrics)
        
        # ARPU = 10000 / 100 = 100
        # Churn = 5 / 100 = 0.05
        # LTV = ARPU / churn_rate = 100 / 0.05 = 2000
        expected_ltv = 100.0 / 0.05
        self.assertAlmostEqual(metrics['ltv'], expected_ltv, places=2)
    
    def test_ltv_cac_ratio(self):
        """Test LTV to CAC ratio calculation"""
        revenue_df = pd.DataFrame({
            'date': ['2023-01-01'],
            'revenue': [10000],
            'customer_count': [100]
        })
        customer_df = pd.DataFrame({
            'new_customers': [10],
            'churn_count': [5],
            'start_count': [100]
        })
        expense_df = pd.DataFrame({
            'marketing_expense': [1000]
        })
        
        metrics = self.calculator.compute_startup_metrics(revenue_df, customer_df, expense_df)
        
        self.assertIn('ltv_cac_ratio', metrics)
        # CAC = 1000 / 10 = 100
        # LTV = 100 / 0.05 = 2000
        # Ratio = 2000 / 100 = 20
        self.assertAlmostEqual(metrics['ltv_cac_ratio'], 20.0, places=2)
    
    def test_burn_and_runway_calculation(self):
        """Test monthly burn and runway calculation"""
        revenue_df = pd.DataFrame({'date': ['2023-01-01']})
        customer_df = pd.DataFrame({'customer_id': [1]})
        expense_df = pd.DataFrame({
            'date': ['2023-01-01', '2023-02-01', '2023-03-01', '2023-04-01'],
            'total_expense': [10000, 12000, 11000, 13000],
            'cash_balance': [100000, 90000, 78000, 65000]
        })
        
        metrics = self.calculator.compute_startup_metrics(revenue_df, customer_df, expense_df)
        
        self.assertIn('monthly_burn', metrics)
        self.assertIn('runway_months', metrics)
        
        # Last 3 months: 12000, 11000, 13000 -> avg = 12000
        expected_burn = (12000 + 11000 + 13000) / 3.0
        self.assertAlmostEqual(metrics['monthly_burn'], expected_burn, places=2)
        
        # Runway = cash_balance / monthly_burn = 65000 / 12000
        expected_runway = 65000.0 / expected_burn
        self.assertAlmostEqual(metrics['runway_months'], expected_runway, places=2)
    
    def test_empty_dataframes(self):
        """Test with empty dataframes"""
        revenue_df = pd.DataFrame()
        customer_df = pd.DataFrame()
        
        metrics = self.calculator.compute_startup_metrics(revenue_df, customer_df)
        
        # Should return empty dict or dict with no metrics
        self.assertIsInstance(metrics, dict)
    
    def test_missing_columns(self):
        """Test with missing required columns"""
        revenue_df = pd.DataFrame({'some_column': [1, 2, 3]})
        customer_df = pd.DataFrame({'other_column': [1, 2, 3]})
        
        # Should not raise exception, just log warnings
        metrics = self.calculator.compute_startup_metrics(revenue_df, customer_df)
        
        self.assertIsInstance(metrics, dict)
    
    def test_no_expense_df(self):
        """Test when expense_df is None"""
        revenue_df = pd.DataFrame({
            'date': ['2023-01-01'],
            'recurring_revenue': [10000]
        })
        customer_df = pd.DataFrame({'customer_id': [1]})
        
        metrics = self.calculator.compute_startup_metrics(revenue_df, customer_df, None)
        
        self.assertIsInstance(metrics, dict)
        self.assertIn('mrr', metrics)
        self.assertNotIn('monthly_burn', metrics)
        self.assertNotIn('runway_months', metrics)
    
    def test_zero_churn_no_ltv(self):
        """Test that LTV is not calculated when churn is zero"""
        revenue_df = pd.DataFrame({
            'date': ['2023-01-01'],
            'revenue': [10000],
            'customer_count': [100]
        })
        customer_df = pd.DataFrame({
            'new_customers': [10],
            'churn_count': [0],
            'start_count': [100]
        })
        expense_df = pd.DataFrame({
            'marketing_expense': [1000]
        })
        
        metrics = self.calculator.compute_startup_metrics(revenue_df, customer_df, expense_df)
        
        # LTV should not be calculated when churn is 0
        self.assertNotIn('ltv', metrics)
    
    def test_invalid_dates_handling(self):
        """Test handling of invalid dates"""
        revenue_df = pd.DataFrame({
            'date': ['invalid', '2023-02-01', None],
            'recurring_revenue': [10000, 12000, 15000]
        })
        customer_df = pd.DataFrame({'customer_id': [1, 2, 3]})
        
        # Should not raise exception
        metrics = self.calculator.compute_startup_metrics(revenue_df, customer_df)
        
        self.assertIsInstance(metrics, dict)


if __name__ == '__main__':
    unittest.main()
