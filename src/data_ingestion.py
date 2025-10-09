"""
Data Ingestion Module for Commercial-View

Handles data loading from Google Sheets/Drive and local files.
Provides fallback mechanisms and robust error handling.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Optional
import pandas as pd

# Optional Google API imports
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GOOGLE_AVAILABLE = True
except ImportError:
    gspread = None
    Credentials = None
    GOOGLE_AVAILABLE = False

logger = logging.getLogger(__name__)

# Constants
DEFAULT_DATA_DIR = "./data"
GOOGLE_SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Default file names
DEFAULT_FILE_NAMES = {
    "loan_data": "Abaco - Loan Tape_Loan Data_Table.csv",
    "customer_data": "Abaco - Loan Tape_Customer Data_Table.csv",
    "historic_real_payment": "Abaco - Loan Tape_Historic Real Payment_Table.csv",
    "payment_schedule": "Abaco - Loan Tape_Payment Schedule_Table.csv",
    "collateral": "Abaco - Loan Tape_Collateral_Table.csv",
    "financials": "financials-abaco-consolidated-financials-2024.xlsx"
}


class DataLoader:
    """
    DataLoader fetches data from Google Sheets/Drive if available, else from local files.
    Loads datasets like loan_data, customer_data, payment_schedule into pandas DataFrames.
    """

    def __init__(self):
        """Initialize DataLoader with Google API and local file configurations."""
        self.google_client = None
        self.use_google = False
        self.datasets: Dict[str, pd.DataFrame] = {}
        
        # Setup paths and file names
        self.data_dir = Path(os.getenv("DATA_DIR", DEFAULT_DATA_DIR))
        self.file_names = self._get_file_names()
        self.sheets_ids = self._get_sheets_ids()
        
        # Initialize Google client
        self._initialize_google_client()

    def _get_file_names(self) -> Dict[str, str]:
        """Get file names from environment variables or defaults."""
        return {
            "loan_data": os.getenv("LOAN_DATA_CSV", DEFAULT_FILE_NAMES["loan_data"]),
            "customer_data": os.getenv("CUSTOMER_DATA_CSV", DEFAULT_FILE_NAMES["customer_data"]),
            "historic_real_payment": os.getenv("HISTORIC_PAYMENT_CSV", DEFAULT_FILE_NAMES["historic_real_payment"]),
            "payment_schedule": os.getenv("PAYMENT_SCHEDULE_CSV", DEFAULT_FILE_NAMES["payment_schedule"]),
            "collateral": os.getenv("COLLATERAL_CSV", DEFAULT_FILE_NAMES["collateral"]),
            "financials": os.getenv("FINANCIALS_XLSX", DEFAULT_FILE_NAMES["financials"])
        }

    def _get_sheets_ids(self) -> Dict[str, Optional[str]]:
        """Get Google Sheets IDs from environment variables."""
        return {
            "loan_data": os.getenv("GOOGLE_SHEETS_DOC_ID"),
            "customer_data": os.getenv("GOOGLE_SHEETS_CUSTOMER_ID"),
            "payment_schedule": os.getenv("GOOGLE_SHEETS_PAYMENT_ID"),
        }

    def _initialize_google_client(self) -> None:
        """Initialize Google Sheets client with service account or OAuth."""
        if not GOOGLE_AVAILABLE:
            logger.info("gspread not installed; using local files only.")
            return

        # Try service account authentication first
        if self._init_service_account():
            return

        # Fallback to OAuth authentication
        self._init_oauth()

    def _init_service_account(self) -> bool:
        """Initialize Google client with service account credentials."""
        service_account_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        if not service_account_json:
            return False

        try:
            creds = Credentials.from_service_account_file(
                service_account_json,
                scopes=GOOGLE_SCOPES
            )
            self.google_client = gspread.authorize(creds)
            self.use_google = True
            logger.info("✅ Initialized Google Sheets client with service account.")
            return True
        except Exception as e:
            logger.error(f"Google Sheets service account init failed: {e}")
            return False

    def _init_oauth(self) -> None:
        """Initialize Google client with OAuth credentials."""
        try:
            self.google_client = gspread.oauth()
            self.use_google = True
            logger.info("✅ Initialized Google Sheets client with user OAuth.")
        except Exception as e:
            logger.warning(f"Could not initialize Google OAuth: {e}")
            logger.info("Falling back to local files.")

    def load_from_google_sheets(self, sheet_key: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """
        Load data from Google Sheet by key.

        Args:
            sheet_key: Spreadsheet ID or URL
            sheet_name: Optional worksheet name (defaults to first sheet)

        Returns:
            DataFrame with loaded data

        Raises:
            RuntimeError: If Google client not initialized
            Exception: If sheet loading fails
        """
        if not self.google_client:
            raise RuntimeError("Google client not initialized")

        try:
            spreadsheet = self.google_client.open_by_key(sheet_key)
            worksheet = spreadsheet.worksheet(sheet_name) if sheet_name else spreadsheet.sheet1
            
            data = worksheet.get_all_records()
            df = pd.DataFrame(data)
            
            logger.info(f"✅ Loaded data from Google Sheet {sheet_key} (rows={len(df)})")
            return df
            
        except Exception as e:
            logger.error(f"Error reading Google Sheet {sheet_key}: {e}")
            raise

    def _load_local_file(self, file_path: Path) -> pd.DataFrame:
        """
        Load data from local file (CSV or Excel).

        Args:
            file_path: Path to the file

        Returns:
            DataFrame with loaded data
        """
        if not file_path.exists():
            logger.warning(f"File {file_path} not found.")
            return pd.DataFrame()

        try:
            if file_path.suffix.lower() in ['.csv', '.txt']:
                df = pd.read_csv(file_path)
            elif file_path.suffix.lower() in ['.xls', '.xlsx']:
                df = pd.read_excel(file_path)
            else:
                logger.error(f"Unsupported file type: {file_path.suffix}")
                return pd.DataFrame()
            
            logger.info(f"✅ Loaded {file_path.name} (rows={len(df)})")
            return df
            
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            return pd.DataFrame()

    def _load_dataset_from_google(self, dataset_name: str) -> Optional[pd.DataFrame]:
        """
        Try to load a dataset from Google Sheets.

        Args:
            dataset_name: Name of the dataset

        Returns:
            DataFrame if successful, None otherwise
        """
        if not self.use_google:
            return None

        sheet_id = self.sheets_ids.get(dataset_name)
        if not sheet_id:
            return None

        try:
            df = self.load_from_google_sheets(sheet_id)
            return df
        except Exception as e:
            logger.warning(f"Google Sheets load failed for {dataset_name}: {e}")
            return None

    def _get_file_path(self, filename: str) -> Path:
        """Get absolute file path."""
        file_path = Path(filename)
        if file_path.is_absolute():
            return file_path
        return self.data_dir / filename

    def load_dataset(self, dataset_name: str) -> pd.DataFrame:
        """
        Load a single dataset from Google Sheets or local file.

        Args:
            dataset_name: Name of the dataset to load

        Returns:
            DataFrame with loaded data (empty if failed)
        """
        # Try Google Sheets first
        df = self._load_dataset_from_google(dataset_name)
        if df is not None and not df.empty:
            return df

        # Fallback to local file
        filename = self.file_names.get(dataset_name)
        if not filename:
            logger.warning(f"No filename configured for dataset: {dataset_name}")
            return pd.DataFrame()

        file_path = self._get_file_path(filename)
        return self._load_local_file(file_path)

    def load_all_data(self) -> Dict[str, pd.DataFrame]:
        """
        Load all required datasets from Google or local files.

        Returns:
            Dictionary mapping dataset names to DataFrames
        """
        logger.info("Loading all datasets...")
        
        for dataset_name in self.file_names.keys():
            if dataset_name not in self.datasets or self.datasets[dataset_name].empty:
                self.datasets[dataset_name] = self.load_dataset(dataset_name)

        # Log summary
        loaded_count = sum(1 for df in self.datasets.values() if not df.empty)
        logger.info(f"✅ Loaded {loaded_count}/{len(self.file_names)} datasets successfully")

        return self.datasets

    def load_loan_data(self) -> pd.DataFrame:
        """Load loan data specifically."""
        if "loan_data" not in self.datasets or self.datasets["loan_data"].empty:
            self.datasets["loan_data"] = self.load_dataset("loan_data")
        return self.datasets["loan_data"]

    def load_customer_data(self) -> pd.DataFrame:
        """Load customer data specifically."""
        if "customer_data" not in self.datasets or self.datasets["customer_data"].empty:
            self.datasets["customer_data"] = self.load_dataset("customer_data")
        return self.datasets["customer_data"]

    def load_payment_schedule(self) -> pd.DataFrame:
        """Load payment schedule data specifically."""
        if "payment_schedule" not in self.datasets or self.datasets["payment_schedule"].empty:
            self.datasets["payment_schedule"] = self.load_dataset("payment_schedule")
        return self.datasets["payment_schedule"]

    def load_historic_real_payment(self) -> pd.DataFrame:
        """Load historic payment data specifically."""
        if "historic_real_payment" not in self.datasets or self.datasets["historic_real_payment"].empty:
            self.datasets["historic_real_payment"] = self.load_dataset("historic_real_payment")
        return self.datasets["historic_real_payment"]

    def load_collateral(self) -> pd.DataFrame:
        """Load collateral data specifically."""
        if "collateral" not in self.datasets or self.datasets["collateral"].empty:
            self.datasets["collateral"] = self.load_dataset("collateral")
        return self.datasets["collateral"]

    def get_dataset_summary(self) -> Dict[str, Dict[str, any]]:
        """
        Get summary information about loaded datasets.

        Returns:
            Dictionary with dataset statistics
        """
        summary = {}
        for name, df in self.datasets.items():
            summary[name] = {
                "loaded": not df.empty,
                "rows": len(df),
                "columns": len(df.columns) if not df.empty else 0,
                "memory_usage": df.memory_usage(deep=True).sum() if not df.empty else 0
            }
        return summary
