"""
Production data loader for Commercial-View
Implements the sequence diagram for proper data path resolution
"""

import os
import pandas as pd
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Union
from datetime import datetime

logger = logging.getLogger(__name__)


class DataLoader:
    """
    Production data loader implementing proper path resolution sequence
    Handles CLI --data-dir, COMMERCIAL_VIEW_DATA_PATH env var, and defaults
    """

    DEFAULT_BASE_PATH = Path("data")

    def __init__(self, base_path: Optional[Union[str, Path]] = None):
        """
        Initialize data loader with proper path resolution
        Follows sequence: CLI arg -> ENV var -> DEFAULT_BASE_PATH
        """
        self.base_path = self._resolve_data_path(base_path)
        self.google_drive_url = (
            "https://drive.google.com/drive/folders/1qIg_BnIf_IWYcWqCuvLaYU_Gu4C2-Dj8"
        )

        logger.info(f"DataLoader initialized with path: {self.base_path}")

    def _resolve_data_path(self, base_path: Optional[Union[str, Path]]) -> Path:
        """
        Resolve data path following the sequence diagram logic
        1. Use CLI provided path if given
        2. Check COMMERCIAL_VIEW_DATA_PATH environment variable
        3. Fall back to DEFAULT_BASE_PATH
        """
        # Step 1: Use CLI provided path if available
        if base_path is not None:
            resolved_path = Path(base_path)
            logger.info(f"Using CLI provided data path: {resolved_path}")
            return resolved_path

        # Step 2: Check environment variable
        env_path = os.getenv("COMMERCIAL_VIEW_DATA_PATH")
        if env_path:
            resolved_path = Path(env_path)
            logger.info(f"Using environment variable data path: {resolved_path}")
            return resolved_path

        # Step 3: Use default path
        logger.info(f"Using default data path: {self.DEFAULT_BASE_PATH}")
        return self.DEFAULT_BASE_PATH

    def load_loan_data(
        self, base_path: Optional[Union[str, Path]] = None
    ) -> Optional[pd.DataFrame]:
        """
        Load loan data with proper path resolution
        Implements sequence diagram step: DL->>FS: open `loan_data.csv`
        """
        file_path = self._get_file_path("loan_data.csv", base_path)

        try:
            if not file_path.exists():
                raise FileNotFoundError(
                    f"Loan data file not found: {file_path}\n"
                    f"Expected location: {file_path.absolute()}\n"
                    f"Please ensure the file exists or set COMMERCIAL_VIEW_DATA_PATH environment variable.\n"
                    f"Production data source: {self.google_drive_url}"
                )

            df = pd.read_csv(file_path)

            # Validate commercial lending data structure
            required_columns = ["Customer ID", "Loan Amount", "Interest Rate", "Status"]
            self._validate_dataframe_structure(df, required_columns, "loan_data")

            logger.info(f"✅ Loaded {len(df)} loan records from {file_path}")
            return df

        except FileNotFoundError as e:
            logger.error(str(e))
            raise
        except Exception as e:
            logger.error(f"Failed to load loan data from {file_path}: {e}")
            raise

    def load_payment_schedule(
        self, base_path: Optional[Union[str, Path]] = None
    ) -> Optional[pd.DataFrame]:
        """
        Load payment schedule data with proper path resolution
        """
        file_path = self._get_file_path("payment_schedule.csv", base_path)

        try:
            if not file_path.exists():
                raise FileNotFoundError(
                    f"Payment schedule file not found: {file_path}\n"
                    f"Expected location: {file_path.absolute()}\n"
                    f"Please ensure the file exists or set COMMERCIAL_VIEW_DATA_PATH environment variable.\n"
                    f"Production data source: {self.google_drive_url}"
                )

            df = pd.read_csv(file_path)

            required_columns = ["Customer ID", "Due Date", "Total Payment"]
            self._validate_dataframe_structure(df, required_columns, "payment_schedule")

            logger.info(
                f"✅ Loaded {len(df)} payment schedule records from {file_path}"
            )
            return df

        except FileNotFoundError as e:
            logger.error(str(e))
            raise
        except Exception as e:
            logger.error(f"Failed to load payment schedule from {file_path}: {e}")
            raise

    def load_historic_real_payment(
        self, base_path: Optional[Union[str, Path]] = None
    ) -> Optional[pd.DataFrame]:
        """
        Load historic payment data with proper path resolution
        """
        file_path = self._get_file_path("historic_real_payment.csv", base_path)

        try:
            if not file_path.exists():
                raise FileNotFoundError(
                    f"Historic payment file not found: {file_path}\n"
                    f"Expected location: {file_path.absolute()}\n"
                    f"Please ensure the file exists or set COMMERCIAL_VIEW_DATA_PATH environment variable.\n"
                    f"Production data source: {self.google_drive_url}"
                )

            df = pd.read_csv(file_path)

            required_columns = ["Payment Date", "Amount Paid", "Days Past Due"]
            self._validate_dataframe_structure(
                df, required_columns, "historic_real_payment"
            )

            logger.info(
                f"✅ Loaded {len(df)} historic payment records from {file_path}"
            )
            return df

        except FileNotFoundError as e:
            logger.error(str(e))
            raise
        except Exception as e:
            logger.error(f"Failed to load historic payments from {file_path}: {e}")
            raise

    def load_customer_data(
        self, base_path: Optional[Union[str, Path]] = None
    ) -> Optional[pd.DataFrame]:
        """
        Load customer data with proper path resolution
        """
        file_path = self._get_file_path("customer_data.csv", base_path)

        try:
            if not file_path.exists():
                raise FileNotFoundError(
                    f"Customer data file not found: {file_path}\n"
                    f"Expected location: {file_path.absolute()}\n"
                    f"Please ensure the file exists or set COMMERCIAL_VIEW_DATA_PATH environment variable.\n"
                    f"Production data source: {self.google_drive_url}"
                )

            df = pd.read_csv(file_path)

            if df.empty:
                logger.warning(f"Customer data file is empty: {file_path}")
                return pd.DataFrame()

            logger.info(f"✅ Loaded {len(df)} customer records from {file_path}")
            return df

        except FileNotFoundError as e:
            logger.error(str(e))
            raise
        except Exception as e:
            logger.error(f"Failed to load customer data from {file_path}: {e}")
            raise

    def load_collateral(
        self, base_path: Optional[Union[str, Path]] = None
    ) -> Optional[pd.DataFrame]:
        """
        Load collateral data with proper path resolution
        """
        file_path = self._get_file_path("collateral.csv", base_path)

        try:
            if not file_path.exists():
                raise FileNotFoundError(
                    f"Collateral file not found: {file_path}\n"
                    f"Expected location: {file_path.absolute()}\n"
                    f"Please ensure the file exists or set COMMERCIAL_VIEW_DATA_PATH environment variable.\n"
                    f"Production data source: {self.google_drive_url}"
                )

            df = pd.read_csv(file_path)

            if df.empty:
                logger.warning(f"Collateral file is empty: {file_path}")
                return pd.DataFrame()

            logger.info(f"✅ Loaded {len(df)} collateral records from {file_path}")
            return df

        except FileNotFoundError as e:
            logger.error(str(e))
            raise
        except Exception as e:
            logger.error(f"Failed to load collateral data from {file_path}: {e}")
            raise

    def _get_file_path(
        self, filename: str, base_path: Optional[Union[str, Path]]
    ) -> Path:
        """
        Get file path with proper resolution logic
        Implements the path resolution from sequence diagram
        """
        if base_path is not None:
            # CLI provided base_path takes precedence
            resolved_base = Path(base_path)
        else:
            # Use instance base_path (already resolved in __init__)
            resolved_base = self.base_path

        return resolved_base / filename

    def _validate_dataframe_structure(
        self, df: pd.DataFrame, required_columns: list, dataset_name: str
    ):
        """Validate DataFrame has required commercial lending structure"""
        if df.empty:
            raise ValueError(f"{dataset_name} file is empty")

        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(
                f"Missing required columns in {dataset_name}: {missing_columns}\n"
                f"Available columns: {list(df.columns)}\n"
                f"Required columns: {required_columns}"
            )

    def get_data_status(self) -> Dict[str, Any]:
        """Get comprehensive data availability status"""
        data_files = {
            "loan_data": "loan_data.csv",
            "payment_schedule": "payment_schedule.csv",
            "historic_real_payment": "historic_real_payment.csv",
            "customer_data": "customer_data.csv",
        }

        status = {
            "data_source": "Production Google Drive",
            "resolved_path": str(self.base_path.absolute()),
            "google_drive_url": self.google_drive_url,
            "datasets": {},
        }

        for dataset_name, filename in data_files.items():
            file_path = self.base_path / filename

            if file_path.exists():
                try:
                    df = pd.read_csv(file_path)
                    status["datasets"][dataset_name] = {
                        "available": True,
                        "records": len(df),
                        "file_size_mb": round(
                            file_path.stat().st_size / (1024 * 1024), 2
                        ),
                        "last_modified": datetime.fromtimestamp(
                            file_path.stat().st_mtime
                        ).isoformat(),
                    }
                except Exception as e:
                    status["datasets"][dataset_name] = {
                        "available": False,
                        "error": str(e),
                    }
            else:
                status["datasets"][dataset_name] = {
                    "available": False,
                    "file_path": str(file_path.absolute()),
                    "error": "File not found",
                }

        return status


# Module-level convenience functions for backward compatibility
# These create a default DataLoader instance and call the appropriate methods

_default_loader: Optional[DataLoader] = None


def _get_default_loader(base_path: Optional[Union[str, Path]] = None) -> DataLoader:
    """Get or create default DataLoader instance"""
    global _default_loader
    if _default_loader is None or base_path is not None:
        _default_loader = DataLoader(base_path)
    return _default_loader


def load_loan_data(base_path: Optional[Union[str, Path]] = None) -> Optional[pd.DataFrame]:
    """Load loan data using default DataLoader instance"""
    loader = _get_default_loader(base_path)
    return loader.load_loan_data(base_path)


def load_historic_real_payment(base_path: Optional[Union[str, Path]] = None) -> Optional[pd.DataFrame]:
    """Load historic real payment data using default DataLoader instance"""
    loader = _get_default_loader(base_path)
    return loader.load_historic_real_payment(base_path)


def load_payment_schedule(base_path: Optional[Union[str, Path]] = None) -> Optional[pd.DataFrame]:
    """Load payment schedule data using default DataLoader instance"""
    loader = _get_default_loader(base_path)
    return loader.load_payment_schedule(base_path)


def load_customer_data(base_path: Optional[Union[str, Path]] = None) -> Optional[pd.DataFrame]:
    """Load customer data using default DataLoader instance"""
    loader = _get_default_loader(base_path)
    return loader.load_customer_data(base_path)


def load_collateral(base_path: Optional[Union[str, Path]] = None) -> Optional[pd.DataFrame]:
    """Load collateral data using default DataLoader instance"""
    loader = _get_default_loader(base_path)
    return loader.load_collateral(base_path)


def _resolve_base_path(base_path: Optional[Union[str, Path]] = None) -> Path:
    """Resolve base path using DataLoader logic"""
    loader = _get_default_loader(base_path)
    return loader.base_path


# Pricing filenames constant for backward compatibility
PRICING_FILENAMES = {
    "loan_data": "loan_data.csv",
    "payment_schedule": "payment_schedule.csv",
    "historic_real_payment": "historic_real_payment.csv",
    "customer_data": "customer_data.csv",
    "collateral": "collateral.csv"
}

