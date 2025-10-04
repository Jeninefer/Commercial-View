"""Utilities for loading data files used throughout the application."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Union

import pandas as pd
from pandas import DataFrame


ENV_VAR_NAME = "COMMERCIAL_VIEW_DATA_PATH"
DEFAULT_BASE_PATH = Path(__file__).resolve().parents[1] / "data" / "pricing"


def _resolve_base_path(base_path: Optional[Union[str, Path]] = None) -> Path:
    """Return the directory that contains the source CSV files.

    The resolution order is:
    1. Explicit ``base_path`` argument.
    2. ``COMMERCIAL_VIEW_DATA_PATH`` environment variable.
    3. Repository-relative default ``data/pricing`` directory.
    """

    if base_path is not None:
        return Path(base_path)

    env_value = os.getenv(ENV_VAR_NAME)
    if env_value:
        return Path(env_value)

    return DEFAULT_BASE_PATH


def _read_csv(filename: str, base_path: Optional[Union[str, Path]] = None) -> DataFrame:
    """Read a CSV file from the configured base path.

    Raises:
        FileNotFoundError: If the resolved CSV file does not exist.
    """

    directory = _resolve_base_path(base_path)
    file_path = directory / filename

    if not file_path.exists():
        raise FileNotFoundError(
            f"""CSV file not found: {file_path}. Configure the data directory using the
`{ENV_VAR_NAME}` environment variable or pass a `base_path` argument."""
        )

    return pd.read_csv(file_path)


def load_loan_data(base_path: Optional[Union[str, Path]] = None) -> DataFrame:
    """Load the loan data CSV file."""

    return _read_csv("Abaco - Loan Tape_Loan Data_Table.csv", base_path)


def load_historic_real_payment(base_path: Optional[Union[str, Path]] = None) -> DataFrame:
    """Load the historic real payment CSV file."""

    return _read_csv("Abaco - Loan Tape_Historic Real Payment_Table.csv", base_path)


def load_payment_schedule(base_path: Optional[Union[str, Path]] = None) -> DataFrame:
    """Load the payment schedule CSV file."""

    return _read_csv("Abaco - Loan Tape_Payment Schedule_Table.csv", base_path)


def load_customer_data(base_path: Optional[Union[str, Path]] = None) -> DataFrame:
    """Load the customer data CSV file."""

    return _read_csv("Abaco - Loan Tape_Customer Data_Table.csv", base_path)


def load_collateral(base_path: Optional[Union[str, Path]] = None) -> DataFrame:
    """Load the collateral CSV file."""

    return _read_csv("Abaco - Loan Tape_Collateral_Table.csv", base_path)