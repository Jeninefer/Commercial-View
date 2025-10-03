# Commercial-View

Principal KPI and Pricing Enrichment Functionality

## Overview

This repository provides production-safe pricing enrichment functionality for commercial loan portfolios. The main module enables enriching loan data with pricing information from various data sources through exact joins and interval/band matching.

## Features

- **Multiple data format support**: CSV, JSON, Parquet, and YAML pricing grids
- **Flexible join strategies**:
  - Exact key-based joins
  - Interval/band matching for range-based pricing (e.g., tenor ranges, ticket sizes)
- **Automatic calculations**:
  - APR-EIR spread computation
  - Pricing availability flags
- **Robust error handling** with clear validation messages
- **Type-safe** with proper type hints

## Installation

```bash
pip install -r requirements.txt
```

### Dependencies

- pandas >= 1.3.0
- numpy >= 1.20.0
- pyyaml >= 5.4.0
- pyarrow >= 5.0.0

## Usage

### Basic Exact Join

```python
from src.pricing_enrichment import enrich_with_pricing
import pandas as pd

# Your loan data
loans_df = pd.DataFrame({
    'loan_id': [1, 2, 3],
    'product': ['A', 'B', 'C']
})

# Enrich with pricing from CSV file
enriched = enrich_with_pricing(
    loans_df,
    'pricing_grid.csv',
    join_keys=['product']
)
```

### Band/Interval Matching

```python
# Loan data with tenor
loans_df = pd.DataFrame({
    'loan_id': [1, 2, 3],
    'tenor_days': [30, 90, 180]
})

# Pricing grid with ranges
# pricing_grid.csv contains: tenor_min, tenor_max, apr, eir, recommended_rate

# Enrich using band matching
enriched = enrich_with_pricing(
    loans_df,
    'pricing_grid.csv',
    band_keys={'tenor_days': ['tenor_min', 'tenor_max']}
)
```

### Combined Exact Join and Band Matching

```python
loans_df = pd.DataFrame({
    'loan_id': [1, 2, 3],
    'product': ['A', 'A', 'B'],
    'tenor_days': [30, 90, 180]
})

enriched = enrich_with_pricing(
    loans_df,
    'pricing_grid.csv',
    join_keys=['product'],
    band_keys={'tenor_days': ['tenor_min', 'tenor_max']}
)
```

## API Reference

### `enrich_with_pricing()`

Main function for enriching loan data with pricing information.

**Parameters:**
- `loans_df` (pd.DataFrame): Input loan data (must be non-empty)
- `pricing_grid_path` (str): Path to pricing grid file
- `join_keys` (Optional[Sequence[str]]): Columns for exact join matching
- `band_keys` (Optional[Mapping[str, Sequence[str]]]): Dictionary mapping feature columns to [min_col, max_col] for range matching
- `rate_cols` (Sequence[str]): Rate columns for spread calculation (default: ("apr", "eir"))
- `recommended_col` (str): Column name for recommended rate (default: "recommended_rate")

**Returns:**
- `pd.DataFrame`: Enriched DataFrame with pricing information

**Raises:**
- `ValueError`: If loans_df is empty or required keys are missing

### Computed Columns

The function automatically adds:
- `apr_eir_spread`: Difference between APR and EIR (if both exist)
- `has_pricing`: Boolean flag indicating if pricing was found

## File Format Support

### CSV
```csv
product,apr,eir,recommended_rate
A,5.0,4.5,5.0
B,6.0,5.5,6.0
```

### JSON
```json
[
  {"product": "A", "apr": 5.0, "eir": 4.5, "recommended_rate": 5.0},
  {"product": "B", "apr": 6.0, "eir": 5.5, "recommended_rate": 6.0}
]
```

### YAML
```yaml
pricing_grid:
  - product: A
    apr: 5.0
    eir: 4.5
    recommended_rate: 5.0
  - product: B
    apr: 6.0
    eir: 5.5
    recommended_rate: 6.0
```

### Parquet
Use pandas to create: `df.to_parquet('pricing_grid.parquet')`

## Examples

See the `examples/` directory for complete working examples:

```bash
python examples/pricing_enrichment_examples.py
```

## Testing

Run the comprehensive test suite:

```bash
pytest tests/test_pricing_enrichment.py -v
```

The test suite includes:
- File format loading tests
- Exact join validation
- Band matching scenarios
- Error handling cases
- Edge cases (empty grids, missing keys, infinite bounds)

## Requirements

- Python 3.7+
- See `requirements.txt` for package dependencies

## Project Structure

```
Commercial-View/
├── src/
│   ├── __init__.py
│   └── pricing_enrichment.py    # Main module
├── tests/
│   ├── __init__.py
│   └── test_pricing_enrichment.py  # Test suite
├── examples/
│   └── pricing_enrichment_examples.py  # Usage examples
├── requirements.txt
└── README.md
```

## License

This project is part of the Commercial-View Principal KPI system.
