# Commercial-View
Principal KPI

## Overview

Commercial-View is a loan portfolio analysis tool that calculates principal KPIs including weighted statistics for key metrics such as APR, EIR, and term.

## Features

- **Weighted Statistics Calculation**: Calculate weighted averages for loan portfolio metrics
- **Multi-language Support**: Handles both English and Spanish column names
- **Case-Insensitive Matching**: Automatically matches columns regardless of case
- **Alias Resolution**: Recognizes common column name variations
- **Robust Error Handling**: Guards against zero/NaN weights and missing data
- **Flexible Weight Field**: Auto-detects alternative weight columns

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from loan_analyzer import LoanAnalyzer
import pandas as pd

# Create loan portfolio data
loan_data = pd.DataFrame({
    'outstanding_balance': [10000, 25000, 15000],
    'apr': [5.5, 6.0, 5.75],
    'eir': [5.65, 6.17, 5.91],
    'term': [12, 24, 18]
})

# Calculate weighted statistics
analyzer = LoanAnalyzer()
weighted_stats = analyzer.calculate_weighted_stats(loan_data)
print(weighted_stats)
```

### Custom Metrics

```python
# Calculate only specific metrics
weighted_stats = analyzer.calculate_weighted_stats(
    loan_data, 
    metrics=['apr', 'eir']
)
```

### Spanish Column Names

```python
loan_data_spanish = pd.DataFrame({
    'saldo_actual': [10000, 25000, 15000],
    'tasa_anual': [5.5, 6.0, 5.75],
    'tasa_efectiva': [5.65, 6.17, 5.91],
    'plazo_dias': [365, 730, 547]
})

weighted_stats = analyzer.calculate_weighted_stats(loan_data_spanish)
```

## Supported Column Aliases

### Weight Fields
- `outstanding_balance`, `olb`, `current_balance`, `saldo_actual`, `balance`

### Metrics
- **APR**: `apr`, `effective_apr`, `annual_rate`, `tasa_anual`
- **EIR**: `eir`, `effective_interest_rate`, `tasa_efectiva`
- **Term**: `term`, `tenor_days`, `plazo_dias`, `tenor`

## Running Tests

```bash
pytest test_loan_analyzer.py -v
```

## Example

See `example_usage.py` for a comprehensive example demonstrating all features.

```bash
python example_usage.py
```
