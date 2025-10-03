# Commercial-View
Principal KPI Analysis Tools

## Overview

This repository contains tools for analyzing commercial loan payments, calculating payment timelines, and determining Days Past Due (DPD) for loan portfolios.

## Features

- **Payment Timeline Calculation**: Match payments to scheduled dues and track payment status
- **DPD Calculation**: Calculate Days Past Due for each loan
- **Efficient Data Processing**: Avoids redundant standardization for better performance

## Recent Refactoring

The codebase has been refactored to avoid redundant data standardization:

- `calculate_payment_timeline` now checks if data is already standardized before calling `standardize_dataframes`
- `calculate_dpd` standardizes data once and passes standardized data to `calculate_payment_timeline`
- This eliminates double processing and improves performance for large datasets

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from payment_analyzer import PaymentAnalyzer
import pandas as pd
from datetime import datetime

# Create analyzer
analyzer = PaymentAnalyzer()

# Prepare your schedule and payment data
schedule_df = pd.DataFrame({...})
payments_df = pd.DataFrame({...})

# Calculate DPD (standardizes once internally)
dpd_df = analyzer.calculate_dpd(schedule_df, payments_df, reference_date=datetime.now())

# Or calculate payment timeline directly
timeline = analyzer.calculate_payment_timeline(schedule_df, payments_df)
```

See `example_usage.py` for a complete example.

## Testing

```bash
pytest test_payment_analyzer.py -v
```
