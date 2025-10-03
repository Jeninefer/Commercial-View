# Commercial-View

## Pricing Enrichment Module

This repository contains a pricing enrichment module for loan data analysis. The module enables enrichment of loan datasets with pricing information and calculation of APR-EIR spreads.

### Features

- **APR-EIR Spread Calculation**: Automatically calculates the spread between APR and EIR rates
- **Exact Match Join**: Merge loan data with pricing data using exact-match join keys
- **Interval Band Matching**: Match loan features to pricing bands/intervals
- **Flexible Column Detection**: Auto-detect rate columns or use explicit hints
- **Global Instance Pattern**: Safe singleton pattern for consistent pricing data access
- **Auto-loading**: Automatically find and load pricing files from common locations

### Installation

```bash
pip install -r requirements.txt
```

### Quick Start

```python
import pandas as pd
from src.pricing_enrichment import enrich_pricing

# Create sample loan data
loan_df = pd.DataFrame({
    'loan_id': [1, 2, 3],
    'APR': [0.05, 0.06, 0.07],
    'EIR': [0.04, 0.05, 0.06],
    'amount': [10000, 20000, 30000]
})

# Enrich with pricing data and calculate spread
enriched_df = enrich_pricing(loan_df, autoload=False)
print(enriched_df)
```

### Usage Examples

#### Basic APR-EIR Spread Calculation

```python
from src.pricing_enrichment import enrich_pricing

enriched_df = enrich_pricing(loan_df, autoload=False)
# Adds 'apr_eir_spread' column
```

#### With Explicit Column Hints

```python
enriched_df = enrich_pricing(
    loan_df,
    apr_col_hint='annual_percentage_rate',
    eir_col_hint='effective_interest_rate',
    autoload=False
)
```

#### With Join Keys (Exact Matching)

```python
from src.pricing_enrichment import pricing_enricher

# Load recommended pricing data
pricing_enricher.recommended_pricing = pricing_data

enriched_df = enrich_pricing(
    loan_df,
    join_keys=['product', 'region'],
    autoload=False
)
```

#### With Band Keys (Interval Matching)

```python
from src.pricing_enrichment import pricing_enricher

# Load pricing grid with bands
pricing_enricher.pricing_grid = pricing_grid_data

enriched_df = enrich_pricing(
    loan_df,
    band_keys={'tenor_days': ('tenor_min', 'tenor_max')},
    autoload=False
)
```

#### Combined Usage

```python
enriched_df = enrich_pricing(
    loan_df,
    join_keys=['product'],
    band_keys={'tenor_days': ('tenor_min', 'tenor_max')},
    apr_col_hint='APR',
    eir_col_hint='EIR',
    autoload=True
)
```

### API Reference

#### `enrich_pricing(loan_df, **kwargs)`

Main function to enrich loan data with pricing information.

**Parameters:**
- `loan_df` (pd.DataFrame): Input loan DataFrame (required, non-empty)
- `join_keys` (List[str], optional): Columns for exact matching between datasets
- `band_keys` (Dict[str, Tuple[str, str]], optional): Interval mapping, e.g., `{"tenor_days": ("tenor_min", "tenor_max")}`
- `apr_col_hint` (str, optional): Explicit APR column name
- `eir_col_hint` (str, optional): Explicit EIR column name
- `recommended_rate_col` (str, default="recommended_rate"): Name for recommended rate column
- `autoload` (bool, default=True): Auto-find/load pricing files if not already loaded

**Returns:**
- `pd.DataFrame`: Enriched DataFrame with pricing information and spread calculations

**Raises:**
- `ValueError`: If loan_df is None or empty

#### `PricingEnricher` Class

Core class for managing pricing data and enrichment operations.

**Methods:**
- `__init__(pricing_paths: Optional[List[str]] = None)`: Initialize with optional pricing file paths
- `load_pricing_data()`: Load pricing data from configured paths
- `enrich_loan_data(loan_df, **kwargs)`: Enrich loan data with pricing information

### Testing

Run the test suite:

```bash
python -m unittest discover -s tests -v
```

Run examples:

```bash
python examples/usage_examples.py
```

### Project Structure

```
Commercial-View/
├── src/
│   ├── __init__.py
│   └── pricing_enrichment.py    # Main module
├── tests/
│   ├── __init__.py
│   └── test_pricing_enrichment.py
├── examples/
│   └── usage_examples.py
├── requirements.txt
└── README.md
```

### Dependencies

- pandas >= 1.3.0
- numpy >= 1.20.0

### License

Principal KPI
