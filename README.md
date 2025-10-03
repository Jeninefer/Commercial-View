# Commercial-View

Principal KPI Analytics for Commercial Loan Portfolios

## Overview

Commercial-View is a comprehensive Python package for analyzing commercial loan portfolios. It provides key performance indicators (KPIs), customer segmentation, delinquency analysis, and revenue metrics for financial institutions managing commercial lending portfolios.

## Features

- **DPD Bucketing**: Categorize loans by days past due with configurable buckets
- **Customer Segmentation**: Segment customers by exposure levels (A-F rating)
- **Customer Type Classification**: Classify customers as New, Recurring, or Recovered
- **Weighted Statistics**: Calculate weighted averages for APR, EIR, and loan terms
- **HHI Calculation**: Measure portfolio concentration with Herfindahl-Hirschman Index
- **Revenue Metrics**: Track expected vs. effective revenue and efficiency
- **Line Utilization**: Monitor credit line usage across customers
- **Customer DPD Statistics**: Aggregate days past due statistics at customer level

## Installation

```bash
pip install -e .
```

Or install dependencies directly:

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from commercial_view import PaymentAnalyzer
import pandas as pd

# Initialize analyzer
analyzer = PaymentAnalyzer(dpd_threshold=90)

# DPD Bucketing
dpd_data = pd.DataFrame({
    "loan_id": [1, 2, 3],
    "days_past_due": [0, 45, 120]
})
result = analyzer.get_dpd_buckets(dpd_data)
print(result)

# Customer Segmentation
loans = pd.DataFrame({
    "loan_id": [1, 2, 3],
    "customer_id": ["A", "B", "C"],
    "outstanding_balance": [10000, 25000, 15000]
})
segmented = analyzer.calculate_customer_segments(loans)
print(segmented)
```

## API Reference

### PaymentAnalyzer Class

#### `__init__(config=None, dpd_threshold=90)`
Initialize the analyzer with optional configuration and DPD threshold.

#### `get_dpd_buckets(dpd_df)`
Categorize loans into DPD buckets and flag defaults.

**Parameters:**
- `dpd_df`: DataFrame with `days_past_due` column

**Returns:**
- DataFrame with `dpd_bucket` and `default_flag` columns added

#### `calculate_customer_segments(loans_df, exposure_col='outstanding_balance')`
Segment customers by exposure into 6 tiers (A-F, A being highest).

**Parameters:**
- `loans_df`: DataFrame with loan data
- `exposure_col`: Column name for exposure amount

**Returns:**
- DataFrame with `segment` column added

#### `determine_customer_type(loans_df, dpd_df)`
Classify customers as New, Recurring, or Recovered based on loan history.

**Parameters:**
- `loans_df`: DataFrame with loan and customer data
- `dpd_df`: DataFrame with DPD data

**Returns:**
- DataFrame with `customer_type` column added

#### `calculate_weighted_stats(loans_df, weight_col='outstanding_balance')`
Calculate weighted statistics for APR, EIR, and term.

**Parameters:**
- `loans_df`: DataFrame with loan data
- `weight_col`: Column to use as weights

**Returns:**
- Dictionary with weighted statistics

#### `calculate_hhi(loans_df, exposure_col='outstanding_balance', group_by=None)`
Calculate Herfindahl-Hirschman Index for portfolio concentration.

**Parameters:**
- `loans_df`: DataFrame with loan data
- `exposure_col`: Column name for exposure
- `group_by`: Column to group by (auto-detected if None)

**Returns:**
- HHI value (0-10000 scale)

### Standalone Functions

#### `calculate_revenue_metrics(loans_df)`
Calculate expected and effective revenue metrics.

#### `calculate_line_utilization(loans_df)`
Calculate credit line utilization ratios.

#### `calculate_customer_dpd_stats(loans_df, dpd_df)`
Calculate customer-level DPD aggregates (mean, median, max, min).

## Examples

See the `examples/usage_example.py` file for comprehensive usage examples covering all major features.

Run the example:

```bash
python examples/usage_example.py
```

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

## Requirements

- Python >= 3.8
- pandas >= 1.3.0
- numpy >= 1.20.0

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

