"""Unit tests for FeatureEngineer class."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from feature_engineer import FeatureEngineer


class TestFeatureEngineer:
    """Test suite for FeatureEngineer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.fe = FeatureEngineer()
        self.reference_date = datetime(2024, 1, 1)
    
    def test_classify_new_customer(self):
        """Test classification of new customers (loan_count <= 1)."""
        df = pd.DataFrame({
            'customer_id': [1, 2],
            'loan_count': [0, 1],
            'last_active_date': ['2023-12-01', '2023-11-01']
        })
        
        result = self.fe.classify_client_type(
            df,
            reference_date=self.reference_date
        )
        
        assert 'customer_type' in result.columns
        assert result.loc[0, 'customer_type'] == 'New'
        assert result.loc[1, 'customer_type'] == 'New'
    
    def test_classify_recurrent_customer(self):
        """Test classification of recurrent customers (>1 loan and days_since_last <= 90)."""
        # Create a date 60 days before reference date
        recent_date = (self.reference_date - timedelta(days=60)).strftime('%Y-%m-%d')
        
        df = pd.DataFrame({
            'customer_id': [1],
            'loan_count': [3],
            'last_active_date': [recent_date]
        })
        
        result = self.fe.classify_client_type(
            df,
            reference_date=self.reference_date
        )
        
        assert result.loc[0, 'customer_type'] == 'Recurrent'
        assert result.loc[0, 'days_since_last'] == 60
    
    def test_classify_recovered_customer(self):
        """Test classification of recovered customers (>1 loan and days_since_last > 90)."""
        # Create a date 100 days before reference date
        old_date = (self.reference_date - timedelta(days=100)).strftime('%Y-%m-%d')
        
        df = pd.DataFrame({
            'customer_id': [1],
            'loan_count': [2],
            'last_active_date': [old_date]
        })
        
        result = self.fe.classify_client_type(
            df,
            reference_date=self.reference_date
        )
        
        assert result.loc[0, 'customer_type'] == 'Recovered'
        assert result.loc[0, 'days_since_last'] == 100
    
    def test_boundary_condition_90_days(self):
        """Test boundary condition at exactly 90 days."""
        # Exactly 90 days should be Recurrent (not > 90)
        date_90 = (self.reference_date - timedelta(days=90)).strftime('%Y-%m-%d')
        
        df = pd.DataFrame({
            'customer_id': [1],
            'loan_count': [2],
            'last_active_date': [date_90]
        })
        
        result = self.fe.classify_client_type(
            df,
            reference_date=self.reference_date
        )
        
        assert result.loc[0, 'customer_type'] == 'Recurrent'
        assert result.loc[0, 'days_since_last'] == 90
    
    def test_boundary_condition_91_days(self):
        """Test boundary condition at 91 days."""
        # 91 days should be Recovered (> 90)
        date_91 = (self.reference_date - timedelta(days=91)).strftime('%Y-%m-%d')
        
        df = pd.DataFrame({
            'customer_id': [1],
            'loan_count': [2],
            'last_active_date': [date_91]
        })
        
        result = self.fe.classify_client_type(
            df,
            reference_date=self.reference_date
        )
        
        assert result.loc[0, 'customer_type'] == 'Recovered'
        assert result.loc[0, 'days_since_last'] == 91
    
    def test_missing_last_active_column(self):
        """Test handling when last_active_date column is missing."""
        df = pd.DataFrame({
            'customer_id': [1, 2],
            'loan_count': [0, 3]
        })
        
        result = self.fe.classify_client_type(df)
        
        assert 'days_since_last' in result.columns
        assert pd.isna(result.loc[0, 'days_since_last'])
        # Without last_active_date, classification is based only on loan_count
        assert result.loc[0, 'customer_type'] == 'New'  # loan_count <= 1
        assert result.loc[1, 'customer_type'] == 'Recurrent'  # loan_count > 1, no date info
    
    def test_custom_column_names(self):
        """Test with custom column names."""
        df = pd.DataFrame({
            'cust_id': [1],
            'num_loans': [2],
            'last_date': ['2023-10-01']
        })
        
        result = self.fe.classify_client_type(
            df,
            customer_id_col='cust_id',
            loan_count_col='num_loans',
            last_active_col='last_date',
            reference_date=self.reference_date
        )
        
        assert 'customer_type' in result.columns
        # 93 days before reference date => Recovered
        assert result.loc[0, 'customer_type'] == 'Recovered'
    
    def test_default_reference_date(self):
        """Test that default reference_date uses current date."""
        df = pd.DataFrame({
            'customer_id': [1],
            'loan_count': [1],
            'last_active_date': ['2023-01-01']
        })
        
        # Should not raise an error
        result = self.fe.classify_client_type(df)
        
        assert 'customer_type' in result.columns
        assert 'days_since_last' in result.columns
    
    def test_null_loan_count(self):
        """Test handling of null (NaN) loan count values.
        
        Note: The implementation uses explicit NaN checking for loan_count.
        When loan_count is NaN, classification is based on days_since_last.
        If days_since_last < 90, the customer is classified as Recurrent.
        """
        df = pd.DataFrame({
            'customer_id': [1, 2],
            'loan_count': [None, np.nan],
            'last_active_date': ['2023-12-01', '2023-11-01']
        })
        
        result = self.fe.classify_client_type(
            df,
            reference_date=self.reference_date
        )
        
        # Due to NaN behavior, these are classified based on days_since_last
        # Since days_since_last < 90, they're classified as Recurrent
        assert result.loc[0, 'customer_type'] == 'Recurrent'
        assert result.loc[1, 'customer_type'] == 'Recurrent'
    
    def test_multiple_customer_types(self):
        """Test a mix of different customer types."""
        df = pd.DataFrame({
            'customer_id': [1, 2, 3, 4],
            'loan_count': [0, 2, 3, 5],
            'last_active_date': [
                '2023-12-01',  # New (loan_count = 0)
                '2023-10-20',  # Recurrent (loan_count = 2, 73 days)
                '2023-09-01',  # Recovered (loan_count = 3, 122 days)
                '2023-12-25'   # Recurrent (loan_count = 5, 7 days)
            ]
        })
        
        result = self.fe.classify_client_type(
            df,
            reference_date=self.reference_date
        )
        
        assert result.loc[0, 'customer_type'] == 'New'
        assert result.loc[1, 'customer_type'] == 'Recurrent'
        assert result.loc[2, 'customer_type'] == 'Recovered'
        assert result.loc[3, 'customer_type'] == 'Recurrent'
    
    def test_dataframe_not_modified(self):
        """Test that original DataFrame is not modified."""
        df = pd.DataFrame({
            'customer_id': [1],
            'loan_count': [2],
            'last_active_date': ['2023-12-01']
        })
        
        original_columns = df.columns.tolist()
        result = self.fe.classify_client_type(df, reference_date=self.reference_date)
        
        # Original DataFrame should not have new columns
        assert df.columns.tolist() == original_columns
        assert 'customer_type' not in df.columns
        # Result should have new columns
        assert 'customer_type' in result.columns
