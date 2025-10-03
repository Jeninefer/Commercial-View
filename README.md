# Commercial-View
Principal KPI Calculator

## Overview
This package provides a comprehensive KPI calculator for analyzing commercial and fintech metrics. It supports calculation of startup metrics (MRR, ARR, CAC, LTV, etc.), fintech metrics (GMV, default rates, etc.), valuation metrics, and a viability index.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from abaco_core import KPICalculator
import pandas as pd

# Initialize the calculator
calc = KPICalculator()

# Prepare your data
data_dict = {
    "revenue": pd.DataFrame({
        "date": ["2023-01-01", "2023-02-01"],
        "recurring_revenue": [10000, 12000]
    }),
    "customer": pd.DataFrame({
        "churn_count": [5],
        "start_count": [100]
    })
}

# Compute KPIs
result = calc.compute_kpis(data_dict)

# Export results
json_path = calc.export_metrics_to_json(result)
csv_paths = calc.export_metrics_to_csv(result)

# Get summary
summary = calc.summarize_kpis(result)
print(summary)
```

## Features

- **Startup Metrics**: MRR, ARR, Churn Rate, NRR, CAC, LTV, LTV/CAC ratio, Runway
- **Fintech Metrics**: GMV, Default Rate, Take Rate, Active Users, Average EIR
- **Valuation Metrics**: Pre/Post-money valuation, Enterprise Value, EV multiples, Dilution
- **Viability Index**: Composite score based on key health indicators

## Testing

```bash
pytest tests/
```
