"""
Tests for DPD Analyzer Module
"""

import pandas as pd
import numpy as np
import pytest

from dpd_analyzer import DPDAnalyzer


def test_assign_dpd_buckets_current():
    """Test assigning buckets for current (0 DPD) accounts."""
    analyzer = DPDAnalyzer()
    df = pd.DataFrame({"days_past_due": [0, 0, 0]})
    
    result = analyzer.assign_dpd_buckets(df)
    
    assert all(result["dpd_bucket"] == "Current")
    assert all(result["dpd_bucket_value"] == 0)
    assert all(result["dpd_bucket_description"] == "No payment due")
    assert all(result["default_flag"] == False)


def test_assign_dpd_buckets_early_delinquency():
    """Test assigning buckets for early delinquency (1-29 days)."""
    analyzer = DPDAnalyzer()
    df = pd.DataFrame({"days_past_due": [1, 15, 29]})
    
    result = analyzer.assign_dpd_buckets(df)
    
    assert all(result["dpd_bucket"] == "1-29")
    assert all(result["dpd_bucket_value"] == 1)
    assert all(result["dpd_bucket_description"] == "Early delinquency")
    assert all(result["default_flag"] == False)


def test_assign_dpd_buckets_30_days():
    """Test assigning buckets for 30-59 days delinquent."""
    analyzer = DPDAnalyzer()
    df = pd.DataFrame({"days_past_due": [30, 45, 59]})
    
    result = analyzer.assign_dpd_buckets(df)
    
    assert all(result["dpd_bucket"] == "30-59")
    assert all(result["dpd_bucket_value"] == 30)
    assert all(result["dpd_bucket_description"] == "Delinquent 30 days")
    assert all(result["default_flag"] == False)


def test_assign_dpd_buckets_60_days():
    """Test assigning buckets for 60-89 days delinquent."""
    analyzer = DPDAnalyzer()
    df = pd.DataFrame({"days_past_due": [60, 75, 89]})
    
    result = analyzer.assign_dpd_buckets(df)
    
    assert all(result["dpd_bucket"] == "60-89")
    assert all(result["dpd_bucket_value"] == 60)
    assert all(result["dpd_bucket_description"] == "Delinquent 60 days")
    assert all(result["default_flag"] == False)


def test_assign_dpd_buckets_default_90():
    """Test assigning buckets for 90-119 days (default)."""
    analyzer = DPDAnalyzer()
    df = pd.DataFrame({"days_past_due": [90, 100, 119]})
    
    result = analyzer.assign_dpd_buckets(df)
    
    assert all(result["dpd_bucket"] == "90-119")
    assert all(result["dpd_bucket_value"] == 90)
    assert all(result["dpd_bucket_description"] == "Default 90 days")
    assert all(result["default_flag"] == True)


def test_assign_dpd_buckets_default_120():
    """Test assigning buckets for 120-149 days (default)."""
    analyzer = DPDAnalyzer()
    df = pd.DataFrame({"days_past_due": [120, 135, 149]})
    
    result = analyzer.assign_dpd_buckets(df)
    
    assert all(result["dpd_bucket"] == "120-149")
    assert all(result["dpd_bucket_value"] == 120)
    assert all(result["dpd_bucket_description"] == "Default 120 days")
    assert all(result["default_flag"] == True)


def test_assign_dpd_buckets_default_150():
    """Test assigning buckets for 150-179 days (default)."""
    analyzer = DPDAnalyzer()
    df = pd.DataFrame({"days_past_due": [150, 165, 179]})
    
    result = analyzer.assign_dpd_buckets(df)
    
    assert all(result["dpd_bucket"] == "150-179")
    assert all(result["dpd_bucket_value"] == 150)
    assert all(result["dpd_bucket_description"] == "Default 150 days")
    assert all(result["default_flag"] == True)


def test_assign_dpd_buckets_default_180_plus():
    """Test assigning buckets for 180+ days (default)."""
    analyzer = DPDAnalyzer()
    df = pd.DataFrame({"days_past_due": [180, 200, 365]})
    
    result = analyzer.assign_dpd_buckets(df)
    
    assert all(result["dpd_bucket"] == "180+")
    assert all(result["dpd_bucket_value"] == 180)
    assert all(result["dpd_bucket_description"] == "Default 180+ days")
    assert all(result["default_flag"] == True)


def test_assign_dpd_buckets_mixed():
    """Test assigning buckets with mixed DPD values."""
    analyzer = DPDAnalyzer()
    df = pd.DataFrame({"days_past_due": [0, 15, 45, 75, 100, 135, 165, 200]})
    
    result = analyzer.assign_dpd_buckets(df)
    
    expected_buckets = ["Current", "1-29", "30-59", "60-89", "90-119", "120-149", "150-179", "180+"]
    assert list(result["dpd_bucket"]) == expected_buckets
    
    expected_values = [0, 1, 30, 60, 90, 120, 150, 180]
    assert list(result["dpd_bucket_value"]) == expected_values
    
    expected_flags = [False, False, False, False, True, True, True, True]
    assert list(result["default_flag"]) == expected_flags


def test_assign_dpd_buckets_nan_values():
    """Test handling of NaN/non-numeric values."""
    analyzer = DPDAnalyzer()
    df = pd.DataFrame({"days_past_due": [None, "invalid", 15, np.nan]})
    
    result = analyzer.assign_dpd_buckets(df)
    
    # NaN and invalid values should be treated as 0
    assert result["dpd_bucket"].iloc[0] == "Current"
    assert result["dpd_bucket"].iloc[1] == "Current"
    assert result["dpd_bucket"].iloc[2] == "1-29"
    assert result["dpd_bucket"].iloc[3] == "Current"


def test_assign_dpd_buckets_custom_threshold():
    """Test with custom DPD threshold."""
    analyzer = DPDAnalyzer(dpd_threshold=60)
    df = pd.DataFrame({"days_past_due": [0, 30, 60, 90]})
    
    result = analyzer.assign_dpd_buckets(df)
    
    # With threshold of 60, only 60+ should be marked as default
    expected_flags = [False, False, True, True]
    assert list(result["default_flag"]) == expected_flags


def test_detect_field_exact_match():
    """Test exact field name matching."""
    analyzer = DPDAnalyzer()
    df = pd.DataFrame(columns=["account_id", "days_past_due", "amount"])
    
    result = analyzer.detect_field(df, ["days_past_due"])
    assert result == "days_past_due"
    
    # Case insensitive
    result = analyzer.detect_field(df, ["DAYS_PAST_DUE"])
    assert result == "days_past_due"


def test_detect_field_contains_match():
    """Test substring matching in field names."""
    analyzer = DPDAnalyzer()
    df = pd.DataFrame(columns=["account_id", "total_days_past_due", "amount"])
    
    result = analyzer.detect_field(df, ["days_past_due"])
    assert result == "total_days_past_due"


def test_detect_field_shortest_match():
    """Test that shortest matching field is returned."""
    analyzer = DPDAnalyzer()
    df = pd.DataFrame(columns=["dpd", "days_past_due", "total_days_past_due_amount"])
    
    result = analyzer.detect_field(df, ["dpd"])
    assert result == "dpd"
    
    # When searching for "days", should return shortest match
    result = analyzer.detect_field(df, ["days"])
    assert result == "days_past_due"


def test_detect_field_regex_match():
    """Test regex pattern matching."""
    analyzer = DPDAnalyzer()
    df = pd.DataFrame(columns=["account_id", "dpd_value", "amount"])
    
    result = analyzer.detect_field(df, ["dpd.*"])
    assert result == "dpd_value"


def test_detect_field_multiple_patterns():
    """Test matching with multiple patterns."""
    analyzer = DPDAnalyzer()
    df = pd.DataFrame(columns=["account_id", "delinquency_days", "amount"])
    
    # Should try patterns in order and return first match
    result = analyzer.detect_field(df, ["days_past_due", "dpd", "delinquency"])
    assert result == "delinquency_days"


def test_detect_field_no_match():
    """Test when no field matches."""
    analyzer = DPDAnalyzer()
    df = pd.DataFrame(columns=["account_id", "amount", "balance"])
    
    result = analyzer.detect_field(df, ["days_past_due", "dpd"])
    assert result is None


def test_detect_field_invalid_regex():
    """Test handling of invalid regex patterns."""
    analyzer = DPDAnalyzer()
    df = pd.DataFrame(columns=["account_id", "amount"])
    
    # Invalid regex should be skipped, not raise error
    result = analyzer.detect_field(df, ["[invalid(regex"])
    assert result is None


def test_detect_field_case_insensitive():
    """Test case-insensitive matching."""
    analyzer = DPDAnalyzer()
    df = pd.DataFrame(columns=["Account_ID", "Days_Past_Due", "Amount"])
    
    result = analyzer.detect_field(df, ["days_past_due"])
    assert result == "Days_Past_Due"
    
    result = analyzer.detect_field(df, ["ACCOUNT_ID"])
    assert result == "Account_ID"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
