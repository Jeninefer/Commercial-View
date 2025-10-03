# Commercial-View
Principal KPI Analysis

A Python library for enriching commercial loan data with pricing information using exact key joins and interval-based matching.

## Installation

```bash
pip install -e .
```

## Features

- **Exact Key Joins**: Match loans with pricing configurations using exact column matches (from Parquet files)
- **Interval/Band Joins**: Match loans within specified ranges (tenor, ticket size) combined with exact keys (from YAML files)
- **Flexible Configuration**: Support for both Parquet and YAML pricing configuration files
- **Rate Selection**: Filter specific rate columns and recommended rates from pricing grids

## Usage

### Example 1: Exact Keys Only (Parquet)

Use exact key matching when you have discrete pricing configurations:

```python
import pandas as pd
from commercial_view import enrich_with_pricing

# Sample loans data
loans_df = pd.DataFrame({
    'loan_id': [1, 2, 3],
    'country': ['USA', 'USA', 'UK'],
    'sector': ['tech', 'retail', 'tech'],
    'risk_band': ['A', 'A', 'B'],
    'amount': [100000, 50000, 75000]
})

# Enrich with pricing using exact key joins
loans = enrich_with_pricing(
    loans_df,
    "configs/pricing_grid.parquet",
    join_keys=["country", "sector", "risk_band"]
)

# Result includes base_rate and margin columns
print(loans)
```

### Example 2: Interval + Exact Keys (YAML)

Use interval matching for range-based pricing (e.g., tenor days, ticket size):

```python
import pandas as pd
from commercial_view import enrich_with_pricing

# Sample loans data with interval columns
loans_df = pd.DataFrame({
    'loan_id': [1, 2, 3],
    'country': ['USA', 'USA', 'UK'],
    'risk_band': ['A', 'B', 'A'],
    'tenor_days': [90, 180, 60],
    'ticket_usd': [50000, 100000, 75000]
})

# Enrich with pricing using interval + exact key joins
loans = enrich_with_pricing(
    loans_df,
    "configs/pricing_grid.yaml",
    join_keys=["country", "risk_band"],
    band_keys={
        "tenor_days": ["tenor_min", "tenor_max"],
        "ticket_usd": ["ticket_min", "ticket_max"]
    },
    rate_cols=("apr", "eir"),
    recommended_col="recommended_rate"
)

# Result includes apr, eir, and recommended_rate columns
print(loans)
```

## Configuration File Formats

### Parquet Format (Exact Keys)

Create a Parquet file with pricing configurations:

```python
import pandas as pd

pricing_data = pd.DataFrame({
    'country': ['USA', 'USA', 'UK'],
    'sector': ['tech', 'retail', 'tech'],
    'risk_band': ['A', 'A', 'B'],
    'base_rate': [0.05, 0.055, 0.08],
    'margin': [0.02, 0.025, 0.04]
})

pricing_data.to_parquet('configs/pricing_grid.parquet')
```

### YAML Format (Intervals + Exact Keys)

Create a YAML file with interval-based pricing:

```yaml
- country: USA
  risk_band: A
  tenor_min: 30
  tenor_max: 180
  ticket_min: 10000
  ticket_max: 100000
  apr: 0.05
  eir: 0.051
  recommended_rate: 0.052

- country: USA
  risk_band: B
  tenor_min: 181
  tenor_max: 365
  ticket_min: 50000
  ticket_max: 250000
  apr: 0.08
  eir: 0.083
  recommended_rate: 0.085
```

## API Reference

### `enrich_with_pricing()`

```python
enrich_with_pricing(
    df: pd.DataFrame,
    pricing_config_path: str,
    join_keys: List[str],
    band_keys: Optional[Dict[str, List[str]]] = None,
    rate_cols: Optional[Tuple[str, ...]] = None,
    recommended_col: Optional[str] = None
) -> pd.DataFrame
```

**Parameters:**

- `df` (pd.DataFrame): The loans DataFrame to enrich
- `pricing_config_path` (str): Path to the pricing configuration file (.parquet or .yaml)
- `join_keys` (List[str]): Exact key columns to join on
- `band_keys` (Optional[Dict[str, List[str]]]): Dictionary mapping DataFrame columns to [min_col, max_col] in pricing config
- `rate_cols` (Optional[Tuple[str, ...]]): Rate column names to include from pricing config
- `recommended_col` (Optional[str]): Name of the recommended rate column

**Returns:**

- pd.DataFrame: Enriched DataFrame with pricing information

## Development

### Running Tests

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

### Project Structure

```
Commercial-View/
├── commercial_view/         # Main package
│   ├── __init__.py
│   └── pricing.py          # Pricing enrichment logic
├── configs/                # Sample configuration files
│   ├── pricing_grid.parquet
│   └── pricing_grid.yaml
├── tests/                  # Test suite
│   └── test_pricing.py
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
├── setup.py               # Package setup
└── README.md              # This file
```

## License

MIT License

