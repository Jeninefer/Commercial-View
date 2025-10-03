# Commercial-View
Principal KPI tracking and metrics collection system.

## Overview

This repository provides a robust metrics collection and tracking system for commercial operations. The `MetricsRegistry` class allows you to record, track, and export various metrics including performance latencies, data quality scores, and custom business metrics.

## Features

- **Timer Management**: Track operation latencies with start/end timer functions
- **Metric Recording**: Record arbitrary metrics with timestamps and metadata
- **Data Quality Metrics**: Automatically calculate data quality scores from pandas DataFrames
- **Rules Tracking**: Track number of validation rules evaluated
- **Metric Aggregation**: Get latest metrics with count, average, min, max statistics
- **Export/Import**: Export metrics to JSON for persistence or analysis
- **Automatic Cleanup**: Clear old metrics beyond a specified retention period

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Jeninefer/Commercial-View.git
cd Commercial-View
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Example

```python
from src.metrics_registry import MetricsRegistry
import pandas as pd

# Initialize the registry
registry = MetricsRegistry()

# Record a simple metric
registry.record_metric("revenue", 50000.00, {"region": "North"})

# Time an operation
registry.start_timer("data_processing")
# ... perform operation ...
latency = registry.end_timer("data_processing")

# Record data quality metrics
df = pd.DataFrame({'col1': [1, 2, None], 'col2': [4, 5, 6]})
registry.record_data_metrics(df, "sales_data")

# Get latest metrics summary
latest = registry.get_latest_metrics(hours_back=24)
print(latest)

# Export metrics
registry.export_metrics("metrics_output.json")
```

### Running Tests

Run the comprehensive test suite:

```bash
python -m unittest tests.test_metrics_registry -v
```

### Running the Example

See a full demonstration:

```bash
python example.py
```

## API Reference

### MetricsRegistry

#### `__init__()`
Initialize a new metrics registry.

#### `record_metric(metric_name: str, value: Any, metadata: Optional[Dict] = None)`
Record a metric with optional metadata.

#### `start_timer(operation: str)`
Start timing an operation.

#### `end_timer(operation: str) -> float`
End timing an operation and record the latency. Returns the latency in seconds.

#### `record_data_metrics(df: pd.DataFrame, operation: str = "processing")`
Record metrics about a DataFrame including row count and data quality score.

#### `record_rules_evaluated(n_rules: int, operation: str = "validation")`
Record the number of validation rules evaluated.

#### `get_latest_metrics(hours_back: int = 24) -> Dict[str, Any]`
Get aggregated statistics for metrics within the specified time window.

#### `export_metrics(filepath: str)`
Export all metrics to a JSON file.

#### `clear_old_metrics(hours_to_keep: int = 168)`
Remove metrics older than the specified retention period (default: 1 week).

## Project Structure

```
Commercial-View/
├── src/
│   ├── __init__.py
│   └── metrics_registry.py     # Main MetricsRegistry class
├── tests/
│   ├── __init__.py
│   └── test_metrics_registry.py # Comprehensive test suite
├── example.py                   # Usage example
├── requirements.txt             # Project dependencies
└── README.md                    # This file
```

## License

This project is open source and available for commercial use.
