import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from abaco_core.feature_engineering import FeatureEngineer


def test_segment_customers_by_exposure():
    """Test customer segmentation by exposure"""
    print("Testing segment_customers_by_exposure...")
    
    fe = FeatureEngineer()
    
    # Test data with varying exposures
    df = pd.DataFrame({
        'customer_id': ['C1', 'C1', 'C2', 'C2', 'C3', 'C3', 'C4', 'C4', 'C5', 'C5', 'C6', 'C6'],
        'outstanding_balance': [1000, 500, 2000, 1000, 3000, 500, 4000, 1000, 5000, 2000, 6000, 3000]
    })
    
    result = fe.segment_customers_by_exposure(df, 'customer_id', 'outstanding_balance')
    
    assert 'segment' in result.columns, "segment column should be present"
    assert 'exposure' in result.columns, "exposure column should be present"
    assert len(result) == 6, "Should have 6 unique customers"
    assert all(result['segment'].isin(['A', 'B', 'C', 'D', 'E', 'F'])), "Segments should be A-F"
    
    print("✓ segment_customers_by_exposure test passed")


def test_assign_dpd_buckets():
    """Test DPD bucket assignment"""
    print("Testing assign_dpd_buckets...")
    
    fe = FeatureEngineer()
    
    df = pd.DataFrame({
        'loan_id': ['L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7', 'L8'],
        'days_past_due': [0, 15, 45, 75, 105, 135, 165, 200]
    })
    
    result = fe.assign_dpd_buckets(df, 'days_past_due')
    
    assert 'dpd_bucket' in result.columns, "dpd_bucket column should be present"
    assert 'is_default' in result.columns, "is_default column should be present"
    assert result.loc[0, 'dpd_bucket'] == 'Current', "0 DPD should be Current"
    assert result.loc[1, 'dpd_bucket'] == '1-29', "15 DPD should be 1-29"
    assert result.loc[2, 'dpd_bucket'] == '30-59', "45 DPD should be 30-59"
    assert result.loc[3, 'dpd_bucket'] == '60-89', "75 DPD should be 60-89"
    assert result.loc[4, 'is_default'] == 1, "105 DPD should be marked as default"
    assert result.loc[7, 'dpd_bucket'] == '180+', "200 DPD should be 180+"
    
    print("✓ assign_dpd_buckets test passed")


def test_classify_customer_type():
    """Test customer type classification"""
    print("Testing classify_customer_type...")
    
    fe = FeatureEngineer()
    
    # Customer dataframe
    customer_df = pd.DataFrame({
        'customer_id': ['C1', 'C2', 'C3', 'C4']
    })
    
    # Loan history with different patterns
    loan_history = pd.DataFrame({
        'customer_id': ['C1', 'C2', 'C2', 'C3', 'C3', 'C3', 'C4', 'C4'],
        'loan_start_date': [
            '2023-01-01',  # C1: single loan (New)
            '2023-01-01', '2023-02-01',  # C2: loans within 90 days (Recurrent)
            '2023-01-01', '2023-02-01', '2023-06-01',  # C3: gap > 90 days (Recovered)
            '2023-01-01', '2023-01-15'  # C4: loans within 90 days (Recurrent)
        ]
    })
    
    result = fe.classify_customer_type(customer_df, loan_history, 'customer_id', 'loan_start_date')
    
    assert 'customer_type' in result.columns, "customer_type column should be present"
    assert result.loc[result['customer_id'] == 'C1', 'customer_type'].iloc[0] == 'New', "C1 should be New"
    assert result.loc[result['customer_id'] == 'C2', 'customer_type'].iloc[0] == 'Recurrent', "C2 should be Recurrent"
    assert result.loc[result['customer_id'] == 'C3', 'customer_type'].iloc[0] == 'Recovered', "C3 should be Recovered"
    
    print("✓ classify_customer_type test passed")


def test_calculate_weighted_stats():
    """Test weighted statistics calculation"""
    print("Testing calculate_weighted_stats...")
    
    fe = FeatureEngineer()
    
    df = pd.DataFrame({
        'apr': [10.0, 15.0, 20.0],
        'term': [12, 24, 36],
        'outstanding_balance': [1000, 2000, 1000]
    })
    
    result = fe.calculate_weighted_stats(df, 'outstanding_balance', ['apr', 'term'])
    
    assert 'weighted_apr' in result.columns, "weighted_apr should be present"
    assert 'weighted_term' in result.columns, "weighted_term should be present"
    
    # Weighted APR = (10*1000 + 15*2000 + 20*1000) / 4000 = 15.0
    expected_apr = (10.0*1000 + 15.0*2000 + 20.0*1000) / 4000
    assert abs(result['weighted_apr'].iloc[0] - expected_apr) < 0.01, "Weighted APR calculation incorrect"
    
    print("✓ calculate_weighted_stats test passed")


def test_calculate_line_utilization():
    """Test line utilization calculation"""
    print("Testing calculate_line_utilization...")
    
    fe = FeatureEngineer()
    
    df = pd.DataFrame({
        'loan_id': ['L1', 'L2', 'L3'],
        'line_amount': [10000, 5000, 20000],
        'outstanding_balance': [8000, 6000, 15000]
    })
    
    result = fe.calculate_line_utilization(df, 'line_amount', 'outstanding_balance')
    
    assert 'line_utilization' in result.columns, "line_utilization should be present"
    assert result.loc[0, 'line_utilization'] == 0.8, "L1 utilization should be 0.8"
    assert result.loc[1, 'line_utilization'] == 1.0, "L2 utilization should be capped at 1.0"
    assert result.loc[2, 'line_utilization'] == 0.75, "L3 utilization should be 0.75"
    
    print("✓ calculate_line_utilization test passed")


def test_calculate_hhi():
    """Test HHI (concentration) calculation"""
    print("Testing calculate_hhi...")
    
    fe = FeatureEngineer()
    
    df = pd.DataFrame({
        'customer_id': ['C1', 'C1', 'C2', 'C2', 'C3'],
        'outstanding_balance': [3000, 2000, 2000, 1000, 2000]
    })
    
    result = fe.calculate_hhi(df, 'customer_id', 'outstanding_balance')
    
    # C1: 5000, C2: 3000, C3: 2000, Total: 10000
    # Shares: 0.5, 0.3, 0.2
    # HHI = (0.5^2 + 0.3^2 + 0.2^2) * 10000 = (0.25 + 0.09 + 0.04) * 10000 = 3800
    expected_hhi = 3800
    assert abs(result - expected_hhi) < 1, f"HHI should be {expected_hhi}, got {result}"
    
    print("✓ calculate_hhi test passed")


def test_enrich_master_dataframe():
    """Test master dataframe enrichment"""
    print("Testing enrich_master_dataframe...")
    
    fe = FeatureEngineer()
    
    df = pd.DataFrame({
        'loan_id': ['L1', 'L2', 'L3'],
        'customer_id': ['C1', 'C2', 'C3'],
        'outstanding_balance': [1000, 2000, 1500],
        'days_past_due': [0, 45, 105],
        'line_amount': [5000, 10000, 7500],
        'apr': [10, 15, 12],
        'term': [12, 24, 18]
    })
    
    result = fe.enrich_master_dataframe(df)
    
    assert 'dpd_bucket' in result.columns, "dpd_bucket should be added"
    assert 'is_default' in result.columns, "is_default should be added"
    assert 'line_utilization' in result.columns, "line_utilization should be added"
    assert 'outstanding_balance_zscore' in result.columns, "outstanding_balance_zscore should be added"
    assert 'apr_zscore' in result.columns, "apr_zscore should be added"
    
    print("✓ enrich_master_dataframe test passed")


def test_missing_column_handling():
    """Test handling of missing columns with column name matching"""
    print("Testing missing column handling...")
    
    fe = FeatureEngineer()
    
    # Test with alternative column names
    df = pd.DataFrame({
        'customer_id': ['C1', 'C2'],
        'current_balance': [1000, 2000]  # Alternative to outstanding_balance
    })
    
    result = fe.segment_customers_by_exposure(df, 'customer_id')
    assert 'exposure' in result.columns, "Should handle alternative column names"
    
    print("✓ missing column handling test passed")


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Running FeatureEngineer Tests")
    print("=" * 60)
    
    test_segment_customers_by_exposure()
    test_assign_dpd_buckets()
    test_classify_customer_type()
    test_calculate_weighted_stats()
    test_calculate_line_utilization()
    test_calculate_hhi()
    test_enrich_master_dataframe()
    test_missing_column_handling()
    
    print("=" * 60)
    print("All tests passed successfully! ✓")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
