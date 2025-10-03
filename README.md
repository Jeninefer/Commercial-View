# Commercial-View
Principal KPI Analytics

## Overview

Commercial-View is a Python package for calculating principal KPIs and analytics for commercial loan portfolios. It provides tools for analyzing Days Past Due (DPD) statistics and other loan performance metrics.

## Features

- **Customer DPD Statistics**: Calculate median, mean, max, min, and count of Days Past Due by customer
- Safe merging of loan and DPD data
- Flexible field mapping for custom schemas
- Comprehensive logging

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Calculate Customer DPD Statistics

```python
from commercial_view.analytics import CustomerAnalytics
import pandas as pd

# Initialize analytics
analytics = CustomerAnalytics()

# Prepare your data
dpd_df = pd.DataFrame({
    "loan_id": ["L1", "L2", "L3"],
    "days_past_due": [0, 15, 30]
})

loan_df = pd.DataFrame({
    "loan_id": ["L1", "L2", "L3"],
    "customer_id": ["C1", "C1", "C2"]
})

# Calculate statistics
stats = analytics.calculate_customer_dpd_stats(
    dpd_df=dpd_df,
    loan_df=loan_df,
    customer_id_field="customer_id",
    loan_id_field="loan_id"
)

print(stats)
```

Output:
```
  customer_id  dpd_mean  dpd_median  dpd_max  dpd_min  dpd_count
0          C1       7.5         7.5       15        0          2
1          C2      30.0        30.0       30       30          1
```

## Running Tests

```bash
pytest tests/
```

## License

MIT
