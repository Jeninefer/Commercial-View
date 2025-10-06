"""Tests for data loading and validation utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd
import pytest

from src.data_loader import (
    EXPECTED_SCHEMAS,
    PRICING_FILENAMES,
    _resolve_base_path,
    load_historic_real_payment,
    load_loan_data,
    load_payment_schedule,
    load_targets,
)


@pytest.fixture
def dataset_payloads() -> Dict[str, pd.DataFrame]:
    """Provide in-memory DataFrames aligned with the documented schemas."""
    return {
        "loan_data": pd.DataFrame(
            [
                {
                    "Loan ID": "L-9001",
                    "Customer ID": "C-9001",
                    "Disbursement Date": "2023-01-01",
                    "Disbursement Amount": 100000,
                    "Outstanding Loan Value": 85000,
                    "Days in Default": 0,
                    "Interest Rate APR": 9.75,
                }
            ]
        ),
        "historic_real_payment": pd.DataFrame(
            [
                {
                    "Loan ID": "L-9001",
                    "True Payment Date": "2023-02-01",
                    "True Principal Payment": 5000,
                    "True Interest Payment": 420,
                }
            ]
        ),
        "payment_schedule": pd.DataFrame(
            [
                {
                    "Loan ID": "L-9001",
                    "Due Date": "2023-02-15",
                    "Scheduled Principal": 5200,
                    "Scheduled Interest": 380,
                    "Total Payment": 5580,
                }
            ]
        ),
        "targets": pd.DataFrame(
            [
                {
                    "Metric": "Portfolio Outstanding",
                    "Target Value": 125_000_000,
                    "Owner": "Director of Portfolio Management",
                    "Due Date": "2023-12-31",
                }
            ]
        ),
    }


@pytest.fixture
def populated_tmpdir(tmp_path: Path, dataset_payloads: Dict[str, pd.DataFrame]) -> Path:
    """Create a temporary directory populated with valid CSV datasets."""
    for key, frame in dataset_payloads.items():
        filename = PRICING_FILENAMES[key]
        frame.to_csv(tmp_path / filename, index=False)
    return tmp_path


def test_default_sample_datasets_load_successfully(monkeypatch):
    """Ensure bundled sanitized datasets are readable and well-formed."""
    monkeypatch.delenv("COMMERCIAL_VIEW_DATA_PATH", raising=False)

    loan_df = load_loan_data()
    schedule_df = load_payment_schedule()
    payment_df = load_historic_real_payment()
    targets_df = load_targets()

    assert set(EXPECTED_SCHEMAS["loan_data"]).issubset(loan_df.columns)
    assert set(EXPECTED_SCHEMAS["payment_schedule"]).issubset(schedule_df.columns)
    assert set(EXPECTED_SCHEMAS["historic_real_payment"]).issubset(payment_df.columns)
    assert set(EXPECTED_SCHEMAS["targets"]).issubset(targets_df.columns)


def test_missing_dataset_raises_file_not_found(tmp_path: Path):
    """Loading from an empty directory should fail with a descriptive error."""
    with pytest.raises(FileNotFoundError) as excinfo:
        load_loan_data(tmp_path)
    assert "loan data" in str(excinfo.value).lower()


def test_schema_validation_error(tmp_path: Path, dataset_payloads: Dict[str, pd.DataFrame]):
    """Missing mandatory columns trigger a ValueError with column details."""
    invalid = dataset_payloads["historic_real_payment"].drop(columns=["True Principal Payment"])
    invalid.to_csv(tmp_path / PRICING_FILENAMES["historic_real_payment"], index=False)

    with pytest.raises(ValueError) as excinfo:
        load_historic_real_payment(tmp_path)

    message = str(excinfo.value)
    assert "True Principal Payment" in message
    assert "Historic Real Payment" in message


def test_direct_file_path_supported(tmp_path: Path, dataset_payloads: Dict[str, pd.DataFrame]):
    """Passing a CSV file path directly should be supported for ad-hoc loads."""
    file_path = tmp_path / "custom_schedule.csv"
    dataset_payloads["payment_schedule"].to_csv(file_path, index=False)

    loaded = load_payment_schedule(file_path)
    assert loaded.equals(dataset_payloads["payment_schedule"])  # preserves schema and values


def test_resolve_base_path_honors_environment(monkeypatch, populated_tmpdir: Path):
    """_resolve_base_path should prioritise the COMMERCIAL_VIEW_DATA_PATH override."""
    monkeypatch.setenv("COMMERCIAL_VIEW_DATA_PATH", str(populated_tmpdir))

    resolved = _resolve_base_path()
    assert resolved == populated_tmpdir.resolve()


def test_targets_loader_reads_from_env_override(monkeypatch, populated_tmpdir: Path):
    """load_targets should pick up CSVs stored in a custom directory."""
    monkeypatch.setenv("COMMERCIAL_VIEW_DATA_PATH", str(populated_tmpdir))

    targets_df = load_targets()
    assert not targets_df.empty
    assert set(EXPECTED_SCHEMAS["targets"]).issubset(targets_df.columns)
