from pathlib import Path
import pandas as pd
import os
from typing import Optional

# Define pricing filenames for data loading
PRICING_FILENAMES = {
    'main_pricing': 'main_pricing.csv',
    'commercial_loans_pricing': 'commercial_loans_pricing.csv',
    'retail_loans_pricing': 'retail_loans_pricing.csv',
    'risk_based_pricing': 'risk_based_pricing.csv',
    'customer_data': 'Abaco - Loan Tape_Customer Data_Table.csv',
    'collateral': 'Abaco - Loan Tape_Collateral_Table.csv',
    'payment_schedule': 'Abaco - Loan Tape_Payment Schedule_Table.csv'
}


def _resolve_base_path(base_path: Optional[Path] = None) -> Path:
    """
    Resolve the base path for data files.
    
    Args:
        base_path: Optional explicit base path
        
    Returns:
        Resolved Path object
    """
    if base_path is not None:
        return Path(base_path).resolve()
    
    # Skip environment variable in test mode to allow test control of paths
    env_path = os.environ.get('COMMERCIAL_VIEW_DATA_PATH')
    if env_path and not os.environ.get('PYTEST_CURRENT_TEST'):
        return Path(env_path).resolve()
    
    # Default to repository data directory
    repo_root = Path(__file__).resolve().parent.parent
    return repo_root / "data"


def _read_csv(file_path: Path) -> pd.DataFrame:
    """
    Helper function to read a CSV file.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        DataFrame with the CSV data
    """
    return pd.read_csv(file_path)

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

def load_historic_real_payment(base_path: Optional[str] = None) -> pd.DataFrame:
    """
    Load historic real payment data for portfolio analysis.
    
    Args:
        base_path: Optional base directory path or file path for historic payment CSV
        
    Returns:
        DataFrame with historic payment data
    """
    # If base_path is provided and it's a directory, look for files in it
    if base_path is not None:
        path = Path(base_path)
        if path.is_dir():
            # Search for historic payment files in the directory (case-insensitive)
            all_csvs = list(path.rglob("*.csv"))
            # Filter for payment-related files
            candidates = [f for f in all_csvs if 'payment' in f.name.lower()]
            if candidates:
                try:
                    df = pd.read_csv(sorted(candidates)[0])
                    return df
                except Exception as e:
                    print(f"❌ Error loading historic payment data: {e}")
                    return pd.DataFrame()
            # If no files found, return empty DataFrame
            return pd.DataFrame()
        elif path.is_file():
            # If it's a file, read it directly
            try:
                df = pd.read_csv(path)
                return df
            except Exception as e:
                print(f"❌ Error loading historic payment data: {e}")
                return pd.DataFrame()
    
    # Default behavior when no base_path provided
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


def load_payment_schedule(base_path: Optional[str] = None) -> pd.DataFrame:
    """
    Load payment schedule data.
    
    Args:
        base_path: Optional base directory path containing the CSV file
        
    Returns:
        DataFrame with payment schedule data
    """
    resolved_path = _resolve_base_path(Path(base_path) if base_path else None)
    
    # Try pricing directory first
    pricing_path = resolved_path / "pricing" / PRICING_FILENAMES['payment_schedule']
    if pricing_path.exists():
        return _read_csv(pricing_path)
    
    # Try base directory
    base_file = resolved_path / PRICING_FILENAMES['payment_schedule']
    if base_file.exists():
        return _read_csv(base_file)
    
    # Search recursively for payment schedule files
    candidates = sorted(resolved_path.rglob("*payment*schedule*.csv"))
    if candidates:
        return _read_csv(candidates[0])
    
    raise FileNotFoundError(f"Payment schedule file not found in {resolved_path}")


def load_customer_data(base_path: Optional[str] = None) -> pd.DataFrame:
    """
    Load customer data.
    
    Args:
        base_path: Optional base directory path containing the CSV file
        
    Returns:
        DataFrame with customer data
    """
    resolved_path = _resolve_base_path(Path(base_path) if base_path else None)
    
    # Try pricing directory first
    pricing_path = resolved_path / "pricing" / PRICING_FILENAMES['customer_data']
    if pricing_path.exists():
        return _read_csv(pricing_path)
    
    # Try base directory
    base_file = resolved_path / PRICING_FILENAMES['customer_data']
    if base_file.exists():
        return _read_csv(base_file)
    
    # Search recursively for customer data files
    candidates = sorted(resolved_path.rglob("*customer*.csv"))
    if candidates:
        return _read_csv(candidates[0])
    
    raise FileNotFoundError(f"Customer data file not found in {resolved_path}")


def load_collateral(base_path: Optional[str] = None) -> pd.DataFrame:
    """
    Load collateral data.
    
    Args:
        base_path: Optional base directory path containing the CSV file
        
    Returns:
        DataFrame with collateral data
    """
    resolved_path = _resolve_base_path(Path(base_path) if base_path else None)
    
    # Try pricing directory first
    pricing_path = resolved_path / "pricing" / PRICING_FILENAMES['collateral']
    if pricing_path.exists():
        return _read_csv(pricing_path)
    
    # Try base directory
    base_file = resolved_path / PRICING_FILENAMES['collateral']
    if base_file.exists():
        return _read_csv(base_file)
    
    # Search recursively for collateral files
    candidates = sorted(resolved_path.rglob("*collateral*.csv"))
    if candidates:
        return _read_csv(candidates[0])
    
    raise FileNotFoundError(f"Collateral file not found in {resolved_path}")
