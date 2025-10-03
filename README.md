# Commercial-View
Principal KPI - Feature Engineering Module

## Overview

This repository contains a feature engineering module for commercial loan portfolio analysis. The module provides tools for client segmentation, classification, and metric calculation.

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Features

The `FeatureEngineer` class provides the following methods:

### 1. Client Segmentation by Exposure
Segments clients into categories based on their outstanding balance.

```python
segment_clients_by_exposure(df, exposure_col='outstanding_balance', segments=None)
```

### 2. DPD Bucket Classification
Classifies days past due into standardized buckets (Current, 1-30, 31-60, 61-90, 91-180, 180+).

```python
classify_dpd_buckets(df, dpd_col='days_past_due')
```

### 3. Client Type Classification
Classifies clients as New, Regular, High-Value, Dormant, or Inactive based on loan count and activity.

```python
classify_client_type(df, customer_id_col='customer_id', loan_count_col='loan_count', last_active_col='last_active_date')
```

### 4. Weighted Metrics Calculation
Calculates weighted averages for specified metrics.

```python
calculate_weighted_metrics(df, metrics, weight_col='outstanding_balance')
```

### 5. Line Utilization Calculation
Calculates the utilization percentage of credit lines.

```python
calculate_line_utilization(df, balance_col='outstanding_balance', line_col='line_amount')
```

### 6. Master Dataframe Enrichment
Applies all feature engineering methods to enrich a dataframe.

```python
enrich_master_dataframe(df)
```

## Usage

```python
from feature_engineer import (
    segment_clients_by_exposure,
    classify_dpd_buckets,
    classify_client_type,
    calculate_weighted_metrics,
    calculate_line_utilization,
    enrich_master_dataframe
)

import pandas as pd

# Create sample data
df = pd.DataFrame({
    'customer_id': [1, 2, 3],
    'outstanding_balance': [5000, 50000, 150000],
    'line_amount': [10000, 100000, 200000],
    'days_past_due': [0, 30, 90],
    'loan_count': [1, 3, 10],
    'last_active_date': [datetime.now()] * 3
})

# Enrich the dataframe with all features
enriched_df = enrich_master_dataframe(df)
```

## Examples

Run the example script to see all features in action:

```bash
python example_usage.py
```

## Testing

Run the test suite to verify the implementation:

```bash
python test_feature_engineer.py
```

Run the verification script to check compliance with requirements:

```bash
python verify_implementation.py
```
