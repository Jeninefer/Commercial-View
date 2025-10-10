"""
<<<<<<< Updated upstream
Production data loader for Commercial-View
Implements the sequence diagram for proper data path resolution
"""

import os
=======
Data Loader Module for Commercial-View

Handles loading and processing of commercial lending data from various sources
including Abaco loan tapes, CSV files, and Google Drive integration.
"""

import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path
>>>>>>> Stashed changes
import pandas as pd
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Union
from datetime import datetime

logger = logging.getLogger(__name__)

<<<<<<< Updated upstream

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
=======
class DataLoader:
    """
    Data loader for Commercial-View platform.
    
    Supports multiple data sources including:
    - Abaco loan tape CSV files
    - Generic CSV files
    - Google Drive integration (future)
    """
    
    def __init__(self, config_dir: str = None, data_dir: str = None):
        """
        Initialize DataLoader.
        
        Args:
            config_dir: Directory containing configuration files
            data_dir: Directory containing data files
        """
        self.config_dir = config_dir or os.path.join(os.getcwd(), 'config')
        self.data_dir = data_dir or os.path.join(os.getcwd(), 'data')
        
        # Ensure directories exist
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        
        logger.info(f"DataLoader initialized with config_dir: {self.config_dir}, data_dir: {self.data_dir}")
    
    def load_csv(self, filepath: str) -> Optional[pd.DataFrame]:
        """
        Load a single CSV file.
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            DataFrame or None if loading fails
        """
        try:
            if not os.path.exists(filepath):
                logger.warning(f"File not found: {filepath}")
                return None
                
            df = pd.read_csv(filepath)
            logger.info(f"✅ Loaded CSV: {filepath} ({len(df)} rows, {len(df.columns)} columns)")
            return df
            
        except Exception as e:
            logger.error(f"Error loading CSV {filepath}: {e}")
            return None
    
    def load_loan_data(self) -> Optional[pd.DataFrame]:
        """
        Load generic loan data from data directory.
        
        Returns:
            DataFrame with loan data or None
        """
        loan_files = [
            'loan_data.csv',
            'loans.csv',
            'Abaco - Loan Tape_Loan Data_Table.csv'
        ]
        
        for filename in loan_files:
            filepath = os.path.join(self.data_dir, filename)
            df = self.load_csv(filepath)
            if df is not None:
                return df
        
        logger.warning("No loan data files found")
        return None
    
    def load_abaco_data(self, config_path: str = None) -> Dict[str, pd.DataFrame]:
        """
        Load Abaco loan data using the schema configuration.
        
        Args:
            config_path: Path to abaco_column_maps.yml config file
            
        Returns:
            Dictionary containing loaded DataFrames
        """
        if not config_path:
            config_path = os.path.join(self.config_dir, 'abaco_column_maps.yml')
        
        try:
            # Try to load config - if it doesn't exist, we'll use defaults
            config = {}
            if os.path.exists(config_path):
                import yaml
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                logger.info(f"✅ Loaded Abaco config from {config_path}")
            else:
                logger.warning(f"Config file not found: {config_path} - using defaults")
            
            data = {}
            
            # Load Loan Data
            loan_data_path = os.path.join(self.data_dir, 'Abaco - Loan Tape_Loan Data_Table.csv')
            if os.path.exists(loan_data_path):
                df = self.load_csv(loan_data_path)
                if df is not None:
                    df = self._apply_abaco_transformations(df, config, 'loan_data')
                    data['loan_data'] = df
                    logger.info(f"✅ Loaded {len(df)} loan records")
            
            # Load Payment History  
            payment_history_path = os.path.join(self.data_dir, 'Abaco - Loan Tape_Historic Real Payment_Table.csv')
            if os.path.exists(payment_history_path):
                df = self.load_csv(payment_history_path)
                if df is not None:
                    df = self._apply_abaco_transformations(df, config, 'payment_history')
                    data['payment_history'] = df
                    logger.info(f"✅ Loaded {len(df)} payment history records")
            
            # Load Payment Schedule
            payment_schedule_path = os.path.join(self.data_dir, 'Abaco - Loan Tape_Payment Schedule_Table.csv')
            if os.path.exists(payment_schedule_path):
                df = self.load_csv(payment_schedule_path)
                if df is not None:
                    df = self._apply_abaco_transformations(df, config, 'payment_schedule')
                    data['payment_schedule'] = df
                    logger.info(f"✅ Loaded {len(df)} payment schedule records")
            
            if not data:
                logger.warning("No Abaco CSV files found in data directory")
                
            return data
            
        except Exception as e:
            logger.error(f"Error loading Abaco data: {e}")
            return {}
    
    def _apply_abaco_transformations(self, df: pd.DataFrame, config: Dict, table_type: str) -> pd.DataFrame:
        """Apply data transformations for Abaco data."""
        try:
            # Convert datetime columns
            datetime_cols = config.get('data_types', {}).get('datetime_columns', [])
            for col in datetime_cols:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Add delinquency buckets for loan data
            if table_type == 'loan_data' and 'Days in Default' in df.columns:
                bucket_config = config.get('delinquency_buckets', {})
                df['delinquency_bucket'] = df['Days in Default'].apply(
                    lambda x: self._get_delinquency_bucket(x, bucket_config)
                )
            
            # Calculate derived fields
            if table_type == 'loan_data':
                # Risk score calculation
                df['risk_score'] = self._calculate_abaco_risk_score(df)
                
            logger.info(f"✅ Applied transformations to {table_type}")
            return df
            
        except Exception as e:
            logger.error(f"Error applying transformations: {e}")
            return df
    
    def _get_delinquency_bucket(self, days: int, bucket_config: Dict) -> str:
        """Map days in default to delinquency bucket."""
        if not bucket_config:
            # Default buckets if no config
            if days == 0:
                return 'current'
            elif 1 <= days <= 3:
                return 'early'
            elif 4 <= days <= 7:
                return 'moderate'
            elif 8 <= days <= 15:
                return 'late'
            elif 16 <= days <= 30:
                return 'severe'
            elif 31 <= days <= 60:
                return 'default'
            else:
                return 'npl'
        
        # Use config-based buckets
        for bucket_name, day_ranges in bucket_config.items():
            if len(day_ranges) == 1:
                if days == day_ranges[0]:
                    return bucket_name
            else:
                if day_ranges[0] <= days <= day_ranges[1]:
                    return bucket_name
        return 'unknown'
    
    def _calculate_abaco_risk_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate risk score for Abaco loans."""
        risk_scores = pd.Series([0.0] * len(df), index=df.index)
        
        # Days in Default component (0-1 scale)
        if 'Days in Default' in df.columns:
            max_days = df['Days in Default'].max() or 1
            risk_scores += 0.4 * (df['Days in Default'] / max_days)
        
        # Loan Status component
        if 'Loan Status' in df.columns:
            status_risk = df['Loan Status'].map({
                'Current': 0.0,
                'Complete': 0.0,
                'Default': 1.0
            }).fillna(0.5)
            risk_scores += 0.3 * status_risk
        
        # Interest Rate component (higher rate = higher risk)
        if 'Interest Rate APR' in df.columns:
            max_rate = df['Interest Rate APR'].max() or 1
            risk_scores += 0.1 * (df['Interest Rate APR'] / max_rate)
        
        return risk_scores.clip(0.0, 1.0)


# Convenience functions
def load_abaco_portfolio(data_dir: str = None, config_dir: str = None) -> Dict[str, pd.DataFrame]:
    """
    Convenience function to load Abaco portfolio data.
    
    Args:
        data_dir: Directory containing Abaco CSV files
        config_dir: Directory containing configuration files
        
    Returns:
        Dictionary with loaded DataFrames
    """
    loader = DataLoader(config_dir=config_dir, data_dir=data_dir)
    return loader.load_abaco_data()
>>>>>>> Stashed changes
