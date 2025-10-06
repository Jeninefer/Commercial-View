"""Unit tests for the metrics calculator utilities."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.metrics_calculator import MetricsCalculator


def test_weighted_metrics_happy_path() -> None:
    calculator = MetricsCalculator()
    df = pd.DataFrame(
        {
            "outstanding_balance": [100, 200, 300],
            "apr": [0.1, 0.12, 0.2],
            "term": [12, 18, 24],
        }
    )

    result = calculator.calculate_weighted_metrics(df, ["apr", "term"])

    assert set(result.keys()) == {"weighted_apr", "weighted_term"}
    assert result["weighted_apr"] == pytest.approx(0.1566666667)
    assert result["weighted_term"] == pytest.approx(20.0)


def test_weighted_metrics_missing_weight_column_returns_empty() -> None:
    calculator = MetricsCalculator()
    df = pd.DataFrame({"apr": [0.1], "term": [12]})

    result = calculator.calculate_weighted_metrics(df, ["apr"])

    assert result == {}


def test_weighted_metrics_skips_missing_metric_columns() -> None:
    calculator = MetricsCalculator()
    df = pd.DataFrame(
        {
            "outstanding_balance": [100, 0, 50],
            "apr": [0.1, 0.15, np.nan],
        }
    )

    result = calculator.calculate_weighted_metrics(df, ["apr", "term"])

    assert set(result.keys()) == {"weighted_apr"}
    assert result["weighted_apr"] == pytest.approx(0.1)


def test_safe_division_handles_scalar_zero() -> None:
    calculator = MetricsCalculator()

    assert calculator.safe_division(10, 0, default=0.0) == 0.0
    assert calculator.safe_division(10, 2, default=0.0) == 5.0


def test_safe_division_handles_array_inputs_with_invalid_values() -> None:
    calculator = MetricsCalculator()

    numerator = pd.Series([10, 20, "bad"])
    denominator = pd.Series([2, 0, 4])

    result = calculator.safe_division(numerator, denominator, default=-1)

    assert list(result) == [5.0, -1, -1]
