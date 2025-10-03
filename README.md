# Commercial-View
Principal KPI Analysis

## Overview
This package provides tools for customer classification and KPI analysis for commercial operations.

## Installation

```bash
pip install -r requirements.txt
```

## Features

### FeatureEngineer Class
The `FeatureEngineer` class provides feature engineering capabilities for customer analysis.

#### classify_client_type Method
Classifies customers into three categories based on their loan history and activity patterns:
- **New**: Customers with 1 or fewer loans
- **Recurrent**: Customers with more than 1 loan and last active ≤90 days ago
- **Recovered**: Customers with more than 1 loan and last active >90 days ago

## Usage

```python
from commercial_view import FeatureEngineer
import pandas as pd
from datetime import datetime

# Create sample data
df = pd.DataFrame({
    'customer_id': [1, 2, 3],
    'loan_count': [1, 3, 2],
    'last_active_date': ['2023-12-15', '2023-11-20', '2023-08-15']
})

# Initialize and classify
fe = FeatureEngineer()
result = fe.classify_client_type(df, reference_date=datetime(2024, 1, 1))

print(result[['customer_id', 'loan_count', 'customer_type']])
```

## Running Tests

```bash
python -m unittest tests.test_feature_engineer -v
```

## Example

Run the example script to see the classification in action:

```bash
python example.py
```
