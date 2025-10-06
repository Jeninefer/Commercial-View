from __future__ import annotations

from pathlib import Path
from typing import Dict, Union

import pandas as pd

PRICING_FILENAMES: Dict[str, str] = {
    "loan_data": "loan_data.csv",
    "historic_real_payment": "historic_real_payment.csv",
    "payment_schedule": "payment_schedule.csv",
    "customer_data": "customer_data.csv",
    "collateral": "collateral.csv",
}


def _read_csv(path_or_dir: Union[str, Path], default_name: str) -> pd.DataFrame:
    p = Path(path_or_dir)
    if p.is_dir():
        file_path = p / default_name
    else:
        file_path = p
    return pd.read_csv(file_path)


def load_loan_data(path: Union[str, Path]) -> pd.DataFrame:
    return _read_csv(path, PRICING_FILENAMES["loan_data"])


def load_historic_real_payment(path: Union[str, Path]) -> pd.DataFrame:
    return _read_csv(path, PRICING_FILENAMES["historic_real_payment"])


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
    "PRICING_FILENAMES",
]
