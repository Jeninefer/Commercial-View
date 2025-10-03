# Commercial-View
Principal KPI and Feature Engineering Module

## Overview
Commercial-View is a feature engineering library for commercial lending and credit risk analytics. It provides tools for customer segmentation, risk bucketing, and portfolio analysis.

## Features

### FeatureEngineer Class
The `FeatureEngineer` class provides the following capabilities:

1. **Customer Segmentation by Exposure**
   - Segments customers into groups (A-F) based on their total exposure
   - Handles missing columns with intelligent name matching

2. **DPD (Days Past Due) Bucketing**
   - Classifies loans into DPD buckets (Current, 1-29, 30-59, 60-89, 90-119, 120-149, 150-179, 180+)
   - Automatically flags defaults (DPD >= 90)

3. **Customer Type Classification**
   - Classifies customers as New, Recurrent, or Recovered
   - Based on loan history patterns and gaps between loans

4. **Weighted Statistics**
   - Calculates exposure-weighted metrics (APR, EIR, term, etc.)
   - Useful for portfolio-level analysis

5. **Line Utilization**
   - Computes credit line utilization ratios
   - Automatically caps at 100%

6. **Concentration Analysis (HHI)**
   - Calculates Herfindahl-Hirschman Index
   - Measures portfolio concentration risk

7. **Master Dataframe Enrichment**
   - One-stop enrichment with multiple features
   - Includes z-score standardization for key metrics

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from abaco_core.feature_engineering import FeatureEngineer
import pandas as pd

# Initialize
fe = FeatureEngineer()

# Example: Segment customers by exposure
loan_df = pd.DataFrame({
    'customer_id': ['C1', 'C1', 'C2'],
    'outstanding_balance': [1000, 500, 2000]
})

segments = fe.segment_customers_by_exposure(loan_df, 'customer_id')
print(segments)

# Example: Assign DPD buckets
dpd_df = pd.DataFrame({
    'loan_id': ['L1', 'L2', 'L3'],
    'days_past_due': [0, 45, 105]
})

bucketed = fe.assign_dpd_buckets(dpd_df)
print(bucketed)
```

## Testing

Run tests with:

```bash
python tests/test_feature_engineering.py
```

## Requirements

- Python 3.7+
- pandas >= 1.3.0
- numpy >= 1.21.0
