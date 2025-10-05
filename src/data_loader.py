from pathlib import Path
import pandas as pd

def load_loan_data(base_path) -> pd.DataFrame:
    base = Path(base_path)

    if base.is_file():
        return pd.read_csv(base)

    if not base.exists() or not base.is_dir():
        raise FileNotFoundError(f"{base} not found")

    # Prefer loan-like names, then any CSV (recursive, deterministic)
    candidates = sorted(base.rglob("*loan*.csv")) or sorted(base.rglob("*.csv"))
    if not candidates:
        raise FileNotFoundError(f"No CSV files found under {base}")

    return pd.read_csv(candidates[0])
