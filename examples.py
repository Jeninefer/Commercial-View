"""
Example usage of the FeatureEngineer class
"""
import pandas as pd
from abaco_core.feature_engineering import FeatureEngineer


def main():
    # Initialize the feature engineer
    fe = FeatureEngineer()
    
    print("=" * 70)
    print("FeatureEngineer Example Usage")
    print("=" * 70)
    
    # Example 1: Customer Segmentation
    print("\n1. Customer Segmentation by Exposure")
    print("-" * 70)
    loan_data = pd.DataFrame({
        'customer_id': ['C1', 'C1', 'C2', 'C2', 'C3', 'C3', 'C4', 'C4', 'C5', 'C5', 'C6', 'C6'],
        'outstanding_balance': [1000, 500, 2000, 1000, 3000, 500, 4000, 1000, 5000, 2000, 6000, 3000]
    })
    segments = fe.segment_customers_by_exposure(loan_data, 'customer_id')
    print(segments.to_string(index=False))
    
    # Example 2: DPD Bucketing
    print("\n2. DPD Bucket Assignment")
    print("-" * 70)
    dpd_data = pd.DataFrame({
        'loan_id': ['L1', 'L2', 'L3', 'L4', 'L5', 'L6'],
        'days_past_due': [0, 15, 45, 75, 105, 200]
    })
    dpd_buckets = fe.assign_dpd_buckets(dpd_data)
    print(dpd_buckets[['loan_id', 'days_past_due', 'dpd_bucket', 'is_default']].to_string(index=False))
    
    # Example 3: Customer Type Classification
    print("\n3. Customer Type Classification")
    print("-" * 70)
    customer_df = pd.DataFrame({
        'customer_id': ['C1', 'C2', 'C3']
    })
    loan_history = pd.DataFrame({
        'customer_id': ['C1', 'C2', 'C2', 'C3', 'C3', 'C3'],
        'loan_start_date': ['2023-01-01', '2023-01-01', '2023-02-01', '2023-01-01', '2023-02-01', '2023-06-01']
    })
    customer_types = fe.classify_customer_type(customer_df, loan_history, 'customer_id', 'loan_start_date')
    print(customer_types.to_string(index=False))
    
    # Example 4: Weighted Statistics
    print("\n4. Weighted Statistics")
    print("-" * 70)
    weighted_data = pd.DataFrame({
        'apr': [10.0, 15.0, 20.0],
        'term': [12, 24, 36],
        'outstanding_balance': [1000, 2000, 1000]
    })
    weighted_stats = fe.calculate_weighted_stats(weighted_data, 'outstanding_balance', ['apr', 'term'])
    print(weighted_stats.to_string(index=False))
    
    # Example 5: Line Utilization
    print("\n5. Line Utilization")
    print("-" * 70)
    line_data = pd.DataFrame({
        'loan_id': ['L1', 'L2', 'L3'],
        'line_amount': [10000, 5000, 20000],
        'outstanding_balance': [8000, 6000, 15000]
    })
    line_util = fe.calculate_line_utilization(line_data)
    print(line_util[['loan_id', 'line_amount', 'outstanding_balance', 'line_utilization']].to_string(index=False))
    
    # Example 6: HHI Calculation
    print("\n6. Concentration (HHI) Calculation")
    print("-" * 70)
    hhi_data = pd.DataFrame({
        'customer_id': ['C1', 'C1', 'C2', 'C2', 'C3'],
        'outstanding_balance': [3000, 2000, 2000, 1000, 2000]
    })
    hhi = fe.calculate_hhi(hhi_data, 'customer_id')
    print(f"Portfolio HHI: {hhi:.2f}")
    
    # Example 7: Master Enrichment
    print("\n7. Master Dataframe Enrichment")
    print("-" * 70)
    master_data = pd.DataFrame({
        'loan_id': ['L1', 'L2', 'L3'],
        'customer_id': ['C1', 'C2', 'C3'],
        'outstanding_balance': [1000, 2000, 1500],
        'days_past_due': [0, 45, 105],
        'line_amount': [5000, 10000, 7500],
        'apr': [10, 15, 12],
        'term': [12, 24, 18]
    })
    enriched = fe.enrich_master_dataframe(master_data)
    print(enriched[['loan_id', 'dpd_bucket', 'is_default', 'line_utilization', 'apr_zscore']].to_string(index=False))
    
    print("\n" + "=" * 70)
    print("Examples completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
