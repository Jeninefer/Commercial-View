# Commercial-View

Principal KPI Calculator for Commercial Loan Portfolio Analysis

## Overview

Commercial-View is a comprehensive Python library for calculating Key Performance Indicators (KPIs) for commercial loan portfolios. It provides a flexible and extensible framework for analyzing loan data across multiple dimensions including exposure, yield, delinquency, utilization, segment mix, and vintage metrics.

## Features

- **Comprehensive KPI Calculation**: Calculate all KPIs at once or specific metric groups
- **Flexible Configuration**: Customize calculations with `KPIConfig`
- **Multiple Metric Categories**:
  - Exposure Metrics (balance, principal, outstanding amounts)
  - Yield Metrics (interest rates, income, portfolio yield)
  - Delinquency Metrics (rates, buckets, days past due)
  - Utilization Metrics (credit utilization, available credit)
  - Segment Mix Metrics (distribution by segment and product type)
  - Vintage Metrics (loan age, origination dates, maturity)
- **Input Validation**: Built-in DataFrame validation
- **Type Safety**: Full type hints for better IDE support

## Installation

```bash
pip install -r requirements.txt
```

Or install the package:

```bash
pip install -e .
```

## Quick Start

```python
import pandas as pd
from commercial_view import calculate_comprehensive_kpis

# Load your loan data
loan_df = pd.DataFrame({
    'balance': [1000, 2000, 3000],
    'interest_rate': [5.0, 6.0, 7.0],
    'delinquent': [0, 1, 0],
    # ... other columns
})

# Calculate all KPIs
kpis = calculate_comprehensive_kpis(loan_df)

# Access specific metrics
print(f"Total Balance: ${kpis['exposure_metrics']['total_balance']:,.2f}")
print(f"Delinquency Rate: {kpis['delinquency_metrics']['delinquency_rate']:.2f}%")
```

## API Reference

### Public Functions

#### calculate_comprehensive_kpis
Calculate all KPIs based on configuration.

```python
def calculate_comprehensive_kpis(loan_df: pd.DataFrame, config: Optional[KPIConfig] = None) -> Dict[str, Any]
```

#### calculate_exposure_metrics
Calculate exposure-related metrics (balance, principal, outstanding amounts).

```python
def calculate_exposure_metrics(loan_df: pd.DataFrame) -> Dict[str, float]
```

#### calculate_yield_metrics
Calculate yield-related metrics (interest rates, income, portfolio yield).

```python
def calculate_yield_metrics(loan_df: pd.DataFrame) -> Dict[str, float]
```

#### calculate_delinquency_metrics
Calculate delinquency-related metrics (rates, buckets, days past due).

```python
def calculate_delinquency_metrics(loan_df: pd.DataFrame) -> Dict[str, float]
```

#### calculate_utilization_metrics
Calculate utilization-related metrics (credit utilization, available credit).

```python
def calculate_utilization_metrics(loan_df: pd.DataFrame) -> Dict[str, float]
```

#### calculate_segment_mix_metrics
Calculate segment mix metrics (distribution by segment and product type).

```python
def calculate_segment_mix_metrics(loan_df: pd.DataFrame) -> Dict[str, float]
```

#### calculate_vintage_metrics
Calculate vintage-related metrics (loan age, origination dates, maturity).

```python
def calculate_vintage_metrics(loan_df: pd.DataFrame) -> Dict[str, float]
```

### Configuration

Use `KPIConfig` to customize calculations:

```python
from commercial_view import KPIConfig, calculate_comprehensive_kpis

config = KPIConfig(
    include_exposure_metrics=True,
    include_yield_metrics=True,
    include_delinquency_metrics=False,
    include_metadata=False,
)

kpis = calculate_comprehensive_kpis(loan_df, config)
```

## Expected DataFrame Columns

The library expects specific columns depending on which metrics you're calculating:

### Exposure Metrics
- `balance`: Current loan balance
- `principal`: Principal amount
- `outstanding_amount`: Outstanding amount

### Yield Metrics
- `interest_rate`: Interest rate (percentage)
- `interest_income`: Interest income
- `balance`: Required for weighted averages

### Delinquency Metrics
- `delinquent`: Binary flag (0/1)
- `days_past_due`: Days past due
- `balance`: Required for balance-based rates

### Utilization Metrics
- `balance`: Current balance
- `credit_limit`: Credit limit

### Segment Mix Metrics
- `segment`: Loan segment (e.g., 'retail', 'commercial')
- `product_type`: Product type (e.g., 'term_loan', 'line_of_credit')
- `balance`: Optional, for balance-based distribution

### Vintage Metrics
- `loan_age`: Loan age in days
- `origination_date`: Origination date
- `maturity_date`: Maturity date
- `balance`: Optional, for weighted averages

## Examples

See the [examples](examples/) directory for complete usage examples:

```bash
python examples/usage_example.py
```

## Testing

Run the test suite:

```bash
python -m unittest tests.test_kpi_calculator -v
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

