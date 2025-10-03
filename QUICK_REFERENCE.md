# Quick Reference Guide

## Installation
```bash
pip install -r requirements.txt
```

## Import
```python
from feature_engineer import (
    segment_clients_by_exposure,
    classify_dpd_buckets,
    classify_client_type,
    calculate_weighted_metrics,
    calculate_line_utilization,
    enrich_master_dataframe
)
```

## Function Signatures

### 1. segment_clients_by_exposure
```python
segment_clients_by_exposure(df, exposure_col='outstanding_balance', segments=None)
# Returns: DataFrame with 'exposure_segment' column
```

### 2. classify_dpd_buckets
```python
classify_dpd_buckets(df, dpd_col='days_past_due')
# Returns: DataFrame with 'dpd_bucket' column
```

### 3. classify_client_type
```python
classify_client_type(df, customer_id_col='customer_id', 
                    loan_count_col='loan_count', 
                    last_active_col='last_active_date')
# Returns: DataFrame with 'client_type' column
```

### 4. calculate_weighted_metrics
```python
calculate_weighted_metrics(df, metrics, weight_col='outstanding_balance')
# metrics: list of column names to weight
# Returns: DataFrame with 'weighted_{metric}' columns
```

### 5. calculate_line_utilization
```python
calculate_line_utilization(df, balance_col='outstanding_balance', 
                          line_col='line_amount')
# Returns: DataFrame with 'line_utilization' column
```

### 6. enrich_master_dataframe
```python
enrich_master_dataframe(df)
# Applies all enrichments
# Returns: DataFrame with all feature columns added
```

## Quick Example
```python
import pandas as pd
from feature_engineer import enrich_master_dataframe

# Sample data
df = pd.DataFrame({
    'customer_id': [1, 2, 3],
    'outstanding_balance': [10000, 50000, 150000],
    'line_amount': [20000, 100000, 200000],
    'days_past_due': [0, 30, 90],
    'loan_count': [1, 3, 10]
})

# Enrich with all features
enriched = enrich_master_dataframe(df)
print(enriched.columns)
# ['customer_id', 'outstanding_balance', 'line_amount', 'days_past_due', 
#  'loan_count', 'exposure_segment', 'dpd_bucket', 'client_type', 
#  'line_utilization']
```

## Testing
```bash
python test_feature_engineer.py          # Run unit tests
python verify_implementation.py          # Verify requirements
python example_usage.py                  # See examples
```
