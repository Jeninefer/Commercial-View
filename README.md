# Commercial-View - abaco_core

A Python library for financial calculations and KPI analysis, specifically designed for loan portfolio management and viability assessment.

## Overview

The `abaco_core` library provides robust tools for:
- **Loan Pricing Enrichment**: Match loans against pricing bands with interval matching logic
- **Payment Processing**: Handle payment calculations and identify defaults based on configurable Days Past Due (DPD) thresholds
- **KPI Calculations**: Compute financial viability indices and portfolio performance metrics

## Installation

```bash
pip install -r requirements.txt
```

Or install directly:

```bash
pip install pandas>=1.3.0
```

## Usage

### PricingEnricher

The `PricingEnricher` class enriches loan data with pricing band information using interval matching.

**Key Feature**: Robust handling of non-matching loans. If a loan doesn't match any pricing band, the pricing grid columns will contain NaN values instead of causing errors.

```python
from abaco_core import PricingEnricher
import pandas as pd

# Create pricing bands
pricing_bands = pd.DataFrame({
    'term': [12, 24, 36],
    'min_score': [600, 650, 700],
    'max_score': [649, 699, 850],
    'rate': [0.08, 0.07, 0.06]
})

# Create loan data
loans = pd.DataFrame({
    'loan_id': [1, 2, 3],
    'term': [12, 24, 48],  # Note: loan 3 won't match (no 48-month band)
    'score': [620, 670, 720]
})

# Enrich loans with pricing data
enricher = PricingEnricher(pricing_bands)
enriched_loans = enricher.enrich_loan_data(loans, band_keys=['term'])

# Result: loan 3 will have NaN values in *_grid columns
```

**Implementation Detail**: The `enrich_loan_data` method handles None entries in the matching process by replacing them with empty dictionaries, producing NaN values for unmatched loans. This prevents errors when creating the matched DataFrame.

### PaymentProcessor

The `PaymentProcessor` class handles payment calculations and default identification with configurable thresholds.

**Key Feature**: Configurable default threshold to match your organization's credit policies.

```python
from abaco_core import PaymentProcessor
import pandas as pd

# Initialize with custom threshold (default is 180 days)
processor = PaymentProcessor(default_threshold=180)

# Check individual loan default status
is_defaulted = processor.is_default(days_past_due=185)  # Returns True
is_current = processor.is_default(days_past_due=175)    # Returns False

# Use custom threshold for specific check
is_technical_default = processor.is_default(days_past_due=95, threshold=90)  # Returns True

# Process a portfolio
payments = pd.DataFrame({
    'loan_id': [1, 2, 3, 4],
    'days_past_due': [0, 45, 95, 190]
})

processed = processor.process_payments(payments)
# Adds 'is_default' column based on threshold

# Calculate portfolio default rate
default_rate = processor.calculate_default_rate(payments)
```

**Default Threshold Guidelines**:
- **90 days**: Technical default per Basel II/III standards, commonly used for regulatory reporting
- **180 days**: Common write-off threshold in US markets (default setting)
- **360 days**: Full write-off
- Configure based on your organization's credit policies and regulatory requirements

**What "default" means**:
- 90+ day DPD: Technical default per Basel standards
- 180+ day DPD: Write-off threshold (default in this library)
- Your organization may have different policies; adjust the threshold accordingly

### KPICalculator

The `KPICalculator` class computes financial viability indices and portfolio KPIs.

**Key Feature**: Currently uses startup metrics for viability calculation. Returns 0.0 (not applicable) when startup metrics are not provided.

```python
from abaco_core import KPICalculator
import pandas as pd

calculator = KPICalculator()

# Compute viability with startup metrics
startup_metrics = {
    'burn_rate': 50000,        # Monthly cash burn
    'runway_months': 18,        # Months of operation remaining
    'revenue_growth': 0.15,     # 15% growth rate
    'revenue': 80000            # Monthly revenue
}

viability = calculator.compute_viability_index(startup_metrics=startup_metrics)
# Returns score between 0.0 and 1.0 based on metric thresholds

# Calculate portfolio KPIs
loans = pd.DataFrame({
    'loan_id': [1, 2, 3],
    'principal': [10000, 20000, 15000],
    'interest_rate': [0.08, 0.07, 0.09],
    'days_past_due': [0, 30, 5]
})

kpis = calculator.calculate_portfolio_kpis(loans)
# Returns dict with total_loans, total_principal, average_loan_size, etc.
```

**Important Note on Viability Index**:

The `compute_viability_index` method currently requires `startup_metrics` to compute viability. If startup metrics are not provided (None or empty), the method returns 0.0.

**For pure fintech operations with only loan data** (no startup metrics available):
- The viability_index will return 0.0, which should be interpreted as "viability not applicable" rather than "not viable"
- Ensure your application logic documents this behavior
- Consider alternative approaches if needed:
  1. Explicitly state in documentation that viability requires startup metrics
  2. Extend the method to compute viability from loan_metrics alone
  3. Use `calculate_portfolio_kpis()` for loan-only analysis

**Custom Thresholds**:

```python
custom_thresholds = {
    'min_runway_months': 18,      # Require 18 months runway
    'max_burn_rate': 75000,       # Max $75k monthly burn
    'min_revenue_growth': 0.20,   # Require 20% growth
    'min_revenue': 100000         # Min $100k revenue
}

viability = calculator.compute_viability_index(
    startup_metrics=startup_metrics,
    thresholds=custom_thresholds
)
```

## Configuration and Defaults

### PaymentProcessor Default Threshold

The default threshold for identifying defaults is **180 days** DPD (Days Past Due). This aligns with common write-off policies in US financial markets.

To configure for different DPD policies:

```python
# Regulatory/technical default (Basel standards)
processor_90 = PaymentProcessor(default_threshold=90)

# Write-off threshold (US common practice)
processor_180 = PaymentProcessor(default_threshold=180)

# Custom policy
processor_custom = PaymentProcessor(default_threshold=120)
```

### KPICalculator Viability Thresholds

Default thresholds for viability calculation:
- `min_runway_months`: 12 months
- `max_burn_rate`: $100,000 per month
- `min_revenue_growth`: 10% (0.1)
- `min_revenue`: $50,000 per month

Override with custom thresholds as shown in the usage examples above.

## Architecture

The library consists of three main modules:

1. **pricing_enricher.py**: Handles loan-to-pricing-band matching with robust error handling
2. **payment_processor.py**: Manages payment processing and default detection
3. **kpi_calculator.py**: Computes viability indices and portfolio KPIs

Each module is designed to be:
- **Robust**: Handles edge cases like missing data, non-matching records, and None values
- **Configurable**: Allows customization of thresholds and policies
- **Well-documented**: Includes comprehensive docstrings and usage examples

## Error Handling and Edge Cases

### PricingEnricher
- **Non-matching loans**: Produces NaN values in grid columns instead of errors
- **Empty pricing bands**: Returns loans unchanged with empty grid columns
- **None values**: Automatically filtered and replaced with empty dicts

### PaymentProcessor
- **Missing DPD data**: Handle with pandas NaN checking before calling is_default
- **Negative DPD**: Treated as 0 (current)
- **Empty portfolios**: Returns 0.0 default rate

### KPICalculator
- **Missing startup metrics**: Returns 0.0 (not applicable)
- **Partial metrics**: Calculates viability based on available metrics only
- **Empty portfolios**: Returns appropriate defaults (0 loans, 0 principal, etc.)

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Code Style

The library follows PEP 8 style guidelines with comprehensive docstrings in Google style.

## Contributing

Contributions are welcome! Please ensure:
1. All new code includes docstrings
2. Edge cases are handled appropriately
3. Tests are added for new functionality
4. Documentation is updated

## License

MIT License

## Contact

For questions or issues, contact: jeninefer@abacocapital.co
