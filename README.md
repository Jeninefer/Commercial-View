# Commercial-View
Principal KPI Analyzer

## Overview

Commercial-View is a comprehensive KPI (Key Performance Indicator) analysis tool designed for commercial businesses, startups, and fintech companies. It provides detailed metrics calculation across multiple business dimensions including startup metrics, fintech metrics, valuation metrics, and viability indices.

## Features

- **Startup Metrics**: Revenue growth, customer acquisition, ARPU, CAC, LTV/CAC ratios
- **Fintech Metrics**: Loan portfolio analysis, default rates, NPL ratios, collection rates, user engagement
- **Valuation Metrics**: Pre/post-money valuation, enterprise value, revenue/EBITDA multiples, dilution
- **Viability Index**: Automated business health scoring (0-100)
- **JSON Export**: Export all metrics for reporting and integration

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from kpi_analyzer import KPIAnalyzer
import pandas as pd

# Initialize the analyzer
analyzer = KPIAnalyzer()

# Prepare your data
revenue_df = pd.DataFrame({
    "date": ["2023-01", "2023-02", "2023-03"],
    "revenue": [50000, 60000, 75000]
})

customer_df = pd.DataFrame({
    "date": ["2023-01", "2023-02", "2023-03"],
    "customer_id": [1, 2, 3]
})

valuation_df = pd.DataFrame({
    "pre_money_valuation": [5000000],
    "investment_amount": [1000000],
    "market_cap": [7000000],
    "total_debt": [500000],
    "cash": [200000],
    "revenue": [300000],
    "ebitda": [50000]
})

# Compute KPIs
kpis = analyzer.compute_kpis(
    revenue_df=revenue_df,
    customer_df=customer_df,
    valuation_df=valuation_df
)

print(kpis)
```

## Usage

### Running the Example

```bash
python example.py
```

This will compute sample KPIs and display formatted results.

### Running Tests

```bash
pytest test_kpi_analyzer.py -v
```

## API Reference

### KPIAnalyzer Class

#### Methods

##### `compute_kpis()`

Main method to compute all KPIs.

**Parameters:**
- `revenue_df` (pd.DataFrame): DataFrame containing revenue data with columns: `date`, `revenue`
- `customer_df` (pd.DataFrame): DataFrame containing customer data with columns: `date`, `customer_id`
- `valuation_df` (pd.DataFrame): DataFrame containing valuation data
- `loan_df` (Optional[pd.DataFrame]): DataFrame containing loan data (for fintech metrics)
- `payment_df` (Optional[pd.DataFrame]): DataFrame containing payment data
- `user_df` (Optional[pd.DataFrame]): DataFrame containing user data
- `default_dpd_threshold` (int): Days past due threshold for defaults (default: 180)
- `export` (bool): Whether to export results to JSON (default: False)

**Returns:**
Dictionary containing:
- `startup`: Startup metrics
- `fintech`: Fintech metrics (if loan_df provided)
- `valuation`: Valuation metrics
- `viability_index`: Business health score (0-100)

##### `compute_startup_metrics()`

Computes startup-related metrics including revenue, growth, customers, ARPU, CAC, and LTV/CAC ratios.

##### `compute_fintech_metrics()`

Computes fintech-related metrics including loan portfolio analysis, default rates, and payment metrics.

##### `compute_viability_index()`

Calculates a business viability score (0-100) based on startup metrics.

##### `safe_division()`

Utility method for safe division with default values.

## Data Format

### Revenue DataFrame
```python
{
    "date": ["2023-01", "2023-02"],
    "revenue": [10000, 12000]
}
```

### Customer DataFrame
```python
{
    "date": ["2023-01", "2023-02"],
    "customer_id": [1, 2]
}
```

### Valuation DataFrame
```python
{
    "pre_money_valuation": [1000000],
    "investment_amount": [250000],
    "market_cap": [1500000],
    "total_debt": [100000],
    "cash": [50000],
    "revenue": [100000],
    "ebitda": [20000],
    "marketing_expense": [5000]  # Optional
}
```

### Loan DataFrame (Optional)
```python
{
    "loan_id": [1, 2, 3],
    "amount": [10000, 20000, 15000],
    "dpd": [0, 30, 200],  # Days past due
    "status": ["active", "active", "default"]
}
```

## Output Example

```json
{
  "startup": {
    "total_revenue": 275000.0,
    "revenue_growth": 0.2,
    "total_customers": 4,
    "arpu": 68750.0,
    "cac": 5000.0,
    "ltv_cac_ratio": 41.25
  },
  "fintech": {
    "total_loans": 10,
    "total_loan_amount": 182000.0,
    "default_rate": 0.2,
    "npl_ratio": 0.3
  },
  "valuation": {
    "pre_money_valuation": 5000000.0,
    "post_money_valuation": 6000000.0,
    "enterprise_value": 7300000.0,
    "revenue_multiple": 24.33,
    "ebitda_multiple": 146.0
  },
  "viability_index": 60.0
}
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

