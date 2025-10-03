import pytest
import pandas as pd
import time
import json
import os
from datetime import datetime, timezone, timedelta
from metrics_registry import MetricsRegistry


def test_metrics_registry_initialization():
    """Test that MetricsRegistry initializes correctly."""
    registry = MetricsRegistry()
    assert len(registry.metrics) == 0
    assert len(registry.start_times) == 0


def test_timer_operations():
    """Test start_timer and end_timer methods."""
    registry = MetricsRegistry()
    
    # Start and end a timer
    registry.start_timer('test_op')
    time.sleep(0.1)  # Sleep for 100ms
    latency = registry.end_timer('test_op')
    
    # Check that latency is approximately 0.1 seconds
    assert 0.09 < latency < 0.15, f"Expected ~0.1s, got {latency}s"
    
    # Check that the timer was removed from start_times
    assert 'test_op' not in registry.start_times
    
    # Check that a metric was recorded
    assert 'latency_ms' in registry.metrics
    assert len(registry.metrics['latency_ms']) == 1
    assert registry.metrics['latency_ms'][0]['metadata']['operation'] == 'test_op'


def test_end_timer_without_start():
    """Test end_timer when timer was never started."""
    registry = MetricsRegistry()
    latency = registry.end_timer('nonexistent')
    assert latency == 0.0


def test_record_metric():
    """Test recording a metric."""
    registry = MetricsRegistry()
    registry.record_metric('test_metric', 42, {'tag': 'test'})
    
    assert 'test_metric' in registry.metrics
    assert len(registry.metrics['test_metric']) == 1
    
    metric = registry.metrics['test_metric'][0]
    assert metric['value'] == 42
    assert metric['metadata']['tag'] == 'test'
    assert 'timestamp' in metric


def test_record_data_metrics():
    """Test recording data metrics from a DataFrame."""
    registry = MetricsRegistry()
    
    # Create a test DataFrame with some null values
    df = pd.DataFrame({
        'A': [1, 2, None, 4],
        'B': [5, None, 7, 8],
        'C': [9, 10, 11, 12]
    })
    
    registry.record_data_metrics(df, 'test_processing')
    
    # Check n_rows metric
    assert 'n_rows' in registry.metrics
    assert registry.metrics['n_rows'][0]['value'] == 4
    
    # Check quality_score metric
    assert 'quality_score' in registry.metrics
    quality_score = registry.metrics['quality_score'][0]['value']
    # 2 nulls out of 12 cells = 10/12 = 0.833333
    expected_score = 1 - (2 / 12)
    assert abs(quality_score - expected_score) < 0.000001


def test_record_data_metrics_empty_dataframe():
    """Test recording metrics from an empty DataFrame."""
    registry = MetricsRegistry()
    df = pd.DataFrame()
    
    registry.record_data_metrics(df, 'empty_processing')
    
    assert registry.metrics['n_rows'][0]['value'] == 0
    assert registry.metrics['quality_score'][0]['value'] == 0.0


def test_record_rules_evaluated():
    """Test recording the number of rules evaluated."""
    registry = MetricsRegistry()
    registry.record_rules_evaluated(10, 'test_validation')
    
    assert 'n_rules_evaluated' in registry.metrics
    assert registry.metrics['n_rules_evaluated'][0]['value'] == 10
    assert registry.metrics['n_rules_evaluated'][0]['metadata']['operation'] == 'test_validation'


def test_get_latest_metrics():
    """Test getting latest metrics."""
    registry = MetricsRegistry()
    
    # Record some numeric metrics
    for i in range(5):
        registry.record_metric('test_metric', i * 10)
    
    # Record some non-numeric metrics
    registry.record_metric('string_metric', 'test_value')
    
    latest = registry.get_latest_metrics(hours_back=24)
    
    # Check numeric metrics
    assert 'test_metric' in latest
    assert latest['test_metric']['count'] == 5
    assert latest['test_metric']['latest'] == 40
    assert latest['test_metric']['avg'] == 20.0
    assert latest['test_metric']['min'] == 0
    assert latest['test_metric']['max'] == 40
    
    # Check non-numeric metrics
    assert 'string_metric' in latest
    assert latest['string_metric']['count'] == 1
    assert latest['string_metric']['latest'] == 'test_value'


def test_export_metrics(tmp_path):
    """Test exporting metrics to a file."""
    registry = MetricsRegistry()
    registry.record_metric('test_metric', 42)
    
    filepath = tmp_path / "metrics.json"
    registry.export_metrics(str(filepath))
    
    # Check that file was created
    assert os.path.exists(filepath)
    
    # Check file content
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    assert 'test_metric' in data
    assert len(data['test_metric']) == 1
    assert data['test_metric'][0]['value'] == 42


def test_clear_old_metrics():
    """Test clearing old metrics."""
    registry = MetricsRegistry()
    
    # Record a metric
    registry.record_metric('test_metric', 42)
    
    # Manually set an old timestamp (older than the default 168 hours)
    old_timestamp = (datetime.now(timezone.utc) - timedelta(hours=200)).isoformat()
    registry.metrics['old_metric'].append({
        'timestamp': old_timestamp,
        'value': 100,
        'metadata': {}
    })
    
    # Clear old metrics (keep only last 168 hours)
    registry.clear_old_metrics(hours_to_keep=168)
    
    # Check that old metric was removed
    assert len(registry.metrics['old_metric']) == 0
    
    # Check that recent metric is still there
    assert len(registry.metrics['test_metric']) == 1


def test_get_latest_metrics_with_old_data():
    """Test get_latest_metrics filters out old data."""
    registry = MetricsRegistry()
    
    # Add an old metric
    old_timestamp = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()
    registry.metrics['old_metric'].append({
        'timestamp': old_timestamp,
        'value': 100,
        'metadata': {}
    })
    
    # Add a recent metric
    registry.record_metric('recent_metric', 42)
    
    # Get metrics from last 24 hours
    latest = registry.get_latest_metrics(hours_back=24)
    
    # Old metric should not be included
    assert 'old_metric' not in latest
    
    # Recent metric should be included
    assert 'recent_metric' in latest


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
