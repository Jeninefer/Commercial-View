"""Integration tests that exercise the CommercialViewPipeline orchestration."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Dict, Tuple

import pandas as pd
import pytest


def _bootstrap_pipeline(monkeypatch: pytest.MonkeyPatch) -> Tuple[object, Dict[str, int], pd.DataFrame, pd.DataFrame]:
    """Prepare the pipeline module with patched data loaders for deterministic runs."""

    import src.data_loader as data_loader

    calls: Dict[str, int] = {}

    loan_df = pd.DataFrame(
        {
            "Loan ID": [1, 2, 3],
            "Outstanding Loan Value": [1000.0, 500.0, 200.0],
            "Days in Default": [0, 45, 190],
            "Customer ID": ["A", "B", "C"],
            "Interest Rate APR": [0.12, 0.15, 0.2],
            "Disbursement Date": ["2024-01-01", "2024-02-01", "2024-03-01"],
            "Disbursement Amount": [1000.0, 500.0, 200.0],
        }
    )
    loan_df["Disbursement Date"] = pd.to_datetime(loan_df["Disbursement Date"])

    payment_df = pd.DataFrame(
        {
            "Loan ID": [1, 1, 2],
            "True Payment Date": ["2024-02-01", "2024-03-01", "2024-03-15"],
            "True Principal Payment": [200.0, 300.0, 100.0],
        }
    )
    payment_df["True Payment Date"] = pd.to_datetime(payment_df["True Payment Date"])

    customer_df = pd.DataFrame({"customer_id": ["A", "B"]})

    def make_loader(name: str, frame: pd.DataFrame, error: Exception | None = None):
        def _loader(base_path: Path | None = None) -> pd.DataFrame:
            calls[name] = calls.get(name, 0) + 1
            if error is not None:
                raise error
            return frame.copy()

        return _loader

    monkeypatch.setattr(data_loader, "load_loan_data", make_loader("loan_data", loan_df))
    monkeypatch.setattr(data_loader, "load_historic_real_payment", make_loader("historic_real_payment", payment_df))
    monkeypatch.setattr(
        data_loader,
        "load_payment_schedule",
        make_loader("payment_schedule", pd.DataFrame(), error=FileNotFoundError("missing schedule")),
    )
    monkeypatch.setattr(data_loader, "load_customer_data", make_loader("customer_data", customer_df))
    monkeypatch.setattr(
        data_loader,
        "load_collateral",
        make_loader("collateral", pd.DataFrame(), error=FileNotFoundError("missing collateral")),
    )

    import src.pipeline
    importlib.reload(src.pipeline)
    pipeline = src.pipeline

    return pipeline, calls, loan_df, payment_df


def test_pipeline_load_all_datasets_handles_missing_sources(monkeypatch: pytest.MonkeyPatch) -> None:
    pipeline, calls, _, _ = _bootstrap_pipeline(monkeypatch)

    instance = pipeline.CommercialViewPipeline(base_path=Path("/tmp"))
    datasets = instance.load_all_datasets()

    assert {"loan_data", "historic_real_payment", "payment_schedule", "customer_data", "collateral"} == set(
        datasets.keys()
    )
    assert calls["loan_data"] == 1
    assert datasets["payment_schedule"].empty
    assert datasets["collateral"].empty


def test_pipeline_compute_dpd_metrics_creates_expected_columns(monkeypatch: pytest.MonkeyPatch) -> None:
    pipeline, _, loan_df, _ = _bootstrap_pipeline(monkeypatch)

    instance = pipeline.CommercialViewPipeline()
    instance._datasets["loan_data"] = loan_df.copy()

    dpd_metrics = instance.compute_dpd_metrics()

    assert set(["dpd_bucket", "past_due_amount", "is_default", "reference_date"]).issubset(dpd_metrics.columns)
    assert (dpd_metrics.loc[dpd_metrics["Loan ID"] == 3, "is_default"]).item() is True


def test_pipeline_compute_portfolio_metrics_returns_scalar_summary(monkeypatch: pytest.MonkeyPatch) -> None:
    pipeline, _, loan_df, _ = _bootstrap_pipeline(monkeypatch)

    instance = pipeline.CommercialViewPipeline()
    instance._datasets["loan_data"] = loan_df.copy()

    metrics = instance.compute_portfolio_metrics()

    assert metrics["portfolio_outstanding"] == pytest.approx(1700.0)
    assert metrics["active_clients"] == 3
    assert "dpd_distribution" in metrics


def test_pipeline_compute_recovery_metrics_builds_cohort_summary(monkeypatch: pytest.MonkeyPatch) -> None:
    pipeline, _, loan_df, payment_df = _bootstrap_pipeline(monkeypatch)

    instance = pipeline.CommercialViewPipeline()
    instance._datasets["loan_data"] = loan_df.copy()
    instance._datasets["historic_real_payment"] = payment_df.copy()

    recovery = instance.compute_recovery_metrics()

    assert not recovery.empty
    assert set(["cohort", "months_since_disbursement", "recovery_pct"]).issubset(recovery.columns)


def test_pipeline_generate_executive_summary_includes_data_quality(monkeypatch: pytest.MonkeyPatch) -> None:
    pipeline, _, loan_df, payment_df = _bootstrap_pipeline(monkeypatch)

    instance = pipeline.CommercialViewPipeline()
    instance._datasets["loan_data"] = loan_df.copy()
    instance._datasets["historic_real_payment"] = payment_df.copy()

    summary = instance.generate_executive_summary()

    assert "portfolio_overview" in summary
    assert summary["data_quality"]["datasets_loaded"] >= 1
