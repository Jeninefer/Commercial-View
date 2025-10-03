# Commercial-View

Commercial payment processing and KPI calculation library for analyzing loan portfolios, calculating Days Past Due (DPD), and generating payment timelines.

## Features

- **Flexible Column Detection**: Automatically detects loan ID, payment dates, and amounts from various column naming conventions
- **Payment Timeline Calculation**: Tracks cumulative due amounts, payments, and gaps over time
- **DPD (Days Past Due) Analysis**: Calculates days past due for each loan with customizable default thresholds
- **DPD Bucket Assignment**: Categorizes loans into delinquency buckets (Current, 1-29, 30-59, 60-89, 90-119, 120-149, 150-179, 180+)
- **Multi-language Support**: Supports English and Spanish column names
- **Date Flexibility**: Works with various date formats and allows custom reference dates

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Example

```python
from abaco_core import PaymentProcessor
import pandas as pd
from datetime import date

# Create payment processor with default 180-day threshold
processor = PaymentProcessor()

# Prepare schedule data
schedule = pd.DataFrame({
    "loan_id": ["L001", "L001", "L002"],
    "due_date": ["2024-01-01", "2024-02-01", "2024-01-15"],
    "due_amount": [100, 100, 200]
})

# Prepare payment data
payments = pd.DataFrame({
    "loan_id": ["L001", "L002"],
    "payment_date": ["2024-01-05", "2024-01-20"],
    "payment_amount": [100, 150]
})

# Calculate payment timeline
timeline = processor.calculate_payment_timeline(
    schedule, payments, reference_date=date(2024, 3, 1)
)

# Calculate DPD
dpd = processor.calculate_dpd(
    schedule, payments, reference_date=date(2024, 3, 1)
)

# Assign DPD buckets
dpd_with_buckets = processor.assign_dpd_buckets(dpd)
```

### Custom DPD Threshold

```python
# Use 90-day threshold for default classification
processor = PaymentProcessor(dpd_threshold=90)
```

### Flexible Column Names

The processor automatically detects columns with various naming conventions:

- **Loan IDs**: `loan_id`, `id_loan`, `loanid`, `idprestamo`, `id_prestamo`, `application_id`
- **Due Dates**: `due_date`, `fecha_vencimiento`, `scheduled_date`, `date_due`, `installment_date`
- **Due Amounts**: `due_amount`, `amount_due`, `scheduled_installment`, `cuota`, `monto_cuota`
- **Payment Dates**: `payment_date`, `fecha_pago`, `date_paid`, `paid_date`
- **Payment Amounts**: `payment_amount`, `amount_paid`, `monto_pago`

## Output Data

### Payment Timeline
- `loan_id`: Loan identifier
- `date`: Transaction date
- `due_amount`: Amount due on this date
- `payment_amount`: Amount paid on this date
- `cumulative_due`: Running total of amounts due
- `cumulative_paid`: Running total of payments made
- `cumulative_gap`: Difference between cumulative due and paid

### DPD Calculation
- `loan_id`: Loan identifier
- `past_due_amount`: Total amount past due
- `days_past_due`: Number of days since first arrears
- `first_arrears_date`: Date of first arrears
- `last_payment_date`: Date of most recent payment
- `last_due_date`: Date of most recent due payment
- `is_default`: Boolean flag based on DPD threshold
- `reference_date`: Date used for calculations

### DPD Buckets
- `dpd_bucket`: Category label (e.g., "Current", "1-29", "30-59", "180+")
- `dpd_bucket_value`: Numeric value for sorting (0, 1, 30, 60, 90, 120, 150, 180)
- `dpd_bucket_description`: Human-readable description
- `default_flag`: Boolean flag for loans in default

## Testing

Run the test suite:

```bash
pytest tests/test_payment_logic.py -v
```

## Requirements

- Python 3.7+
- pandas >= 1.3.0
- numpy >= 1.21.0

## License

See LICENSE file for details.

