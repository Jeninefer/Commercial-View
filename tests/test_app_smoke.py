"""Smoke tests that ensure the FastAPI application imports cleanly."""

from __future__ import annotations

import importlib
from pathlib import Path
import sys

import pandas as pd
import pytest

pytest.importorskip("requests")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src import data_loader


def _write_pricing_csvs(base_dir: Path) -> None:
    base_dir.mkdir(parents=True, exist_ok=True)

    loan_df = pd.DataFrame(
        {
            "Loan ID": ["LN-001"],
            "Customer ID": ["CUST-001"],
            "Customer Name": ["Acme Corp"],
            "Loan Status": ["Current"],
            "Disbursement Amount": [1_000_000],
            "Outstanding Loan Value": [900_000],
            "Interest Rate APR": [0.12],
            "Days in Default": [0],
            "Disbursement Date": ["2024-01-01"],
        }
    )

    payment_df = pd.DataFrame(
        {
            "Loan ID": ["LN-001"],
            "Payment Date": ["2024-02-01"],
            "Total Payment": [50_000],
            "Principal Payment": [45_000],
            "Interest Payment": [5_000],
            "Fee Payment": [0],
            "Tax Payment": [0],
            "Outstanding Loan Value": [855_000],
        }
    )

    historic_df = payment_df.copy()
    historic_df["True Payment Status"] = ["On Time"]

    customer_df = pd.DataFrame(
        {
            "Customer ID": ["CUST-001"],
            "Customer Name": ["Acme Corp"],
        }
    )

    collateral_df = pd.DataFrame(
        {
            "Customer ID": ["CUST-001"],
            "Customer Name": ["Acme Corp"],
            "Loan ID": ["LN-001"],
            "Collateral ID": ["COL-001"],
            "Collateral Original": [500_000],
            "Collateral Current": [480_000],
        }
    )

    datasets = {
        "loan_data": loan_df,
        "payment_schedule": payment_df,
        "historic_real_payment": historic_df,
        "customer_data": customer_df,
        "collateral": collateral_df,
    }

    for dataset_key, dataframe in datasets.items():
        filename = data_loader.PRICING_FILENAMES[dataset_key]
        dataframe.to_csv(base_dir / filename, index=False)


@pytest.mark.parametrize("module_name", ["run"])
def test_fastapi_app_imports_without_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, module_name: str
) -> None:
    pricing_dir = tmp_path / "pricing"
    _write_pricing_csvs(pricing_dir)

    monkeypatch.setenv("COMMERCIAL_VIEW_DATA_PATH", str(pricing_dir))

    module = importlib.import_module(module_name)
    assert hasattr(module, "app"), "FastAPI application should be defined"


@pytest.mark.parametrize("module_name", ["run"])
def test_fastapi_app_startup_smoke(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, module_name: str
) -> None:
    pricing_dir = tmp_path / "pricing"
    _write_pricing_csvs(pricing_dir)

    monkeypatch.setenv("COMMERCIAL_VIEW_DATA_PATH", str(pricing_dir))

    module = importlib.import_module(module_name)
    assert hasattr(module, "startup_event")

    import asyncio

    asyncio.run(module.startup_event())

    try:
        assert "loan_data" in module.datasets
        assert not module.datasets["loan_data"].empty
    finally:
        module.datasets = {}
        module.data_loader = None
