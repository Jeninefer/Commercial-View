import unittest
import json
import time
import tempfile
import os
from datetime import datetime, timezone, timedelta
import pandas as pd

from metrics_registry import MetricsRegistry


class TestMetricsRegistry(unittest.TestCase):
    """Test suite for MetricsRegistry class."""

    def setUp(self):
        """Set up test fixtures."""
        self.registry = MetricsRegistry()

    def test_initialization(self):
        """Test that MetricsRegistry initializes correctly."""
        self.assertIsInstance(self.registry.metrics, dict)
        self.assertIsInstance(self.registry.start_times, dict)
        self.assertEqual(len(self.registry.metrics), 0)
        self.assertEqual(len(self.registry.start_times), 0)

    def test_now_iso(self):
        """Test ISO timestamp generation."""
        timestamp = self.registry._now_iso()
        self.assertIsInstance(timestamp, str)
        # Verify it's a valid ISO format
        parsed = datetime.fromisoformat(timestamp)
        self.assertIsInstance(parsed, datetime)

    def test_start_timer(self):
        """Test starting a timer."""
        operation = "test_op"
        self.registry.start_timer(operation)
        self.assertIn(operation, self.registry.start_times)
        self.assertIsInstance(self.registry.start_times[operation], float)

    def test_end_timer(self):
        """Test ending a timer."""
        operation = "test_op"
        self.registry.start_timer(operation)
        time.sleep(0.01)  # Sleep for 10ms
        latency = self.registry.end_timer(operation)
        
        self.assertGreater(latency, 0)
        self.assertNotIn(operation, self.registry.start_times)
        # Check that latency metric was recorded
        self.assertIn('latency_ms', self.registry.metrics)
        self.assertEqual(len(self.registry.metrics['latency_ms']), 1)
        self.assertGreater(self.registry.metrics['latency_ms'][0]['value'], 0)

    def test_end_timer_without_start(self):
        """Test ending a timer that was never started."""
        latency = self.registry.end_timer("non_existent_op")
        self.assertEqual(latency, 0.0)

    def test_record_metric(self):
        """Test recording a metric."""
        metric_name = "test_metric"
        value = 42
        metadata = {'key': 'value'}
        
        self.registry.record_metric(metric_name, value, metadata)
        
        self.assertIn(metric_name, self.registry.metrics)
        self.assertEqual(len(self.registry.metrics[metric_name]), 1)
        
        recorded = self.registry.metrics[metric_name][0]
        self.assertEqual(recorded['value'], value)
        self.assertEqual(recorded['metadata'], metadata)
        self.assertIn('timestamp', recorded)

    def test_record_metric_without_metadata(self):
        """Test recording a metric without metadata."""
        metric_name = "test_metric"
        value = 100
        
        self.registry.record_metric(metric_name, value)
        
        recorded = self.registry.metrics[metric_name][0]
        self.assertEqual(recorded['metadata'], {})

    def test_record_data_metrics(self):
        """Test recording data metrics from a DataFrame."""
        df = pd.DataFrame({
            'A': [1, 2, 3, None],
            'B': [4, 5, None, 7],
            'C': [8, 9, 10, 11]
        })
        
        self.registry.record_data_metrics(df, 'test_processing')
        
        # Check n_rows metric
        self.assertIn('n_rows', self.registry.metrics)
        self.assertEqual(self.registry.metrics['n_rows'][0]['value'], 4)
        
        # Check quality_score metric
        self.assertIn('quality_score', self.registry.metrics)
        quality_score = self.registry.metrics['quality_score'][0]['value']
        # Expected: 2 nulls out of 12 cells = 1 - (2/12) = 0.833333
        self.assertAlmostEqual(quality_score, 0.833333, places=5)

    def test_record_data_metrics_empty_dataframe(self):
        """Test recording data metrics from an empty DataFrame."""
        df = pd.DataFrame()
        
        self.registry.record_data_metrics(df, 'empty_processing')
        
        self.assertEqual(self.registry.metrics['n_rows'][0]['value'], 0)
        self.assertEqual(self.registry.metrics['quality_score'][0]['value'], 0.0)

    def test_record_rules_evaluated(self):
        """Test recording rules evaluated."""
        n_rules = 15
        
        self.registry.record_rules_evaluated(n_rules, 'test_validation')
        
        self.assertIn('n_rules_evaluated', self.registry.metrics)
        self.assertEqual(self.registry.metrics['n_rules_evaluated'][0]['value'], 15)
        self.assertEqual(
            self.registry.metrics['n_rules_evaluated'][0]['metadata']['operation'],
            'test_validation'
        )

    def test_get_latest_metrics(self):
        """Test getting latest metrics."""
        # Record some numeric metrics
        self.registry.record_metric('test_metric', 10)
        self.registry.record_metric('test_metric', 20)
        self.registry.record_metric('test_metric', 30)
        
        latest = self.registry.get_latest_metrics(hours_back=24)
        
        self.assertIn('test_metric', latest)
        self.assertEqual(latest['test_metric']['count'], 3)
        self.assertEqual(latest['test_metric']['latest'], 30)
        self.assertEqual(latest['test_metric']['avg'], 20)
        self.assertEqual(latest['test_metric']['min'], 10)
        self.assertEqual(latest['test_metric']['max'], 30)

    def test_get_latest_metrics_non_numeric(self):
        """Test getting latest metrics with non-numeric values."""
        self.registry.record_metric('string_metric', 'value1')
        self.registry.record_metric('string_metric', 'value2')
        
        latest = self.registry.get_latest_metrics(hours_back=24)
        
        self.assertIn('string_metric', latest)
        self.assertEqual(latest['string_metric']['count'], 2)
        self.assertEqual(latest['string_metric']['latest'], 'value2')
        # Should not have avg, min, max for non-numeric values
        self.assertNotIn('avg', latest['string_metric'])

    def test_get_latest_metrics_with_time_filter(self):
        """Test getting latest metrics with time filtering."""
        # This test would require mocking time to properly test
        # For now, just verify it doesn't crash with a small time window
        self.registry.record_metric('test_metric', 42)
        latest = self.registry.get_latest_metrics(hours_back=1)
        self.assertIn('test_metric', latest)

    def test_export_metrics(self):
        """Test exporting metrics to a file."""
        self.registry.record_metric('metric1', 100)
        self.registry.record_metric('metric2', 200)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            filepath = f.name
        
        try:
            self.registry.export_metrics(filepath)
            
            # Verify file exists and contains valid JSON
            self.assertTrue(os.path.exists(filepath))
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.assertIn('metric1', data)
            self.assertIn('metric2', data)
            self.assertEqual(len(data['metric1']), 1)
            self.assertEqual(len(data['metric2']), 1)
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

    def test_clear_old_metrics(self):
        """Test clearing old metrics."""
        # Record a metric
        self.registry.record_metric('test_metric', 42)
        
        # Manually add an old timestamp
        old_timestamp = (datetime.now(timezone.utc) - timedelta(days=8)).isoformat()
        self.registry.metrics['old_metric'].append({
            'timestamp': old_timestamp,
            'value': 999,
            'metadata': {}
        })
        
        # Clear metrics older than 7 days (168 hours)
        self.registry.clear_old_metrics(hours_to_keep=168)
        
        # test_metric should still be there (it's recent)
        self.assertIn('test_metric', self.registry.metrics)
        
        # old_metric should be gone
        self.assertTrue(
            len(self.registry.metrics['old_metric']) == 0 or
            'old_metric' not in self.registry.metrics or
            len([r for r in self.registry.metrics['old_metric'] 
                 if r['timestamp'] == old_timestamp]) == 0
        )

    def test_multiple_operations_flow(self):
        """Test a complete workflow with multiple operations."""
        # Start and end a timer
        self.registry.start_timer('data_load')
        time.sleep(0.01)
        self.registry.end_timer('data_load')
        
        # Record data metrics
        df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        self.registry.record_data_metrics(df, 'loading')
        
        # Record rules
        self.registry.record_rules_evaluated(10, 'validation')
        
        # Get latest metrics
        latest = self.registry.get_latest_metrics()
        
        # Verify all metrics are present
        self.assertIn('latency_ms', latest)
        self.assertIn('n_rows', latest)
        self.assertIn('quality_score', latest)
        self.assertIn('n_rules_evaluated', latest)


if __name__ == '__main__':
    unittest.main()
