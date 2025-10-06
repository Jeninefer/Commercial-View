"""Robust data loading utilities for Commercial View ETL pipeline."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Iterable, Optional, Union

import pandas as pd

PathLike = Union[str, Path]

DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent / "data"

PRICING_FILENAMES: Dict[str, str] = {
    "loan_data": "loan_data.csv",
    "historic_real_payment": "historic_real_payment.csv",
    "payment_schedule": "payment_schedule.csv",
    "customer_data": "customer_data.csv",
    "collateral": "collateral.csv",
    "targets": "Q4_Targets.csv",
}

EXPECTED_SCHEMAS: Dict[str, Iterable[str]] = {
    "loan_data": (
        "Loan ID",
        "Customer ID",
        "Disbursement Date",
        "Disbursement Amount",
        "Outstanding Loan Value",
        "Days in Default",
        "Interest Rate APR",
    ),
    "historic_real_payment": (
        "Loan ID",
        "True Payment Date",
        "True Principal Payment",
        "True Interest Payment",
    ),
    "payment_schedule": (
        "Loan ID",
        "Due Date",
        "Scheduled Principal",
        "Scheduled Interest",
        "Total Payment",
    ),
    "targets": (
        "Metric",
        "Target Value",
        "Owner",
        "Due Date",
    ),
}


def _resolve_base_path(base: Optional[PathLike] = None) -> Path:
    """Resolve the base directory containing CSV datasets."""
    if base is None:
        env_path = os.getenv("COMMERCIAL_VIEW_DATA_PATH")
        path = Path(env_path).expanduser() if env_path else DEFAULT_DATA_DIR
    else:
        path = Path(base).expanduser()

    if not path.exists():
        raise FileNotFoundError(f"Base path {path} not found")

    return path.resolve()


def _dataset_path(base_or_file: Optional[PathLike], dataset: str) -> Path:
    """Return the CSV path for the requested dataset."""
    if dataset not in PRICING_FILENAMES:
        raise KeyError(f"Unknown dataset '{dataset}'")

    if base_or_file is None:
        env_path = os.getenv("COMMERCIAL_VIEW_DATA_PATH")
        if env_path:
            env_candidate = Path(env_path)
            if env_candidate.is_dir():
                candidate = env_candidate / PRICING_FILENAMES[dataset]
            else:
                candidate = env_candidate
        else:
            candidate = DEFAULT_DATA_DIR / PRICING_FILENAMES[dataset]
    else:
        resolved = Path(base_or_file)
        if resolved.is_dir():
            candidate = resolved / PRICING_FILENAMES[dataset]
        else:
            candidate = resolved

    if not candidate.exists():
        raise FileNotFoundError(
            f"Expected {dataset.replace('_', ' ')} dataset at {candidate} but the file does not exist."
        )

    return candidate.resolve()


def _read_csv(path: PathLike) -> pd.DataFrame:
    """Read a CSV file into a DataFrame with UTF-8 fallback."""
    try:
        return pd.read_csv(path)
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="latin-1")


def _validate_schema(df: pd.DataFrame, dataset: str) -> None:
    """Ensure DataFrame contains the expected columns for the dataset."""
    expected = set(EXPECTED_SCHEMAS.get(dataset, ()))
    if not expected:
        return

    missing = expected.difference(df.columns)
    if missing:
        formatted = ", ".join(sorted(missing))
        raise ValueError(
            f"{dataset.replace('_', ' ').title()} dataset is missing required columns: {formatted}"
        )


def _load_dataset(dataset: str, base_path: Optional[PathLike] = None) -> pd.DataFrame:
    """Generic loader that applies path resolution and schema validation."""
    csv_path = _dataset_path(base_path, dataset)
    dataframe = _read_csv(csv_path)
    _validate_schema(dataframe, dataset)
    return dataframe


def load_loan_data(base_path: Optional[PathLike] = None) -> pd.DataFrame:
    """Load the loan data dataset.

    Args:
        base_path: Optional path to the directory or file containing the dataset.

    Returns:
        pd.DataFrame: DataFrame containing loan data.
    """
    return _load_dataset("loan_data", base_path)


def load_historic_real_payment(base_path: Optional[PathLike] = None) -> pd.DataFrame:
    """Load the historic real payment dataset.

    Args:
        base_path: Optional path to the directory or file containing the dataset.

    Returns:
        pd.DataFrame: DataFrame containing historic real payment data.
    """
    return _load_dataset("historic_real_payment", base_path)


def load_payment_schedule(base_path: Optional[PathLike] = None) -> pd.DataFrame:
    """Load the payment schedule dataset.

    Args:
        base_path: Optional path to the directory or file containing the dataset.

    Returns:
        pd.DataFrame: DataFrame containing payment schedule data.
    """
    return _load_dataset("payment_schedule", base_path)


def load_customer_data(base_path: Optional[PathLike] = None) -> pd.DataFrame:
    """Load the customer data dataset.

    Args:
        base_path: Optional path to the directory or file containing the dataset.

    Returns:
        pd.DataFrame: DataFrame containing customer data.
    """
    return _load_dataset("customer_data", base_path)


def load_collateral(base_path: Optional[PathLike] = None) -> pd.DataFrame:
    """Load the collateral dataset.

    Args:
        base_path: Optional path to the directory or file containing the dataset.

    Returns:
        pd.DataFrame: DataFrame containing collateral data.
    """
    return _load_dataset("collateral", base_path)


def load_targets(base_path: Optional[PathLike] = None) -> pd.DataFrame:
    """Load the targets dataset.

    Args:
        base_path: Optional path to the directory or file containing the dataset.

    Returns:
        pd.DataFrame: DataFrame containing targets data.
    """
    return _load_dataset("targets", base_path)
__all__ = [
    "load_loan_data",
    "load_historic_real_payment",
    "load_payment_schedule",
    "load_customer_data",
    "load_collateral",
    "load_targets",
    "_resolve_base_path",
    "PRICING_FILENAMES",
    "EXPECTED_SCHEMAS",
]
