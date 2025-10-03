"""
Tests for Feature Engineering Module
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from feature_engineer import (
    FeatureEngineer,
    segment_clients_by_exposure,
    classify_dpd_buckets,
    classify_client_type,
    calculate_weighted_metrics,
    calculate_line_utilization,
    enrich_master_dataframe
)


def test_segment_clients_by_exposure():
    """Test client segmentation by exposure"""
    print("Testing segment_clients_by_exposure...")
    
    df = pd.DataFrame({
        'customer_id': [1, 2, 3, 4, 5],
        'outstanding_balance': [5000, 25000, 75000, 150000, 200000]
    })
    
    result = segment_clients_by_exposure(df)
    
    assert 'exposure_segment' in result.columns
    assert len(result) == 5
    print("✓ segment_clients_by_exposure test passed")
    print(f"  Segments created: {result['exposure_segment'].unique()}")
    

def test_classify_dpd_buckets():
    """Test DPD bucket classification"""
    print("\nTesting classify_dpd_buckets...")
    
    df = pd.DataFrame({
        'customer_id': [1, 2, 3, 4, 5, 6, 7],
        'days_past_due': [0, 15, 45, 75, 120, 200, np.nan]
    })
    
    result = classify_dpd_buckets(df)
    
    assert 'dpd_bucket' in result.columns
    assert len(result) == 7
    assert result.loc[0, 'dpd_bucket'] == 'Current'
    assert result.loc[1, 'dpd_bucket'] == '1-30'
    assert result.loc[2, 'dpd_bucket'] == '31-60'
    assert result.loc[3, 'dpd_bucket'] == '61-90'
    assert result.loc[4, 'dpd_bucket'] == '91-180'
    assert result.loc[5, 'dpd_bucket'] == '180+'
    assert result.loc[6, 'dpd_bucket'] == 'Unknown'
    print("✓ classify_dpd_buckets test passed")
    print(f"  Buckets created: {result['dpd_bucket'].unique()}")


def test_classify_client_type():
    """Test client type classification"""
    print("\nTesting classify_client_type...")
    
    df = pd.DataFrame({
        'customer_id': [1, 2, 3, 4, 5],
        'loan_count': [0, 1, 1, 3, 10],
        'last_active_date': [
            datetime.now(),
            datetime.now(),
            datetime.now() - timedelta(days=200),
            datetime.now(),
            datetime.now()
        ]
    })
    
    result = classify_client_type(df)
    
    assert 'client_type' in result.columns
    assert len(result) == 5
    assert result.loc[0, 'client_type'] == 'Inactive'
    assert result.loc[1, 'client_type'] == 'New'
    assert result.loc[2, 'client_type'] == 'Dormant'
    assert result.loc[3, 'client_type'] == 'Regular'
    assert result.loc[4, 'client_type'] == 'High-Value'
    print("✓ classify_client_type test passed")
    print(f"  Client types: {result['client_type'].unique()}")


def test_calculate_weighted_metrics():
    """Test weighted metrics calculation"""
    print("\nTesting calculate_weighted_metrics...")
    
    df = pd.DataFrame({
        'customer_id': [1, 2, 3],
        'outstanding_balance': [100, 200, 300],
        'interest_rate': [5.0, 6.0, 7.0],
        'risk_score': [10, 20, 30]
    })
    
    result = calculate_weighted_metrics(df, ['interest_rate', 'risk_score'])
    
    assert 'weighted_interest_rate' in result.columns
    assert 'weighted_risk_score' in result.columns
    assert len(result) == 3
    
    # Check that weighted values sum correctly (normalized by total weight)
    total_weighted_rate = result['weighted_interest_rate'].sum()
    expected_rate = (100*5.0 + 200*6.0 + 300*7.0) / 600
    assert abs(total_weighted_rate - expected_rate) < 0.01
    
    print("✓ calculate_weighted_metrics test passed")
    print(f"  Weighted interest_rate sum: {total_weighted_rate:.2f}")


def test_calculate_line_utilization():
    """Test line utilization calculation"""
    print("\nTesting calculate_line_utilization...")
    
    df = pd.DataFrame({
        'customer_id': [1, 2, 3, 4],
        'outstanding_balance': [50000, 75000, 0, 100000],
        'line_amount': [100000, 100000, 100000, 0]
    })
    
    result = calculate_line_utilization(df)
    
    assert 'line_utilization' in result.columns
    assert len(result) == 4
    assert result.loc[0, 'line_utilization'] == 50.0
    assert result.loc[1, 'line_utilization'] == 75.0
    assert result.loc[2, 'line_utilization'] == 0.0
    assert result.loc[3, 'line_utilization'] == 0.0
    print("✓ calculate_line_utilization test passed")
    print(f"  Utilization rates: {result['line_utilization'].values}")


def test_enrich_master_dataframe():
    """Test master dataframe enrichment"""
    print("\nTesting enrich_master_dataframe...")
    
    df = pd.DataFrame({
        'customer_id': [1, 2, 3],
        'outstanding_balance': [5000, 50000, 150000],
        'line_amount': [10000, 100000, 200000],
        'days_past_due': [0, 30, 90],
        'loan_count': [1, 3, 10],
        'last_active_date': [datetime.now(), datetime.now(), datetime.now()]
    })
    
    result = enrich_master_dataframe(df)
    
    # Check that all enrichment columns are present
    assert 'exposure_segment' in result.columns
    assert 'dpd_bucket' in result.columns
    assert 'client_type' in result.columns
    assert 'line_utilization' in result.columns
    assert len(result) == 3
    print("✓ enrich_master_dataframe test passed")
    print(f"  Columns added: exposure_segment, dpd_bucket, client_type, line_utilization")


def test_assertions():
    """Test that assertions work correctly"""
    print("\nTesting assertions...")
    
    # Test that non-DataFrame input raises assertion error
    try:
        segment_clients_by_exposure("not a dataframe")
        assert False, "Should have raised assertion error"
    except AssertionError as e:
        assert str(e) == "df must be a DataFrame"
        print("✓ DataFrame assertion test passed")
    
    # Test that invalid metrics raises assertion error
    try:
        df = pd.DataFrame({'col': [1, 2, 3]})
        calculate_weighted_metrics(df, [])
        assert False, "Should have raised assertion error"
    except AssertionError as e:
        assert str(e) == "metrics must be a non-empty list"
        print("✓ Metrics assertion test passed")


def test_feature_engineer_class():
    """Test that FeatureEngineer class can be instantiated"""
    print("\nTesting FeatureEngineer class...")
    
    fe = FeatureEngineer()
    assert fe is not None
    
    df = pd.DataFrame({
        'outstanding_balance': [10000, 20000],
        'days_past_due': [0, 30]
    })
    
    result = fe.segment_clients_by_exposure(df)
    assert 'exposure_segment' in result.columns
    
    result = fe.classify_dpd_buckets(df)
    assert 'dpd_bucket' in result.columns
    
    print("✓ FeatureEngineer class test passed")


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Running Feature Engineering Tests")
    print("=" * 60)
    
    test_segment_clients_by_exposure()
    test_classify_dpd_buckets()
    test_classify_client_type()
    test_calculate_weighted_metrics()
    test_calculate_line_utilization()
    test_enrich_master_dataframe()
    test_assertions()
    test_feature_engineer_class()
    
    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
