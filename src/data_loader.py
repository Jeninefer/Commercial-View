"""
Data Loader Module for Commercial View
Handles loading and basic processing of portfolio data
"""

import pandas as pd
import logging
from pathlib import Path
from typing import Dict, Optional, List, Any

logger = logging.getLogger(__name__)


class DataLoader:
    """Data loading and basic preprocessing class"""

    def __init__(self, data_path: str = "data/raw"):
        self.data_path = Path(data_path)

    def load_customer_data(self) -> Optional[pd.DataFrame]:
        """Load customer data"""
        file_path = self.data_path / "Abaco - Loan Tape_Customer Data_Table"
        return self._load_excel_file(file_path, "customer_data")

    def load_loan_data(self) -> Optional[pd.DataFrame]:
        """Load loan data"""
        file_path = self.data_path / "Abaco - Loan Tape_Loan Data_Table"
        return self._load_excel_file(file_path, "loan_data")

    def load_payment_history(self) -> Optional[pd.DataFrame]:
        """Load payment history"""
        file_path = self.data_path / "Abaco - Loan Tape_Historic Real Payment_Table"
        return self._load_excel_file(file_path, "payment_history")

    def load_payment_schedule(self) -> Optional[pd.DataFrame]:
        """Load payment schedule"""
        file_path = self.data_path / "Abaco - Loan Tape_Payment Schedule_Table"
        return self._load_excel_file(file_path, "payment_schedule")

    def _load_excel_file(
        self, file_path: Path, data_type: str
    ) -> Optional[pd.DataFrame]:
        """Helper method to load Excel files"""
        try:
            if file_path.exists():
                logger.info(f"Loading {data_type} from {file_path}")
                df = pd.read_excel(file_path)
                logger.info(f"Loaded {len(df)} rows for {data_type}")
                return df
            else:
                logger.warning(f"File not found: {file_path}")
                return None
        except Exception as e:
            logger.error(f"Error loading {data_type}: {e}")
            return None

    def load_all_data(self) -> Dict[str, pd.DataFrame]:
        """Load all available datasets"""
        datasets = {}

        loaders = {
            "customer_data": self.load_customer_data,
            "loan_data": self.load_loan_data,
            "payment_history": self.load_payment_history,
            "payment_schedule": self.load_payment_schedule,
        }

        for name, loader in loaders.items():
            data = loader()
            if data is not None:
                datasets[name] = data

        return datasets

# Standalone functions for backwards compatibility with tests and pipeline
def load_customer_data() -> Optional[pd.DataFrame]:
    """Load customer data - standalone function"""
    loader = DataLoader()
    return loader.load_customer_data()

def load_loan_data() -> Optional[pd.DataFrame]:
    """Load loan data - standalone function"""
    loader = DataLoader()
    return loader.load_loan_data()

def load_payment_data() -> Optional[pd.DataFrame]:
    """Load payment data - standalone function"""
    loader = DataLoader()
    return loader.load_payment_history()

def load_schedule_data() -> Optional[pd.DataFrame]:
    """Load schedule data - standalone function"""
    loader = DataLoader()
    return loader.load_payment_schedule()

# Additional functions that tests and pipeline are looking for
def load_historic_real_payment() -> Optional[pd.DataFrame]:
    """Load historic real payment data - alias for payment history"""
    loader = DataLoader()
    return loader.load_payment_history()

def load_payment_schedule() -> Optional[pd.DataFrame]:
    """Load payment schedule data - standalone function"""
    loader = DataLoader()
    return loader.load_payment_schedule()

def load_collateral() -> Optional[pd.DataFrame]:
    """Load collateral data - placeholder function"""
    logger.warning("Collateral data not available in current dataset")
    return pd.DataFrame()  # Return empty DataFrame as placeholder

def load_abaco_data(data_type: str = "all") -> Dict[str, pd.DataFrame]:
    """Load Abaco data by type or all data"""
    loader = DataLoader()
    
    if data_type == "all":
        return loader.load_all_data()
    elif data_type == "customer":
        result = loader.load_customer_data()
        return {"customer_data": result} if result is not None else {}
    elif data_type == "loan":
        result = loader.load_loan_data()
        return {"loan_data": result} if result is not None else {}
    elif data_type == "payment":
        result = loader.load_payment_history()
        return {"payment_history": result} if result is not None else {}
    elif data_type == "schedule":
        result = loader.load_payment_schedule()
        return {"payment_schedule": result} if result is not None else {}
    else:
        return {}

# Data validation functions
def validate_data_files() -> Dict[str, bool]:
    """Validate that all required data files exist"""
    data_path = Path("data/raw")
    required_files = [
        "Abaco - Loan Tape_Customer Data_Table",
        "Abaco - Loan Tape_Loan Data_Table", 
        "Abaco - Loan Tape_Historic Real Payment_Table",
        "Abaco - Loan Tape_Payment Schedule_Table"
    ]
    
    validation_results = {}
    for file in required_files:
        file_path = data_path / file
        validation_results[file] = file_path.exists()
    
    return validation_results

def get_data_summary() -> Dict[str, Any]:
    """Get summary of available data"""
    validation = validate_data_files()
    loader = DataLoader()
    
    summary = {
        "files_available": sum(validation.values()),
        "total_files": len(validation),
        "validation_details": validation,
        "data_path": str(loader.data_path)
    }
    
    return summary
