"""Example usage of Commercial-View DPD analysis module."""

import pandas as pd
from commercial_view import DPDAnalyzer, add_dpd_bucket_descriptions


def example_dpd_bucket_descriptions():
    """Example: Adding descriptions to DPD buckets."""
    print("=" * 60)
    print("Example 1: Adding DPD Bucket Descriptions")
    print("=" * 60)
    
    # Sample DPD data with buckets
    dpd_df = pd.DataFrame({
        'loan_id': [1001, 1002, 1003, 1004, 1005],
        'dpd_bucket': ['Current', '1-29', '30-59', '90-119', '180+'],
        'amount': [10000, 5000, 7500, 12000, 8000]
    })
    
    print("\nInput DataFrame:")
    print(dpd_df)
    
    # Add descriptions
    result = add_dpd_bucket_descriptions(dpd_df)
    
    print("\nOutput DataFrame with Descriptions:")
    print(result)


def example_classify_payment_status():
    """Example: Classifying customer payment status."""
    print("\n" + "=" * 60)
    print("Example 2: Classifying Customer Payment Status")
    print("=" * 60)
    
    # Sample loan data
    loan_df = pd.DataFrame({
        'customer_id': [101, 101, 102, 103, 103],
        'loan_id': [1001, 1002, 2001, 3001, 3002],
        'loan_amount': [50000, 30000, 75000, 40000, 25000]
    })
    
    # Sample customer data
    customer_df = pd.DataFrame({
        'customer_id': [101, 102, 103],
        'customer_name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
        'customer_segment': ['Premium', 'Standard', 'Premium']
    })
    
    # Sample DPD data
    dpd_df = pd.DataFrame({
        'loan_id': [1001, 1002, 2001, 3001, 3002],
        'days_past_due': [0, 15, 0, 95, 120],
        'is_default': [False, False, False, True, True],
        'first_arrears_date': ['2023-06-01', '2023-07-15', None, '2023-03-01', '2023-02-15'],
        'last_payment_date': ['2024-01-15', '2024-01-20', '2024-01-10', '2023-12-01', '2023-11-15']
    })
    
    print("\nLoan DataFrame:")
    print(loan_df)
    print("\nCustomer DataFrame:")
    print(customer_df)
    print("\nDPD DataFrame:")
    print(dpd_df)
    
    # Classify payment status
    analyzer = DPDAnalyzer()
    result = analyzer.classify_customer_payment_status(
        loan_df=loan_df,
        customer_df=customer_df,
        dpd_df=dpd_df,
        customer_id_field='customer_id',
        threshold_days=90
    )
    
    print("\nResult with Payment Status:")
    print(result[['customer_id', 'customer_name', 'payment_status', 'max_dpd', 
                  'loan_count', 'has_defaulted']])


def example_calculate_dpd_stats():
    """Example: Calculating per-customer DPD statistics."""
    print("\n" + "=" * 60)
    print("Example 3: Calculating Per-Customer DPD Statistics")
    print("=" * 60)
    
    # Sample loan data
    loan_df = pd.DataFrame({
        'customer_id': [101, 101, 102, 103, 103, 103],
        'loan_id': [1001, 1002, 2001, 3001, 3002, 3003]
    })
    
    # Sample DPD data with amounts
    dpd_df = pd.DataFrame({
        'loan_id': [1001, 1002, 2001, 3001, 3002, 3003],
        'days_past_due': [0, 15, 5, 95, 120, 60],
        'is_default': [False, False, False, True, True, False],
        'past_due_amount': [0, 500, 100, 8000, 12000, 2000]
    })
    
    print("\nLoan DataFrame:")
    print(loan_df)
    print("\nDPD DataFrame:")
    print(dpd_df)
    
    # Calculate statistics
    analyzer = DPDAnalyzer()
    result = analyzer.calculate_per_customer_dpd_stats(
        loan_df=loan_df,
        dpd_df=dpd_df,
        customer_id_field='customer_id'
    )
    
    print("\nPer-Customer DPD Statistics:")
    print(result[['customer_id', 'dpd_mean', 'dpd_max', 'default_count', 
                  'past_due_amount_sum', 'weighted_dpd']])


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Commercial-View: DPD Analysis Examples")
    print("=" * 60)
    
    example_dpd_bucket_descriptions()
    example_classify_payment_status()
    example_calculate_dpd_stats()
    
    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)
