"""Test the DPD analysis functions."""

import pandas as pd
import numpy as np
from commercial_view.dpd_analysis import DPDAnalyzer, add_dpd_bucket_descriptions


def test_add_dpd_bucket_descriptions():
    """Test the add_dpd_bucket_descriptions function."""
    print("\n=== Testing add_dpd_bucket_descriptions ===")
    
    # Create test data
    dpd_df = pd.DataFrame({
        'dpd_bucket': ['Current', '1-29', '30-59', '60-89', '90-119', '120-149', '150-179', '180+', 'Unknown-bucket'],
        'loan_id': [1, 2, 3, 4, 5, 6, 7, 8, 9]
    })
    
    # Test normal case
    result = add_dpd_bucket_descriptions(dpd_df)
    print("\nInput DataFrame:")
    print(dpd_df)
    print("\nOutput DataFrame:")
    print(result)
    
    # Verify the descriptions
    expected_descriptions = {
        'Current': 'No payment due',
        '1-29': 'Early delinquency',
        '30-59': 'Delinquent 30 days',
        '60-89': 'Delinquent 60 days',
        '90-119': 'Default 90 days',
        '120-149': 'Default 120 days',
        '150-179': 'Default 150 days',
        '180+': 'Default 180+ days',
    }
    
    for bucket, expected_desc in expected_descriptions.items():
        actual_desc = result[result['dpd_bucket'] == bucket]['dpd_bucket_description'].values[0]
        assert actual_desc == expected_desc, f"Expected '{expected_desc}' but got '{actual_desc}' for bucket '{bucket}'"
    
    # Check unknown bucket
    unknown_desc = result[result['dpd_bucket'] == 'Unknown-bucket']['dpd_bucket_description'].values[0]
    assert unknown_desc == 'Unknown', f"Expected 'Unknown' for unmapped bucket, but got '{unknown_desc}'"
    
    # Test error case
    try:
        bad_df = pd.DataFrame({'loan_id': [1, 2, 3]})
        add_dpd_bucket_descriptions(bad_df)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"\nCorrectly raised ValueError: {e}")
    
    print("\n✓ add_dpd_bucket_descriptions tests passed!")


def test_classify_customer_payment_status():
    """Test the classify_customer_payment_status method."""
    print("\n=== Testing classify_customer_payment_status ===")
    
    analyzer = DPDAnalyzer()
    
    # Create test data
    loan_df = pd.DataFrame({
        'customer_id': [1, 1, 2, 3, 3, 3],
        'loan_id': [101, 102, 201, 301, 302, 303]
    })
    
    customer_df = pd.DataFrame({
        'customer_id': [1, 2, 3],
        'customer_name': ['Alice', 'Bob', 'Charlie']
    })
    
    dpd_df = pd.DataFrame({
        'loan_id': [101, 102, 201, 301, 302, 303],
        'days_past_due': [0, 30, 0, 120, 90, 60],
        'is_default': [False, False, False, True, True, False],
        'first_arrears_date': ['2023-01-15', '2023-02-01', None, '2023-01-01', '2023-01-15', '2023-03-01'],
        'last_payment_date': ['2023-12-01', '2023-12-15', '2023-12-01', '2023-06-01', '2023-05-01', '2023-12-01']
    })
    
    # Test normal case
    result = analyzer.classify_customer_payment_status(loan_df, customer_df, dpd_df)
    print("\nCustomer DataFrame:")
    print(customer_df)
    print("\nLoan DataFrame:")
    print(loan_df)
    print("\nDPD DataFrame:")
    print(dpd_df)
    print("\nResult DataFrame:")
    print(result)
    print("\nColumns in result:", result.columns.tolist())
    
    # Verify expected columns
    expected_cols = ['customer_id', 'customer_name', 'max_dpd', 'mean_dpd', 'median_dpd', 
                     'has_defaulted', 'loan_count', 'first_arrears_date', 'last_payment_date', 
                     'payment_status']
    for col in expected_cols:
        assert col in result.columns, f"Expected column '{col}' not found in result"
    
    # Verify customer 1 has 2 loans (Recurrent)
    cust1 = result[result['customer_id'] == 1]
    assert cust1['loan_count'].values[0] == 2, "Customer 1 should have 2 loans"
    
    # Verify customer 3 has 3 loans (Recurrent)
    cust3 = result[result['customer_id'] == 3]
    assert cust3['loan_count'].values[0] == 3, "Customer 3 should have 3 loans"
    
    # Test error cases
    try:
        bad_loan_df = pd.DataFrame({'customer_id': [1, 2]})
        analyzer.classify_customer_payment_status(bad_loan_df, customer_df, dpd_df)
        assert False, "Should have raised ValueError for missing loan_id"
    except ValueError as e:
        print(f"\nCorrectly raised ValueError: {e}")
    
    print("\n✓ classify_customer_payment_status tests passed!")


def test_calculate_per_customer_dpd_stats():
    """Test the calculate_per_customer_dpd_stats method."""
    print("\n=== Testing calculate_per_customer_dpd_stats ===")
    
    analyzer = DPDAnalyzer()
    
    # Create test data
    loan_df = pd.DataFrame({
        'customer_id': [1, 1, 2, 3, 3],
        'loan_id': [101, 102, 201, 301, 302]
    })
    
    dpd_df = pd.DataFrame({
        'loan_id': [101, 102, 201, 301, 302],
        'days_past_due': [0, 30, 15, 120, 90],
        'is_default': [False, False, False, True, True],
        'past_due_amount': [0, 500, 200, 5000, 3000]
    })
    
    # Test normal case
    result = analyzer.calculate_per_customer_dpd_stats(loan_df, dpd_df)
    print("\nLoan DataFrame:")
    print(loan_df)
    print("\nDPD DataFrame:")
    print(dpd_df)
    print("\nResult DataFrame:")
    print(result)
    print("\nColumns in result:", result.columns.tolist())
    
    # Verify expected columns
    expected_cols = ['customer_id', 'dpd_mean', 'dpd_median', 'dpd_min', 'dpd_max', 'dpd_std',
                     'default_count', 'default_rate', 'past_due_amount_sum', 'past_due_amount_mean',
                     'past_due_amount_max', 'loan_count', 'weighted_dpd']
    for col in expected_cols:
        assert col in result.columns, f"Expected column '{col}' not found in result"
    
    # Verify customer 1 stats
    cust1 = result[result['customer_id'] == 1]
    assert cust1['loan_count'].values[0] == 2, "Customer 1 should have 2 loans"
    assert cust1['dpd_mean'].values[0] == 15.0, "Customer 1 mean DPD should be 15"
    assert cust1['default_count'].values[0] == 0, "Customer 1 should have 0 defaults"
    
    # Verify customer 3 stats
    cust3 = result[result['customer_id'] == 3]
    assert cust3['loan_count'].values[0] == 2, "Customer 3 should have 2 loans"
    assert cust3['default_count'].values[0] == 2, "Customer 3 should have 2 defaults"
    
    # Test error cases
    try:
        bad_loan_df = pd.DataFrame({'loan_id': [101, 102]})
        analyzer.calculate_per_customer_dpd_stats(bad_loan_df, dpd_df)
        assert False, "Should have raised ValueError for missing customer_id"
    except ValueError as e:
        print(f"\nCorrectly raised ValueError: {e}")
    
    print("\n✓ calculate_per_customer_dpd_stats tests passed!")


if __name__ == "__main__":
    print("Starting DPD Analysis Tests...")
    test_add_dpd_bucket_descriptions()
    test_classify_customer_payment_status()
    test_calculate_per_customer_dpd_stats()
    print("\n" + "="*50)
    print("All tests passed! ✓")
    print("="*50)
