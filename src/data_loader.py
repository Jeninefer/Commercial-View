"""Robust CSV loaders for Commercial-View datasets."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Iterable, Optional

import pandas as pd


DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent / "data"

PRICING_FILENAMES: Dict[str, str] = {
    "loan_data": "loan_data.csv",
    "historic_real_payment": "historic_real_payment.csv",
    "payment_schedule": "payment_schedule.csv",
    "customer_data": "customer_data.csv",
    "collateral": "collateral.csv",
}

_GLOB_PATTERNS: Dict[str, Iterable[str]] = {
    "loan_data": ("*loan*.csv", "*credit*.csv"),
    "historic_real_payment": ("*historic*payment*.csv", "*payment*.csv"),
    "payment_schedule": ("*schedule*.csv", "*calendar*.csv"),
    "customer_data": ("*customer*.csv", "*client*.csv"),
    "collateral": ("*collateral*.csv", "*asset*.csv"),
}


def _resolve_base_path(base_path: Optional[Path | str] = None) -> Path:
    """Return the canonical dataset directory or file."""
    if base_path is None:
        return DEFAULT_DATA_DIR

    resolved = Path(base_path).expanduser().resolve()
    return resolved


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")
    return pd.read_csv(path)


def _discover_file(base: Path, dataset_key: str) -> Path:
    """Locate the CSV file for the given dataset key."""
    if base.is_file():
        return base

    if not base.exists() or not base.is_dir():
        raise FileNotFoundError(f"{base} not found")

    explicit = base / PRICING_FILENAMES.get(dataset_key, "")
    if explicit.exists():
        return explicit

    for pattern in _GLOB_PATTERNS.get(dataset_key, ("*.csv",)):
        matches = sorted(base.rglob(pattern))
        if matches:
            return matches[0]

    fallback = sorted(base.rglob("*.csv"))
    if fallback:
        return fallback[0]

    raise FileNotFoundError(f"No CSV files found for {dataset_key} under {base}")


def load_loan_data(base_path: Optional[Path | str] = None) -> pd.DataFrame:
    base = _resolve_base_path(base_path)
    csv_path = _discover_file(base, "loan_data")
    return _read_csv(csv_path)


def load_historic_real_payment(base_path: Optional[Path | str] = None) -> pd.DataFrame:
    base = _resolve_base_path(base_path)
    try:
        csv_path = _discover_file(base, "historic_real_payment")
        df = _read_csv(csv_path)
        return df
    except FileNotFoundError:
        print(f"⚠️  Historic payment file not found: {base}")
        return pd.DataFrame(
            {
                "loan_id": [],
                "payment_date": [],
                "payment_amount": [],
                "principal_amount": [],
                "interest_amount": [],
                "payment_type": [],
            }
        )
    except Exception as exc:  # pragma: no cover - defensive guard
        print(f"❌ Error loading historic payment data: {exc}")
        return pd.DataFrame()


def load_payment_schedule(base_path: Optional[Path | str] = None) -> pd.DataFrame:
    base = _resolve_base_path(base_path)
    csv_path = _discover_file(base, "payment_schedule")
    return _read_csv(csv_path)


def load_customer_data(base_path: Optional[Path | str] = None) -> pd.DataFrame:
    base = _resolve_base_path(base_path)
    csv_path = _discover_file(base, "customer_data")
    return _read_csv(csv_path)


def load_collateral(base_path: Optional[Path | str] = None) -> pd.DataFrame:
    base = _resolve_base_path(base_path)
    csv_path = _discover_file(base, "collateral")
    return _read_csv(csv_path)
