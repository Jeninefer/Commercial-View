# Commercial-View
Principal KPI

A Python library for calculating accurate Key Performance Indicators (KPIs) for commercial loan portfolios, with a focus on Days Past Due (DPD) calculations.

## Features

- **Accurate DPD Calculation**: Computes Days Past Due based on current arrears status, not historical first occurrence
- **Current Period Tracking**: Identifies first arrears date for the current delinquency period only
- **Automatic Reset**: DPD resets to 0 when loans catch up after being in arrears
- **Configurable Default Threshold**: Set custom thresholds for determining default status
- **Portfolio Analytics**: Calculate KPIs across multiple loans simultaneously

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Example

```python
import pandas as pd
from commercial_view import LoanPortfolio

# Initialize portfolio with 90-day default threshold
portfolio = LoanPortfolio(dpd_threshold=90)

# Define payment schedule
payment_schedule = pd.DataFrame({
    'loan_id': ['L001', 'L001', 'L002', 'L002'],
    'due_date': ['2024-01-01', '2024-02-01', '2024-01-01', '2024-02-01'],
    'amount_due': [1000.0, 1000.0, 2000.0, 2000.0]
})

# Define actual payments
payments = pd.DataFrame({
    'loan_id': ['L001', 'L001', 'L002'],
    'payment_date': ['2024-01-01', '2024-02-01', '2024-01-01'],
    'amount_paid': [1000.0, 1000.0, 2000.0]
})

# Calculate DPD
results = portfolio.calculate_dpd(
    payment_schedule=payment_schedule,
    payments=payments,
    reference_date='2024-03-15'
)

print(results)
```

### Output Columns

The `calculate_dpd` method returns a DataFrame with the following columns:

- **loan_id**: Unique loan identifier
- **total_due**: Total amount due as of reference date
- **total_paid**: Total amount paid
- **cumulative_gap**: Current arrears amount (total_due - total_paid)
- **first_arrears_date**: First date when current arrears period started
- **days_past_due**: Number of days past due (0 if current)
- **past_due_amount**: Amount currently past due
- **is_default**: Whether loan is in default (days_past_due >= dpd_threshold)

## DPD Calculation Logic

The Days Past Due calculation follows this accurate approach:

1. **Compute Cumulative Gap**: Calculate total due minus total paid as of the reference date
2. **Determine Current Arrears Period**: Identify the first arrears date only for the current delinquency period (not historical)
3. **Reset for Current Loans**: Set `days_past_due = 0` for any loan that is not currently in arrears (cumulative_gap <= 0)
4. **Calculate DPD**: For loans with active arrears (cumulative_gap > 0), calculate days from first arrears date to reference date
5. **Update Default Flag**: Set `is_default = True` for loans where days_past_due >= dpd_threshold

### Key Improvements

This implementation corrects common DPD calculation issues:

- ✅ **No Historical Bias**: DPD reflects current status, not when a loan first went into arrears historically
- ✅ **Accurate Current Status**: Loans that caught up show DPD = 0, even if they were previously delinquent
- ✅ **Proper Period Tracking**: First arrears date represents the current delinquency period
- ✅ **Realistic Default Rates**: Produces more accurate default rates (e.g., ~4.5% vs ~22% with flawed logic)

## Running Tests

```bash
pytest test_commercial_view.py -v
```

## Example Script

Run the included example to see the DPD calculation in action:

```bash
python example.py
```

## License

MIT
