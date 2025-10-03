# PricingEnricher

A Python class for enriching loan data with pricing information from CSV files.

## Features

- **Automatic File Discovery**: Finds pricing CSV files in configurable directories
- **Smart Column Mapping**: Automatically detects matching columns between loan and pricing data
- **Flexible Join Methods**: Supports both exact joins and interval-based matching
- **APR-EIR Spread Calculation**: Automatically calculates spread when both rates are present
- **Multiple Pricing Sources**: Handles both pricing grids and recommended pricing

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from abaco_core.pricing import PricingEnricher
import pandas as pd

# Initialize with custom paths
enricher = PricingEnricher(pricing_paths=["./exports"])

# Or use default paths
enricher = PricingEnricher()

# Load pricing data
enricher.load_pricing_data()

# Enrich loan data
loan_df = pd.DataFrame({
    "segment": ["A", "B"],
    "term": [12, 24],
    "amount": [10000, 25000]
})

enriched_df = enricher.enrich_loan_data(loan_df)
```

## File Discovery

The `PricingEnricher` looks for CSV files in the configured directories that match these patterns:
- `pricing_grid` - for pricing grid files
- `recommended_pricing` - for recommended pricing files
- `pricing_recommendations` - alternative naming
- `price_matrix` - alternative naming

### Example File Names
- `pricing_grid_2024.csv` ✓
- `recommended_pricing.csv` ✓
- `pricing_recommendations_v2.csv` ✓
- `price_matrix.csv` ✓

## Automatic Column Mapping

The class automatically maps columns between loan and pricing data. It recognizes:

| Loan Column | Pricing Column |
|------------|---------------|
| `client_segment`, `customer_segment`, `segment` | `segment` |
| `risk_score` | `risk_score` |
| `risk_rating` | `risk_rating` |
| `score` | `score` |
| `rating` | `rating` |
| `term`, `tenure`, `plazo` | `term` |
| `loan_amount`, `amount`, `monto` | `amount` |

## Advanced Usage

### Interval-Based Matching

Use band keys for range-based matching:

```python
# Pricing grid with ranges
# amount_min, amount_max, rate
# 0, 9999, 0.08
# 10000, 29999, 0.06
# 30000, 100000, 0.04

band_keys = {"loan_amount": ("amount_min", "amount_max")}
enriched = enricher.enrich_loan_data(
    loan_df,
    band_keys=band_keys
)
```

### Explicit Join Keys

Specify join keys manually:

```python
enriched = enricher.enrich_loan_data(
    loan_df,
    join_keys=["segment", "term"]
)
```

### APR-EIR Spread

If your loan data has APR and EIR columns, the spread is calculated automatically:

```python
loan_df = pd.DataFrame({
    "loan_id": [1, 2],
    "APR": [0.08, 0.10],
    "EIR": [0.07, 0.09]
})

enriched = enricher.enrich_loan_data(loan_df)
# enriched now has an 'apr_eir_spread' column
```

### Custom Column Hints

Specify APR/EIR columns explicitly:

```python
enriched = enricher.enrich_loan_data(
    loan_df,
    apr_col_hint="annual_percentage_rate",
    eir_col_hint="effective_interest_rate"
)
```

## Pricing Data Priority

When both recommended pricing and pricing grid are available:
1. **Recommended pricing** is applied first (exact join)
2. **Pricing grid** fills in missing values (exact or interval join)

Columns from recommended pricing get no suffix, grid columns get `_grid` suffix.

## API Reference

### PricingEnricher

#### `__init__(pricing_paths: Optional[List[str]] = None)`
Initialize the enricher with custom pricing file paths.

#### `find_pricing_files() -> Dict[str, str]`
Discover pricing CSV files in configured directories.

#### `load_pricing_data(pricing_files: Optional[Dict[str, str]] = None) -> bool`
Load pricing data from CSV files.

#### `enrich_loan_data(loan_df, *, join_keys=None, band_keys=None, apr_col_hint=None, eir_col_hint=None, recommended_rate_col="recommended_rate", autoload=True) -> pd.DataFrame`
Enrich loan dataframe with pricing information.

**Parameters:**
- `loan_df`: Input loan dataframe
- `join_keys`: List of column names to join on
- `band_keys`: Dict mapping feature to (low_col, high_col) for interval matching
- `apr_col_hint`: Column name hint for APR
- `eir_col_hint`: Column name hint for EIR
- `recommended_rate_col`: Name of recommended rate column (default: "recommended_rate")
- `autoload`: Automatically load pricing data if not loaded (default: True)

**Returns:** Enriched dataframe with pricing information

## Examples

See `examples/pricing_example.py` for a complete working example.

## Testing

Run the test suite:

```bash
python -m unittest tests.test_pricing -v
```

## License

This is example code for demonstration purposes.
