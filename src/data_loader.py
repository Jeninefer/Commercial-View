"""Utilities for loading pricing-related CSV data."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Optional, Union

import pandas as pd
from pandas import DataFrame
import yaml

PathLike = Union[str, os.PathLike[str]]

_ENV_VAR = "COMMERCIAL_VIEW_PRICING_PATH"
_REPO_ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_DATA_PATH = _REPO_ROOT / "data" / "pricing"

_CONFIG_FILENAME = "pricing_config.yml"
# Map internal data type names to config keys. Config keys are now descriptive and aligned with data type names.
_CONFIG_KEY_MAP = {
    "loan_data": "loan_data_csv",
    "historic_real_payment": "historic_real_payment_csv",
    "payment_schedule": "payment_schedule_csv",
    "customer_data": "customer_data_csv",
    # 'collateral' is not mapped to a config key and will always use the default filename, regardless of config.
}

_DEFAULT_PRICING_FILENAMES = {
    "loan_data": "main_pricing.csv",
    "historic_real_payment": "commercial_loans_pricing.csv",
    "payment_schedule": "retail_loans_pricing.csv",
    "customer_data": "risk_based_pricing.csv",
    "collateral": "risk_based_pricing_enhanced.csv",
}


def _load_pricing_filenames() -> Dict[str, str]:
    """Load pricing filenames from config, falling back to repository defaults."""

    config_path = _REPO_ROOT / "config" / _CONFIG_FILENAME
    if not config_path.exists():
        return _DEFAULT_PRICING_FILENAMES.copy()

    with config_path.open("r", encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file) or {}

    pricing_files = config.get("pricing_files", {})
    resolved: Dict[str, str] = {}

    for key, default_filename in _DEFAULT_PRICING_FILENAMES.items():
        config_key = _CONFIG_KEY_MAP.get(key)
        candidate = None
        if config_key and isinstance(pricing_files, dict):
            candidate = pricing_files.get(config_key)

        if candidate and isinstance(candidate, (str, os.PathLike)):
            resolved[key] = str(candidate)
        else:
            resolved[key] = default_filename

    return resolved


PRICING_FILENAMES = _load_pricing_filenames()


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
]
