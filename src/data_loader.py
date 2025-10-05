"""Utilities for loading pricing-related CSV data and orchestrating dataset ingestion."""

from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

import pandas as pd
import yaml
from pandas import DataFrame

PathLike = Union[str, os.PathLike[str]]

logger = logging.getLogger(__name__)

_ENV_VAR = "COMMERCIAL_VIEW_DATA_PATH"
_REPO_ROOT = Path(__file__).resolve().parents[2]
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
      2. The ``COMMERCIAL_VIEW_DATA_PATH`` environment variable.
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
            f"CSV file not found: {file_path}. "
            f"Configure the data directory using the '{_ENV_VAR}' environment variable "
            "or pass a 'base_path' argument."
        )

    return pd.read_csv(file_path)


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
    "load_loan_data",
    "load_historic_real_payment",
    "load_payment_schedule",
    "load_customer_data",
    "load_collateral",
    "DataLoader",
]


class DataLoader:
    """Production-oriented loader that orchestrates all pricing datasets."""

    def __init__(
        self,
        base_path: Optional[PathLike] = None,
        config_dir: Optional[PathLike] = None,
    ) -> None:
        self.base_path = base_path
        self.config_dir = (
            Path(config_dir)
            if config_dir is not None
            else (_REPO_ROOT / "config")
        )
        self.column_maps = self._load_column_mappings()
        self.datasets: Dict[str, DataFrame] = {}
        self.validation_errors: List[Dict[str, Union[str, datetime]]] = []

    def _load_column_mappings(self) -> Dict[str, Dict[str, str]]:
        mapping_path = self.config_dir / "column_maps.yml"
        if not mapping_path.exists():
            logger.warning("Column mapping file not found at %s", mapping_path)
            return {}

        try:
            with mapping_path.open("r", encoding="utf-8") as handle:
                return yaml.safe_load(handle) or {}
        except yaml.YAMLError as exc:  # pragma: no cover - defensive guard
            logger.error("Failed to parse column mapping YAML: %s", exc)
            return {}

    def load_all_datasets(self) -> Dict[str, DataFrame]:
        """Load all configured datasets, capturing validation issues."""

        dataset_configs = {
            "loan_data": {
                "loader": load_loan_data,
                "mapping": "loan_data",
                "date_columns": ["origination_date"],
                "numeric_columns": [
                    "loan_amount",
                    "interest_rate",
                    "outstanding_balance",
                    "days_past_due",
                ],
                "required_columns": ["loan_id", "customer_id", "loan_amount"],
            },
            "payment_schedule": {
                "loader": load_payment_schedule,
                "mapping": "payment_data",
                "date_columns": ["payment_date"],
                "numeric_columns": [
                    "total_payment",
                    "principal_paid",
                    "interest_paid",
                    "fees_paid",
                    "tax_paid",
                    "outstanding_balance",
                ],
                "required_columns": ["loan_id", "payment_date"],
            },
            "historic_real_payment": {
                "loader": load_historic_real_payment,
                "mapping": "payment_data",
                "date_columns": ["payment_date"],
                "numeric_columns": [
                    "total_payment",
                    "principal_paid",
                    "interest_paid",
                    "fees_paid",
                    "tax_paid",
                ],
                "required_columns": ["loan_id"],
            },
            "customer_data": {
                "loader": load_customer_data,
                "mapping": "customer_data",
                "required_columns": ["customer_id", "customer_name"],
            },
            "collateral": {
                "loader": load_collateral,
                "mapping": "collateral_data",
                "required_columns": ["loan_id", "customer_id"],
            },
        }

        self.datasets = {}
        self.validation_errors = []

        for dataset_name, config in dataset_configs.items():
            loader = config["loader"]
            try:
                df = loader(self.base_path)
            except (FileNotFoundError, NotADirectoryError) as exc:
                logger.warning("%s not loaded: %s", dataset_name, exc)
                self._record_error(dataset_name, str(exc))
                continue
            except Exception as exc:  # pragma: no cover - unexpected failures
                logger.exception("Unexpected error loading %s", dataset_name)
                self._record_error(dataset_name, str(exc))
                continue

            mapping_key = config.get("mapping")
            if mapping_key:
                df = self._apply_column_mappings(df, mapping_key)

            for column in config.get("date_columns", []):
                if column in df.columns:
                    df[column] = pd.to_datetime(df[column], errors="coerce")

            for column in config.get("numeric_columns", []):
                if column in df.columns:
                    df[column] = pd.to_numeric(df[column], errors="coerce")

            self._validate_required_columns(
                df,
                dataset_name,
                config.get("required_columns", []),
            )

            self.datasets[dataset_name] = df
            logger.info("Loaded %s with %d rows", dataset_name, len(df))

        return self.datasets

    def _apply_column_mappings(
        self,
        df: DataFrame,
        dataset_key: str,
    ) -> DataFrame:
        mapping = self.column_maps.get(dataset_key)
        if not mapping:
            return df

        rename_dict = {source: target for target, source in mapping.items() if source in df.columns}
        if rename_dict:
            df = df.rename(columns=rename_dict)
        return df

    def _validate_required_columns(
        self,
        df: DataFrame,
        dataset_name: str,
        required_columns: List[str],
    ) -> None:
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            message = f"Missing required columns: {missing_columns}"
            logger.warning("%s validation issue: %s", dataset_name, message)
            self._record_error(dataset_name, message)

    def _record_error(self, dataset: str, error: str) -> None:
        self.validation_errors.append(
            {
                "dataset": dataset,
                "error": error,
                "timestamp": datetime.now(),
            }
        )

    def get_data_quality_report(self) -> Dict[str, object]:
        """Generate a summary of the loaded datasets and validation issues."""

        summary = {
            "total_datasets_loaded": len(self.datasets),
            "total_rows": sum(len(df) for df in self.datasets.values()),
            "validation_errors": len(self.validation_errors),
            "generated_at": datetime.now().isoformat(),
        }

        dataset_reports = {
            name: {
                "row_count": len(df),
                "column_count": len(df.columns),
                "null_counts": df.isnull().sum().to_dict(),
                "dtypes": df.dtypes.astype(str).to_dict(),
                "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024 / 1024,
            }
            for name, df in self.datasets.items()
        }

        return {
            "summary": summary,
            "datasets": dataset_reports,
            "validation_errors": self.validation_errors,
        }
