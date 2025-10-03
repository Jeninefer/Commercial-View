# Commercial-View
Principal KPI

## MetricsRegistry

A robust metrics collection and management system for tracking performance, data quality, and operational metrics in Python applications.

### Features

- **Performance Monitoring**: Timer-based latency tracking for operations
- **Data Quality Metrics**: Automatic quality score calculation for pandas DataFrames
- **Custom Metrics**: Record any metric with optional metadata
- **Time-based Filtering**: Retrieve metrics from specific time windows
- **Export/Import**: JSON-based metric persistence
- **Automatic Cleanup**: Remove old metrics based on retention policies

### Installation

```bash
pip install -r requirements.txt
```

### Quick Start

```python
from metrics_registry import MetricsRegistry
import pandas as pd

# Initialize registry
registry = MetricsRegistry()

# Track operation latency
registry.start_timer('data_load')
# ... perform operation ...
registry.end_timer('data_load')

# Track data quality
df = pd.DataFrame({'col1': [1, 2, None], 'col2': [4, 5, 6]})
registry.record_data_metrics(df, 'validation')

# Get latest metrics
latest = registry.get_latest_metrics(hours_back=24)
print(latest)
```

### Usage Examples

See `example_usage.py` for comprehensive usage examples.

### Testing

Run the test suite:

```bash
python3 -m unittest test_metrics_registry.py -v
```

### API Reference

#### Core Methods

- `start_timer(operation: str)` - Start timing an operation
- `end_timer(operation: str) -> float` - End timing and record latency
- `record_metric(metric_name: str, value: Any, metadata: Optional[Dict])` - Record a custom metric
- `record_data_metrics(df: pd.DataFrame, operation: str)` - Record DataFrame quality metrics
- `record_rules_evaluated(n_rules: int, operation: str)` - Record validation rule counts
- `get_latest_metrics(hours_back: int = 24) -> Dict[str, Any]` - Retrieve recent metrics
- `export_metrics(filepath: str)` - Export metrics to JSON file
- `clear_old_metrics(hours_to_keep: int = 168)` - Remove old metrics
