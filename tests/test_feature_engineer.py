"""
Tests for FeatureEngineer DPD bucket classification.
"""

import unittest
import pandas as pd
import numpy as np
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from feature_engineer import FeatureEngineer


class TestFeatureEngineer(unittest.TestCase):
    """Test cases for FeatureEngineer.assign_dpd_buckets method."""
    
    def setUp(self):
        """Set up test data."""
        self.engineer = FeatureEngineer()
        
        # Create sample data with various DPD values
        self.sample_data = pd.DataFrame({
            'loan_id': range(1, 11),
            'days_past_due': [0, 15, 35, 65, 95, 125, 155, 185, 200, 365]
        })
    
    def test_default_risk_threshold(self):
        """Test that default risk threshold is 90 days."""
        self.assertEqual(self.engineer.risk_threshold, 90)
    
    def test_custom_threshold(self):
        """Test custom threshold initialization."""
        custom_engineer = FeatureEngineer(risk_threshold=120)
        self.assertEqual(custom_engineer.risk_threshold, 120)
    
    def test_bucket_assignment(self):
        """Test that buckets are correctly assigned."""
        result = self.engineer.assign_dpd_buckets(self.sample_data)
        
        # Check that all required columns are present
        self.assertIn('dpd_bucket', result.columns)
        self.assertIn('dpd_risk_category', result.columns)
        self.assertIn('is_default', result.columns)
        
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
    
    def test_is_default_flag_at_90(self):
        """Test that is_default is set correctly at 90 days threshold (High Risk)."""
        result = self.engineer.assign_dpd_buckets(self.sample_data)
        
        # Loans < 90 days should not have is_default = True
        self.assertFalse(result.loc[0, 'is_default'])  # 0 days
        self.assertFalse(result.loc[1, 'is_default'])  # 15 days
        self.assertFalse(result.loc[2, 'is_default'])  # 35 days
        self.assertFalse(result.loc[3, 'is_default'])  # 65 days
        
        # Loans >= 90 days should have is_default = True (High Risk threshold)
        self.assertTrue(result.loc[4, 'is_default'])   # 95 days
        self.assertTrue(result.loc[5, 'is_default'])   # 125 days
        self.assertTrue(result.loc[6, 'is_default'])   # 155 days
        self.assertTrue(result.loc[7, 'is_default'])   # 185 days
        self.assertTrue(result.loc[8, 'is_default'])   # 200 days
        self.assertTrue(result.loc[9, 'is_default'])   # 365 days
    
    def test_risk_categories(self):
        """Test that risk categories are correctly assigned."""
        result = self.engineer.assign_dpd_buckets(self.sample_data)
        
        # Current
        self.assertEqual(result.loc[0, 'dpd_risk_category'], 'Current')
        
        # Early Delinquency
        self.assertEqual(result.loc[2, 'dpd_risk_category'], 'Early Delinquency')  # 35 days
        self.assertEqual(result.loc[3, 'dpd_risk_category'], 'Early Delinquency')  # 65 days
        
        # High Risk
        self.assertEqual(result.loc[4, 'dpd_risk_category'], 'High Risk')  # 95 days
        self.assertEqual(result.loc[5, 'dpd_risk_category'], 'High Risk')  # 125 days
        self.assertEqual(result.loc[6, 'dpd_risk_category'], 'High Risk')  # 155 days
        
        # Default
        self.assertEqual(result.loc[7, 'dpd_risk_category'], 'Default')  # 185 days
        self.assertEqual(result.loc[8, 'dpd_risk_category'], 'Default')  # 200 days
        self.assertEqual(result.loc[9, 'dpd_risk_category'], 'Default')  # 365 days
    
    def test_high_risk_threshold(self):
        """Test that 90+ days are marked as High Risk (is_default=True)."""
        result = self.engineer.assign_dpd_buckets(self.sample_data)
        
        # 95 days - should be DPD_90 (High Risk) with is_default=True
        row_95 = result.loc[result['days_past_due'] == 95].iloc[0]
        self.assertEqual(row_95['dpd_bucket'], 'DPD_90')
        self.assertEqual(row_95['dpd_risk_category'], 'High Risk')
        self.assertTrue(row_95['is_default'])
        
        # 125 days - should be DPD_120 (High Risk) with is_default=True
        row_125 = result.loc[result['days_past_due'] == 125].iloc[0]
        self.assertEqual(row_125['dpd_bucket'], 'DPD_120')
        self.assertEqual(row_125['dpd_risk_category'], 'High Risk')
        self.assertTrue(row_125['is_default'])
    
    def test_boundary_values(self):
        """Test boundary values for bucket assignment."""
        boundary_data = pd.DataFrame({
            'loan_id': range(1, 9),
            'days_past_due': [29, 30, 59, 60, 89, 90, 179, 180]
        })
        
        result = self.engineer.assign_dpd_buckets(boundary_data)
        
        # Test boundaries
        self.assertEqual(result.loc[0, 'dpd_bucket'], 'Current')     # 29
        self.assertEqual(result.loc[1, 'dpd_bucket'], 'DPD_30')      # 30
        self.assertEqual(result.loc[2, 'dpd_bucket'], 'DPD_30')      # 59
        self.assertEqual(result.loc[3, 'dpd_bucket'], 'DPD_60')      # 60
        self.assertEqual(result.loc[4, 'dpd_bucket'], 'DPD_60')      # 89
        self.assertEqual(result.loc[5, 'dpd_bucket'], 'DPD_90')      # 90
        self.assertEqual(result.loc[6, 'dpd_bucket'], 'DPD_120')     # 179
        self.assertEqual(result.loc[7, 'dpd_bucket'], 'DPD_180')     # 180
        
        # is_default flag boundaries (90 days threshold)
        self.assertFalse(result.loc[4, 'is_default'])  # 89 - not default
        self.assertTrue(result.loc[5, 'is_default'])   # 90 - is default (High Risk)
    
    def test_custom_column_name(self):
        """Test using a custom column name for days past due."""
        custom_data = pd.DataFrame({
            'loan_id': [1, 2, 3],
            'custom_dpd': [50, 100, 200]
        })
        
        result = self.engineer.assign_dpd_buckets(custom_data, dpd_column='custom_dpd')
        
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
            self.engineer.assign_dpd_buckets(invalid_data)
    
    def test_difference_from_payment_processor(self):
        """Test that is_default is more aggressive than default_flag would be."""
        result = self.engineer.assign_dpd_buckets(self.sample_data)
        
        # Between 90-179 days: is_default should be True (for risk analysis)
        # This is different from PaymentProcessor where default_flag would be False
        row_95 = result.loc[result['days_past_due'] == 95].iloc[0]
        self.assertTrue(row_95['is_default'])  # FeatureEngineer: High Risk
        
        row_125 = result.loc[result['days_past_due'] == 125].iloc[0]
        self.assertTrue(row_125['is_default'])  # FeatureEngineer: High Risk
        
        row_155 = result.loc[result['days_past_due'] == 155].iloc[0]
        self.assertTrue(row_155['is_default'])  # FeatureEngineer: High Risk


if __name__ == '__main__':
    unittest.main()
