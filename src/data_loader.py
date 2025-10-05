from __future__ import annotations

from pathlib import Path
from typing import Dict, Union

import pandas as pd

_DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _resolve_base_path(base: Union[str, Path, None] = None) -> Path:
    return Path(base).resolve() if base else _DEFAULT_DATA_DIR


PRICING_FILENAMES: Dict[str, str] = {
    "loan_data": "loan_data.csv",
    "historic_real_payment": "historic_real_payment.csv",
    "payment_schedule": "payment_schedule.csv",
    "customer_data": "customer_data.csv",
    "collateral": "collateral.csv",
}


def _read_csv(path_or_dir: Union[str, Path], default_name: str | None = None) -> pd.DataFrame:
    p = Path(path_or_dir)
    if p.is_dir():
def load_loan_data(base_path: Union[str, Path]) -> pd.DataFrame:
    return _read_csv(base_path, PRICING_FILENAMES["loan_data"])

def load_historic_real_payment(base_path: Union[str, Path]) -> pd.DataFrame:
    return _read_csv(base_path, PRICING_FILENAMES["historic_real_payment"])

def load_payment_schedule(base_path: Union[str, Path]) -> pd.DataFrame:
    return _read_csv(base_path, PRICING_FILENAMES["payment_schedule"])

def load_customer_data(base_path: Union[str, Path]) -> pd.DataFrame:
    return _read_csv(base_path, PRICING_FILENAMES["customer_data"])

def load_collateral(base_path: Union[str, Path]) -> pd.DataFrame:
    return _read_csv(base_path, PRICING_FILENAMES["collateral"])
def load_payment_schedule(path: Union[str, Path]) -> pd.DataFrame:
    return _read_csv(path, PRICING_FILENAMES["payment_schedule"])


def load_customer_data(path: Union[str, Path]) -> pd.DataFrame:
    return _read_csv(path, PRICING_FILENAMES["customer_data"])


def load_collateral(path: Union[str, Path]) -> pd.DataFrame:
    return _read_csv(path, PRICING_FILENAMES["collateral"])


__all__ = [
    "load_loan_data",
    "load_historic_real_payment",
    "load_payment_schedule",
    "load_customer_data",
    "load_collateral",
    "_resolve_base_path",
    "PRICING_FILENAMES",
]
