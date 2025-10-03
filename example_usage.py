"""
Example usage of the Feature Engineering Module
"""

import pandas as pd
from datetime import datetime, timedelta
from feature_engineer import (
    segment_clients_by_exposure,
    classify_dpd_buckets,
    classify_client_type,
    calculate_weighted_metrics,
    calculate_line_utilization,
    enrich_master_dataframe
)

print("="*70)
print("Feature Engineering Module - Example Usage")
print("="*70)

# Create sample data
sample_data = pd.DataFrame({
    'customer_id': [1, 2, 3, 4, 5],
    'outstanding_balance': [5000, 25000, 75000, 150000, 200000],
    'line_amount': [10000, 50000, 100000, 200000, 250000],
    'days_past_due': [0, 15, 45, 90, 150],
    'loan_count': [1, 1, 3, 5, 12],
    'last_active_date': [
        datetime.now(),
        datetime.now() - timedelta(days=30),
        datetime.now() - timedelta(days=60),
        datetime.now() - timedelta(days=90),
        datetime.now() - timedelta(days=10)
    ],
    'interest_rate': [5.0, 5.5, 6.0, 6.5, 7.0],
    'risk_score': [10, 15, 20, 25, 30]
})

print("\n1. Original Data:")
print(sample_data)

# Example 1: Segment clients by exposure
print("\n" + "="*70)
print("Example 1: Segment Clients by Exposure")
print("="*70)
result = segment_clients_by_exposure(sample_data)
print(result[['customer_id', 'outstanding_balance', 'exposure_segment']])

# Example 2: Classify DPD buckets
print("\n" + "="*70)
print("Example 2: Classify Days Past Due Buckets")
print("="*70)
result = classify_dpd_buckets(sample_data)
print(result[['customer_id', 'days_past_due', 'dpd_bucket']])

# Example 3: Classify client type
print("\n" + "="*70)
print("Example 3: Classify Client Type")
print("="*70)
result = classify_client_type(sample_data)
print(result[['customer_id', 'loan_count', 'client_type']])

# Example 4: Calculate weighted metrics
print("\n" + "="*70)
print("Example 4: Calculate Weighted Metrics")
print("="*70)
result = calculate_weighted_metrics(sample_data, ['interest_rate', 'risk_score'])
print(result[['customer_id', 'outstanding_balance', 'interest_rate', 'weighted_interest_rate', 'risk_score', 'weighted_risk_score']])

# Example 5: Calculate line utilization
print("\n" + "="*70)
print("Example 5: Calculate Line Utilization")
print("="*70)
result = calculate_line_utilization(sample_data)
print(result[['customer_id', 'outstanding_balance', 'line_amount', 'line_utilization']])

# Example 6: Enrich master dataframe (applies all features)
print("\n" + "="*70)
print("Example 6: Enrich Master Dataframe (All Features)")
print("="*70)
result = enrich_master_dataframe(sample_data)
print("\nColumns in enriched dataframe:")
print(result.columns.tolist())
print("\nSample of enriched data:")
print(result[['customer_id', 'exposure_segment', 'dpd_bucket', 'client_type', 'line_utilization']].head())

print("\n" + "="*70)
print("Examples completed successfully!")
print("="*70)
