"""Tests covering AI-powered services such as feature engineering and optimizers."""

from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd

from src.feature_engineer import FeatureEngineer
from src.field_detector import FieldDetector
from src.portfolio_optimizer import PortfolioOptimizer


def test_feature_engineer_classifies_new_customer_when_single_loan() -> None:
    engineer = FeatureEngineer()
    frame = pd.DataFrame({"customer_id": [1], "loan_count": [1], "last_active_date": ["2024-01-01"]})

    result = engineer.classify_client_type(frame)

    assert result.loc[0, "customer_type"] == FeatureEngineer.CUSTOMER_TYPES["NEW"]


def test_feature_engineer_classifies_recovered_after_long_gap() -> None:
    engineer = FeatureEngineer()
    reference = datetime(2024, 6, 1)
    frame = pd.DataFrame(
        {
            "customer_id": [1],
            "loan_count": [3],
            "last_active_date": [(reference - timedelta(days=200)).strftime("%Y-%m-%d")],
        }
    )

    result = engineer.classify_client_type(frame, reference_date=reference)

    assert result.loc[0, "customer_type"] == FeatureEngineer.CUSTOMER_TYPES["RECOVERED"]


def test_feature_engineer_defaults_to_recurrent_with_recent_activity() -> None:
    engineer = FeatureEngineer()
    reference = datetime(2024, 6, 1)
    frame = pd.DataFrame(
        {
            "customer_id": [1],
            "loan_count": [4],
            "last_active_date": [(reference - timedelta(days=30)).strftime("%Y-%m-%d")],
        }
    )

    result = engineer.classify_client_type(frame, reference_date=reference)

    assert result.loc[0, "customer_type"] == FeatureEngineer.CUSTOMER_TYPES["RECURRENT"]


def test_feature_engineer_handles_missing_last_active_column() -> None:
    engineer = FeatureEngineer()
    frame = pd.DataFrame({"customer_id": [1], "loan_count": [2]})

    result = engineer.classify_client_type(frame)

    assert result.loc[0, "customer_type"] == FeatureEngineer.CUSTOMER_TYPES["RECURRENT"]
    assert "days_since_last" in result.columns


def test_field_detector_identifies_payment_and_total_columns() -> None:
    detector = FieldDetector()
    frame = pd.DataFrame(columns=["True_Payment_Date", "total_paid", "other"])

    detected = detector.detect_payment_fields(frame)

    assert detected["payment_date"] == "True_Payment_Date"
    assert detected["total_payment"] == "total_paid"


def test_field_detector_returns_empty_when_no_match_found() -> None:
    detector = FieldDetector()
    frame = pd.DataFrame(columns=["foo", "bar"])

    assert detector.detect_payment_fields(frame) == {}


def test_portfolio_optimizer_flags_concentration_risk() -> None:
    optimizer = PortfolioOptimizer()
    frame = pd.DataFrame(
        {
            "customer_id": ["A", "A", "B"],
            "outstanding_balance": [80, 60, 10],
        }
    )

    result = optimizer.optimize(frame)

    assert any("High concentration risk" in alert for alert in result["risk_alerts"])


def test_portfolio_optimizer_returns_empty_alerts_when_safe() -> None:
    optimizer = PortfolioOptimizer()
    frame = pd.DataFrame(
        {
            "customer_id": ["A", "B", "C", "D", "E"],
            "outstanding_balance": [20, 20, 20, 20, 20],
        }
    )

    result = optimizer.optimize(frame)

    assert result["risk_alerts"] == []


def test_portfolio_optimizer_generate_alerts_for_high_dpd() -> None:
    optimizer = PortfolioOptimizer()
    frame = pd.DataFrame(
        {
            "loan_id": [1, 2, 3],
            "days_past_due": [10, 200, 95],
        }
    )

    alerts = optimizer.generate_alerts(frame)

    assert alerts[0]["type"] == "DPD_ALERT"
    assert alerts[0]["count"] == 2


def test_portfolio_optimizer_generate_alerts_returns_empty_for_clean_portfolio() -> None:
    optimizer = PortfolioOptimizer()
    frame = pd.DataFrame({"loan_id": [1], "days_past_due": [5]})

    assert optimizer.generate_alerts(frame) == []
