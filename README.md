# Commercial-View

Portfolio optimization package for commercial lending with Principal KPI analysis.

## Overview

This package provides a `PortfolioOptimizer` class that helps optimize loan portfolio selection based on scoring criteria while respecting hard limit constraints on APR, customer concentration, and industry concentration.

## Installation

```bash
pip install -e .
```

## Usage

```python
from commercial_view import PortfolioOptimizer
import pandas as pd

# Define rules and weights
rules = {
    "hard_limits": {
        "apr": {
            "0-5": {"max_pct": 0.3},
            "5-7": {"max_pct": 0.4},
            "7-10": {"max_pct": 0.5},
            "10+": {"max_pct": 0.2}
        },
        "payer": {
            "any_anchor": {"max_pct": 0.04}
        },
        "industry": {
            "any_sector": {"max_pct": 0.35}
        }
    }
}

weights = {
    "apr": 0.6,
    "term_fit": 0.35,
    "origination_count": 0.05
}

# Create optimizer
optimizer = PortfolioOptimizer(rules=rules, weights=weights)

# Optimize portfolio
candidates = pd.DataFrame({...})  # Your candidate loans
selected = optimizer.optimize(candidates, aum_total=1000000, target_term=48)
```

## Key Fix

The `optimize()` method previously created a `selected` DataFrame with portfolio results but failed to return it. This has been fixed - the method now properly returns the selected loans DataFrame with:
- `selected` column (boolean flag)
- `selected_amount_cum` column (cumulative amount)

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

Run the demonstration:

```bash
python demonstrate_fix.py
```
