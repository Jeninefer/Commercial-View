"""Tests for StartupAnalyzer.compute_viability_index"""

import unittest
from startup_analyzer import StartupAnalyzer


class TestComputeViabilityIndex(unittest.TestCase):
    """Test cases for the compute_viability_index method."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use default thresholds: runway_months_min=12, ltv_cac_ratio_min=3.0, nrr_min=1.0
        self.analyzer = StartupAnalyzer()
    
    def test_perfect_score(self):
        """Test with metrics that achieve maximum score."""
        metrics = {
            "runway_months": 24,  # >= 2*12
            "ltv_cac_ratio": 6.0,  # >= 2*3.0
            "nrr": 1.2  # >= 1.2*1.0
        }
        score = self.analyzer.compute_viability_index(metrics)
        # 0.4*100 + 0.4*100 + 0.2*100 = 100
        self.assertEqual(score, 100)
    
    def test_good_score(self):
        """Test with good metrics (75 on all dimensions)."""
        metrics = {
            "runway_months": 12,  # >= 12 (75)
            "ltv_cac_ratio": 3.0,  # >= 3.0 (75)
            "nrr": 1.0  # >= 1.0 (75)
        }
        score = self.analyzer.compute_viability_index(metrics)
        # 0.4*75 + 0.4*75 + 0.2*75 = 75
        self.assertEqual(score, 75)
    
    def test_medium_score(self):
        """Test with medium metrics (50 on all dimensions)."""
        metrics = {
            "runway_months": 6,  # >= 12/2 (50)
            "ltv_cac_ratio": 1.5,  # >= 3.0/2 (50)
            "nrr": 0.8  # >= 0.8*1.0 (50)
        }
        score = self.analyzer.compute_viability_index(metrics)
        # 0.4*50 + 0.4*50 + 0.2*50 = 50
        self.assertEqual(score, 50)
    
    def test_low_score(self):
        """Test with low but non-zero metrics (25 on all dimensions)."""
        metrics = {
            "runway_months": 3,  # > 0 but < 6 (25)
            "ltv_cac_ratio": 0.5,  # > 0 but < 1.5 (25)
            "nrr": 0.5  # > 0 but < 0.8 (25)
        }
        score = self.analyzer.compute_viability_index(metrics)
        # 0.4*25 + 0.4*25 + 0.2*25 = 25
        self.assertEqual(score, 25)
    
    def test_zero_score(self):
        """Test with all zero metrics."""
        metrics = {
            "runway_months": 0,
            "ltv_cac_ratio": 0,
            "nrr": 0
        }
        score = self.analyzer.compute_viability_index(metrics)
        self.assertEqual(score, 0)
    
    def test_missing_metrics(self):
        """Test with missing metrics (should default to 0)."""
        metrics = {}
        score = self.analyzer.compute_viability_index(metrics)
        self.assertEqual(score, 0)
    
    def test_ltv_cac_alternate_key(self):
        """Test that ltv_cac alternate key name works."""
        metrics = {
            "runway_months": 12,
            "ltv_cac": 3.0,  # Using alternate key name
            "nrr": 1.0
        }
        score = self.analyzer.compute_viability_index(metrics)
        self.assertEqual(score, 75)
    
    def test_mixed_scores(self):
        """Test with mixed performance across dimensions."""
        metrics = {
            "runway_months": 24,  # 100 points
            "ltv_cac_ratio": 1.5,  # 50 points
            "nrr": 0  # 0 points
        }
        score = self.analyzer.compute_viability_index(metrics)
        # 0.4*100 + 0.4*50 + 0.2*0 = 60
        self.assertEqual(score, 60)
    
    def test_custom_thresholds(self):
        """Test with custom thresholds."""
        custom_analyzer = StartupAnalyzer(thresholds={
            "runway_months_min": 6,
            "ltv_cac_ratio_min": 2.0,
            "nrr_min": 0.9
        })
        metrics = {
            "runway_months": 6,
            "ltv_cac_ratio": 2.0,
            "nrr": 0.9
        }
        score = custom_analyzer.compute_viability_index(metrics)
        # All metrics at threshold = 75 on each dimension
        # 0.4*75 + 0.4*75 + 0.2*75 = 75
        self.assertEqual(score, 75)
    
    def test_none_values_treated_as_zero(self):
        """Test that None values are treated as 0."""
        metrics = {
            "runway_months": None,
            "ltv_cac_ratio": None,
            "nrr": None
        }
        score = self.analyzer.compute_viability_index(metrics)
        self.assertEqual(score, 0)
    
    def test_rounding(self):
        """Test that score is properly rounded to integer."""
        metrics = {
            "runway_months": 24,  # 100 points
            "ltv_cac_ratio": 3.0,  # 75 points
            "nrr": 1.0  # 75 points
        }
        score = self.analyzer.compute_viability_index(metrics)
        # 0.4*100 + 0.4*75 + 0.2*75 = 40 + 30 + 15 = 85
        self.assertEqual(score, 85)
        self.assertIsInstance(score, int)


if __name__ == '__main__':
    unittest.main()
