# Commercial-View
Principal KPI

## PricingEnricher Module

This repository includes a `PricingEnricher` class for enriching loan data with pricing information from CSV files.

### Features
- Automatic pricing file discovery
- Smart column mapping between loan and pricing data
- Support for exact joins and interval-based matching
- APR-EIR spread calculation
- Multiple pricing source support

### Quick Start

```python
from abaco_core.pricing import PricingEnricher
import pandas as pd

# Initialize and load pricing data
enricher = PricingEnricher(pricing_paths=["./exports"])
enricher.load_pricing_data()

# Enrich loan data
loan_df = pd.DataFrame({
    "segment": ["A", "B"],
    "term": [12, 24],
    "amount": [10000, 25000]
})

enriched_df = enricher.enrich_loan_data(loan_df)
```

### Documentation
- [Full Documentation](docs/PRICING_ENRICHER.md)
- [Usage Examples](examples/pricing_example.py)

### Testing

Run the test suite:
```bash
python -m unittest tests.test_pricing -v
```

All 24 tests pass successfully.

