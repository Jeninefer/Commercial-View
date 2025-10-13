"""
Abaco Data Loader - Commercial View Integration
Loads and validates 48,853 Abaco records
Portfolio: $208,192,588.65 USD
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any
import pandas as pd
import json

logger = logging.getLogger(__name__)


def load_loan_data(base_path: Optional[Path] = None) -> pd.DataFrame:
    """
    Load Abaco loan data (16,205 records).

    Args:
        base_path: Optional base path for data files

    Returns:
        DataFrame with loan data
    """
    try:
        if base_path:
            file_path = base_path / "Abaco - Loan Tape_Loan Data_Table.csv"
        else:
            file_path = Path("data/Abaco - Loan Tape_Loan Data_Table.csv")

        if not file_path.exists():
            logger.warning(f"Loan data file not found: {file_path}")
            return pd.DataFrame()

        df = pd.read_csv(file_path)
        logger.info(f"Loaded {len(df)} loan records")
        return df
    except Exception as e:
        logger.error(f"Error loading loan data: {e}")
        return pd.DataFrame()


def load_historic_real_payment(base_path: Optional[Path] = None) -> pd.DataFrame:
    """
    Load Abaco payment history (16,443 records).

    Args:
        base_path: Optional base path for data files

    Returns:
        DataFrame with payment history
    """
    try:
        if base_path:
            file_path = base_path / "Abaco - Loan Tape_Historic Real Payment_Table.csv"
        else:
            file_path = Path("data/Abaco - Loan Tape_Historic Real Payment_Table.csv")

        if not file_path.exists():
            logger.warning(f"Payment history file not found: {file_path}")
            return pd.DataFrame()

        df = pd.read_csv(file_path)
        logger.info(f"Loaded {len(df)} payment records")
        return df
    except Exception as e:
        logger.error(f"Error loading payment history: {e}")
        return pd.DataFrame()


def load_payment_schedule(base_path: Optional[Path] = None) -> pd.DataFrame:
    """
    Load Abaco payment schedule (16,205 records).

    Args:
        base_path: Optional base path for data files

    Returns:
        DataFrame with payment schedule
    """
    try:
        if base_path:
            file_path = base_path / "Abaco - Loan Tape_Payment Schedule_Table.csv"
        else:
            file_path = Path("data/Abaco - Loan Tape_Payment Schedule_Table.csv")

        if not file_path.exists():
            logger.warning(f"Payment schedule file not found: {file_path}")
            return pd.DataFrame()

        df = pd.read_csv(file_path)
        logger.info(f"Loaded {len(df)} payment schedule records")
        return df
    except Exception as e:
        logger.error(f"Error loading payment schedule: {e}")
        return pd.DataFrame()


def load_customer_data(base_path: Optional[Path] = None) -> pd.DataFrame:
    """
    Load customer data (placeholder for future implementation).

    Args:
        base_path: Optional base path for data files

    Returns:
        DataFrame with customer data
    """
    logger.info("Customer data not yet implemented")
    return pd.DataFrame()


def load_collateral(base_path: Optional[Path] = None) -> pd.DataFrame:
    """
    Load collateral data (placeholder for future implementation).

    Args:
        base_path: Optional base path for data files

    Returns:
        DataFrame with collateral data
    """
    logger.info("Collateral data not yet implemented")
    return pd.DataFrame()


def load_abaco_schema() -> Dict[str, Any]:
    """
    Load Abaco schema configuration.

    Returns:
        Dictionary with schema configuration
    """
    try:
        schema_path = Path("config/abaco_schema_autodetected.json")

        if not schema_path.exists():
            logger.warning(f"Schema file not found: {schema_path}")
            return {}

        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)

        logger.info("Loaded Abaco schema successfully")
        return schema
    except Exception as e:
        logger.error(f"Error loading Abaco schema: {e}")
        return {}


def validate_portfolio_data(
    loan_data: pd.DataFrame,
    payment_history: pd.DataFrame,
    payment_schedule: pd.DataFrame
) -> Dict[str, Any]:
    """
    Validate complete Abaco portfolio (48,853 records).

    Args:
        loan_data: Loan data DataFrame
        payment_history: Payment history DataFrame
        payment_schedule: Payment schedule DataFrame

    Returns:
        Dictionary with validation results
    """
    validation = {
        'total_records': len(loan_data) + len(payment_history) + len(payment_schedule),
        'loan_records': len(loan_data),
        'payment_records': len(payment_history),
        'schedule_records': len(payment_schedule),
        'is_valid': True,
        'errors': []
    }

    # Validate expected record counts
    if len(loan_data) != 16205:
        validation['errors'].append(f"Expected 16,205 loan records, got {len(loan_data)}")
        validation['is_valid'] = False

    if len(payment_history) != 16443:
        validation['errors'].append(f"Expected 16,443 payment records, got {len(payment_history)}")
        validation['is_valid'] = False

    if len(payment_schedule) != 16205:
        validation['errors'].append(f"Expected 16,205 schedule records, got {len(payment_schedule)}")
        validation['is_valid'] = False

    logger.info(f"Portfolio validation: {validation['total_records']} records, valid={validation['is_valid']}")

    return validation


class DataLoader:
    """DataLoader class wrapper for Abaco data loading functions."""
    
    def __init__(self, schema_path=None):
        self.schema_path = schema_path
        self.records_loaded = 0
        
    def load_abaco_dataset(self, records=48853, base_path=None):
        """Load Abaco dataset."""
        from pathlib import Path
        df = load_loan_data(base_path)
        self.records_loaded = len(df)
        return df
    
    def load_abaco_data(self, base_path=None):
        """Load all Abaco data tables."""
        return {
            'loan_data': load_loan_data(base_path),
            'payment_history': load_historic_real_payment(base_path),
            'payment_schedule': load_payment_schedule(base_path)
        }
    
    def get_processing_stats(self):
        """Get processing statistics."""
        return {'records_loaded': self.records_loaded}

__all__ = ['DataLoader', 'load_loan_data', 'load_historic_real_payment', 
           'load_payment_schedule', 'load_customer_data', 'load_collateral',
           'load_abaco_schema', 'validate_portfolio_data']
