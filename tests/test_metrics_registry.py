import unittest
import time
import pandas as pd
import json
import os
import tempfile
from datetime import datetime, timedelta
from metrics_registry import MetricsRegistry

class TestMetricsRegistry(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.registry = MetricsRegistry()
    
    def test_init(self):
        """Test initialization of MetricsRegistry."""
        registry = MetricsRegistry()
        self.assertEqual(len(registry.metrics), 0)
        self.assertEqual(len(registry.start_times), 0)
    
    def test_record_metric(self):
        """Test recording a metric."""
        self.registry.record_metric("test_metric", 42, {"tag": "test"})
        
        self.assertIn("test_metric", self.registry.metrics)
        self.assertEqual(len(self.registry.metrics["test_metric"]), 1)
        
        metric = self.registry.metrics["test_metric"][0]
        self.assertEqual(metric["value"], 42)
        self.assertEqual(metric["metadata"]["tag"], "test")
        self.assertIn("timestamp", metric)
        self.assertTrue(metric["timestamp"].endswith("Z"))
    
    def test_record_metric_without_metadata(self):
        """Test recording a metric without metadata."""
        self.registry.record_metric("test_metric", 100)
        
        metric = self.registry.metrics["test_metric"][0]
        self.assertEqual(metric["value"], 100)
        self.assertEqual(metric["metadata"], {})
    
    def test_start_and_end_timer(self):
        """Test timer functionality."""
        operation = "test_operation"
        
        self.registry.start_timer(operation)
        self.assertIn(operation, self.registry.start_times)
        
        time.sleep(0.1)  # Sleep for 100ms
        
        latency = self.registry.end_timer(operation)
        
        # Check that latency is approximately 100ms (within reasonable tolerance)
        self.assertGreaterEqual(latency, 0.09)
        self.assertLessEqual(latency, 0.15)
        
        # Check that timer was removed
        self.assertNotIn(operation, self.registry.start_times)
        
        # Check that latency metric was recorded
        self.assertIn("latency_ms", self.registry.metrics)
        latency_ms = self.registry.metrics["latency_ms"][0]["value"]
        self.assertGreaterEqual(latency_ms, 90)
        self.assertLessEqual(latency_ms, 150)
    
    def test_end_timer_without_start(self):
        """Test ending a timer that was never started."""
        latency = self.registry.end_timer("nonexistent_operation")
        self.assertEqual(latency, 0.0)
    
    def test_record_data_metrics(self):
        """Test recording data metrics from DataFrame."""
        df = pd.DataFrame({
            'A': [1, 2, 3, None],
            'B': [4, 5, None, 7],
            'C': [8, 9, 10, 11]
        })
        
        self.registry.record_data_metrics(df, "test_processing")
        
        # Check n_rows metric
        self.assertIn("n_rows", self.registry.metrics)
        self.assertEqual(self.registry.metrics["n_rows"][0]["value"], 4)
        self.assertEqual(self.registry.metrics["n_rows"][0]["metadata"]["operation"], "test_processing")
        
        # Check quality_score metric (completeness)
        self.assertIn("quality_score", self.registry.metrics)
        quality_score = self.registry.metrics["quality_score"][0]["value"]
        
        # We have 2 null values out of 12 total cells, so completeness is 10/12 = 0.8333...
        expected_completeness = 1 - (2 / 12)
        self.assertAlmostEqual(quality_score, expected_completeness, places=5)
    
    def test_record_data_metrics_empty_df(self):
        """Test recording data metrics from empty DataFrame."""
        df = pd.DataFrame()
        
        self.registry.record_data_metrics(df, "empty_processing")
        
        # Check n_rows metric
        self.assertEqual(self.registry.metrics["n_rows"][0]["value"], 0)
        
        # Check quality_score - should be 1 (no nulls in empty df)
        quality_score = self.registry.metrics["quality_score"][0]["value"]
        self.assertEqual(quality_score, 1.0)
    
    def test_record_rules_evaluated(self):
        """Test recording number of rules evaluated."""
        self.registry.record_rules_evaluated(10, "test_validation")
        
        self.assertIn("n_rules_evaluated", self.registry.metrics)
        self.assertEqual(self.registry.metrics["n_rules_evaluated"][0]["value"], 10)
        self.assertEqual(self.registry.metrics["n_rules_evaluated"][0]["metadata"]["operation"], "test_validation")
    
    def test_get_latest_metrics(self):
        """Test retrieving latest metrics."""
        # Record multiple metrics
        self.registry.record_metric("metric1", 10)
        self.registry.record_metric("metric1", 20)
        self.registry.record_metric("metric1", 30)
        self.registry.record_metric("metric2", 100)
        
        latest = self.registry.get_latest_metrics(hours_back=24)
        
        self.assertIn("metric1", latest)
        self.assertIn("metric2", latest)
        
        # Check metric1 stats
        m1 = latest["metric1"]
        self.assertEqual(m1["count"], 3)
        self.assertEqual(m1["latest"], 30)
        self.assertEqual(m1["avg"], 20.0)
        self.assertEqual(m1["min"], 10)
        self.assertEqual(m1["max"], 30)
        
        # Check metric2 stats
        m2 = latest["metric2"]
        self.assertEqual(m2["count"], 1)
        self.assertEqual(m2["latest"], 100)
        self.assertEqual(m2["avg"], 100.0)
        self.assertEqual(m2["min"], 100)
        self.assertEqual(m2["max"], 100)
    
    def test_get_latest_metrics_with_time_filter(self):
        """Test getting metrics within time window."""
        # This is harder to test without manipulating time
        # Just verify it returns empty dict when no recent metrics
        latest = self.registry.get_latest_metrics(hours_back=0)
        self.assertEqual(latest, {})
    
    def test_export_metrics(self):
        """Test exporting metrics to file."""
        self.registry.record_metric("test_metric", 42, {"tag": "test"})
        self.registry.record_metric("another_metric", 100)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            filepath = f.name
        
        try:
            self.registry.export_metrics(filepath)
            
            # Read the file and verify contents
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.assertIn("test_metric", data)
            self.assertIn("another_metric", data)
            self.assertEqual(len(data["test_metric"]), 1)
            self.assertEqual(data["test_metric"][0]["value"], 42)
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)
    
    def test_clear_old_metrics(self):
        """Test clearing old metrics."""
        # Record some metrics
        self.registry.record_metric("metric1", 10)
        self.registry.record_metric("metric2", 20)
        
        # Verify metrics exist
        self.assertEqual(len(self.registry.metrics["metric1"]), 1)
        self.assertEqual(len(self.registry.metrics["metric2"]), 1)
        
        # Clear metrics older than 0 hours (should clear all)
        self.registry.clear_old_metrics(hours_to_keep=0)
        
        # Metrics should be empty
        self.assertEqual(len(self.registry.metrics["metric1"]), 0)
        self.assertEqual(len(self.registry.metrics["metric2"]), 0)
    
    def test_clear_old_metrics_keeps_recent(self):
        """Test that clear_old_metrics keeps recent metrics."""
        # Record a metric
        self.registry.record_metric("metric1", 10)
        
        # Clear metrics older than 24 hours (should keep our recent metric)
        self.registry.clear_old_metrics(hours_to_keep=24)
        
        # Metric should still exist
        self.assertEqual(len(self.registry.metrics["metric1"]), 1)


if __name__ == '__main__':
    unittest.main()
