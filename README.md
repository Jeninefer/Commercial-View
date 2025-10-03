# Commercial-View
Principal KPI Analysis for Loan Portfolios

## Overview

Commercial-View is a Python library for analyzing loan portfolios with a focus on Days Past Due (DPD) bucket assignment and default risk analysis.

## Features

- **DPD Bucket Assignment**: Automatically assign loans to standard or custom DPD buckets
- **Default Flag Calculation**: Mark loans as defaulted based on configurable thresholds
- **Flexible Configuration**: Support for both default and custom bucket definitions
- **Data Quality Handling**: Robust handling of missing and invalid data

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from src.commercial_view import LoanAnalyzer
import pandas as pd

# Create a loan analyzer with default settings
analyzer = LoanAnalyzer(dpd_threshold=90)

# Prepare your loan data
df = pd.DataFrame({
    'loan_id': [1, 2, 3, 4],
    'days_past_due': [0, 15, 45, 100]
})

# Assign DPD buckets and default flags
result = analyzer.assign_dpd_buckets(df)
print(result)
```

## Usage

### Default DPD Buckets

The default bucket configuration includes:
- **Current**: 0 days past due
- **1-29**: 1-29 days past due
- **30-59**: 30-59 days past due
- **60-89**: 60-89 days past due
- **90-119**: 90-119 days past due
- **120-149**: 120-149 days past due
- **150-179**: 150-179 days past due
- **180+**: 180+ days past due

### Custom DPD Buckets

You can define custom buckets by passing a configuration:

```python
config = {
    "dpd_buckets": [
        (0, 0, "Current"),
        (1, 29, "Early Delinquency"),
        (30, 89, "Moderate Delinquency"),
        (90, 179, "Severe Delinquency"),
        (180, None, "Default")  # None for open-ended bucket
    ]
}

analyzer = LoanAnalyzer(config=config, dpd_threshold=90)
result = analyzer.assign_dpd_buckets(df)
```

### Custom Default Threshold

Adjust the threshold for marking loans as defaulted:

```python
# Mark loans as defaulted at 60+ days past due
analyzer = LoanAnalyzer(dpd_threshold=60)
```

## API Reference

### LoanAnalyzer

#### `__init__(config=None, dpd_threshold=90)`

Initialize the LoanAnalyzer.

**Parameters:**
- `config` (dict, optional): Configuration dictionary that may contain 'dpd_buckets'
- `dpd_threshold` (int, default=90): Days past due threshold for default flag

#### `assign_dpd_buckets(dpd_df)`

Assign DPD buckets to loans.

**Parameters:**
- `dpd_df` (pd.DataFrame): DataFrame containing a 'days_past_due' column

**Returns:**
- pd.DataFrame: Copy of input DataFrame with added columns:
  - `dpd_bucket`: The assigned DPD bucket label
  - `default_flag`: Binary flag (0 or 1) indicating default status

**Raises:**
- ValueError: If input is not a DataFrame or missing 'days_past_due' column

## Examples

See `example.py` for comprehensive usage examples.

## Running Tests

```bash
pytest tests/ -v
```

## License

MIT License
