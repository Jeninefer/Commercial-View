# Commercial-View

Principal KPI calculator for loan analytics. This package provides tools for analyzing loan payment timelines and calculating Days Past Due (DPD) metrics.

## Features

- **Payment Timeline Calculation**: Track cumulative dues, payments, and gaps over time for each loan
- **DPD Calculation**: Calculate Days Past Due (DPD) for loans with arrears tracking
- **Default Classification**: Automatically classify loans as defaulted based on configurable DPD thresholds
- **Flexible Date Handling**: Support for both datetime and date objects

## Installation

```bash
pip install -r requirements.txt
```

Or install in development mode:

```bash
pip install -e .
```

## Usage

### Basic Example

```python
from commercial_view import LoanAnalyzer
import pandas as pd
from datetime import date

# Initialize the analyzer with a 90-day default threshold
analyzer = LoanAnalyzer(dpd_threshold=90)

# Prepare schedule data
schedule_df = pd.DataFrame({
    'loan_id': ['L001', 'L001', 'L001'],
    'due_date': ['2024-01-01', '2024-02-01', '2024-03-01'],
    'due_amount': [1000, 1000, 1000]
})

# Prepare payment data
payments_df = pd.DataFrame({
    'loan_id': ['L001', 'L001'],
    'payment_date': ['2024-01-05', '2024-02-10'],
    'payment_amount': [1000, 500]
})

# Calculate payment timeline
timeline = analyzer.calculate_payment_timeline(
    schedule_df, 
    payments_df, 
    reference_date=date(2024, 3, 15)
)

print(timeline)
# Output shows cumulative_due, cumulative_paid, and cumulative_gap by loan and date

# Calculate DPD
dpd_result = analyzer.calculate_dpd(
    schedule_df, 
    payments_df, 
    reference_date=date(2024, 3, 15)
)

print(dpd_result)
# Output includes: loan_id, past_due_amount, days_past_due, first_arrears_date,
#                  last_payment_date, last_due_date, is_default, reference_date
```

### Payment Timeline

The `calculate_payment_timeline` method returns a DataFrame with the following columns:
- `loan_id`: Loan identifier
- `date`: Date of transaction or due date
- `due_amount`: Amount due on that date
- `payment_amount`: Amount paid on that date
- `cumulative_due`: Cumulative amount due up to that date
- `cumulative_paid`: Cumulative amount paid up to that date
- `cumulative_gap`: Difference between cumulative due and paid (arrears)

### DPD Calculation

The `calculate_dpd` method returns a DataFrame with the following columns:
- `loan_id`: Loan identifier
- `past_due_amount`: Current amount past due (non-negative)
- `days_past_due`: Number of days the loan has been in arrears
- `first_arrears_date`: First date when the loan went into arrears
- `last_payment_date`: Most recent payment date
- `last_due_date`: Most recent due date
- `is_default`: Boolean indicating if loan is in default (DPD >= threshold)
- `reference_date`: Reference date used for calculations

## Requirements

- Python >= 3.9
- pandas >= 1.3.0
- numpy >= 1.20.0

## Running Tests

```bash
python -m unittest tests.test_loan_analyzer -v
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
