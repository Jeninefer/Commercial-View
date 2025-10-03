"""
Tests for PaymentProcessor DPD bucket classification.
"""

import unittest
import pandas as pd
import numpy as np
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from payment_processor import PaymentProcessor


class TestPaymentProcessor(unittest.TestCase):
    """Test cases for PaymentProcessor.assign_dpd_buckets method."""
    
    def setUp(self):
        """Set up test data."""
        self.processor = PaymentProcessor()
        
        # Create sample data with various DPD values
        self.sample_data = pd.DataFrame({
            'loan_id': range(1, 11),
            'days_past_due': [0, 15, 35, 65, 95, 125, 155, 185, 200, 365]
        })
    
    def test_default_threshold(self):
        """Test that default threshold is 180 days."""
        self.assertEqual(self.processor.dpd_threshold, 180)
    
    def test_custom_threshold(self):
        """Test custom threshold initialization."""
        custom_processor = PaymentProcessor(dpd_threshold=150)
        self.assertEqual(custom_processor.dpd_threshold, 150)
    
    def test_bucket_assignment(self):
        """Test that buckets are correctly assigned."""
        result = self.processor.assign_dpd_buckets(self.sample_data)
        
        # Check that all required columns are present
        self.assertIn('dpd_bucket', result.columns)
        self.assertIn('dpd_bucket_description', result.columns)
        self.assertIn('default_flag', result.columns)
        
        # Check specific bucket assignments
        self.assertEqual(result.loc[0, 'dpd_bucket'], 'Current')
        self.assertEqual(result.loc[1, 'dpd_bucket'], 'Current')
        self.assertEqual(result.loc[2, 'dpd_bucket'], 'DPD_30')
        self.assertEqual(result.loc[3, 'dpd_bucket'], 'DPD_60')
        self.assertEqual(result.loc[4, 'dpd_bucket'], 'DPD_90')
        self.assertEqual(result.loc[5, 'dpd_bucket'], 'DPD_120')
        self.assertEqual(result.loc[6, 'dpd_bucket'], 'DPD_120')
        self.assertEqual(result.loc[7, 'dpd_bucket'], 'DPD_180')
        self.assertEqual(result.loc[8, 'dpd_bucket'], 'DPD_180')
        self.assertEqual(result.loc[9, 'dpd_bucket'], 'DPD_180')
    
    def test_default_flag_at_180(self):
        """Test that default_flag is set correctly at 180 days threshold."""
        result = self.processor.assign_dpd_buckets(self.sample_data)
        
        # Loans < 180 days should not have default_flag = True
        self.assertFalse(result.loc[0, 'default_flag'])  # 0 days
        self.assertFalse(result.loc[4, 'default_flag'])  # 95 days
        self.assertFalse(result.loc[5, 'default_flag'])  # 125 days
        self.assertFalse(result.loc[6, 'default_flag'])  # 155 days
        
        # Loans >= 180 days should have default_flag = True
        self.assertTrue(result.loc[7, 'default_flag'])   # 185 days
        self.assertTrue(result.loc[8, 'default_flag'])   # 200 days
        self.assertTrue(result.loc[9, 'default_flag'])   # 365 days
    
    def test_high_risk_not_default(self):
        """Test that 90-179 day loans are High Risk but not default_flag=True."""
        result = self.processor.assign_dpd_buckets(self.sample_data)
        
        # 95 days - should be DPD_90 (High Risk) but default_flag=False
        row_95 = result.loc[result['days_past_due'] == 95].iloc[0]
        self.assertEqual(row_95['dpd_bucket'], 'DPD_90')
        self.assertIn('High Risk', row_95['dpd_bucket_description'])
        self.assertFalse(row_95['default_flag'])
        
        # 125 days - should be DPD_120 (High Risk) but default_flag=False
        row_125 = result.loc[result['days_past_due'] == 125].iloc[0]
        self.assertEqual(row_125['dpd_bucket'], 'DPD_120')
        self.assertIn('High Risk', row_125['dpd_bucket_description'])
        self.assertFalse(row_125['default_flag'])
    
    def test_boundary_values(self):
        """Test boundary values for bucket assignment."""
        boundary_data = pd.DataFrame({
            'loan_id': range(1, 9),
            'days_past_due': [29, 30, 59, 60, 89, 90, 179, 180]
        })
        
        result = self.processor.assign_dpd_buckets(boundary_data)
        
        # Test boundaries
        self.assertEqual(result.loc[0, 'dpd_bucket'], 'Current')     # 29
        self.assertEqual(result.loc[1, 'dpd_bucket'], 'DPD_30')      # 30
        self.assertEqual(result.loc[2, 'dpd_bucket'], 'DPD_30')      # 59
        self.assertEqual(result.loc[3, 'dpd_bucket'], 'DPD_60')      # 60
        self.assertEqual(result.loc[4, 'dpd_bucket'], 'DPD_60')      # 89
        self.assertEqual(result.loc[5, 'dpd_bucket'], 'DPD_90')      # 90
        self.assertEqual(result.loc[6, 'dpd_bucket'], 'DPD_120')     # 179
        self.assertEqual(result.loc[7, 'dpd_bucket'], 'DPD_180')     # 180
        
        # Default flag boundaries
        self.assertFalse(result.loc[6, 'default_flag'])  # 179 - not default
        self.assertTrue(result.loc[7, 'default_flag'])   # 180 - is default
    
    def test_custom_column_name(self):
        """Test using a custom column name for days past due."""
        custom_data = pd.DataFrame({
            'loan_id': [1, 2, 3],
            'custom_dpd': [50, 100, 200]
        })
        
        result = self.processor.assign_dpd_buckets(custom_data, dpd_column='custom_dpd')
        
        self.assertEqual(result.loc[0, 'dpd_bucket'], 'DPD_30')
        self.assertEqual(result.loc[1, 'dpd_bucket'], 'DPD_90')
        self.assertEqual(result.loc[2, 'dpd_bucket'], 'DPD_180')
    
    def test_missing_column_error(self):
        """Test that error is raised when dpd column is missing."""
        invalid_data = pd.DataFrame({
            'loan_id': [1, 2, 3],
            'amount': [1000, 2000, 3000]
        })
        
        with self.assertRaises(ValueError):
            self.processor.assign_dpd_buckets(invalid_data)
    
    def test_description_clarity(self):
        """Test that descriptions clearly indicate High Risk vs Default."""
        result = self.processor.assign_dpd_buckets(self.sample_data)
        
        # 95 days should mention "High Risk"
        desc_95 = result.loc[result['days_past_due'] == 95, 'dpd_bucket_description'].iloc[0]
        self.assertIn('High Risk', desc_95)
        self.assertNotIn('Default', desc_95)
        
        # 185 days should mention "Default"
        desc_185 = result.loc[result['days_past_due'] == 185, 'dpd_bucket_description'].iloc[0]
        self.assertIn('Default', desc_185)


if __name__ == '__main__':
    unittest.main()
