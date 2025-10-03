# Commercial-View
Principal KPI Analytics for Commercial Lending

## Overview
Commercial-View provides KPI analytics tools for commercial lending portfolios, with a focus on weighted metrics calculation.

## Features
- **Weighted Metrics Calculation**: Compute weighted averages for metrics based on outstanding balances or custom weights
- **Robust Data Handling**: Automatically filters out invalid data (NaN, infinite, zero, and negative weights)
- **Multiple Metrics Support**: Calculate weighted averages for multiple metrics simultaneously
- **Comprehensive Logging**: Detailed warnings and error messages for data quality issues

## Installation

```bash
pip install -e .
```

For development:
```bash
pip install -e .
pip install -r requirements-dev.txt
```

## Usage

```python
import pandas as pd
from commercial_view import MetricsCalculator

# Create sample data
data = pd.DataFrame({
    'outstanding_balance': [10000, 25000, 50000],
    'interest_rate': [4.5, 5.0, 5.5],
    'credit_score': [720, 680, 750]
})

# Calculate weighted metrics
calculator = MetricsCalculator()
metrics = calculator.calculate_weighted_metrics(
    df=data,
    metrics=['interest_rate', 'credit_score'],
    weight_col='outstanding_balance'
)

print(metrics)
# Output: {'weighted_interest_rate': 5.18, 'weighted_credit_score': 726.15}
```

See `example.py` for a complete working example.

## Testing

Run the test suite:
```bash
pytest tests/
```

Run tests with coverage:
```bash
pytest tests/ --cov=commercial_view
```

## Method Documentation

### `calculate_weighted_metrics(df, metrics, weight_col='outstanding_balance')`

Compute weighted averages for explicit metric columns with guards against zero/NaN weights.

**Parameters:**
- `df` (pd.DataFrame): Input DataFrame containing metrics and weight column
- `metrics` (List[str]): List of metric column names to calculate weighted averages for
- `weight_col` (str): Column name to use as weights (default: 'outstanding_balance')

**Returns:**
- `Dict[str, float]`: Dictionary with keys `weighted_{metric}` and their calculated values

**Edge Cases Handled:**
- Missing weight column: Returns empty dict with error log
- Missing metric columns: Skips with warning
- NaN, infinite, zero, or negative weights: Automatically filtered out
- Empty DataFrame or no valid data: Returns empty dict with warning

## License
This project is part of the Commercial-View Principal KPI system
