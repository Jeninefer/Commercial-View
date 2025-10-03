# Commercial-View
Principal KPI Analysis for Startup Viability

## Overview

This repository provides a Python implementation for analyzing startup viability based on key performance indicators (KPIs). The `StartupAnalyzer` class computes a viability index score (0-100) using weighted metrics.

## Features

- **Viability Index Calculation**: Computes a comprehensive score based on three key metrics:
  - **Runway (40%)**: Months of cash runway remaining
  - **LTV/CAC Ratio (40%)**: Lifetime value to customer acquisition cost ratio
  - **Net Revenue Retention (20%)**: Growth rate of recurring revenue

- **Configurable Thresholds**: Customize minimum thresholds for each metric
- **Flexible Input**: Supports multiple key names and handles missing values gracefully

## Installation

No external dependencies required. Simply use the `startup_analyzer.py` module.

```bash
# Clone the repository
git clone https://github.com/Jeninefer/Commercial-View.git
cd Commercial-View
```

## Usage

```python
from startup_analyzer import StartupAnalyzer

# Create analyzer with default thresholds
analyzer = StartupAnalyzer()

# Calculate viability index
metrics = {
    "runway_months": 12,
    "ltv_cac_ratio": 3.0,
    "nrr": 1.0
}
score = analyzer.compute_viability_index(metrics)
print(f"Viability Index: {score}/100")  # Output: Viability Index: 75/100
```

### Custom Thresholds

```python
# Use custom thresholds
custom_analyzer = StartupAnalyzer(thresholds={
    "runway_months_min": 6,
    "ltv_cac_ratio_min": 2.0,
    "nrr_min": 0.9
})
```

## Scoring System

The viability index is calculated using a weighted scoring system:

### Runway Score (40% weight)
- **100 points**: >= 2x minimum threshold
- **75 points**: >= minimum threshold
- **50 points**: >= 0.5x minimum threshold
- **25 points**: > 0
- **0 points**: 0

### LTV/CAC Score (40% weight)
- **100 points**: >= 2x minimum threshold
- **75 points**: >= minimum threshold
- **50 points**: >= 0.5x minimum threshold
- **25 points**: > 0
- **0 points**: 0

### NRR Score (20% weight)
- **100 points**: >= 1.2x minimum threshold
- **75 points**: >= minimum threshold
- **50 points**: >= 0.8x minimum threshold
- **25 points**: > 0
- **0 points**: 0

## Default Thresholds

- `runway_months_min`: 12 months
- `ltv_cac_ratio_min`: 3.0
- `nrr_min`: 1.0 (representing 100% retention)

## Examples

See `example.py` for comprehensive usage examples.

```bash
python example.py
```

## Testing

Run the test suite using unittest:

```bash
python -m unittest test_startup_analyzer.py -v
```

## License

This project is open source and available for use.
