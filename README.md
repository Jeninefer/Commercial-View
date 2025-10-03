# Commercial-View

A comprehensive toolkit for analyzing Days Past Due (DPD) in commercial loan portfolios.

## Overview

Commercial-View provides functionality for analyzing and categorizing loan accounts based on their days past due status. It includes tools for bucket assignment, field detection, and portfolio analysis.

## Features

- **DPD Bucket Assignment**: Automatically categorize accounts into standard DPD buckets (Current, 1-29, 30-59, etc.)
- **Default Detection**: Flag accounts that meet default criteria (customizable threshold)
- **Smart Field Detection**: Automatically detect relevant columns in DataFrames using multiple matching strategies
- **Comprehensive Analysis**: Generate detailed descriptions and metrics for portfolio analysis

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Example

```python
import pandas as pd
from dpd_analyzer import DPDAnalyzer

# Create sample data
data = pd.DataFrame({
    "account_id": ["ACC001", "ACC002", "ACC003"],
    "days_past_due": [0, 45, 120],
    "balance": [1000, 5000, 3000]
})

# Initialize analyzer (default threshold: 90 days)
analyzer = DPDAnalyzer(dpd_threshold=90)

# Assign DPD buckets
result = analyzer.assign_dpd_buckets(data)

print(result)
```

### Field Detection

```python
# Detect fields in a DataFrame
df = pd.DataFrame(columns=["account_number", "total_days_past_due", "balance"])

# Try multiple patterns
field = analyzer.detect_field(df, ["days_past_due", "dpd", "days"])
print(f"Detected field: {field}")  # Output: total_days_past_due
```

## DPD Buckets

The analyzer assigns accounts to the following buckets:

| Bucket | Days Past Due | Description | Default Flag |
|--------|---------------|-------------|--------------|
| Current | 0 | No payment due | No |
| 1-29 | 1-29 days | Early delinquency | No |
| 30-59 | 30-59 days | Delinquent 30 days | No |
| 60-89 | 60-89 days | Delinquent 60 days | No |
| 90-119 | 90-119 days | Default 90 days | Yes |
| 120-149 | 120-149 days | Default 120 days | Yes |
| 150-179 | 150-179 days | Default 150 days | Yes |
| 180+ | 180+ days | Default 180+ days | Yes |

## API Reference

### DPDAnalyzer

#### `__init__(dpd_threshold: int = 90)`
Initialize the DPD Analyzer with a custom default threshold.

#### `assign_dpd_buckets(dpd_df: pd.DataFrame) -> pd.DataFrame`
Assign DPD buckets to a DataFrame containing days past due information.

**Parameters:**
- `dpd_df`: DataFrame with a 'days_past_due' column

**Returns:**
- DataFrame with added columns:
  - `dpd_bucket`: The bucket label
  - `dpd_bucket_value`: Numeric value representing the bucket
  - `dpd_bucket_description`: Human-readable description
  - `default_flag`: Boolean flag indicating if account is in default

#### `detect_field(df: pd.DataFrame, patterns: List[str]) -> Optional[str]`
Detect a field in a DataFrame based on a list of patterns.

**Parameters:**
- `df`: DataFrame to search for matching column names
- `patterns`: List of patterns to match against column names

**Returns:**
- The name of the first matching column, or None if no match found

## Running Tests

```bash
python -m pytest test_dpd_analyzer.py -v
```

## Example Output

Run the example script to see the analyzer in action:

```bash
python example_usage.py
```

## License

MIT License
