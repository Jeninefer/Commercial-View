# MetricsRegistry Documentation

## Overview

The `MetricsRegistry` class is a comprehensive solution for collecting and managing performance metrics in Python applications. It provides functionality for timing operations, recording custom metrics, tracking data quality, and exporting metrics for analysis.

## Features

- **Timer Operations**: Start and stop timers to measure operation latency
- **Custom Metrics**: Record any metric with values and metadata
- **Data Quality Metrics**: Automatically calculate data quality scores from pandas DataFrames
- **Validation Tracking**: Track the number of validation rules evaluated
- **Metrics Export**: Export all metrics to JSON format
- **Time-based Filtering**: Get metrics from specific time windows
- **Automatic Cleanup**: Clear old metrics to prevent memory bloat

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Example

```python
from metrics_registry import MetricsRegistry
import pandas as pd

# Initialize the registry
registry = MetricsRegistry()

# Time an operation
registry.start_timer('data_load')
# ... perform operation ...
latency = registry.end_timer('data_load')

# Record a custom metric
registry.record_metric('temperature', 72.5, {'location': 'server_room'})

# Record data quality metrics
df = pd.DataFrame({'col1': [1, 2, None], 'col2': [4, 5, 6]})
registry.record_data_metrics(df, 'sales_data')

# Get recent metrics
latest = registry.get_latest_metrics(hours_back=24)
print(latest)
```

## API Reference

### `__init__()`
Initialize a new MetricsRegistry instance.

### `start_timer(operation: str) -> None`
Start a timer for the specified operation.

### `end_timer(operation: str) -> float`
End a timer and record the latency. Returns the latency in seconds.

### `record_metric(metric_name: str, value: Any, metadata: Optional[Dict] = None) -> None`
Record a custom metric with optional metadata.

### `record_data_metrics(df: pd.DataFrame, operation: str = 'processing') -> None`
Analyze a DataFrame and record:
- Number of rows
- Data quality score (based on completeness)

### `record_rules_evaluated(n_rules: int, operation: str = 'validation') -> None`
Record the number of validation rules evaluated.

### `get_latest_metrics(hours_back: int = 24) -> Dict[str, Any]`
Get metrics from the last N hours with statistical summaries.

### `export_metrics(filepath: str) -> None`
Export all metrics to a JSON file.

### `clear_old_metrics(hours_to_keep: int = 168) -> None`
Remove metrics older than the specified number of hours.

## Testing

Run the test suite with:

```bash
pytest test_metrics_registry.py -v
```

## Example Output

See `example_usage.py` for a complete working example demonstrating all features.

## License

This code is provided as-is for the Commercial-View project.
