"""Tests for FeatureEngineer.classify_client_type method"""

import unittest
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from commercial_view import FeatureEngineer


class TestClassifyClientType(unittest.TestCase):
    """Test cases for classify_client_type method"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.fe = FeatureEngineer()
        self.reference_date = datetime(2024, 1, 1)
        
    def test_new_customer_single_loan(self):
        """Test classification of new customer with 1 loan"""
        df = pd.DataFrame({
            'customer_id': [1],
            'loan_count': [1],
            'last_active_date': ['2023-12-01']
        })
        result = self.fe.classify_client_type(df, reference_date=self.reference_date)
        self.assertEqual(result['customer_type'].iloc[0], 'New')
        
    def test_new_customer_zero_loans(self):
        """Test classification of new customer with 0 loans"""
        df = pd.DataFrame({
            'customer_id': [1],
            'loan_count': [0],
            'last_active_date': ['2023-12-01']
        })
        result = self.fe.classify_client_type(df, reference_date=self.reference_date)
        self.assertEqual(result['customer_type'].iloc[0], 'New')
        
    def test_recurrent_customer(self):
        """Test classification of recurrent customer (>1 loan, gap <=90 days)"""
        df = pd.DataFrame({
            'customer_id': [1],
            'loan_count': [3],
            'last_active_date': ['2023-11-15']  # 47 days gap
        })
        result = self.fe.classify_client_type(df, reference_date=self.reference_date)
        self.assertEqual(result['customer_type'].iloc[0], 'Recurrent')
        self.assertEqual(result['days_since_last'].iloc[0], 47)
        
    def test_recovered_customer(self):
        """Test classification of recovered customer (>1 loan, gap >90 days)"""
        df = pd.DataFrame({
            'customer_id': [1],
            'loan_count': [2],
            'last_active_date': ['2023-09-01']  # 122 days gap
        })
        result = self.fe.classify_client_type(df, reference_date=self.reference_date)
        self.assertEqual(result['customer_type'].iloc[0], 'Recovered')
        self.assertEqual(result['days_since_last'].iloc[0], 122)
        
    def test_boundary_90_days(self):
        """Test boundary condition at exactly 90 days"""
        df = pd.DataFrame({
            'customer_id': [1],
            'loan_count': [2],
            'last_active_date': ['2023-10-03']  # Exactly 90 days
        })
        result = self.fe.classify_client_type(df, reference_date=self.reference_date)
        self.assertEqual(result['customer_type'].iloc[0], 'Recurrent')
        self.assertEqual(result['days_since_last'].iloc[0], 90)
        
    def test_boundary_91_days(self):
        """Test boundary condition at 91 days"""
        df = pd.DataFrame({
            'customer_id': [1],
            'loan_count': [2],
            'last_active_date': ['2023-10-02']  # 91 days
        })
        result = self.fe.classify_client_type(df, reference_date=self.reference_date)
        self.assertEqual(result['customer_type'].iloc[0], 'Recovered')
        self.assertEqual(result['days_since_last'].iloc[0], 91)
        
    def test_missing_last_active_column(self):
        """Test when last_active_date column is missing"""
        df = pd.DataFrame({
            'customer_id': [1],
            'loan_count': [2]
        })
        result = self.fe.classify_client_type(df, reference_date=self.reference_date)
        self.assertTrue(pd.isna(result['days_since_last'].iloc[0]))
        self.assertEqual(result['customer_type'].iloc[0], 'Recurrent')
        
    def test_multiple_customers(self):
        """Test classification of multiple customers with different types"""
        df = pd.DataFrame({
            'customer_id': [1, 2, 3, 4],
            'loan_count': [1, 3, 2, 5],
            'last_active_date': ['2023-12-01', '2023-11-15', '2023-08-01', '2023-12-25']
        })
        result = self.fe.classify_client_type(df, reference_date=self.reference_date)
        
        self.assertEqual(result['customer_type'].iloc[0], 'New')
        self.assertEqual(result['customer_type'].iloc[1], 'Recurrent')
        self.assertEqual(result['customer_type'].iloc[2], 'Recovered')
        self.assertEqual(result['customer_type'].iloc[3], 'Recurrent')
        
    def test_default_reference_date(self):
        """Test with default reference date (current date)"""
        df = pd.DataFrame({
            'customer_id': [1],
            'loan_count': [1],
            'last_active_date': [datetime.now().date()]
        })
        result = self.fe.classify_client_type(df)
        self.assertIn('customer_type', result.columns)
        self.assertEqual(result['customer_type'].iloc[0], 'New')
        
    def test_custom_column_names(self):
        """Test with custom column names"""
        df = pd.DataFrame({
            'cust_id': [1],
            'num_loans': [2],
            'last_date': ['2023-09-01']
        })
        result = self.fe.classify_client_type(
            df,
            customer_id_col='cust_id',
            loan_count_col='num_loans',
            last_active_col='last_date',
            reference_date=self.reference_date
        )
        self.assertEqual(result['customer_type'].iloc[0], 'Recovered')
        
    def test_null_loan_count(self):
        """Test handling of null loan count"""
        df = pd.DataFrame({
            'customer_id': [1],
            'loan_count': [None],
            'last_active_date': ['2023-12-01']
        })
        result = self.fe.classify_client_type(df, reference_date=self.reference_date)
        self.assertEqual(result['customer_type'].iloc[0], 'New')
        
    def test_dataframe_not_modified(self):
        """Test that original dataframe is not modified"""
        df = pd.DataFrame({
            'customer_id': [1],
            'loan_count': [2],
            'last_active_date': ['2023-11-01']
        })
        original_columns = df.columns.tolist()
        result = self.fe.classify_client_type(df, reference_date=self.reference_date)
        
        self.assertEqual(df.columns.tolist(), original_columns)
        self.assertNotIn('customer_type', df.columns)
        self.assertNotIn('days_since_last', df.columns)


if __name__ == '__main__':
    unittest.main()
