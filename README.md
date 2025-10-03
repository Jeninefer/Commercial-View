# Commercial-View
Principal KPI Calculator for Startups

A Python library for calculating key performance indicators (KPIs) for startups, including MRR, ARR, churn rate, CAC, LTV, and more.

## Features

The `MetricsCalculator` class provides comprehensive startup metrics calculation:

- **Revenue Metrics**: MRR (Monthly Recurring Revenue), ARR (Annual Recurring Revenue), NRR (Net Revenue Retention), ARPU (Average Revenue Per User)
- **Customer Metrics**: Churn Rate, CAC (Customer Acquisition Cost), LTV (Lifetime Value), LTV/CAC Ratio
- **Financial Health**: Monthly Burn Rate, Runway (in months)

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

```python
from src.metrics_calculator import MetricsCalculator
import pandas as pd

# Create calculator instance
calculator = MetricsCalculator()

# Prepare your data
revenue_df = pd.DataFrame({
    'date': ['2023-01-01', '2023-02-01', '2023-03-01'],
    'recurring_revenue': [10000, 12000, 15000]
})

customer_df = pd.DataFrame({
    'new_customers': [10, 15, 20],
    'churn_count': [5, 6, 7],
    'start_count': [100, 110, 120]
})

expense_df = pd.DataFrame({
    'date': ['2023-01-01', '2023-02-01', '2023-03-01'],
    'marketing_expense': [5000, 6000, 7000],
    'total_expense': [20000, 22000, 24000],
    'cash_balance': [200000, 178000, 154000]
})

# Calculate metrics
metrics = calculator.compute_startup_metrics(revenue_df, customer_df, expense_df)

print(f"MRR: ${metrics['mrr']:,.2f}")
print(f"ARR: ${metrics['arr']:,.2f}")
print(f"Churn Rate: {metrics['churn_rate']:.2%}")
print(f"CAC: ${metrics['cac']:,.2f}")
```

For more examples, see `example_usage.py`.

## Testing

Run the test suite:

```bash
python -m unittest test_metrics_calculator.py -v
```

## Data Format

### Revenue DataFrame
Expected columns (flexible, only required columns are used):
- `date`: Date of the record
- `recurring_revenue`: Monthly recurring revenue
- `revenue`: Total revenue
- `customer_count`: Number of customers
- `start_revenue`: Revenue at start of period
- `end_revenue`: Revenue at end of period

### Customer DataFrame
Expected columns (flexible):
- `new_customers`: Number of new customers acquired
- `churn_count`: Number of churned customers
- `start_count`: Starting customer count
- `is_churned`: Binary indicator (1 for churned, 0 for active)

### Expense DataFrame (Optional)
Expected columns:
- `date`: Date of the record
- `marketing_expense`: Marketing spend
- `total_expense`: Total expenses
- `cash_balance`: Current cash balance

## License

MIT
