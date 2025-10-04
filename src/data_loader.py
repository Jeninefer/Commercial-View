"""Utilities for loading pricing-related CSV data."""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional, Type, TypeVar, Union

import pandas as pd
from pandas import DataFrame
from pydantic import BaseModel

PathLike = Union[str, os.PathLike[str]]

_ENV_VAR = "COMMERCIAL_VIEW_PRICING_PATH"
_REPO_ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_DATA_PATH = _REPO_ROOT / "data" / "pricing"

PRICING_FILENAMES = {
    "loan_data": "Abaco - Loan Tape_Loan Data_Table.csv",
    "historic_real_payment": "Abaco - Loan Tape_Historic Real Payment_Table.csv",
    "payment_schedule": "Abaco - Loan Tape_Payment Schedule_Table.csv",
    "customer_data": "Abaco - Loan Tape_Customer Data_Table.csv",
    "collateral": "Abaco - Loan Tape_Collateral_Table.csv",
}


def _resolve_base_path(base_path: Optional[PathLike] = None) -> Path:
    """Resolve the directory containing pricing data.

    The priority for resolving the base path is:
      1. Explicit ``base_path`` argument provided to the loader.
      2. The ``COMMERCIAL_VIEW_PRICING_PATH`` environment variable.
      3. The repository default ``data/pricing`` directory.
    """

    if base_path is not None:
        candidate = Path(base_path)
    else:
        env_override = os.getenv(_ENV_VAR)
        candidate = Path(env_override) if env_override else _DEFAULT_DATA_PATH

    candidate = candidate.expanduser()
    if not candidate.is_absolute():
        candidate = (_REPO_ROOT / candidate).resolve()
    else:
        candidate = candidate.resolve()

    if not candidate.exists():
        raise FileNotFoundError(
            f"Pricing data directory not found at '{candidate}'. "
            "Set the path explicitly when calling the loader, define the "
            f"'{_ENV_VAR}' environment variable, or create the directory."
        )

    if not candidate.is_dir():
        raise NotADirectoryError(
            f"Expected a directory for pricing data but found '{candidate}'."
        )

    return candidate


def _load_csv(filename: str, base_path: Optional[PathLike] = None) -> DataFrame:
    base_dir = _resolve_base_path(base_path)
    file_path = base_dir / filename

    if not file_path.exists():
        raise FileNotFoundError(
            f"Required pricing file '{filename}' was not found in '{base_dir}'."
        )

    return pd.read_csv(file_path)


TModel = TypeVar("TModel", bound=BaseModel)


def dataframe_to_models(dataframe: DataFrame, model: Type[TModel]) -> List[TModel]:
    """Convert a :class:`~pandas.DataFrame` to a list of Pydantic model instances.

    The helper ensures that any values not serialisable by FastAPI—such as
    ``numpy`` scalar types or ``NaN``—are converted to native Python objects and
    ``None`` respectively before instantiating the models. This centralises the
    schema alignment between the raw CSV data and the API response models.
    """

    if dataframe.empty:
        return []

    records = dataframe.to_dict(orient="records")
    sanitised_records = [
        {
            key: (None if pd.isna(value) else value)
            for key, value in record.items()
        }
        for record in records
    ]

    return [model(**record) for record in sanitised_records]


def load_loan_data(base_path: Optional[PathLike] = None) -> DataFrame:
    """Load the loan data CSV."""

    return _load_csv(PRICING_FILENAMES["loan_data"], base_path)


def load_historic_real_payment(base_path: Optional[PathLike] = None) -> DataFrame:
    """Load the historic real payment CSV."""

    return _load_csv(PRICING_FILENAMES["historic_real_payment"], base_path)


def load_payment_schedule(base_path: Optional[PathLike] = None) -> DataFrame:
    """Load the payment schedule CSV."""

    return _load_csv(PRICING_FILENAMES["payment_schedule"], base_path)


def load_customer_data(base_path: Optional[PathLike] = None) -> DataFrame:
    """Load the customer data CSV."""

    return _load_csv(PRICING_FILENAMES["customer_data"], base_path)


def load_collateral(base_path: Optional[PathLike] = None) -> DataFrame:
    """Load the collateral CSV."""

    return _load_csv(PRICING_FILENAMES["collateral"], base_path)


__all__ = [
    "PRICING_FILENAMES",
    "dataframe_to_models",
    "load_loan_data",
    "load_historic_real_payment",
    "load_payment_schedule",
    "load_customer_data",
    "load_collateral",
]
