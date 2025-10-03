"""Tests for LoanAnalyzer assign_dpd_buckets method."""

import pytest
import pandas as pd
import numpy as np
from src.commercial_view.loan_analyzer import LoanAnalyzer


class TestAssignDPDBuckets:
    """Test suite for assign_dpd_buckets method."""
    
    def test_default_buckets(self):
        """Test default DPD bucket assignment."""
        analyzer = LoanAnalyzer()
        
        # Create test data with various DPD values
        df = pd.DataFrame({
            'loan_id': [1, 2, 3, 4, 5, 6, 7, 8, 9],
            'days_past_due': [0, 15, 30, 45, 75, 100, 130, 160, 200]
        })
        
        result = analyzer.assign_dpd_buckets(df)
        
        # Verify buckets are assigned correctly
        assert result.loc[0, 'dpd_bucket'] == "Current"
        assert result.loc[1, 'dpd_bucket'] == "1-29"
        assert result.loc[2, 'dpd_bucket'] == "30-59"
        assert result.loc[3, 'dpd_bucket'] == "30-59"
        assert result.loc[4, 'dpd_bucket'] == "60-89"
        assert result.loc[5, 'dpd_bucket'] == "90-119"
        assert result.loc[6, 'dpd_bucket'] == "120-149"
        assert result.loc[7, 'dpd_bucket'] == "150-179"
        assert result.loc[8, 'dpd_bucket'] == "180+"
        
        # Verify default flags (threshold = 90 by default)
        assert result.loc[0, 'default_flag'] == 0
        assert result.loc[4, 'default_flag'] == 0  # 75 < 90
        assert result.loc[5, 'default_flag'] == 1  # 100 >= 90
        assert result.loc[8, 'default_flag'] == 1
    
    def test_custom_buckets(self):
        """Test custom DPD bucket configuration."""
        config = {
            "dpd_buckets": [
                (0, 0, "Current"),
                (1, 29, "1-29"),
                (30, 59, "30-59"),
                (60, 89, "60-89"),
                (90, None, "90+")
            ]
        }
        analyzer = LoanAnalyzer(config=config)
        
        df = pd.DataFrame({
            'loan_id': [1, 2, 3, 4, 5],
            'days_past_due': [0, 15, 45, 85, 150]
        })
        
        result = analyzer.assign_dpd_buckets(df)
        
        assert result.loc[0, 'dpd_bucket'] == "Current"
        assert result.loc[1, 'dpd_bucket'] == "1-29"
        assert result.loc[2, 'dpd_bucket'] == "30-59"
        assert result.loc[3, 'dpd_bucket'] == "60-89"
        assert result.loc[4, 'dpd_bucket'] == "90+"
    
    def test_custom_dpd_threshold(self):
        """Test custom DPD threshold for default flag."""
        analyzer = LoanAnalyzer(dpd_threshold=60)
        
        df = pd.DataFrame({
            'loan_id': [1, 2, 3],
            'days_past_due': [30, 60, 90]
        })
        
        result = analyzer.assign_dpd_buckets(df)
        
        assert result.loc[0, 'default_flag'] == 0  # 30 < 60
        assert result.loc[1, 'default_flag'] == 1  # 60 >= 60
        assert result.loc[2, 'default_flag'] == 1  # 90 >= 60
    
    def test_invalid_input_no_dpd_column(self):
        """Test error handling for missing days_past_due column."""
        analyzer = LoanAnalyzer()
        
        df = pd.DataFrame({
            'loan_id': [1, 2, 3],
            'amount': [1000, 2000, 3000]
        })
        
        with pytest.raises(ValueError, match="dpd_df must contain 'days_past_due'"):
            analyzer.assign_dpd_buckets(df)
    
    def test_invalid_input_not_dataframe(self):
        """Test error handling for non-DataFrame input."""
        analyzer = LoanAnalyzer()
        
        with pytest.raises(ValueError, match="dpd_df must contain 'days_past_due'"):
            analyzer.assign_dpd_buckets([1, 2, 3])
    
    def test_coerce_non_numeric_dpd(self):
        """Test handling of non-numeric DPD values."""
        analyzer = LoanAnalyzer()
        
        df = pd.DataFrame({
            'loan_id': [1, 2, 3, 4],
            'days_past_due': [0, 'invalid', np.nan, 45]
        })
        
        result = analyzer.assign_dpd_buckets(df)
        
        # Non-numeric values should be coerced to 0 and assigned "Current"
        assert result.loc[0, 'dpd_bucket'] == "Current"
        assert result.loc[1, 'dpd_bucket'] == "Current"  # 'invalid' -> 0
        assert result.loc[2, 'dpd_bucket'] == "Current"  # NaN -> 0
        assert result.loc[3, 'dpd_bucket'] == "30-59"
    
    def test_original_dataframe_unchanged(self):
        """Test that original DataFrame is not modified."""
        analyzer = LoanAnalyzer()
        
        df = pd.DataFrame({
            'loan_id': [1, 2, 3],
            'days_past_due': [0, 30, 90]
        })
        
        original_columns = df.columns.tolist()
        result = analyzer.assign_dpd_buckets(df)
        
        # Original should remain unchanged
        assert df.columns.tolist() == original_columns
        assert 'dpd_bucket' not in df.columns
        assert 'default_flag' not in df.columns
        
        # Result should have new columns
        assert 'dpd_bucket' in result.columns
        assert 'default_flag' in result.columns
    
    def test_boundary_values_default_buckets(self):
        """Test boundary values for default bucket ranges."""
        analyzer = LoanAnalyzer()
        
        df = pd.DataFrame({
            'loan_id': range(1, 13),
            'days_past_due': [0, 1, 29, 30, 59, 60, 89, 90, 119, 120, 149, 150]
        })
        
        result = analyzer.assign_dpd_buckets(df)
        
        # Test boundaries
        assert result.loc[0, 'dpd_bucket'] == "Current"      # 0
        assert result.loc[1, 'dpd_bucket'] == "1-29"         # 1
        assert result.loc[2, 'dpd_bucket'] == "1-29"         # 29
        assert result.loc[3, 'dpd_bucket'] == "30-59"        # 30
        assert result.loc[4, 'dpd_bucket'] == "30-59"        # 59
        assert result.loc[5, 'dpd_bucket'] == "60-89"        # 60
        assert result.loc[6, 'dpd_bucket'] == "60-89"        # 89
        assert result.loc[7, 'dpd_bucket'] == "90-119"       # 90
        assert result.loc[8, 'dpd_bucket'] == "90-119"       # 119
        assert result.loc[9, 'dpd_bucket'] == "120-149"      # 120
        assert result.loc[10, 'dpd_bucket'] == "120-149"     # 149
        assert result.loc[11, 'dpd_bucket'] == "150-179"     # 150
    
    def test_open_ended_bucket(self):
        """Test open-ended bucket (high=None) in custom config."""
        config = {
            "dpd_buckets": [
                (0, 30, "0-30"),
                (31, None, "31+")
            ]
        }
        analyzer = LoanAnalyzer(config=config)
        
        df = pd.DataFrame({
            'loan_id': [1, 2, 3, 4],
            'days_past_due': [0, 30, 31, 1000]
        })
        
        result = analyzer.assign_dpd_buckets(df)
        
        assert result.loc[0, 'dpd_bucket'] == "0-30"
        assert result.loc[1, 'dpd_bucket'] == "0-30"
        assert result.loc[2, 'dpd_bucket'] == "31+"
        assert result.loc[3, 'dpd_bucket'] == "31+"
    
    def test_negative_dpd_values(self):
        """Test handling of negative DPD values (edge case)."""
        analyzer = LoanAnalyzer()
        
        df = pd.DataFrame({
            'loan_id': [1, 2],
            'days_past_due': [-5, 0]
        })
        
        result = analyzer.assign_dpd_buckets(df)
        
        # Negative values should be included in the first bucket
        assert result.loc[0, 'dpd_bucket'] == "Current"
        assert result.loc[1, 'dpd_bucket'] == "Current"
    
    def test_empty_dataframe(self):
        """Test handling of empty DataFrame."""
        analyzer = LoanAnalyzer()
        
        df = pd.DataFrame({'days_past_due': []})
        
        result = analyzer.assign_dpd_buckets(df)
        
        assert len(result) == 0
        assert 'dpd_bucket' in result.columns
        assert 'default_flag' in result.columns
