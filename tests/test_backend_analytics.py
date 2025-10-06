"""Backend analytics unit tests covering customer and loan metrics."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from src.customer_analytics import CustomerAnalytics
from src.loan_analytics import LoanAnalytics


def test_customer_dpd_stats_missing_columns_returns_empty_dataframe() -> None:
    analytics = CustomerAnalytics()
    dpd_df = pd.DataFrame({"loan_id": [1], "value": [5]})
    loan_df = pd.DataFrame({"loan_id": [1], "customer_code": ["C-1"]})

    result = analytics.calculate_customer_dpd_stats(
        dpd_df, loan_df, customer_id_field="customer_id"
    )

    assert result.empty


def test_customer_dpd_stats_computes_summary_columns() -> None:
    analytics = CustomerAnalytics()
    dpd_df = pd.DataFrame(
        {
            "loan_id": [1, 1, 2, 2],
            "days_past_due": [10, 20, 0, 0],
        }
    )
    loan_df = pd.DataFrame(
        {
            "loan_id": [1, 2],
            "customer_id": ["A", "B"],
        }
    )

    result = analytics.calculate_customer_dpd_stats(
        dpd_df, loan_df, customer_id_field="customer_id"
    ).sort_values("customer_id").reset_index(drop=True)

    expected = pd.DataFrame(
        {
            "customer_id": ["A", "B"],
            "dpd_mean": [15.0, 0.0],
            "dpd_median": [15.0, 0.0],
            "dpd_max": [20.0, 0.0],
            "dpd_min": [10.0, 0.0],
            "dpd_count": [2.0, 2.0],
        }
    )

    assert_frame_equal(result, expected, check_dtype=False)


def test_customer_dpd_stats_drops_null_dpd_values() -> None:
    analytics = CustomerAnalytics()
    dpd_df = pd.DataFrame(
        {
            "loan_id": [1, 1, 2],
            "days_past_due": [np.nan, 30, 45],
        }
    )
    loan_df = pd.DataFrame(
        {
            "loan_id": [1, 2],
            "customer_id": ["A", "B"],
        }
    )

    result = analytics.calculate_customer_dpd_stats(
        dpd_df, loan_df, customer_id_field="customer_id"
    )

    assert (result.loc[result["customer_id"] == "A", "dpd_count"] == 1).all()


def test_customer_dpd_stats_handles_unmatched_loans_safely() -> None:
    analytics = CustomerAnalytics()
    dpd_df = pd.DataFrame(
        {
            "loan_id": [1, 2, 3],
            "days_past_due": [5, 15, 25],
        }
    )
    loan_df = pd.DataFrame(
        {
            "loan_id": [1, 2],
            "customer_id": ["A", "B"],
        }
    )

    result = analytics.calculate_customer_dpd_stats(
        dpd_df, loan_df, customer_id_field="customer_id"
    )

    # Loan 3 has no customer mapping and should be excluded via the left join
    assert set(result["customer_id"]) == {"A", "B"}


def test_loan_analytics_returns_empty_when_weight_column_missing() -> None:
    analytics = LoanAnalytics()
    loan_df = pd.DataFrame(
        {
            "apr": [0.1, 0.12],
            "term": [12, 24],
        }
    )

    result = analytics.calculate_weighted_stats(loan_df)
    assert result.empty


def test_loan_analytics_detects_weight_alias_column() -> None:
    analytics = LoanAnalytics()
    loan_df = pd.DataFrame(
        {
            "APR": [0.1, 0.3],
            "OLB": [1000, 500],
            "term": [12, 6],
        }
    )

    result = analytics.calculate_weighted_stats(loan_df)
    assert result.iloc[0]["weighted_apr"] == pytest.approx(0.1666666667, rel=1e-6)


def test_loan_analytics_resolves_metric_aliases_for_weighted_calculation() -> None:
    analytics = LoanAnalytics()
    loan_df = pd.DataFrame(
        {
            "annual_rate": [0.1, 0.2, 0.3],
            "effective_interest_rate": [0.09, 0.18, 0.27],
            "tenor_days": [180, 360, 540],
            "outstanding_balance": [100, 200, 700],
        }
    )

    result = analytics.calculate_weighted_stats(loan_df)

    assert set(result.columns) == {
        "weighted_apr",
        "weighted_eir",
        "weighted_term",
    }
    # Calculate expected weighted_eir based on the test data
    expected_weighted_eir = (
        (loan_df["effective_interest_rate"] * loan_df["outstanding_balance"]).sum()
        / loan_df["outstanding_balance"].sum()
    )
    assert result.iloc[0]["weighted_eir"] == pytest.approx(expected_weighted_eir, rel=1e-9)


def test_loan_analytics_honours_custom_metric_subset() -> None:
    analytics = LoanAnalytics()
    loan_df = pd.DataFrame(
        {
            "apr": [0.1, 0.2],
            "term": [12, 24],
            "outstanding_balance": [1000, 1000],
        }
    )

    result = analytics.calculate_weighted_stats(loan_df, metrics=["term"])

    assert list(result.columns) == ["weighted_term"]
    assert result.iloc[0]["weighted_term"] == pytest.approx(18.0)
