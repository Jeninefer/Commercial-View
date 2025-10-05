from __future__ import annotations

import os
from pathlib import Path
from typing import Dict

import pandas as pd
from pandas import DataFrame

DEFAULT_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "pricing"
# Prefer COMMERCIAL_VIEW_DATA_PATH, but also support DATA_PATH for backward compatibility.
env_path = os.getenv("COMMERCIAL_VIEW_DATA_PATH") or os.getenv("DATA_PATH")
if env_path:
    env_path = os.path.expandvars(os.path.expanduser(env_path))
DATA_PATH = Path(env_path) if env_path else DEFAULT_DATA_PATH

_FILE_MAP: Dict[str, str] = {
    "loan_data": "Abaco - Loan Tape_Loan Data_Table.csv",
    "historic_real_payment": "Abaco - Loan Tape_Historic Real Payment_Table.csv",
    "payment_schedule": "Abaco - Loan Tape_Payment Schedule_Table.csv",
    "customer_data": "Abaco - Loan Tape_Customer Data_Table.csv",
    "collateral": "Abaco - Loan Tape_Collateral_Table.csv",
}


def _resolve_file_path(filename: str) -> Path:
    file_path = DATA_PATH / filename
    if not file_path.exists():
        raise FileNotFoundError(f"Data file not found: {file_path}")
    return file_path


def _read_csv(filename: str) -> DataFrame:
    file_path = _resolve_file_path(filename)
    return pd.read_csv(file_path)


def load_loan_data() -> DataFrame:
    return _read_csv(_FILE_MAP["loan_data"])


def load_historic_real_payment() -> DataFrame:
    return _read_csv(_FILE_MAP["historic_real_payment"])


def load_payment_schedule() -> DataFrame:
    return _read_csv(_FILE_MAP["payment_schedule"])


def load_customer_data() -> DataFrame:
    return _read_csv(_FILE_MAP["customer_data"])


def load_collateral() -> DataFrame:
    return _read_csv(_FILE_MAP["collateral"])