# abaco-core

Core modules for Payments + DPD, Feature Engineering, Pricing Enrichment, and KPI computation.

## Modules
- `payment_logic.py`: schedule/payments standardization, timeline, DPD, buckets.
- `feature_engineering.py`: exposure segmentation, DPD buckets, client type, HHI, master enrichment.
- `pricing.py`: auto-discovery of pricing files, joins, interval matching, APR–EIR spread.
- `kpi.py`: startup, fintech, valuation metrics, viability index, export.
- `metrics_registry.py`: performance/quality telemetry.

## Python
- 3.10+
- `pip install -e .`

## Logging
```python
from abaco_core import configure_logging
configure_logging()
```

## Usage Examples

### Payment Logic
```python
from abaco_core.payment_logic import PaymentSchedule, DPDCalculator
from datetime import datetime

# Create a payment schedule
schedule = PaymentSchedule('LOAN001', datetime(2024, 1, 1), 1000.0, 'monthly')
schedule.add_payment(datetime(2024, 1, 15), 1000.0)

# Calculate DPD
dpd = DPDCalculator.calculate_dpd(datetime(2024, 1, 1), datetime(2024, 1, 15))
bucket = DPDCalculator.get_dpd_bucket(dpd)
```

### Feature Engineering
```python
from abaco_core.feature_engineering import ExposureSegmentation, HHICalculator

# Segment exposure
segment = ExposureSegmentation.segment_exposure(75000)  # Returns 'medium'

# Calculate HHI
market_shares = [30, 25, 20, 15, 10]
hhi = HHICalculator.calculate_hhi(market_shares)
```

### Pricing
```python
from abaco_core.pricing import APRCalculator, PricingFileDiscovery
from pathlib import Path

# Calculate APR
apr = APRCalculator.calculate_apr(principal=10000, total_interest=1500, term_months=12)

# Discover pricing files
files = PricingFileDiscovery.discover_pricing_files(Path('./pricing_data'))
```

### KPI Calculation
```python
from abaco_core.kpi import StartupMetrics, FintechMetrics, ViabilityIndex

# Calculate startup metrics
burn_rate = StartupMetrics.calculate_burn_rate(expenses=50000, period_months=1)
runway = StartupMetrics.calculate_runway(cash_balance=500000, monthly_burn_rate=burn_rate)

# Calculate fintech metrics
npl_ratio = FintechMetrics.calculate_npl_ratio(non_performing_loans=100000, total_loans=1000000)

# Calculate viability index
metrics = {
    'profitability': 75,
    'liquidity': 80,
    'growth': 70,
    'efficiency': 85,
    'risk': 65
}
viability = ViabilityIndex.calculate_viability_index(metrics)
```

### Metrics Registry
```python
from abaco_core.metrics_registry import MetricsRegistry, PerformanceTracker

# Create registry
registry = MetricsRegistry()

# Record metrics
registry.record_counter('loans_processed', 100)
registry.record_gauge('portfolio_value', 5000000.0)
registry.record_timing('calculation_time', 125.5)

# Track performance
tracker = PerformanceTracker(registry)
with tracker.track_execution('my_operation'):
    # Your code here
    pass

# Get all metrics
metrics = registry.get_all_metrics()
```

## Installation

Install the package in development mode:
```bash
pip install -e .
```

Install with development dependencies:
```bash
pip install -e ".[dev]"
```

## Requirements
- Python 3.10 or higher
- pandas >= 1.5.0
- numpy >= 1.23.0
- openpyxl >= 3.0.0
- pyarrow >= 10.0.0
