"""Tests for data ingestion utilities covering file discovery and processing."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src import data_loader
from src.data_processor import DataProcessor


def test_load_loan_data_from_explicit_file(tmp_path: Path) -> None:
    csv_path = tmp_path / "loan_data.csv"
    df = pd.DataFrame({"loan_id": [1, 2], "value": [100, 200]})
    df.to_csv(csv_path, index=False)

    loaded = data_loader.load_loan_data(csv_path)

    assert list(loaded.columns) == ["loan_id", "value"]
    assert loaded.shape == (2, 2)


def test_load_loan_data_prefers_loan_named_files(tmp_path: Path) -> None:
    (tmp_path / "nested").mkdir()
    generic_path = tmp_path / "nested" / "data.csv"
    loan_path = tmp_path / "loan-book.csv"
    pd.DataFrame({"id": [1]}).to_csv(generic_path, index=False)
    pd.DataFrame({"loan_id": [99]}).to_csv(loan_path, index=False)

    loaded = data_loader.load_loan_data(tmp_path)

    assert "loan_id" in loaded.columns
    assert loaded.iloc[0, 0] == 99


def test_load_loan_data_without_csv_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        data_loader.load_loan_data(tmp_path)


def test_load_historic_real_payment_missing_file_returns_empty_dataframe(tmp_path: Path) -> None:
    missing_file = tmp_path / "missing.csv"

    result = data_loader.load_historic_real_payment(str(missing_file))

    assert result.empty
    assert set(result.columns) == {
        "loan_id",
        "payment_date",
        "payment_amount",
        "principal_amount",
        "interest_amount",
        "payment_type",
    }


def test_load_historic_real_payment_reads_contents(tmp_path: Path) -> None:
    csv_path = tmp_path / "historic.csv"
    frame = pd.DataFrame(
        {
            "loan_id": [1],
            "payment_date": ["2024-01-01"],
            "payment_amount": [100.0],
            "principal_amount": [80.0],
            "interest_amount": [20.0],
            "payment_type": ["regular"],
        }
    )
    frame.to_csv(csv_path, index=False)

    result = data_loader.load_historic_real_payment(str(csv_path))

    assert result.equals(frame)


def test_convert_dates_safely_parses_multiple_formats() -> None:
    processor = DataProcessor()
    frame = pd.DataFrame(
        {
            "payment_date": ["2024-01-05", "2024/02/05"],
            "due_date": ["2024-02-05", "2024/06/02"],
            "other": [1, 2],
        }
    )

    converted = processor.convert_dates_safely(frame, ["payment_date", "due_date"])

    assert pd.api.types.is_datetime64_any_dtype(converted["payment_date"])
    assert converted["payment_date"].notna().sum() >= 1


def test_convert_dates_safely_ignores_missing_columns() -> None:
    processor = DataProcessor()
    frame = pd.DataFrame({"other": [1]})

    converted = processor.convert_dates_safely(frame, ["missing_col"])

    assert converted.equals(frame)


def test_process_loan_schedules_coerces_payment_amounts_to_numeric() -> None:
    processor = DataProcessor()
    frame = pd.DataFrame(
        {
            "payment_date": ["2024-01-01"],
            "due_date": ["2024-01-10"],
            "payment_amount": ["1,000"],
        }
    )

    processed = processor.process_loan_schedules(frame)

    assert pd.api.types.is_numeric_dtype(processed["payment_amount"])
    assert processed.loc[0, "payment_amount"] == pytest.approx(1000.0)
