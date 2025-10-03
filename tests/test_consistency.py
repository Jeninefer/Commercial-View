"""
Tests for consistency between PaymentProcessor and FeatureEngineer DPD classification.
"""

import unittest
import pandas as pd
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from payment_processor import PaymentProcessor
from feature_engineer import FeatureEngineer


class TestDPDConsistency(unittest.TestCase):
    """Test cases for consistency between PaymentProcessor and FeatureEngineer."""
    
    def setUp(self):
        """Set up test data and both processors."""
        self.processor = PaymentProcessor()
        self.engineer = FeatureEngineer()
        
        # Create comprehensive test data
        self.test_data = pd.DataFrame({
            'loan_id': range(1, 12),
            'days_past_due': [0, 15, 45, 75, 89, 90, 100, 150, 179, 180, 300]
        })
    
    def test_bucket_labels_consistency(self):
        """Test that bucket labels are consistent between both methods."""
        processor_result = self.processor.assign_dpd_buckets(self.test_data.copy())
        engineer_result = self.engineer.assign_dpd_buckets(self.test_data.copy())
        
        # Both should assign the same bucket labels
        for idx in range(len(self.test_data)):
            self.assertEqual(
                processor_result.loc[idx, 'dpd_bucket'],
                engineer_result.loc[idx, 'dpd_bucket'],
                f"Bucket mismatch at index {idx} with DPD {self.test_data.loc[idx, 'days_past_due']}"
            )
    
    def test_default_threshold_difference(self):
        """Test the documented difference between default_flag (180) and is_default (90)."""
        processor_result = self.processor.assign_dpd_buckets(self.test_data.copy())
        engineer_result = self.engineer.assign_dpd_buckets(self.test_data.copy())
        
        # Test loans between 90-179 days
        # These should have is_default=True but default_flag=False
        dpd_values = [90, 100, 150, 179]
        
        for dpd in dpd_values:
            row_idx = self.test_data[self.test_data['days_past_due'] == dpd].index[0]
            
            # FeatureEngineer: is_default should be True (High Risk at 90+)
            self.assertTrue(
                engineer_result.loc[row_idx, 'is_default'],
                f"Expected is_default=True for {dpd} days (High Risk)"
            )
            
            # PaymentProcessor: default_flag should be False (not yet accounting default)
            self.assertFalse(
                processor_result.loc[row_idx, 'default_flag'],
                f"Expected default_flag=False for {dpd} days (not yet accounting default)"
            )
    
    def test_180_plus_agreement(self):
        """Test that both methods agree on 180+ days as default/high risk."""
        processor_result = self.processor.assign_dpd_buckets(self.test_data.copy())
        engineer_result = self.engineer.assign_dpd_buckets(self.test_data.copy())
        
        # Test loans >= 180 days
        dpd_values = [180, 300]
        
        for dpd in dpd_values:
            row_idx = self.test_data[self.test_data['days_past_due'] == dpd].index[0]
            
            # Both should flag these as problematic
            self.assertTrue(
                engineer_result.loc[row_idx, 'is_default'],
                f"Expected is_default=True for {dpd} days"
            )
            self.assertTrue(
                processor_result.loc[row_idx, 'default_flag'],
                f"Expected default_flag=True for {dpd} days"
            )
    
    def test_below_90_agreement(self):
        """Test that both methods agree on <90 days as not default."""
        processor_result = self.processor.assign_dpd_buckets(self.test_data.copy())
        engineer_result = self.engineer.assign_dpd_buckets(self.test_data.copy())
        
        # Test loans < 90 days
        dpd_values = [0, 15, 45, 75, 89]
        
        for dpd in dpd_values:
            row_idx = self.test_data[self.test_data['days_past_due'] == dpd].index[0]
            
            # Both should NOT flag these as default
            self.assertFalse(
                engineer_result.loc[row_idx, 'is_default'],
                f"Expected is_default=False for {dpd} days"
            )
            self.assertFalse(
                processor_result.loc[row_idx, 'default_flag'],
                f"Expected default_flag=False for {dpd} days"
            )
    
    def test_dpd_180_bucket_assignment(self):
        """Test that DPD_180 bucket is consistently assigned for 180+ days."""
        processor_result = self.processor.assign_dpd_buckets(self.test_data.copy())
        engineer_result = self.engineer.assign_dpd_buckets(self.test_data.copy())
        
        dpd_values = [180, 300]
        
        for dpd in dpd_values:
            row_idx = self.test_data[self.test_data['days_past_due'] == dpd].index[0]
            
            self.assertEqual(
                processor_result.loc[row_idx, 'dpd_bucket'],
                'DPD_180',
                f"Expected DPD_180 bucket for {dpd} days in PaymentProcessor"
            )
            self.assertEqual(
                engineer_result.loc[row_idx, 'dpd_bucket'],
                'DPD_180',
                f"Expected DPD_180 bucket for {dpd} days in FeatureEngineer"
            )
    
    def test_risk_segmentation_purpose(self):
        """Test that FeatureEngineer serves risk segmentation with 90+ threshold."""
        engineer_result = self.engineer.assign_dpd_buckets(self.test_data.copy())
        
        # Count loans flagged as is_default
        default_count = engineer_result['is_default'].sum()
        
        # Should include all loans >= 90 days (90, 100, 150, 179, 180, 300)
        expected_count = len(self.test_data[self.test_data['days_past_due'] >= 90])
        
        self.assertEqual(
            default_count,
            expected_count,
            "FeatureEngineer should flag all loans >= 90 days for risk analysis"
        )
    
    def test_accounting_default_purpose(self):
        """Test that PaymentProcessor serves accounting default with 180+ threshold."""
        processor_result = self.processor.assign_dpd_buckets(self.test_data.copy())
        
        # Count loans flagged as default_flag
        default_count = processor_result['default_flag'].sum()
        
        # Should include only loans >= 180 days (180, 300)
        expected_count = len(self.test_data[self.test_data['days_past_due'] >= 180])
        
        self.assertEqual(
            default_count,
            expected_count,
            "PaymentProcessor should flag only loans >= 180 days for accounting default"
        )
    
    def test_high_risk_vs_default_boundary(self):
        """Test the critical boundary: HIGH RISK (90) vs DEFAULT (180)."""
        processor_result = self.processor.assign_dpd_buckets(self.test_data.copy())
        engineer_result = self.engineer.assign_dpd_buckets(self.test_data.copy())
        
        # At 90 days: High Risk boundary
        row_90 = self.test_data[self.test_data['days_past_due'] == 90].index[0]
        self.assertTrue(engineer_result.loc[row_90, 'is_default'])  # High Risk
        self.assertFalse(processor_result.loc[row_90, 'default_flag'])  # Not accounting default
        
        # At 180 days: Accounting Default boundary
        row_180 = self.test_data[self.test_data['days_past_due'] == 180].index[0]
        self.assertTrue(engineer_result.loc[row_180, 'is_default'])  # Still High Risk
        self.assertTrue(processor_result.loc[row_180, 'default_flag'])  # Now accounting default
    
    def test_configurable_thresholds(self):
        """Test that both classes support configurable thresholds."""
        # Create custom instances
        custom_processor = PaymentProcessor(dpd_threshold=150)
        custom_engineer = FeatureEngineer(risk_threshold=120)
        
        test_data = pd.DataFrame({
            'loan_id': [1, 2],
            'days_past_due': [130, 160]
        })
        
        processor_result = custom_processor.assign_dpd_buckets(test_data.copy())
        engineer_result = custom_engineer.assign_dpd_buckets(test_data.copy())
        
        # 130 days: above engineer threshold (120) but below processor threshold (150)
        self.assertTrue(engineer_result.loc[0, 'is_default'])
        self.assertFalse(processor_result.loc[0, 'default_flag'])
        
        # 160 days: above both thresholds
        self.assertTrue(engineer_result.loc[1, 'is_default'])
        self.assertTrue(processor_result.loc[1, 'default_flag'])


if __name__ == '__main__':
    unittest.main()
