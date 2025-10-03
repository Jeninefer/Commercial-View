# abaco-core

Core utilities for commercial view analysis.

## Installation

```bash
pip install -e .
```

## Modules

- **logging_config**: Configure logging for the application
- **payment_logic**: Payment processing functionality
- **feature_engineering**: Feature engineering utilities
- **pricing**: Pricing enrichment tools
- **kpi**: KPI calculation utilities
- **metrics_registry**: Metrics tracking registry
- **types**: Type definitions and utilities

## Usage

```python
from abaco_core import configure_logging, PaymentProcessor, FeatureEngineer

# Configure logging
configure_logging()

# Use the modules
processor = PaymentProcessor()
engineer = FeatureEngineer()
```
