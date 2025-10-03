"""
Tests for the PaymentProcessor class.
"""

import pytest
import pandas as pd
from abaco_core import PaymentProcessor


class TestPaymentProcessor:
    """Test suite for PaymentProcessor class."""
    
    def test_is_default_with_default_threshold(self):
        """Test default detection with default 180-day threshold."""
        processor = PaymentProcessor()
        
        # Test cases at boundary
        assert processor.is_default(180) is True   # At threshold
        assert processor.is_default(181) is True   # Above threshold
        assert processor.is_default(179) is False  # Below threshold
        assert processor.is_default(0) is False    # Current
        assert processor.is_default(200) is True   # Well past due
    
    def test_is_default_with_custom_threshold(self):
        """Test default detection with custom threshold."""
        processor = PaymentProcessor(default_threshold=90)
        
        # Test with 90-day threshold (technical default)
        assert processor.is_default(90) is True
        assert processor.is_default(91) is True
        assert processor.is_default(89) is False
        assert processor.is_default(0) is False
    
    def test_is_default_with_override_threshold(self):
        """Test default detection with override threshold parameter."""
        processor = PaymentProcessor(default_threshold=180)
        
        # Use instance threshold
        assert processor.is_default(185) is True
        assert processor.is_default(175) is False
        
        # Override with custom threshold
        assert processor.is_default(95, threshold=90) is True
        assert processor.is_default(85, threshold=90) is False
    
    def test_process_payments(self):
        """Test processing a dataframe of payments."""
        processor = PaymentProcessor(default_threshold=180)
        
        payments = pd.DataFrame({
            'loan_id': [1, 2, 3, 4, 5],
            'days_past_due': [0, 45, 90, 180, 200]
        })
        
        result = processor.process_payments(payments)
        
        # Check that is_default column was added
        assert 'is_default' in result.columns
        
        # Check default status based on 180-day threshold
        assert result.loc[result['loan_id'] == 1, 'is_default'].values[0] == False
        assert result.loc[result['loan_id'] == 2, 'is_default'].values[0] == False
        assert result.loc[result['loan_id'] == 3, 'is_default'].values[0] == False
        assert result.loc[result['loan_id'] == 4, 'is_default'].values[0] == True
        assert result.loc[result['loan_id'] == 5, 'is_default'].values[0] == True
    
    def test_calculate_default_rate(self):
        """Test calculating portfolio default rate."""
        processor = PaymentProcessor(default_threshold=180)
        
        payments = pd.DataFrame({
            'loan_id': [1, 2, 3, 4, 5],
            'days_past_due': [0, 45, 90, 180, 200]
        })
        
        default_rate = processor.calculate_default_rate(payments)
        
        # 2 out of 5 loans are in default (180 and 200 DPD)
        assert default_rate == 0.4
    
    def test_calculate_default_rate_empty_portfolio(self):
        """Test calculating default rate for empty portfolio."""
        processor = PaymentProcessor()
        
        payments = pd.DataFrame(columns=['loan_id', 'days_past_due'])
        
        default_rate = processor.calculate_default_rate(payments)
        
        # Empty portfolio should return 0.0
        assert default_rate == 0.0
    
    def test_calculate_default_rate_no_defaults(self):
        """Test calculating default rate when no loans are in default."""
        processor = PaymentProcessor(default_threshold=180)
        
        payments = pd.DataFrame({
            'loan_id': [1, 2, 3],
            'days_past_due': [0, 30, 90]
        })
        
        default_rate = processor.calculate_default_rate(payments)
        
        assert default_rate == 0.0
    
    def test_calculate_default_rate_all_defaults(self):
        """Test calculating default rate when all loans are in default."""
        processor = PaymentProcessor(default_threshold=90)
        
        payments = pd.DataFrame({
            'loan_id': [1, 2, 3],
            'days_past_due': [90, 180, 200]
        })
        
        default_rate = processor.calculate_default_rate(payments)
        
        assert default_rate == 1.0
    
    def test_different_dpd_policies(self):
        """Test different DPD policy thresholds."""
        # Basel II/III technical default (90 days)
        processor_90 = PaymentProcessor(default_threshold=90)
        
        # US write-off threshold (180 days)
        processor_180 = PaymentProcessor(default_threshold=180)
        
        # Custom policy (120 days)
        processor_120 = PaymentProcessor(default_threshold=120)
        
        dpd = 150
        
        # Same DPD value, different policies
        assert processor_90.is_default(dpd) is True   # 150 >= 90
        assert processor_180.is_default(dpd) is False # 150 < 180
        assert processor_120.is_default(dpd) is True  # 150 >= 120
