"""Tests for LoanAnalyzer class"""

import unittest
from datetime import date, datetime
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pandas as pd
import numpy as np
from commercial_view import LoanAnalyzer


class TestLoanAnalyzer(unittest.TestCase):
    """Test cases for LoanAnalyzer class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = LoanAnalyzer(dpd_threshold=90)
        
        # Sample schedule data
        self.schedule_df = pd.DataFrame({
            'loan_id': ['L001', 'L001', 'L001', 'L002', 'L002'],
            'due_date': ['2024-01-01', '2024-02-01', '2024-03-01', '2024-01-15', '2024-02-15'],
            'due_amount': [1000, 1000, 1000, 500, 500]
        })
        
        # Sample payment data
        self.payments_df = pd.DataFrame({
            'loan_id': ['L001', 'L001', 'L002'],
            'payment_date': ['2024-01-05', '2024-02-10', '2024-01-20'],
            'payment_amount': [1000, 500, 500]
        })
    
    def test_initialization(self):
        """Test LoanAnalyzer initialization"""
        analyzer = LoanAnalyzer(dpd_threshold=60)
        self.assertEqual(analyzer.dpd_threshold, 60)
        
        # Test default threshold
        analyzer_default = LoanAnalyzer()
        self.assertEqual(analyzer_default.dpd_threshold, 90)
    
    def test_standardize_dataframes(self):
        """Test dataframe standardization"""
        schedule_df, payments_df = self.analyzer.standardize_dataframes(
            self.schedule_df, self.payments_df
        )
        
        # Check that date columns are converted to date type
        self.assertTrue(isinstance(schedule_df['due_date'].iloc[0], date))
        self.assertTrue(isinstance(payments_df['payment_date'].iloc[0], date))
        
        # Check that amount columns are numeric
        self.assertTrue(pd.api.types.is_numeric_dtype(schedule_df['due_amount']))
        self.assertTrue(pd.api.types.is_numeric_dtype(payments_df['payment_amount']))
    
    def test_calculate_payment_timeline(self):
        """Test payment timeline calculation"""
        reference_date = date(2024, 3, 1)
        timeline = self.analyzer.calculate_payment_timeline(
            self.schedule_df, self.payments_df, reference_date
        )
        
        # Check that result has expected columns
        expected_cols = ['loan_id', 'date', 'due_amount', 'payment_amount',
                        'cumulative_due', 'cumulative_paid', 'cumulative_gap']
        for col in expected_cols:
            self.assertIn(col, timeline.columns)
        
        # Check that cumulative calculations are correct
        loan_001 = timeline[timeline['loan_id'] == 'L001']
        self.assertTrue((loan_001['cumulative_due'] >= 0).all())
        self.assertTrue((loan_001['cumulative_paid'] >= 0).all())
        
        # Check cumulative gap calculation
        for _, row in timeline.iterrows():
            self.assertAlmostEqual(
                row['cumulative_gap'],
                row['cumulative_due'] - row['cumulative_paid'],
                places=2
            )
    
    def test_calculate_payment_timeline_with_datetime(self):
        """Test payment timeline with datetime reference"""
        reference_datetime = datetime(2024, 3, 1, 12, 0, 0)
        timeline = self.analyzer.calculate_payment_timeline(
            self.schedule_df, self.payments_df, reference_datetime
        )
        
        self.assertIsInstance(timeline, pd.DataFrame)
        self.assertGreater(len(timeline), 0)
    
    def test_calculate_payment_timeline_default_reference(self):
        """Test payment timeline with default reference date"""
        timeline = self.analyzer.calculate_payment_timeline(
            self.schedule_df, self.payments_df
        )
        
        self.assertIsInstance(timeline, pd.DataFrame)
    
    def test_calculate_dpd(self):
        """Test DPD calculation"""
        reference_date = date(2024, 3, 15)
        dpd_result = self.analyzer.calculate_dpd(
            self.schedule_df, self.payments_df, reference_date
        )
        
        # Check that result has expected columns
        expected_cols = ['loan_id', 'past_due_amount', 'days_past_due',
                        'first_arrears_date', 'last_payment_date', 'last_due_date',
                        'is_default', 'reference_date']
        for col in expected_cols:
            self.assertIn(col, dpd_result.columns)
        
        # Check that each loan has one record
        self.assertEqual(len(dpd_result['loan_id'].unique()), len(dpd_result))
        
        # Check that past_due_amount is non-negative
        self.assertTrue((dpd_result['past_due_amount'] >= 0).all())
        
        # Check that days_past_due is non-negative
        self.assertTrue((dpd_result['days_past_due'] >= 0).all())
        
        # Check is_default is boolean
        self.assertTrue(dpd_result['is_default'].dtype == bool)
    
    def test_calculate_dpd_default_classification(self):
        """Test that default classification works correctly"""
        # Create a loan with significant arrears
        old_schedule = pd.DataFrame({
            'loan_id': ['L003'],
            'due_date': ['2023-01-01'],
            'due_amount': [5000]
        })
        
        old_payments = pd.DataFrame({
            'loan_id': ['L003'],
            'payment_date': ['2023-01-15'],
            'payment_amount': [1000]
        })
        
        reference_date = date(2024, 3, 15)
        dpd_result = self.analyzer.calculate_dpd(
            old_schedule, old_payments, reference_date
        )
        
        # Should be marked as default due to exceeding dpd_threshold
        loan_003 = dpd_result[dpd_result['loan_id'] == 'L003']
        self.assertTrue(loan_003['is_default'].iloc[0])
        self.assertGreater(loan_003['days_past_due'].iloc[0], 90)
    
    def test_calculate_dpd_with_datetime(self):
        """Test DPD calculation with datetime reference"""
        reference_datetime = datetime(2024, 3, 15, 12, 0, 0)
        dpd_result = self.analyzer.calculate_dpd(
            self.schedule_df, self.payments_df, reference_datetime
        )
        
        self.assertIsInstance(dpd_result, pd.DataFrame)
        self.assertEqual(dpd_result['reference_date'].iloc[0], date(2024, 3, 15))
    
    def test_empty_dataframes(self):
        """Test with empty dataframes"""
        empty_schedule = pd.DataFrame(columns=['loan_id', 'due_date', 'due_amount'])
        empty_payments = pd.DataFrame(columns=['loan_id', 'payment_date', 'payment_amount'])
        
        timeline = self.analyzer.calculate_payment_timeline(
            empty_schedule, empty_payments, date(2024, 1, 1)
        )
        
        self.assertEqual(len(timeline), 0)
    
    def test_no_payments(self):
        """Test loan with schedule but no payments"""
        no_payments = pd.DataFrame(columns=['loan_id', 'payment_date', 'payment_amount'])
        
        reference_date = date(2024, 3, 15)
        dpd_result = self.analyzer.calculate_dpd(
            self.schedule_df, no_payments, reference_date
        )
        
        # Should show past due amounts for all loans
        self.assertTrue((dpd_result['past_due_amount'] > 0).any())


if __name__ == '__main__':
    unittest.main()
