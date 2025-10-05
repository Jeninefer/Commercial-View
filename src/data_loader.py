from pathlib import Path
import pandas as pd
import os
from typing import Optional

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

def load_historic_real_payment(file_path: Optional[str] = None) -> pd.DataFrame:
    """
    Load historic real payment data for portfolio analysis.
    
    Args:
        file_path: Optional path to historic payment CSV file
        
    Returns:
        DataFrame with historic payment data
    """
    if file_path is None:
        # Default path for historic payment data
        file_path = "data/historic_real_payment.csv"
    
    try:
        if not os.path.exists(file_path):
            print(f"⚠️  Historic payment file not found: {file_path}")
            # Return empty DataFrame with expected columns
            return pd.DataFrame({
                'loan_id': [],
                'payment_date': [],
                'payment_amount': [],
                'principal_amount': [],
                'interest_amount': [],
                'payment_type': []
            })
        
        df = pd.read_csv(file_path)
        print(f"✅ Loaded {len(df)} historic payment records")
        return df
        
    except Exception as e:
        print(f"❌ Error loading historic payment data: {e}")
        return pd.DataFrame()
