# Commercial-View
Principal KPI - Days Past Due (DPD) Analysis for Commercial Lending

## Overview

Commercial-View is a Python package designed to analyze Days Past Due (DPD) metrics for commercial lending portfolios. It provides comprehensive tools for calculating DPD statistics, classifying customer payment status, and analyzing delinquency patterns.

## Features

- **DPD Bucket Descriptions**: Add human-readable descriptions to DPD buckets
- **Customer Payment Status Classification**: Classify customers as New, Recurrent, or Recovered based on payment history
- **Comprehensive DPD Statistics**: Calculate detailed per-customer DPD metrics including weighted averages

## Installation

```bash
pip install -r requirements.txt
```

## Requirements

- Python >= 3.7
- pandas >= 1.3.0
- numpy >= 1.20.0

## Usage

### 1. Adding DPD Bucket Descriptions

```python
from commercial_view import add_dpd_bucket_descriptions
import pandas as pd

dpd_df = pd.DataFrame({
    'loan_id': [1, 2, 3],
    'dpd_bucket': ['Current', '30-59', '180+']
})

result = add_dpd_bucket_descriptions(dpd_df)
# Adds 'dpd_bucket_description' column with descriptions like
# 'No payment due', 'Delinquent 30 days', 'Default 180+ days'
```

### 2. Classifying Customer Payment Status

```python
from commercial_view import DPDAnalyzer

analyzer = DPDAnalyzer()

result = analyzer.classify_customer_payment_status(
    loan_df=loan_df,           # DataFrame with customer_id and loan_id
    customer_df=customer_df,   # DataFrame with customer information
    dpd_df=dpd_df,            # DataFrame with DPD metrics
    customer_id_field='customer_id',
    threshold_days=90
)
# Returns customer data enriched with payment_status, max_dpd, loan_count, etc.
```

### 3. Calculating Per-Customer DPD Statistics

```python
from commercial_view import DPDAnalyzer

analyzer = DPDAnalyzer()

stats = analyzer.calculate_per_customer_dpd_stats(
    loan_df=loan_df,
    dpd_df=dpd_df,
    customer_id_field='customer_id'
)
# Returns comprehensive DPD statistics including mean, median, max, 
# default counts, and weighted DPD by past-due amount
```

## Examples

See `examples.py` for complete working examples of all functionality.

Run examples:
```bash
python examples.py
```

## Testing

Run the test suite:
```bash
python test_dpd_analysis.py
```

## Module Structure

```
commercial_view/
├── __init__.py         # Package initialization
└── dpd_analysis.py     # Core DPD analysis functions and classes
```

## API Documentation

### Functions

#### `add_dpd_bucket_descriptions(dpd_df: pd.DataFrame) -> pd.DataFrame`

Adds descriptive text for DPD buckets.

**Parameters:**
- `dpd_df`: DataFrame containing a 'dpd_bucket' column

**Returns:**
- DataFrame with added 'dpd_bucket_description' column

**Raises:**
- `ValueError`: If 'dpd_bucket' column is not present

### Classes

#### `DPDAnalyzer`

Main analyzer class for DPD data and customer payment status.

##### Methods

**`classify_customer_payment_status(...)`**

Classifies customer payment status based on loan and DPD data.

**Parameters:**
- `loan_df`: DataFrame with loan information
- `customer_df`: DataFrame with customer information
- `dpd_df`: DataFrame with DPD metrics per loan
- `customer_id_field`: Name of the customer ID column (default: "customer_id")
- `threshold_days`: Days threshold for recovery classification (default: 90)

**Returns:**
- DataFrame with customer data enriched with payment status and DPD metrics

**`calculate_per_customer_dpd_stats(...)`**

Calculates comprehensive DPD statistics per customer.

**Parameters:**
- `loan_df`: DataFrame with loan information
- `dpd_df`: DataFrame with DPD metrics per loan
- `customer_id_field`: Name of the customer ID column (default: "customer_id")

**Returns:**
- DataFrame with DPD statistics aggregated per customer

## License

MIT License

