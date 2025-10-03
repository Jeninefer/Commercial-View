# Commercial-View
Principal KPI - Customer Classification Feature Engineering

## Overview
This repository contains a feature engineering module for customer analytics, specifically for classifying customers based on their loan history and activity patterns.

## Features

### FeatureEngineer Class
The `FeatureEngineer` class provides methods for customer analysis:

#### `classify_client_type`
Classifies customers into three categories:
- **New**: Customers with 0 or 1 loan
- **Recurrent**: Customers with >1 loan and last activity within 90 days
- **Recovered**: Customers with >1 loan who returned after >90 days of inactivity

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from src.feature_engineer import FeatureEngineer
import pandas as pd
from datetime import datetime

# Create instance
fe = FeatureEngineer()

# Prepare your data
df = pd.DataFrame({
    'customer_id': [1, 2, 3, 4],
    'loan_count': [0, 2, 3, 5],
    'last_active_date': ['2023-12-01', '2023-10-20', '2023-09-01', '2023-12-25']
})

# Classify customers
result = fe.classify_client_type(
    df,
    customer_id_col='customer_id',
    loan_count_col='loan_count',
    last_active_col='last_active_date',
    reference_date=datetime(2024, 1, 1)
)

print(result[['customer_id', 'customer_type']])
```

## Testing

Run the test suite:

```bash
pytest tests/test_feature_engineer.py -v
```

## Project Structure

```
Commercial-View/
├── src/
│   ├── __init__.py
│   └── feature_engineer.py    # Main feature engineering module
├── tests/
│   ├── __init__.py
│   └── test_feature_engineer.py  # Unit tests
├── requirements.txt
└── README.md
```

## Classification Logic

The classification follows these rules:
1. If `loan_count <= 1`: Customer is classified as **New**
2. If `loan_count > 1` and `days_since_last > 90`: Customer is classified as **Recovered**
3. If `loan_count > 1` and `days_since_last <= 90`: Customer is classified as **Recurrent**

Note: If the `last_active_date` column is missing, classification is based solely on loan count.
