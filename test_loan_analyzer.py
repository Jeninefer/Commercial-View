"""
Tests for the LoanAnalyzer class and calculate_weighted_stats method
"""

import logging
import numpy as np
import pandas as pd
import pytest

from loan_analyzer import LoanAnalyzer


# Configure logging for tests
logging.basicConfig(level=logging.INFO)


class TestCalculateWeightedStats:
    """Test suite for calculate_weighted_stats method"""

    def setup_method(self):
        """Set up test fixtures"""
        self.analyzer = LoanAnalyzer()

    def test_basic_weighted_calculation(self):
        """Test basic weighted average calculation with standard column names"""
        df = pd.DataFrame({
            'outstanding_balance': [1000, 2000, 3000],
            'apr': [5.0, 6.0, 7.0],
            'eir': [5.1, 6.1, 7.1],
            'term': [12, 24, 36]
        })
        
        result = self.analyzer.calculate_weighted_stats(df)
        
        # Expected weighted averages:
        # apr: (1000*5.0 + 2000*6.0 + 3000*7.0) / (1000+2000+3000) = 38000/6000 = 6.333...
        # eir: (1000*5.1 + 2000*6.1 + 3000*7.1) / 6000 = 38600/6000 = 6.433...
        # term: (1000*12 + 2000*24 + 3000*36) / 6000 = 168000/6000 = 28
        
        assert not result.empty
        assert 'weighted_apr' in result.columns
        assert 'weighted_eir' in result.columns
        assert 'weighted_term' in result.columns
        
        assert abs(result['weighted_apr'].iloc[0] - 6.333333) < 0.001
        assert abs(result['weighted_eir'].iloc[0] - 6.433333) < 0.001
        assert abs(result['weighted_term'].iloc[0] - 28.0) < 0.001

    def test_case_insensitive_column_matching(self):
        """Test that column matching is case-insensitive"""
        df = pd.DataFrame({
            'Outstanding_Balance': [1000, 2000],
            'APR': [5.0, 6.0],
            'EIR': [5.1, 6.1],
            'Term': [12, 24]
        })
        
        result = self.analyzer.calculate_weighted_stats(df)
        
        assert not result.empty
        assert 'weighted_apr' in result.columns
        assert 'weighted_eir' in result.columns
        assert 'weighted_term' in result.columns

    def test_alias_matching(self):
        """Test that column aliases are properly matched"""
        df = pd.DataFrame({
            'current_balance': [1000, 2000, 3000],
            'effective_apr': [5.0, 6.0, 7.0],
            'effective_interest_rate': [5.1, 6.1, 7.1],
            'tenor_days': [12, 24, 36]
        })
        
        result = self.analyzer.calculate_weighted_stats(df)
        
        assert not result.empty
        assert 'weighted_apr' in result.columns
        assert 'weighted_eir' in result.columns
        assert 'weighted_term' in result.columns

    def test_spanish_aliases(self):
        """Test that Spanish column aliases work"""
        df = pd.DataFrame({
            'saldo_actual': [1000, 2000],
            'tasa_anual': [5.0, 6.0],
            'tasa_efectiva': [5.1, 6.1],
            'plazo_dias': [12, 24]
        })
        
        result = self.analyzer.calculate_weighted_stats(df)
        
        assert not result.empty
        assert 'weighted_apr' in result.columns
        assert 'weighted_eir' in result.columns
        assert 'weighted_term' in result.columns

    def test_zero_weights_filtered_out(self):
        """Test that zero weights are filtered out"""
        df = pd.DataFrame({
            'outstanding_balance': [0, 1000, 2000],
            'apr': [10.0, 5.0, 6.0],
            'eir': [10.1, 5.1, 6.1],
            'term': [999, 12, 24]
        })
        
        result = self.analyzer.calculate_weighted_stats(df)
        
        # First row with 0 weight should be ignored
        # Expected: (1000*5.0 + 2000*6.0) / 3000 = 17000/3000 = 5.666...
        assert not result.empty
        assert abs(result['weighted_apr'].iloc[0] - 5.666667) < 0.001

    def test_negative_weights_filtered_out(self):
        """Test that negative weights are filtered out"""
        df = pd.DataFrame({
            'outstanding_balance': [-1000, 1000, 2000],
            'apr': [10.0, 5.0, 6.0],
            'eir': [10.1, 5.1, 6.1],
            'term': [999, 12, 24]
        })
        
        result = self.analyzer.calculate_weighted_stats(df)
        
        # First row with negative weight should be ignored
        assert not result.empty
        assert abs(result['weighted_apr'].iloc[0] - 5.666667) < 0.001

    def test_nan_weights_filtered_out(self):
        """Test that NaN weights are filtered out"""
        df = pd.DataFrame({
            'outstanding_balance': [np.nan, 1000, 2000],
            'apr': [10.0, 5.0, 6.0],
            'eir': [10.1, 5.1, 6.1],
            'term': [999, 12, 24]
        })
        
        result = self.analyzer.calculate_weighted_stats(df)
        
        # First row with NaN weight should be ignored
        assert not result.empty
        assert abs(result['weighted_apr'].iloc[0] - 5.666667) < 0.001

    def test_nan_values_filtered_out(self):
        """Test that NaN values in metric columns are filtered out"""
        df = pd.DataFrame({
            'outstanding_balance': [1000, 2000, 3000],
            'apr': [np.nan, 5.0, 6.0],
            'eir': [5.1, 6.1, 7.1],
            'term': [12, 24, 36]
        })
        
        result = self.analyzer.calculate_weighted_stats(df)
        
        # First row should be filtered out for APR
        # Expected APR: (2000*5.0 + 3000*6.0) / 5000 = 28000/5000 = 5.6
        assert not result.empty
        assert abs(result['weighted_apr'].iloc[0] - 5.6) < 0.001
        # EIR should have all three rows
        assert abs(result['weighted_eir'].iloc[0] - 6.433333) < 0.001

    def test_missing_weight_field_returns_empty(self):
        """Test that missing weight field returns empty DataFrame"""
        df = pd.DataFrame({
            'apr': [5.0, 6.0],
            'eir': [5.1, 6.1],
            'term': [12, 24]
        })
        
        result = self.analyzer.calculate_weighted_stats(df, weight_field='nonexistent')
        
        assert result.empty

    def test_weight_field_alternative_detection(self):
        """Test that alternative weight fields are detected"""
        df = pd.DataFrame({
            'olb': [1000, 2000],
            'apr': [5.0, 6.0],
            'eir': [5.1, 6.1],
            'term': [12, 24]
        })
        
        result = self.analyzer.calculate_weighted_stats(df, weight_field='nonexistent')
        
        # Should detect 'olb' as an alternative
        assert not result.empty
        assert 'weighted_apr' in result.columns

    def test_custom_metrics_list(self):
        """Test using custom metrics list"""
        df = pd.DataFrame({
            'outstanding_balance': [1000, 2000],
            'apr': [5.0, 6.0],
            'eir': [5.1, 6.1],
            'term': [12, 24]
        })
        
        result = self.analyzer.calculate_weighted_stats(df, metrics=['apr'])
        
        assert not result.empty
        assert 'weighted_apr' in result.columns
        assert 'weighted_eir' not in result.columns
        assert 'weighted_term' not in result.columns

    def test_missing_metric_column_skipped(self):
        """Test that missing metric columns are skipped gracefully"""
        df = pd.DataFrame({
            'outstanding_balance': [1000, 2000],
            'apr': [5.0, 6.0],
            'term': [12, 24]
        })
        
        result = self.analyzer.calculate_weighted_stats(df)
        
        # EIR should be missing, but others should be present
        assert not result.empty
        assert 'weighted_apr' in result.columns
        assert 'weighted_eir' not in result.columns
        assert 'weighted_term' in result.columns

    def test_all_weights_zero_returns_empty_for_metric(self):
        """Test that all zero weights returns no result for that metric"""
        df = pd.DataFrame({
            'outstanding_balance': [0, 0, 0],
            'apr': [5.0, 6.0, 7.0],
            'eir': [5.1, 6.1, 7.1],
            'term': [12, 24, 36]
        })
        
        result = self.analyzer.calculate_weighted_stats(df)
        
        # Should return empty DataFrame as all weights are 0
        assert result.empty

    def test_empty_dataframe_returns_empty(self):
        """Test that empty input DataFrame returns empty result"""
        df = pd.DataFrame()
        
        result = self.analyzer.calculate_weighted_stats(df)
        
        assert result.empty

    def test_substring_matching_for_columns(self):
        """Test that substring matching works for column names"""
        df = pd.DataFrame({
            'loan_outstanding_balance': [1000, 2000],
            'effective_apr_rate': [5.0, 6.0],
            'current_eir': [5.1, 6.1],
            'loan_term_months': [12, 24]
        })
        
        result = self.analyzer.calculate_weighted_stats(df)
        
        assert not result.empty
        # Should match based on substrings
        assert 'weighted_apr' in result.columns
        assert 'weighted_eir' in result.columns
        assert 'weighted_term' in result.columns

    def test_result_is_dataframe_with_one_row(self):
        """Test that result is a DataFrame with exactly one row"""
        df = pd.DataFrame({
            'outstanding_balance': [1000, 2000, 3000],
            'apr': [5.0, 6.0, 7.0],
            'eir': [5.1, 6.1, 7.1],
            'term': [12, 24, 36]
        })
        
        result = self.analyzer.calculate_weighted_stats(df)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

    def test_original_dataframe_not_modified(self):
        """Test that the original DataFrame is not modified"""
        df = pd.DataFrame({
            'outstanding_balance': [1000, 2000],
            'apr': [5.0, 6.0],
            'eir': [5.1, 6.1],
            'term': [12, 24]
        })
        df_copy = df.copy()
        
        self.analyzer.calculate_weighted_stats(df)
        
        pd.testing.assert_frame_equal(df, df_copy)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
