from pathlib import Path
from typing import Iterable, Optional
import pandas as pd

# Nombres que los tests usan para crear archivos (uno por tipo)
PRICING_FILENAMES = {
    "loan": "loan.csv",
    "historic_real_payment": "historic_real_payment.csv",
    "payment_schedule": "payment_schedule.csv",
    "customer": "customer.csv",
    "collateral": "collateral.csv",
}

# Patrones que el cargador aceptará además de los nombres exactos
PRICING_PATTERNS = {
    "loan": ["*loan*.csv", "*loans*.csv"],
    "historic_real_payment": ["*historic*real*payment*.csv", "*real*payment*.csv", "*payment*.csv"],
    "payment_schedule": ["*payment*schedule*.csv", "*schedule*.csv", "*amort*.csv"],
    "customer": ["*customer*.csv", "*client*.csv", "*borrower*.csv"],
    "collateral": ["*collateral*.csv", "*asset*.csv", "*security*.csv"],
}

def _resolve_base_path(base_path) -> Path:
    p = Path(base_path)
    if p.is_file():
        return p
    if not p.exists():
        raise FileNotFoundError(f"{p} not found")
    return p  # directorio válido

def _pick_csv(base: Path, prefer: Optional[Iterable[str]] = None, exact_name: Optional[str] = None) -> Path:
    # 1) si se da un nombre exacto y existe, úsalo
    if exact_name:
        exact = base / exact_name if base.is_dir() else Path(exact_name)
        if exact.exists() and exact.is_file():
            return exact

    # 2) si base es ya un archivo, devuélvelo
    if base.is_file():
        return base

    # 3) debe ser un directorio
    if not base.is_dir():
        raise FileNotFoundError(f"{base} not found")

    # 4) busca por patrones preferidos y luego cualquier CSV
    prefer = list(prefer or [])
    for pat in prefer:
        hits = sorted(base.rglob(pat))
        if hits:
            return hits[0]

    hits = sorted(base.rglob("*.csv"))
    if not hits:
        raise FileNotFoundError(f"No CSV files found under {base}")
    return hits[0]

def load_loan_data(base_path) -> pd.DataFrame:
    base = _resolve_base_path(base_path)
    path = _pick_csv(base, prefer=PRICING_PATTERNS["loan"], exact_name=PRICING_FILENAMES["loan"])
    return pd.read_csv(path)

def load_historic_real_payment(base_path) -> pd.DataFrame:
    base = _resolve_base_path(base_path)
    path = _pick_csv(base, prefer=PRICING_PATTERNS["historic_real_payment"], exact_name=PRICING_FILENAMES["historic_real_payment"])
    return pd.read_csv(path)

def load_payment_schedule(base_path) -> pd.DataFrame:
    base = _resolve_base_path(base_path)
    path = _pick_csv(base, prefer=PRICING_PATTERNS["payment_schedule"], exact_name=PRICING_FILENAMES["payment_schedule"])
    return pd.read_csv(path)

def load_customer_data(base_path) -> pd.DataFrame:
    base = _resolve_base_path(base_path)
    path = _pick_csv(base, prefer=PRICING_PATTERNS["customer"], exact_name=PRICING_FILENAMES["customer"])
    return pd.read_csv(path)

def load_collateral(base_path) -> pd.DataFrame:
    base = _resolve_base_path(base_path)
    path = _pick_csv(base, prefer=PRICING_PATTERNS["collateral"], exact_name=PRICING_FILENAMES["collateral"])
    return pd.read_csv(path)

__all__ = [
    "load_loan_data",
    "load_historic_real_payment",
    "load_payment_schedule",
    "load_customer_data",
    "load_collateral",
    "PRICING_FILENAMES",
    "_resolve_base_path",
    "_pick_csv",
