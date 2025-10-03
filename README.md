# Commercial-View
Principal KPI Calculator System

A comprehensive KPI calculation system for commercial lending portfolios, combining portfolio analytics with startup, fintech, and valuation metrics.

## Features

- **Portfolio KPIs**: Calculate comprehensive loan portfolio metrics including risk, performance, and portfolio health indicators
- **Startup Metrics**: Track customer acquisition, revenue, and MRR (Monthly Recurring Revenue)
- **Fintech Metrics**: Monitor transaction volumes, success rates, and payment method distributions
- **Valuation Metrics**: Calculate CLTV (Customer Lifetime Value), ARR (Annual Recurring Revenue), and churn rates
- **Production-Safe**: No demo data, no implicit proxies - all calculations require explicit data inputs

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from src import EnhancedKPICalculator
import pandas as pd

# Create calculator
calculator = EnhancedKPICalculator()

# Prepare loan data
loan_df = pd.DataFrame({
    "loan_id": [1, 2, 3],
    "principal": [100000, 200000, 150000],
    "balance": [80000, 180000, 140000],
    "status": ["active", "active", "default"],
})

# Calculate portfolio KPIs
portfolio_kpis = calculator.calculate_portfolio_kpis(loan_df)

# Calculate all metrics (including business metrics if data provided)
all_metrics = calculator.calculate_all_metrics(
    loan_df,
    revenue_df=revenue_df,      # Optional
    customer_df=customer_df,    # Optional
    transaction_df=transaction_df  # Optional
)
```

## Components

### EnhancedKPICalculator
The main calculator class that combines portfolio and business metrics.

**Methods:**
- `calculate_portfolio_kpis(loan_df)`: Calculate portfolio KPIs from loan data
- `calculate_business_metrics(revenue_df, customer_df, transaction_df)`: Calculate startup/fintech/valuation metrics
- `calculate_all_metrics(loan_df, revenue_df, customer_df, transaction_df)`: Calculate all metrics

### ComprehensiveKPICalculator
Specialized calculator for portfolio-level KPIs.

### KPICalculator
Specialized calculator for startup, fintech, and valuation metrics.

### KPIConfig
Configuration class for customizing calculation parameters.

## Usage Examples

See `example.py` for detailed usage examples including:
1. Portfolio KPIs only
2. All metrics with business data
3. Handling missing business data

Run the examples:
```bash
python example.py
```

## Testing

Run the test suite:
```bash
python -m unittest tests.test_kpi_calculators -v
```

## Data Requirements

### Loan DataFrame (Required)
Minimum columns: any columns work, but for full metrics include:
- `principal`: Loan principal amount
- `balance`: Current balance
- `status`: Loan status (active, default, defaulted, charged_off)
- `interest_paid`: Interest paid to date
- `days_past_due`: Days past due

### Revenue DataFrame (Optional)
- `amount`: Revenue amount
- `period`: Revenue period (monthly, one-time, etc.)

### Customer DataFrame (Optional)
- `customer_id`: Customer identifier
- `acquisition_cost`: Customer acquisition cost
- `acquisition_date`: Date customer was acquired
- `status`: Customer status (active, churned, inactive)

### Transaction DataFrame (Optional)
- `transaction_id`: Transaction identifier
- `amount`: Transaction amount
- `status`: Transaction status (success, completed, failed)
- `payment_method`: Payment method used

## License

MIT

