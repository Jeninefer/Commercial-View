# Commercial-View
Principal KPI - Pricing Enrichment Toolkit

## Overview

Commercial-View is a Python toolkit for enriching loan data with pricing information. It provides automated discovery, loading, and matching of pricing data from various file formats to enhance loan portfolios with recommended rates and pricing metrics.

## Features

- **Multi-format Support**: Load pricing data from CSV, Parquet, JSON, and YAML files
- **Automatic Discovery**: Intelligently discover and classify pricing files based on naming conventions
- **Flexible Matching**: Support for both exact joins and band-based matching
- **APR-EIR Analysis**: Automatic calculation of APR-EIR spreads with outlier detection
- **Logging**: Comprehensive logging for monitoring and debugging

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from src.pricing_enricher import PricingEnricher
import pandas as pd

# Create loan data
loans = pd.DataFrame({
    "loan_id": [1, 2, 3],
    "country": ["US", "UK", "US"],
    "sector": ["tech", "finance", "retail"],
    "risk_band": ["A", "B", "A"]
})

# Initialize enricher
enricher = PricingEnricher()

# Enrich loan data
enriched = enricher.enrich_loan_data(
    loans,
    join_keys=["country", "sector", "risk_band"],
    recommended_rate_col="recommended_rate"
)

print(enriched)
```

## Key Components

### PricingEnricher Class

The main class that handles pricing data discovery, loading, and enrichment.

#### Methods

**`find_pricing_files() -> Dict[str, str]`**
- Discovers pricing files in configured paths
- Classifies files as either `pricing_grid` or `recommended_pricing`
- Returns dictionary mapping file types to paths

**`load_pricing_data(pricing_files: Optional[Dict[str, str]] = None) -> bool`**
- Loads pricing data from discovered or provided file paths
- Supports CSV, Parquet, JSON, and YAML formats
- Returns True if at least one dataset was loaded successfully

**`detect_join_keys(df: pd.DataFrame, pricing_df: pd.DataFrame) -> Tuple[list, list]`**
- Automatically detects matching columns between loan and pricing data
- Supports case-insensitive matching and common column aliases
- Returns tuple of (loan_keys, pricing_keys)

**`enrich_loan_data(loan_df: pd.DataFrame, ...) -> pd.DataFrame`**
- Enriches loan data with pricing information
- Supports exact joins and band-based matching
- Calculates APR-EIR spreads and adds pricing coverage flags

### File Classification

The system classifies pricing files based on filename patterns:

- **recommended_pricing**: Files containing "recommend" or "matrix" in the name
- **pricing_grid**: Files containing "grid" or "price" in the name

Supported extensions: `.csv`, `.parquet`, `.pq`, `.json`, `.yml`, `.yaml`

## Usage Examples

### Basic Enrichment with Exact Joins

```python
enricher = PricingEnricher()

enriched_loans = enricher.enrich_loan_data(
    loans,
    join_keys=["country", "sector", "risk_band"]
)
```

### Band-Based Matching

For range-based matching (e.g., tenor or ticket size ranges):

```python
enriched_loans = enricher.enrich_loan_data(
    loans,
    join_keys=["country", "sector"],
    band_keys={
        "tenor_days": ("tenor_min", "tenor_max"),
        "ticket_usd": ("ticket_min", "ticket_max")
    }
)
```

### APR-EIR Spread Analysis

```python
enriched_loans = enricher.enrich_loan_data(
    loans,
    apr_col_hint="annual_percentage_rate",
    eir_col_hint="effective_interest_rate"
)

# Check for extreme spreads
extreme = enriched_loans["apr_eir_spread"].abs() > 0.5
print(f"Loans with extreme spreads: {extreme.sum()}")
```

### Custom Pricing Paths

```python
enricher = PricingEnricher(
    pricing_paths=["./custom/path/pricing", "./data/rates"]
)
```

## Enrichment Process

The enrichment follows a multi-stage process:

1. **Recommended Pricing**: First applies exact joins with `recommended_pricing` data
2. **Pricing Grid**: For rows without recommended rates, applies exact joins with `pricing_grid`
3. **Band Matching**: If band_keys are provided, applies range-based matching
4. **APR-EIR Spread**: Calculates spread between APR and EIR columns if present
5. **Coverage Flag**: Adds `has_pricing` boolean flag indicating enrichment success

## Testing

Run the test suite:

```bash
python -m pytest tests/test_pricing_enricher.py -v
```

Or using unittest:

```bash
python -m unittest tests/test_pricing_enricher.py
```

## Example Script

Run the included example:

```bash
python example.py
```

## Data Directory Structure

```
./
├── data/
│   └── pricing/
│       ├── pricing_grid.csv
│       └── recommended_pricing.csv
├── src/
│   ├── __init__.py
│   └── pricing_enricher.py
├── tests/
│   └── test_pricing_enricher.py
└── example.py
```

## Pricing File Formats

### CSV/Parquet Example
```csv
country,sector,risk_band,recommended_rate
US,tech,A,0.045
UK,finance,B,0.055
```

### JSON Example
```json
[
  {"country": "US", "sector": "tech", "recommended_rate": 0.045},
  {"country": "UK", "sector": "finance", "recommended_rate": 0.055}
]
```

### YAML Example
```yaml
pricing_grid:
  - country: US
    sector: tech
    recommended_rate: 0.045
  - country: UK
    sector: finance
    recommended_rate: 0.055
```

## Logging

Configure logging to see detailed operation information:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Requirements

- Python >= 3.8
- pandas >= 1.5.0
- numpy >= 1.23.0
- pyarrow >= 10.0.0
- PyYAML >= 6.0

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
