"""
Unit tests for DPD Bucket Analyzer
"""

import unittest
import numpy as np
import pandas as pd
from dpd_analyzer import DPDBucketAnalyzer, registry


class TestDPDBucketAnalyzer(unittest.TestCase):
    """Test cases for DPDBucketAnalyzer class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = DPDBucketAnalyzer()
    
    def test_missing_days_past_due_column(self):
        """Test that missing 'days_past_due' column raises ValueError"""
        df = pd.DataFrame({"other_column": [1, 2, 3]})
        with self.assertRaises(ValueError) as context:
            self.analyzer.get_dpd_buckets(df)
        self.assertIn("days_past_due", str(context.exception))
    
    def test_default_buckets(self):
        """Test default DPD bucketing without custom config"""
        df = pd.DataFrame({
            "days_past_due": [0, 15, 45, 75, 100, 130, 165, 200]
        })
        result = self.analyzer.get_dpd_buckets(df)
        
        # Check that dpd_bucket column is added
        self.assertIn("dpd_bucket", result.columns)
        
        # Check expected buckets
        expected_buckets = ["Current", "1-29", "30-59", "60-89", "90-119", "120-149", "150-179", "180+"]
        self.assertEqual(list(result["dpd_bucket"]), expected_buckets)
    
    def test_default_flag(self):
        """Test default flag calculation with default threshold (90)"""
        df = pd.DataFrame({
            "days_past_due": [0, 30, 60, 89, 90, 120]
        })
        result = self.analyzer.get_dpd_buckets(df)
        
        # Check that default_flag column is added
        self.assertIn("default_flag", result.columns)
        
        # Check expected flags (threshold is 90)
        expected_flags = [0, 0, 0, 0, 1, 1]
        self.assertEqual(list(result["default_flag"]), expected_flags)
    
    def test_custom_threshold(self):
        """Test default flag with custom threshold"""
        analyzer = DPDBucketAnalyzer(dpd_threshold=60)
        df = pd.DataFrame({
            "days_past_due": [0, 30, 59, 60, 90]
        })
        result = analyzer.get_dpd_buckets(df)
        
        # Check expected flags (threshold is 60)
        expected_flags = [0, 0, 0, 1, 1]
        self.assertEqual(list(result["default_flag"]), expected_flags)
    
    def test_custom_buckets(self):
        """Test custom DPD buckets from config"""
        config = {
            "dpd_buckets": [
                (0, 0, "Current"),
                (1, 30, "1-30"),
                (31, 90, "31-90"),
                (91, None, "90+")
            ]
        }
        analyzer = DPDBucketAnalyzer(config=config)
        df = pd.DataFrame({
            "days_past_due": [0, 15, 45, 100]
        })
        result = analyzer.get_dpd_buckets(df)
        
        # Check expected buckets
        expected_buckets = ["Current", "1-30", "31-90", "90+"]
        self.assertEqual(list(result["dpd_bucket"]), expected_buckets)
    
    def test_custom_buckets_with_open_ended(self):
        """Test custom buckets with open-ended (None) upper bound"""
        config = {
            "dpd_buckets": [
                (0, 30, "Low"),
                (31, 90, "Medium"),
                (91, None, "High")
            ]
        }
        analyzer = DPDBucketAnalyzer(config=config)
        df = pd.DataFrame({
            "days_past_due": [10, 50, 100, 500, 1000]
        })
        result = analyzer.get_dpd_buckets(df)
        
        # Check expected buckets
        expected_buckets = ["Low", "Medium", "High", "High", "High"]
        self.assertEqual(list(result["dpd_bucket"]), expected_buckets)
    
    def test_coerce_invalid_values(self):
        """Test that invalid DPD values are coerced to 0"""
        df = pd.DataFrame({
            "days_past_due": [0, "invalid", None, 30, np.nan]
        })
        result = self.analyzer.get_dpd_buckets(df)
        
        # Invalid values should be treated as 0 (Current)
        expected_buckets = ["Current", "Current", "Current", "30-59", "Current"]
        self.assertEqual(list(result["dpd_bucket"]), expected_buckets)
    
    def test_original_dataframe_unchanged(self):
        """Test that original dataframe is not modified"""
        df = pd.DataFrame({
            "days_past_due": [0, 30, 60],
            "account_id": [1, 2, 3]
        })
        original_columns = df.columns.tolist()
        result = self.analyzer.get_dpd_buckets(df)
        
        # Original should not have new columns
        self.assertEqual(df.columns.tolist(), original_columns)
        
        # Result should have new columns
        self.assertIn("dpd_bucket", result.columns)
        self.assertIn("default_flag", result.columns)
    
    def test_edge_case_boundary_values(self):
        """Test boundary values for default buckets"""
        df = pd.DataFrame({
            "days_past_due": [0, 1, 29, 30, 59, 60, 89, 90, 179, 180]
        })
        result = self.analyzer.get_dpd_buckets(df)
        
        expected_buckets = [
            "Current",   # 0
            "1-29",      # 1
            "1-29",      # 29
            "30-59",     # 30
            "30-59",     # 59
            "60-89",     # 60
            "60-89",     # 89
            "90-119",    # 90
            "150-179",   # 179
            "180+"       # 180
        ]
        self.assertEqual(list(result["dpd_bucket"]), expected_buckets)
    
    def test_negative_dpd_values(self):
        """Test handling of negative DPD values (treated as 0)"""
        df = pd.DataFrame({
            "days_past_due": [-10, -1, 0, 10]
        })
        result = self.analyzer.get_dpd_buckets(df)
        
        # Note: pd.cut with -inf as lower bound will handle negatives
        # They should fall into "Current" bucket
        self.assertIn("Current", result["dpd_bucket"].iloc[0])
    
    def test_large_dpd_values(self):
        """Test handling of very large DPD values"""
        df = pd.DataFrame({
            "days_past_due": [1000, 5000, 10000]
        })
        result = self.analyzer.get_dpd_buckets(df)
        
        # All should be in 180+ bucket
        expected_buckets = ["180+", "180+", "180+"]
        self.assertEqual(list(result["dpd_bucket"]), expected_buckets)
    
    def test_empty_dataframe(self):
        """Test handling of empty dataframe"""
        df = pd.DataFrame({
            "days_past_due": []
        })
        result = self.analyzer.get_dpd_buckets(df)
        
        # Should return empty dataframe with correct columns
        self.assertEqual(len(result), 0)
        self.assertIn("dpd_bucket", result.columns)
        self.assertIn("default_flag", result.columns)


class TestDataQualityRegistry(unittest.TestCase):
    """Test cases for DataQualityRegistry class"""
    
    def test_registry_exists(self):
        """Test that global registry exists"""
        self.assertIsNotNone(registry)
    
    def test_record_data_metrics(self):
        """Test that record_data_metrics runs without error"""
        df = pd.DataFrame({"days_past_due": [0, 30, 60]})
        # Should not raise any exception
        try:
            registry.record_data_metrics(df, operation="test")
        except Exception as e:
            self.fail(f"record_data_metrics raised an exception: {e}")


if __name__ == "__main__":
    unittest.main()
