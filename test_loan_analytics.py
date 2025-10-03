"""
Tests for the LoanAnalytics module
"""

import unittest
import logging
import numpy as np
import pandas as pd
from loan_analytics import LoanAnalytics


class TestLoanAnalytics(unittest.TestCase):
    """Test cases for LoanAnalytics class"""

    def setUp(self):
        """Set up test fixtures"""
        self.analytics = LoanAnalytics()
        # Configure logging to show warnings/errors during tests
        logging.basicConfig(level=logging.INFO)

    def test_calculate_weighted_stats_basic(self):
        """Test basic weighted stats calculation with standard column names"""
        df = pd.DataFrame({
            'outstanding_balance': [1000, 2000, 3000],
            'apr': [5.0, 6.0, 7.0],
            'eir': [5.1, 6.2, 7.3],
            'term': [360, 240, 180]
        })
        
        result = self.analytics.calculate_weighted_stats(df)
        
        # Check that result is not empty
        self.assertFalse(result.empty)
        
        # Check that expected columns exist
        self.assertIn('weighted_apr', result.columns)
        self.assertIn('weighted_eir', result.columns)
        self.assertIn('weighted_term', result.columns)
        
        # Verify weighted calculations
        # Weighted APR = (5*1000 + 6*2000 + 7*3000) / (1000+2000+3000) = 6.333...
        expected_apr = (5.0*1000 + 6.0*2000 + 7.0*3000) / 6000
        self.assertAlmostEqual(result['weighted_apr'].iloc[0], expected_apr, places=6)

    def test_calculate_weighted_stats_with_aliases(self):
        """Test weighted stats with column aliases"""
        df = pd.DataFrame({
            'current_balance': [1000, 2000, 3000],
            'annual_rate': [5.0, 6.0, 7.0],
            'effective_interest_rate': [5.1, 6.2, 7.3],
            'tenor_days': [360, 240, 180]
        })
        
        result = self.analytics.calculate_weighted_stats(df, weight_field='current_balance')
        
        # Should resolve aliases and calculate
        self.assertFalse(result.empty)
        self.assertIn('weighted_apr', result.columns)
        self.assertIn('weighted_eir', result.columns)
        self.assertIn('weighted_term', result.columns)

    def test_calculate_weighted_stats_with_nan_weights(self):
        """Test handling of NaN weights"""
        df = pd.DataFrame({
            'outstanding_balance': [1000, np.nan, 3000],
            'apr': [5.0, 6.0, 7.0],
            'eir': [5.1, 6.2, 7.3],
            'term': [360, 240, 180]
        })
        
        result = self.analytics.calculate_weighted_stats(df)
        
        # Should skip rows with NaN weights
        self.assertFalse(result.empty)
        # Weighted APR should be calculated from rows 0 and 2 only
        expected_apr = (5.0*1000 + 7.0*3000) / 4000
        self.assertAlmostEqual(result['weighted_apr'].iloc[0], expected_apr, places=6)

    def test_calculate_weighted_stats_with_zero_weights(self):
        """Test handling of zero weights"""
        df = pd.DataFrame({
            'outstanding_balance': [1000, 0, 3000],
            'apr': [5.0, 6.0, 7.0],
            'eir': [5.1, 6.2, 7.3],
            'term': [360, 240, 180]
        })
        
        result = self.analytics.calculate_weighted_stats(df)
        
        # Should skip rows with zero weights
        self.assertFalse(result.empty)
        # Weighted APR should be calculated from rows 0 and 2 only
        expected_apr = (5.0*1000 + 7.0*3000) / 4000
        self.assertAlmostEqual(result['weighted_apr'].iloc[0], expected_apr, places=6)

    def test_calculate_weighted_stats_with_negative_weights(self):
        """Test handling of negative weights"""
        df = pd.DataFrame({
            'outstanding_balance': [1000, -500, 3000],
            'apr': [5.0, 6.0, 7.0],
            'eir': [5.1, 6.2, 7.3],
            'term': [360, 240, 180]
        })
        
        result = self.analytics.calculate_weighted_stats(df)
        
        # Should skip rows with negative weights
        self.assertFalse(result.empty)
        expected_apr = (5.0*1000 + 7.0*3000) / 4000
        self.assertAlmostEqual(result['weighted_apr'].iloc[0], expected_apr, places=6)

    def test_calculate_weighted_stats_missing_weight_field(self):
        """Test when weight field is missing and no alternative found"""
        df = pd.DataFrame({
            'some_other_column': [1000, 2000, 3000],
            'apr': [5.0, 6.0, 7.0],
            'eir': [5.1, 6.2, 7.3],
            'term': [360, 240, 180]
        })
        
        result = self.analytics.calculate_weighted_stats(df, weight_field='non_existent')
        
        # Should return empty DataFrame when weight field not found
        self.assertTrue(result.empty)

    def test_calculate_weighted_stats_missing_metric_columns(self):
        """Test when some metric columns are missing"""
        df = pd.DataFrame({
            'outstanding_balance': [1000, 2000, 3000],
            'apr': [5.0, 6.0, 7.0],
            # eir and term columns missing
        })
        
        result = self.analytics.calculate_weighted_stats(df)
        
        # Should calculate for available metrics only
        self.assertFalse(result.empty)
        self.assertIn('weighted_apr', result.columns)
        self.assertNotIn('weighted_eir', result.columns)
        self.assertNotIn('weighted_term', result.columns)

    def test_calculate_weighted_stats_custom_metrics(self):
        """Test with custom metric list"""
        df = pd.DataFrame({
            'outstanding_balance': [1000, 2000, 3000],
            'apr': [5.0, 6.0, 7.0],
            'eir': [5.1, 6.2, 7.3],
            'term': [360, 240, 180]
        })
        
        result = self.analytics.calculate_weighted_stats(df, metrics=['apr'])
        
        # Should only calculate specified metrics
        self.assertFalse(result.empty)
        self.assertIn('weighted_apr', result.columns)
        self.assertNotIn('weighted_eir', result.columns)
        self.assertNotIn('weighted_term', result.columns)

    def test_calculate_weighted_stats_all_invalid_weights(self):
        """Test when all weights are invalid"""
        df = pd.DataFrame({
            'outstanding_balance': [0, 0, 0],
            'apr': [5.0, 6.0, 7.0],
            'eir': [5.1, 6.2, 7.3],
            'term': [360, 240, 180]
        })
        
        result = self.analytics.calculate_weighted_stats(df)
        
        # Should return empty DataFrame when no valid weights
        self.assertTrue(result.empty)

    def test_calculate_weighted_stats_case_insensitive_match(self):
        """Test case-insensitive column matching"""
        df = pd.DataFrame({
            'Outstanding_Balance': [1000, 2000, 3000],
            'APR': [5.0, 6.0, 7.0],
            'EIR': [5.1, 6.2, 7.3],
            'Term': [360, 240, 180]
        })
        
        result = self.analytics.calculate_weighted_stats(df, weight_field='Outstanding_Balance')
        
        # Should match columns case-insensitively
        self.assertFalse(result.empty)
        self.assertIn('weighted_apr', result.columns)

    def test_calculate_weighted_stats_substring_match(self):
        """Test substring matching for columns"""
        df = pd.DataFrame({
            'my_outstanding_balance_field': [1000, 2000, 3000],
            'field_apr_value': [5.0, 6.0, 7.0],
            'eir_field': [5.1, 6.2, 7.3],
            'term_column': [360, 240, 180]
        })
        
        result = self.analytics.calculate_weighted_stats(df, weight_field='my_outstanding_balance_field')
        
        # Should match columns with substrings
        self.assertFalse(result.empty)
        self.assertIn('weighted_apr', result.columns)
        self.assertIn('weighted_eir', result.columns)
        self.assertIn('weighted_term', result.columns)

    def test_calculate_weighted_stats_empty_dataframe(self):
        """Test with empty DataFrame"""
        df = pd.DataFrame()
        
        result = self.analytics.calculate_weighted_stats(df)
        
        # Should return empty DataFrame
        self.assertTrue(result.empty)

    def test_calculate_weighted_stats_single_row(self):
        """Test with single row DataFrame"""
        df = pd.DataFrame({
            'outstanding_balance': [1000],
            'apr': [5.0],
            'eir': [5.1],
            'term': [360]
        })
        
        result = self.analytics.calculate_weighted_stats(df)
        
        # Should return the same values as weighted
        self.assertFalse(result.empty)
        self.assertAlmostEqual(result['weighted_apr'].iloc[0], 5.0, places=6)
        self.assertAlmostEqual(result['weighted_eir'].iloc[0], 5.1, places=6)
        self.assertAlmostEqual(result['weighted_term'].iloc[0], 360, places=6)


if __name__ == '__main__':
    unittest.main()
