"""Test utilities module."""

import pytest
from src.commercial_view.utils import logger, registry, MetricsRegistry


def test_logger_exists():
    """Test that logger is configured properly."""
    assert logger is not None
    assert logger.name == "commercial_view"


def test_registry_exists():
    """Test that registry is initialized."""
    assert registry is not None
    assert isinstance(registry, MetricsRegistry)


def test_registry_record_metrics():
    """Test recording metrics."""
    import pandas as pd
    
    df = pd.DataFrame({
        "col1": [1, 2, 3],
        "col2": [4, 5, 6]
    })
    
    initial_count = len(registry.metrics)
    registry.record_data_metrics(df, operation="test_operation")
    
    assert len(registry.metrics) == initial_count + 1
    last_metric = registry.metrics[-1]
    assert last_metric["operation"] == "test_operation"
    assert last_metric["row_count"] == 3
    assert "col1" in last_metric["columns"]
    assert "col2" in last_metric["columns"]
