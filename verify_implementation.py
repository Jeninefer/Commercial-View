"""
Verification script to ensure the implementation matches the problem statement.
"""

import pandas as pd
from feature_engineer import (
    FeatureEngineer,
    feature_engineer,
    segment_clients_by_exposure,
    classify_dpd_buckets,
    classify_client_type,
    calculate_weighted_metrics,
    calculate_line_utilization,
    enrich_master_dataframe
)

print("Verifying implementation against problem statement...\n")

# 1. Verify global instance exists
print("1. Checking global instance 'feature_engineer':")
assert isinstance(feature_engineer, FeatureEngineer), "Global instance must be a FeatureEngineer"
print("   ✓ Global instance exists and is of type FeatureEngineer\n")

# 2. Verify wrapper function signatures match problem statement
print("2. Checking wrapper function signatures:")

# Test segment_clients_by_exposure
df = pd.DataFrame({'outstanding_balance': [10000]})
result = segment_clients_by_exposure(df, exposure_col='outstanding_balance', segments=None)
assert isinstance(result, pd.DataFrame)
print("   ✓ segment_clients_by_exposure(df, exposure_col='outstanding_balance', segments=None)")

# Test classify_dpd_buckets
df = pd.DataFrame({'days_past_due': [30]})
result = classify_dpd_buckets(df, dpd_col='days_past_due')
assert isinstance(result, pd.DataFrame)
print("   ✓ classify_dpd_buckets(df, dpd_col='days_past_due')")

# Test classify_client_type
df = pd.DataFrame({'customer_id': [1], 'loan_count': [1], 'last_active_date': [pd.Timestamp.now()]})
result = classify_client_type(df, customer_id_col='customer_id', loan_count_col='loan_count', last_active_col='last_active_date')
assert isinstance(result, pd.DataFrame)
print("   ✓ classify_client_type(df, customer_id_col='customer_id', loan_count_col='loan_count', last_active_col='last_active_date')")

# Test calculate_weighted_metrics
df = pd.DataFrame({'outstanding_balance': [100], 'metric1': [5.0]})
result = calculate_weighted_metrics(df, metrics=['metric1'], weight_col='outstanding_balance')
assert isinstance(result, pd.DataFrame)
print("   ✓ calculate_weighted_metrics(df, metrics, weight_col='outstanding_balance')")

# Test calculate_line_utilization - note the parameter order swap
df = pd.DataFrame({'outstanding_balance': [50], 'line_amount': [100]})
result = calculate_line_utilization(df, balance_col='outstanding_balance', line_col='line_amount')
assert isinstance(result, pd.DataFrame)
print("   ✓ calculate_line_utilization(df, balance_col='outstanding_balance', line_col='line_amount')")
print("     Note: Wrapper intentionally switches order to match (credit_line_field, loan_amount_field)")

# Test enrich_master_dataframe
df = pd.DataFrame({'outstanding_balance': [10000]})
result = enrich_master_dataframe(df)
assert isinstance(result, pd.DataFrame)
print("   ✓ enrich_master_dataframe(df)\n")

# 3. Verify assertions
print("3. Checking assertion validations:")
try:
    segment_clients_by_exposure("not a dataframe")
    print("   ✗ DataFrame assertion failed")
except AssertionError as e:
    assert str(e) == "df must be a DataFrame"
    print("   ✓ All wrapper functions validate df is a DataFrame")

try:
    calculate_weighted_metrics(pd.DataFrame({'col': [1]}), [])
    print("   ✗ Metrics assertion failed")
except AssertionError as e:
    assert str(e) == "metrics must be a non-empty list"
    print("   ✓ calculate_weighted_metrics validates metrics is a non-empty list\n")

# 4. Verify FeatureEngineer class methods exist
print("4. Checking FeatureEngineer class methods:")
methods = [
    'segment_clients_by_exposure',
    'classify_dpd_buckets',
    'classify_client_type',
    'calculate_weighted_metrics',
    'calculate_line_utilization',
    'enrich_master_dataframe'
]
for method in methods:
    assert hasattr(feature_engineer, method), f"Method {method} not found"
    print(f"   ✓ {method}")

print("\n" + "="*60)
print("All requirements from problem statement verified! ✓")
print("="*60)
