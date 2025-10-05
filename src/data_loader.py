"""Utilities for loading pricing-related CSV data."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Union, Dict

import pandas as pd
from pandas import DataFrame

PathLike = Union[str, os.PathLike[str]]

_ENV_VAR = "COMMERCIAL_VIEW_DATA_PATH"
_REPO_ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_DATA_PATH = _REPO_ROOT / "data" / "pricing"

PRICING_FILENAMES = {
    "loan_data": "Abaco - Loan Tape_Loan Data_Table.csv",
    "historic_real_payment": "Abaco - Loan Tape_Historic Real Payment_Table.csv",
    "payment_schedule": "Abaco - Loan Tape_Payment Schedule_Table.csv",
    "customer_data": "Abaco - Loan Tape_Customer Data_Table.csv",
    "collateral": "Abaco - Loan Tape_Collateral_Table.csv",
}

class DataLoader:
    def __init__(self, base_path: Optional[PathLike] = None):
        self.base_path = self._resolve_base_path(base_path)

    def _resolve_base_path(self, base_path: Optional[PathLike] = None) -> Path:
        """Resolve the directory containing pricing data."""
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
                f"Set the path explicitly when calling the loader, define the "
                f"'{_ENV_VAR}' environment variable, or create the directory."
            )

        if not candidate.is_dir():
            raise NotADirectoryError(
                f"Expected a directory for pricing data but found '{candidate}'."
            )

        return candidate

    def _load_csv(self, filename: str) -> DataFrame:
        file_path = self.base_path / filename
        if not file_path.exists():
            raise FileNotFoundError(
                f"CSV file not found: {file_path}. "
                f"Configure the data directory using the '{_ENV_VAR}' environment variable "
                "or pass a 'base_path' argument."
            )
        return pd.read_csv(file_path)

    def load_loan_data(self) -> DataFrame:
        """Load the loan data CSV."""
        return self._load_csv(PRICING_FILENAMES["loan_data"])

    def load_historic_real_payment(self) -> DataFrame:
        """Load the historic real payment CSV."""
        return self._load_csv(PRICING_FILENAMES["historic_real_payment"])

    def load_payment_schedule(self) -> DataFrame:
        """Load the payment schedule CSV."""
        return self._load_csv(PRICING_FILENAMES["payment_schedule"])

    def load_customer_data(self) -> DataFrame:
        """Load the customer data CSV."""
        return self._load_csv(PRICING_FILENAMES["customer_data"])

    def load_collateral(self) -> DataFrame:
        """Load the collateral CSV."""
        return self._load_csv(PRICING_FILENAMES["collateral"])

    def load_all_datasets(self) -> Dict[str, DataFrame]:
        """Load all datasets and return them as a dictionary."""
        return {
            name: self._load_csv(filename)
            for name, filename in PRICING_FILENAMES.items()
        }

    def get_data_quality_report(self) -> dict:
        """Get comprehensive data quality report."""
        # Placeholder for data quality report logic
        return {"status": "not implemented"}

__all__ = ["DataLoader", "PRICING_FILENAMES"]