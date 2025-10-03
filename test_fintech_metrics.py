"""
Tests for Fintech Metrics Calculator

This module contains unit tests for the FintechMetricsCalculator class.
"""

import unittest
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from fintech_metrics import FintechMetricsCalculator


class TestFintechMetricsCalculator(unittest.TestCase):
    """Test suite for FintechMetricsCalculator"""

    def setUp(self):
        """Set up test fixtures"""
        self.calculator = FintechMetricsCalculator()

    def test_safe_division_normal(self):
        """Test safe_division with valid inputs"""
        result = self.calculator.safe_division(10, 2, 0.0)
        self.assertEqual(result, 5.0)

    def test_safe_division_zero_denominator(self):
        """Test safe_division with zero denominator"""
        result = self.calculator.safe_division(10, 0, 0.0)
        self.assertEqual(result, 0.0)

    def test_safe_division_nan_denominator(self):
        """Test safe_division with NaN denominator"""
        result = self.calculator.safe_division(10, np.nan, 0.0)
        self.assertEqual(result, 0.0)

    def test_safe_division_custom_default(self):
        """Test safe_division with custom default value"""
        result = self.calculator.safe_division(10, 0, -1.0)
        self.assertEqual(result, -1.0)

    def test_compute_gmv_with_loan_amount(self):
        """Test GMV calculation with loan_amount column"""
        loan_df = pd.DataFrame({
            'loan_amount': [1000, 2000, 3000],
            'loan_id': [1, 2, 3]
        })
        metrics = self.calculator.compute_fintech_metrics(loan_df)
        self.assertEqual(metrics['gmv'], 6000.0)

    def test_compute_gmv_with_amount(self):
        """Test GMV calculation with amount column"""
        loan_df = pd.DataFrame({
            'amount': [500, 1500, 2500],
            'loan_id': [1, 2, 3]
        })
        metrics = self.calculator.compute_fintech_metrics(loan_df)
        self.assertEqual(metrics['gmv'], 4500.0)

    def test_compute_gmv_with_monto_prestamo(self):
        """Test GMV calculation with monto_prestamo column (Spanish)"""
        loan_df = pd.DataFrame({
            'monto_prestamo': [100, 200, 300],
            'loan_id': [1, 2, 3]
        })
        metrics = self.calculator.compute_fintech_metrics(loan_df)
        self.assertEqual(metrics['gmv'], 600.0)

    def test_compute_gmv_missing_column(self):
        """Test GMV calculation when amount column is missing"""
        loan_df = pd.DataFrame({
            'loan_id': [1, 2, 3]
        })
        metrics = self.calculator.compute_fintech_metrics(loan_df)
        self.assertNotIn('gmv', metrics)

    def test_compute_default_rate_with_dpd(self):
        """Test default rate calculation with days_past_due column"""
        loan_df = pd.DataFrame({
            'loan_amount': [1000, 2000, 3000, 4000],
            'days_past_due': [0, 90, 180, 200]
        })
        metrics = self.calculator.compute_fintech_metrics(loan_df)
        # 2 loans have dpd >= 180 (loans with 180 and 200)
        self.assertEqual(metrics['default_rate'], 0.5)

    def test_compute_default_rate_with_dpd_column(self):
        """Test default rate calculation with dpd column"""
        loan_df = pd.DataFrame({
            'loan_amount': [1000, 2000, 3000],
            'dpd': [0, 100, 190]
        })
        metrics = self.calculator.compute_fintech_metrics(loan_df)
        # 1 loan has dpd >= 180
        self.assertAlmostEqual(metrics['default_rate'], 1/3, places=5)

    def test_compute_default_rate_custom_threshold(self):
        """Test default rate with custom threshold"""
        loan_df = pd.DataFrame({
            'loan_amount': [1000, 2000, 3000],
            'days_past_due': [0, 60, 90]
        })
        metrics = self.calculator.compute_fintech_metrics(loan_df, default_dpd_threshold=60)
        # 2 loans have dpd >= 60
        self.assertAlmostEqual(metrics['default_rate'], 2/3, places=5)

    def test_compute_take_rate(self):
        """Test take rate calculation"""
        loan_df = pd.DataFrame({
            'loan_amount': [1000, 2000, 3000],
            'revenue': [50, 100, 150]
        })
        metrics = self.calculator.compute_fintech_metrics(loan_df)
        # Total revenue = 300, GMV = 6000, take_rate = 300/6000 = 0.05
        self.assertEqual(metrics['take_rate'], 0.05)

    def test_compute_take_rate_no_gmv(self):
        """Test take rate when GMV is not calculated"""
        loan_df = pd.DataFrame({
            'loan_id': [1, 2, 3],
            'revenue': [50, 100, 150]
        })
        metrics = self.calculator.compute_fintech_metrics(loan_df)
        self.assertNotIn('take_rate', metrics)

    def test_compute_take_rate_zero_gmv(self):
        """Test take rate when GMV is zero"""
        loan_df = pd.DataFrame({
            'loan_amount': [0, 0, 0],
            'revenue': [50, 100, 150]
        })
        metrics = self.calculator.compute_fintech_metrics(loan_df)
        # GMV is 0, so take_rate should not be calculated
        self.assertNotIn('take_rate', metrics)

    def test_compute_avg_eir(self):
        """Test average EIR calculation"""
        loan_df = pd.DataFrame({
            'loan_amount': [1000, 2000, 3000],
            'eir': [0.1, 0.2, 0.3]
        })
        metrics = self.calculator.compute_fintech_metrics(loan_df)
        self.assertAlmostEqual(metrics['avg_eir'], 0.2, places=5)

    def test_compute_apr_eir_spread_from_columns(self):
        """Test APR-EIR spread calculation from individual columns"""
        loan_df = pd.DataFrame({
            'loan_amount': [1000, 2000, 3000],
            'apr': [0.15, 0.25, 0.35],
            'eir': [0.1, 0.2, 0.3]
        })
        metrics = self.calculator.compute_fintech_metrics(loan_df)
        self.assertAlmostEqual(metrics['avg_apr_eir_spread'], 0.05, places=5)

    def test_compute_apr_eir_spread_from_spread_column(self):
        """Test APR-EIR spread calculation from spread column"""
        loan_df = pd.DataFrame({
            'loan_amount': [1000, 2000, 3000],
            'apr': [0.15, 0.25, 0.35],
            'eir': [0.1, 0.2, 0.3],
            'apr_eir_spread': [0.04, 0.05, 0.06]
        })
        metrics = self.calculator.compute_fintech_metrics(loan_df)
        self.assertAlmostEqual(metrics['avg_apr_eir_spread'], 0.05, places=5)

    def test_compute_active_users_from_user_df(self):
        """Test active users calculation from user_df"""
        loan_df = pd.DataFrame({
            'loan_amount': [1000, 2000, 3000]
        })
        user_df = pd.DataFrame({
            'user_id': [1, 2, 3, 4, 5],
            'is_active': [1, 1, 0, 1, 0]
        })
        metrics = self.calculator.compute_fintech_metrics(loan_df, user_df=user_df)
        self.assertEqual(metrics['active_users'], 3)
        self.assertEqual(metrics['active_rate'], 0.6)

    def test_compute_active_users_from_payment_df(self):
        """Test active users calculation from payment_df"""
        loan_df = pd.DataFrame({
            'loan_amount': [1000, 2000, 3000]
        })
        # Create payment data with dates in the last 30 days and older
        today = pd.Timestamp.utcnow().normalize()
        recent_date = today - timedelta(days=15)
        old_date = today - timedelta(days=45)
        
        payment_df = pd.DataFrame({
            'customer_id': [1, 2, 3, 4, 1, 2],
            'date': [recent_date, recent_date, old_date, old_date, recent_date, old_date],
            'amount': [100, 200, 300, 400, 150, 250]
        })
        metrics = self.calculator.compute_fintech_metrics(loan_df, payment_df=payment_df)
        # Only customers 1 and 2 have payments in the last 30 days
        self.assertEqual(metrics['active_users'], 2)

    def test_compute_active_users_no_data(self):
        """Test active users when no user or payment data is provided"""
        loan_df = pd.DataFrame({
            'loan_amount': [1000, 2000, 3000]
        })
        metrics = self.calculator.compute_fintech_metrics(loan_df)
        self.assertNotIn('active_users', metrics)
        self.assertNotIn('active_rate', metrics)

    def test_compute_metrics_with_nan_values(self):
        """Test metrics calculation with NaN values in data"""
        loan_df = pd.DataFrame({
            'loan_amount': [1000, np.nan, 3000],
            'days_past_due': [0, np.nan, 190],
            'revenue': [50, np.nan, 150]
        })
        metrics = self.calculator.compute_fintech_metrics(loan_df)
        # NaN values should be treated as 0 for GMV
        self.assertEqual(metrics['gmv'], 4000.0)
        # For default rate, NaN dpd should be treated as 0
        self.assertAlmostEqual(metrics['default_rate'], 1/3, places=5)

    def test_compute_metrics_empty_dataframe(self):
        """Test metrics calculation with empty dataframe"""
        loan_df = pd.DataFrame()
        metrics = self.calculator.compute_fintech_metrics(loan_df)
        # Should return empty dict or handle gracefully
        self.assertIsInstance(metrics, dict)

    def test_compute_metrics_comprehensive(self):
        """Test comprehensive metrics calculation with all features"""
        loan_df = pd.DataFrame({
            'loan_amount': [1000, 2000, 3000, 4000, 5000],
            'days_past_due': [0, 30, 90, 180, 200],
            'revenue': [50, 100, 150, 200, 250],
            'apr': [0.12, 0.15, 0.18, 0.20, 0.22],
            'eir': [0.10, 0.12, 0.15, 0.17, 0.19]
        })
        user_df = pd.DataFrame({
            'user_id': [1, 2, 3, 4, 5],
            'is_active': [1, 1, 1, 0, 0]
        })
        
        metrics = self.calculator.compute_fintech_metrics(loan_df, user_df=user_df)
        
        # Verify all metrics are calculated
        self.assertIn('gmv', metrics)
        self.assertIn('default_rate', metrics)
        self.assertIn('take_rate', metrics)
        self.assertIn('avg_eir', metrics)
        self.assertIn('avg_apr_eir_spread', metrics)
        self.assertIn('active_users', metrics)
        self.assertIn('active_rate', metrics)
        
        # Verify values
        self.assertEqual(metrics['gmv'], 15000.0)
        self.assertEqual(metrics['default_rate'], 0.4)  # 2 out of 5
        self.assertEqual(metrics['take_rate'], 750.0 / 15000.0)
        self.assertEqual(metrics['active_users'], 3)
        self.assertEqual(metrics['active_rate'], 0.6)


if __name__ == '__main__':
    unittest.main()
