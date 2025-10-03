# Commercial-View
Principal KPI

## Overview

This repository provides loan portfolio analytics capabilities, including weighted statistics calculations for commercial loan portfolios.

## Features

- **Weighted Statistics Calculation**: Calculate weighted averages for loan metrics (APR, EIR, term) using outstanding balances or other weight fields
- **Flexible Column Matching**: Supports case-insensitive and alias-based column name matching
- **Robust Data Handling**: Automatically handles missing values, zero weights, and invalid data
- **Multilingual Support**: Includes aliases for Spanish column names (e.g., "tasa_anual", "saldo_actual")

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Example

```python
import pandas as pd
from loan_analytics import LoanAnalytics

# Create sample loan data
loan_data = pd.DataFrame({
    'outstanding_balance': [10000, 25000, 15000],
    'apr': [4.5, 5.5, 6.0],
    'eir': [4.6, 5.7, 6.2],
    'term': [360, 240, 300]
})

# Initialize analytics
analytics = LoanAnalytics()

# Calculate weighted statistics
result = analytics.calculate_weighted_stats(loan_data)
print(result)
```

### Advanced Usage

```python
# Calculate specific metrics only
result = analytics.calculate_weighted_stats(
    loan_data, 
    metrics=['apr', 'term']
)

# Use a different weight field
result = analytics.calculate_weighted_stats(
    loan_data,
    weight_field='current_balance'
)
```

### Supported Column Aliases

The `calculate_weighted_stats` method automatically recognizes various column name formats:

- **APR**: apr, effective_apr, annual_rate, tasa_anual
- **EIR**: eir, effective_interest_rate, tasa_efectiva
- **Term**: term, tenor_days, plazo_dias, tenor
- **Weight fields**: outstanding_balance, olb, current_balance, saldo_actual, balance

## Running Tests

Run the test suite:

```bash
python -m unittest test_loan_analytics.py -v
```

## Example Script

See `example_usage.py` for comprehensive examples demonstrating:
- Basic weighted statistics calculation
- Custom metric selection
- Column alias handling
- Missing value handling

Run the example:

```bash
python example_usage.py
```

## API Documentation

### `LoanAnalytics.calculate_weighted_stats()`

Calculate weighted averages for specified metrics.

**Parameters:**
- `loan_df` (pd.DataFrame): DataFrame containing loan data
- `weight_field` (str, optional): Column name to use as weights. Default: "outstanding_balance"
- `metrics` (List[str], optional): List of metric names to calculate. Default: ["apr", "eir", "term"]

**Returns:**
- `pd.DataFrame`: DataFrame with weighted statistics, or empty DataFrame if calculation fails

**Features:**
- Automatically resolves column name variations through alias matching
- Case-insensitive column matching
- Handles missing values (NaN)
- Excludes zero and negative weights
- Provides detailed logging for debugging

## License

This project is licensed under the MIT License.
