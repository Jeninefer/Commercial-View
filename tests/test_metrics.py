"""Tests for MetricsCalculator.calculate_weighted_metrics method."""
import logging

import numpy as np
import pandas as pd
import pytest

from commercial_view.metrics import MetricsCalculator


class TestCalculateWeightedMetrics:
    """Test suite for calculate_weighted_metrics method."""

    @pytest.fixture
    def calculator(self):
        """Create a MetricsCalculator instance."""
        return MetricsCalculator()

    @pytest.fixture
    def sample_df(self):
        """Create a sample DataFrame for testing."""
        return pd.DataFrame({
            'outstanding_balance': [100, 200, 300],
            'interest_rate': [5.0, 6.0, 7.0],
            'credit_score': [700, 750, 800]
        })

    def test_basic_weighted_average(self, calculator, sample_df):
        """Test basic weighted average calculation."""
        result = calculator.calculate_weighted_metrics(
            sample_df,
            metrics=['interest_rate'],
            weight_col='outstanding_balance'
        )
        
        # Manual calculation: (100*5 + 200*6 + 300*7) / (100+200+300) = 3800/600 = 6.333...
        expected = (100 * 5.0 + 200 * 6.0 + 300 * 7.0) / (100 + 200 + 300)
        assert 'weighted_interest_rate' in result
        assert abs(result['weighted_interest_rate'] - expected) < 1e-10

    def test_multiple_metrics(self, calculator, sample_df):
        """Test weighted averages for multiple metrics."""
        result = calculator.calculate_weighted_metrics(
            sample_df,
            metrics=['interest_rate', 'credit_score'],
            weight_col='outstanding_balance'
        )
        
        assert 'weighted_interest_rate' in result
        assert 'weighted_credit_score' in result
        assert len(result) == 2

    def test_missing_weight_column(self, calculator, sample_df, caplog):
        """Test behavior when weight column is missing."""
        with caplog.at_level(logging.ERROR):
            result = calculator.calculate_weighted_metrics(
                sample_df,
                metrics=['interest_rate'],
                weight_col='nonexistent_column'
            )
        
        assert result == {}
        assert "Weight column nonexistent_column not found" in caplog.text

    def test_missing_metric_column(self, calculator, sample_df, caplog):
        """Test behavior when a metric column is missing."""
        with caplog.at_level(logging.WARNING):
            result = calculator.calculate_weighted_metrics(
                sample_df,
                metrics=['interest_rate', 'nonexistent_metric'],
                weight_col='outstanding_balance'
            )
        
        assert 'weighted_interest_rate' in result
        assert 'weighted_nonexistent_metric' not in result
        assert "Metric nonexistent_metric not found" in caplog.text

    def test_zero_weights(self, calculator, caplog):
        """Test behavior with zero weights."""
        df = pd.DataFrame({
            'outstanding_balance': [0, 0, 0],
            'interest_rate': [5.0, 6.0, 7.0]
        })
        
        with caplog.at_level(logging.WARNING):
            result = calculator.calculate_weighted_metrics(
                df,
                metrics=['interest_rate'],
                weight_col='outstanding_balance'
            )
        
        assert result == {}
        assert "No valid rows to compute weighted metrics" in caplog.text

    def test_negative_weights_filtered(self, calculator):
        """Test that negative weights are filtered out."""
        df = pd.DataFrame({
            'outstanding_balance': [-100, 200, 300],
            'interest_rate': [5.0, 6.0, 7.0]
        })
        
        result = calculator.calculate_weighted_metrics(
            df,
            metrics=['interest_rate'],
            weight_col='outstanding_balance'
        )
        
        # Should only use rows with positive weights (200 and 300)
        expected = (200 * 6.0 + 300 * 7.0) / (200 + 300)
        assert 'weighted_interest_rate' in result
        assert abs(result['weighted_interest_rate'] - expected) < 1e-10

    def test_nan_weights(self, calculator):
        """Test behavior with NaN weights."""
        df = pd.DataFrame({
            'outstanding_balance': [100, np.nan, 300],
            'interest_rate': [5.0, 6.0, 7.0]
        })
        
        result = calculator.calculate_weighted_metrics(
            df,
            metrics=['interest_rate'],
            weight_col='outstanding_balance'
        )
        
        # Should only use rows without NaN weights (100 and 300)
        expected = (100 * 5.0 + 300 * 7.0) / (100 + 300)
        assert 'weighted_interest_rate' in result
        assert abs(result['weighted_interest_rate'] - expected) < 1e-10

    def test_inf_weights(self, calculator):
        """Test behavior with infinite weights."""
        df = pd.DataFrame({
            'outstanding_balance': [100, np.inf, 300],
            'interest_rate': [5.0, 6.0, 7.0]
        })
        
        result = calculator.calculate_weighted_metrics(
            df,
            metrics=['interest_rate'],
            weight_col='outstanding_balance'
        )
        
        # Should only use rows with finite weights (100 and 300)
        expected = (100 * 5.0 + 300 * 7.0) / (100 + 300)
        assert 'weighted_interest_rate' in result
        assert abs(result['weighted_interest_rate'] - expected) < 1e-10

    def test_nan_metric_values(self, calculator):
        """Test behavior with NaN metric values."""
        df = pd.DataFrame({
            'outstanding_balance': [100, 200, 300],
            'interest_rate': [5.0, np.nan, 7.0]
        })
        
        result = calculator.calculate_weighted_metrics(
            df,
            metrics=['interest_rate'],
            weight_col='outstanding_balance'
        )
        
        # Should only use rows without NaN metric values (100 and 300)
        expected = (100 * 5.0 + 300 * 7.0) / (100 + 300)
        assert 'weighted_interest_rate' in result
        assert abs(result['weighted_interest_rate'] - expected) < 1e-10

    def test_empty_dataframe(self, calculator, caplog):
        """Test behavior with empty DataFrame."""
        df = pd.DataFrame({
            'outstanding_balance': [],
            'interest_rate': []
        })
        
        with caplog.at_level(logging.WARNING):
            result = calculator.calculate_weighted_metrics(
                df,
                metrics=['interest_rate'],
                weight_col='outstanding_balance'
            )
        
        assert result == {}
        assert "No valid rows to compute weighted metrics" in caplog.text

    def test_all_nan_metrics(self, calculator, caplog):
        """Test behavior when all metric values are NaN."""
        df = pd.DataFrame({
            'outstanding_balance': [100, 200, 300],
            'interest_rate': [np.nan, np.nan, np.nan]
        })
        
        with caplog.at_level(logging.WARNING):
            result = calculator.calculate_weighted_metrics(
                df,
                metrics=['interest_rate'],
                weight_col='outstanding_balance'
            )
        
        assert result == {}
        assert "No valid data for interest_rate weighted average" in caplog.text

    def test_custom_weight_column(self, calculator):
        """Test using a custom weight column."""
        df = pd.DataFrame({
            'custom_weight': [50, 100, 150],
            'metric': [10.0, 20.0, 30.0]
        })
        
        result = calculator.calculate_weighted_metrics(
            df,
            metrics=['metric'],
            weight_col='custom_weight'
        )
        
        expected = (50 * 10.0 + 100 * 20.0 + 150 * 30.0) / (50 + 100 + 150)
        assert 'weighted_metric' in result
        assert abs(result['weighted_metric'] - expected) < 1e-10

    def test_mixed_valid_invalid_rows(self, calculator):
        """Test with a mix of valid and invalid rows."""
        df = pd.DataFrame({
            'outstanding_balance': [100, 0, np.nan, -50, 200, np.inf],
            'interest_rate': [5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        })
        
        result = calculator.calculate_weighted_metrics(
            df,
            metrics=['interest_rate'],
            weight_col='outstanding_balance'
        )
        
        # Should only use rows with valid weights (100 and 200)
        expected = (100 * 5.0 + 200 * 9.0) / (100 + 200)
        assert 'weighted_interest_rate' in result
        assert abs(result['weighted_interest_rate'] - expected) < 1e-10

    def test_result_is_float(self, calculator, sample_df):
        """Test that result values are Python floats."""
        result = calculator.calculate_weighted_metrics(
            sample_df,
            metrics=['interest_rate'],
            weight_col='outstanding_balance'
        )
        
        assert isinstance(result['weighted_interest_rate'], float)
        # Ensure it's not a numpy float
        assert type(result['weighted_interest_rate']).__module__ == 'builtins'
