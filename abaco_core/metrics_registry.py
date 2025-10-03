"""
Metrics Registry Module

Handles performance and quality telemetry for monitoring and tracking.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from collections import defaultdict
import time

logger = logging.getLogger(__name__)


class MetricsRegistry:
    """Central registry for performance and quality metrics."""
    
    def __init__(self):
        """Initialize the metrics registry."""
        self._metrics = defaultdict(list)
        self._counters = defaultdict(int)
        self._gauges = defaultdict(float)
        self._timings = defaultdict(list)
        self._metadata = {}
        logger.info("Initialized MetricsRegistry")
    
    def record_counter(self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None):
        """
        Record a counter metric.
        
        Args:
            name: Metric name
            value: Value to increment by
            tags: Optional tags for the metric
        """
        self._counters[name] += value
        self._metrics[name].append({
            'type': 'counter',
            'value': value,
            'timestamp': datetime.now(),
            'tags': tags or {}
        })
        logger.debug(f"Counter '{name}' incremented by {value}")
    
    def record_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """
        Record a gauge metric.
        
        Args:
            name: Metric name
            value: Current value
            tags: Optional tags for the metric
        """
        self._gauges[name] = value
        self._metrics[name].append({
            'type': 'gauge',
            'value': value,
            'timestamp': datetime.now(),
            'tags': tags or {}
        })
        logger.debug(f"Gauge '{name}' set to {value}")
    
    def record_timing(self, name: str, duration_ms: float, tags: Optional[Dict[str, str]] = None):
        """
        Record a timing metric.
        
        Args:
            name: Metric name
            duration_ms: Duration in milliseconds
            tags: Optional tags for the metric
        """
        self._timings[name].append(duration_ms)
        self._metrics[name].append({
            'type': 'timing',
            'value': duration_ms,
            'timestamp': datetime.now(),
            'tags': tags or {}
        })
        logger.debug(f"Timing '{name}' recorded: {duration_ms:.2f}ms")
    
    def get_counter(self, name: str) -> int:
        """Get current counter value."""
        return self._counters.get(name, 0)
    
    def get_gauge(self, name: str) -> float:
        """Get current gauge value."""
        return self._gauges.get(name, 0.0)
    
    def get_timing_stats(self, name: str) -> Dict[str, float]:
        """
        Get statistics for timing metric.
        
        Args:
            name: Metric name
        
        Returns:
            Dict with min, max, avg, count
        """
        timings = self._timings.get(name, [])
        
        if not timings:
            return {'min': 0, 'max': 0, 'avg': 0, 'count': 0}
        
        return {
            'min': min(timings),
            'max': max(timings),
            'avg': sum(timings) / len(timings),
            'count': len(timings)
        }
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """
        Get all metrics with their current values.
        
        Returns:
            Dict with all metrics
        """
        return {
            'counters': dict(self._counters),
            'gauges': dict(self._gauges),
            'timings': {name: self.get_timing_stats(name) for name in self._timings}
        }
    
    def reset(self):
        """Reset all metrics."""
        self._metrics.clear()
        self._counters.clear()
        self._gauges.clear()
        self._timings.clear()
        logger.info("Reset all metrics")
    
    def set_metadata(self, key: str, value: Any):
        """Set metadata for the registry."""
        self._metadata[key] = value
    
    def get_metadata(self, key: str) -> Any:
        """Get metadata from the registry."""
        return self._metadata.get(key)


class PerformanceTracker:
    """Track performance metrics for functions and operations."""
    
    def __init__(self, registry: Optional[MetricsRegistry] = None):
        """
        Initialize performance tracker.
        
        Args:
            registry: Optional MetricsRegistry to use
        """
        self.registry = registry or MetricsRegistry()
    
    def track_execution(self, operation_name: str):
        """
        Context manager to track execution time.
        
        Args:
            operation_name: Name of the operation being tracked
        
        Usage:
            with tracker.track_execution('my_operation'):
                # code to track
                pass
        """
        return _ExecutionTimer(operation_name, self.registry)
    
    def track_function(self, func):
        """
        Decorator to track function execution time.
        
        Args:
            func: Function to track
        
        Returns:
            Wrapped function
        """
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration_ms = (time.time() - start_time) * 1000
                self.registry.record_timing(func.__name__, duration_ms)
        
        return wrapper


class _ExecutionTimer:
    """Context manager for timing execution."""
    
    def __init__(self, operation_name: str, registry: MetricsRegistry):
        """Initialize timer."""
        self.operation_name = operation_name
        self.registry = registry
        self.start_time = None
    
    def __enter__(self):
        """Start timing."""
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timing and record metric."""
        duration_ms = (time.time() - self.start_time) * 1000
        self.registry.record_timing(self.operation_name, duration_ms)
        
        if exc_type is not None:
            self.registry.record_counter(f'{self.operation_name}_errors')


class QualityMetrics:
    """Track data quality metrics."""
    
    def __init__(self, registry: Optional[MetricsRegistry] = None):
        """
        Initialize quality metrics tracker.
        
        Args:
            registry: Optional MetricsRegistry to use
        """
        self.registry = registry or MetricsRegistry()
    
    def record_data_quality(self, dataset_name: str, 
                           total_records: int,
                           valid_records: int,
                           null_count: int = 0,
                           duplicate_count: int = 0):
        """
        Record data quality metrics.
        
        Args:
            dataset_name: Name of the dataset
            total_records: Total number of records
            valid_records: Number of valid records
            null_count: Number of null values
            duplicate_count: Number of duplicate records
        """
        self.registry.record_gauge(f'{dataset_name}_total_records', total_records)
        self.registry.record_gauge(f'{dataset_name}_valid_records', valid_records)
        self.registry.record_gauge(f'{dataset_name}_null_count', null_count)
        self.registry.record_gauge(f'{dataset_name}_duplicate_count', duplicate_count)
        
        # Calculate quality score
        if total_records > 0:
            quality_score = (valid_records / total_records) * 100
            self.registry.record_gauge(f'{dataset_name}_quality_score', quality_score)
            logger.info(f"Data quality for {dataset_name}: {quality_score:.2f}%")
    
    def record_validation_result(self, rule_name: str, passed: bool):
        """
        Record validation rule result.
        
        Args:
            rule_name: Name of the validation rule
            passed: Whether validation passed
        """
        metric_name = f'validation_{rule_name}_{"passed" if passed else "failed"}'
        self.registry.record_counter(metric_name)
    
    def get_quality_summary(self, dataset_name: str) -> Dict[str, Any]:
        """
        Get quality summary for a dataset.
        
        Args:
            dataset_name: Name of the dataset
        
        Returns:
            Dict with quality metrics
        """
        return {
            'total_records': self.registry.get_gauge(f'{dataset_name}_total_records'),
            'valid_records': self.registry.get_gauge(f'{dataset_name}_valid_records'),
            'null_count': self.registry.get_gauge(f'{dataset_name}_null_count'),
            'duplicate_count': self.registry.get_gauge(f'{dataset_name}_duplicate_count'),
            'quality_score': self.registry.get_gauge(f'{dataset_name}_quality_score')
        }


# Global registry instance
_global_registry = MetricsRegistry()


def get_global_registry() -> MetricsRegistry:
    """Get the global metrics registry instance."""
    return _global_registry


def record_counter(name: str, value: int = 1, tags: Optional[Dict[str, str]] = None):
    """Record a counter metric to the global registry."""
    _global_registry.record_counter(name, value, tags)


def record_gauge(name: str, value: float, tags: Optional[Dict[str, str]] = None):
    """Record a gauge metric to the global registry."""
    _global_registry.record_gauge(name, value, tags)


def record_timing(name: str, duration_ms: float, tags: Optional[Dict[str, str]] = None):
    """Record a timing metric to the global registry."""
    _global_registry.record_timing(name, duration_ms, tags)


def get_all_metrics() -> Dict[str, Any]:
    """Get all metrics from the global registry."""
    return _global_registry.get_all_metrics()
