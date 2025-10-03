# Commercial-View
Principal KPI Calculator for Fintech Applications

This repository provides a comprehensive tool for calculating key performance indicators (KPIs) for fintech businesses, particularly focused on lending operations.

## Features

The `FintechMetricsCalculator` class computes the following metrics:

- **GMV (Gross Merchandise Value)**: Total loan amount disbursed
- **Default Rate**: Percentage of loans in default (based on days past due threshold)
- **Take Rate**: Revenue as a percentage of GMV
- **Average EIR**: Mean Effective Interest Rate across loans
- **APR-EIR Spread**: Average difference between APR and EIR
- **Active Users**: Number of active users (from user data or recent payment activity)
- **Active Rate**: Percentage of active users

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

```python
from fintech_metrics import FintechMetricsCalculator
import pandas as pd

# Initialize calculator
calculator = FintechMetricsCalculator()

# Prepare your loan data
loan_df = pd.DataFrame({
    'loan_amount': [1000, 2000, 3000],
    'days_past_due': [0, 90, 200],
    'revenue': [50, 100, 150],
    'apr': [0.12, 0.15, 0.18],
    'eir': [0.10, 0.12, 0.15]
})

# Compute metrics
metrics = calculator.compute_fintech_metrics(loan_df)

print(metrics)
# Output: {'gmv': 6000.0, 'default_rate': 0.333, 'take_rate': 0.05, ...}
```

See `example_usage.py` for a complete working example.

## Testing

Run the test suite:

```bash
python -m unittest test_fintech_metrics -v
```

## API Reference

### `FintechMetricsCalculator.compute_fintech_metrics()`

Computes various fintech metrics from loan, payment, and user dataframes.

**Parameters:**
- `loan_df` (pd.DataFrame): Required. DataFrame containing loan information
- `payment_df` (pd.DataFrame, optional): DataFrame containing payment information
- `user_df` (pd.DataFrame, optional): DataFrame containing user information
- `default_dpd_threshold` (int, optional): Days past due threshold for default classification (default: 180)

**Returns:**
- `Dict[str, float]`: Dictionary containing computed metrics

**Expected Column Names:**

The calculator intelligently detects columns using flexible naming:

- Loan amount: `loan_amount`, `amount`, or `monto_prestamo`
- Days past due: `days_past_due`, `dpd`, or `dias_atraso`
- Revenue: `revenue`
- APR: any column containing "apr" (case-insensitive)
- EIR: any column containing "eir" (case-insensitive)
- User active status: `is_active` (in user_df)
- Payment data: `customer_id` and `date` (in payment_df)

## License

This project is open source and available for educational purposes.
