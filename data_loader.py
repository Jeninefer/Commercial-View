import os
from pathlib import Path
from typing import Dict, List, Optional, Union

import pandas as pd
import yaml
import logging
from datetime import datetime
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PathLike = Union[str, os.PathLike[str]]

_ENV_VAR = "COMMERCIAL_VIEW_DATA_PATH"
_REPO_ROOT = Path(__file__).resolve().parent
_DEFAULT_DATA_SUBDIR = Path("data") / "pricing"
_DEFAULT_CONFIG_SUBDIR = Path("config")

class DataLoader:
    """Production-grade data loader with comprehensive error handling and validation."""

    def __init__(
        self,
        data_dir: Optional[PathLike] = None,
        config_dir: Optional[PathLike] = None,
    ):
        self.data_dir = self._resolve_data_dir(data_dir)
        self.config_dir = self._resolve_config_dir(config_dir)
        self.column_maps = self._load_column_mappings()
        self.datasets = {}
        self.validation_errors = []

    def _resolve_data_dir(self, data_dir: Optional[PathLike]) -> Path:
        """Resolve the directory that contains pricing data."""

        if data_dir is not None:
            candidate = Path(data_dir)
        else:
            env_override = os.getenv(_ENV_VAR)
            if env_override:
                candidate = Path(env_override)
            else:
                candidate = _REPO_ROOT / _DEFAULT_DATA_SUBDIR

        candidate = candidate.expanduser()
        if not candidate.is_absolute():
            candidate = (_REPO_ROOT / candidate).resolve()
        else:
            candidate = candidate.resolve()

        if not candidate.exists():
            raise FileNotFoundError(
                f"Pricing data directory not found at '{candidate}'. "
                "Set the path explicitly when calling the loader, define the "
                f"'{_ENV_VAR}' environment variable, or create the directory."
            )

        if not candidate.is_dir():
            raise NotADirectoryError(
                f"Expected a directory for pricing data but found '{candidate}'."
            )

        return candidate

    def _resolve_config_dir(self, config_dir: Optional[PathLike]) -> Path:
        """Resolve the configuration directory used for column mappings."""

        if config_dir is not None:
            candidate = Path(config_dir)
        else:
            candidate = _REPO_ROOT / _DEFAULT_CONFIG_SUBDIR

        candidate = candidate.expanduser()
        if not candidate.is_absolute():
            candidate = (_REPO_ROOT / candidate).resolve()
        else:
            candidate = candidate.resolve()

        if not candidate.exists():
            raise FileNotFoundError(
                f"Configuration directory not found at '{candidate}'."
            )

        if not candidate.is_dir():
            raise NotADirectoryError(
                f"Expected a directory for configuration but found '{candidate}'."
            )

        return candidate

    def _load_column_mappings(self) -> Dict:
        """Load column mappings with error handling."""
        try:
            mapping_path = self.config_dir / "column_maps.yml"
            with mapping_path.open('r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"Column mapping file not found at {mapping_path}")
            return {}
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML: {e}")
            return {}
    
    def load_all_datasets(self) -> Dict[str, pd.DataFrame]:
        """Load all datasets with comprehensive validation and error handling."""
        dataset_loaders = {
            'loan_data': self._load_loan_data,
            'payment_schedule': self._load_payment_schedule,
            'historic_real_payment': self._load_historic_real_payment,
            'customer_data': self._load_customer_data,
            'collateral': self._load_collateral
        }
        
        for dataset_name, loader_func in dataset_loaders.items():
            try:
                logger.info(f"Loading {dataset_name}...")
                df = loader_func()
                if df is not None and not df.empty:
                    self.datasets[dataset_name] = df
                    logger.info(f"Successfully loaded {dataset_name}: {len(df)} rows")
                else:
                    logger.warning(f"No data loaded for {dataset_name}")
            except Exception as e:
                logger.error(f"Failed to load {dataset_name}: {str(e)}")
                self.validation_errors.append({
                    'dataset': dataset_name,
                    'error': str(e),
                    'timestamp': datetime.now()
                })
        
        return self.datasets
    
    def _load_loan_data(self) -> Optional[pd.DataFrame]:
        """Load loan data with proper type conversion and validation."""
        file_pattern = "Abaco - Loan Tape_Loan Data_Table"
        df = self._load_csv_with_pattern(file_pattern)
        
        if df is not None:
            # Apply column mappings
            df = self._apply_column_mappings(df, 'loan_data')
            
            # Convert date columns
            date_columns = ['Disbursement Date']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Convert numeric columns
            numeric_columns = ['TPV', 'Disbursement Amount', 'Interest Rate APR', 
                             'Outstanding Loan Value', 'Days in Default']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Validate critical fields
            self._validate_required_columns(df, ['Loan ID', 'Customer ID', 'Disbursement Amount'])
            
        return df
    
    def _load_payment_schedule(self) -> Optional[pd.DataFrame]:
        """Load payment schedule with validation."""
        file_pattern = "Abaco - Loan Tape_Payment Schedule_Table"
        df = self._load_csv_with_pattern(file_pattern)
        
        if df is not None:
            df = self._apply_column_mappings(df, 'payment_data')
            
            # Convert date columns
            if 'Payment Date' in df.columns:
                df['Payment Date'] = pd.to_datetime(df['Payment Date'], errors='coerce')
            
            # Convert numeric columns
            numeric_columns = ['Total Payment', 'Principal Payment', 'Interest Payment', 
                             'Fee Payment', 'Tax Payment', 'Outstanding Loan Value']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    
        return df
    
    def _load_historic_real_payment(self) -> Optional[pd.DataFrame]:
        """Load historic payment data."""
        file_pattern = "Abaco - Loan Tape_Historic Real Payment_Table"
        df = self._load_csv_with_pattern(file_pattern)
        
        if df is not None:
            df = self._apply_column_mappings(df, 'payment_data')
            
            # Convert date columns
            if 'True Payment Date' in df.columns:
                df['True Payment Date'] = pd.to_datetime(df['True Payment Date'], errors='coerce')
            
            # Add derived columns for analysis
            if 'True Payment Status' in df.columns:
                df['is_late'] = df['True Payment Status'] == 'Late'
                df['is_prepayment'] = df['True Payment Status'] == 'Prepayment'
                
        return df
    
    def _load_customer_data(self) -> Optional[pd.DataFrame]:
        """Load customer data - currently missing."""
        file_patterns = ["Customer Data", "customer_data", "Customer_Data"]
        
        for pattern in file_patterns:
            df = self._load_csv_with_pattern(pattern)
            if df is not None:
                df = self._apply_column_mappings(df, 'customer_data')
                return df
        
        logger.warning("Customer data file not found - this is required for full analysis")
        return None
    
    def _load_collateral(self) -> Optional[pd.DataFrame]:
        """Load collateral data - currently missing."""
        file_patterns = ["Collateral", "collateral", "Collateral_Data"]
        
        for pattern in file_patterns:
            df = self._load_csv_with_pattern(pattern)
            if df is not None:
                df = self._apply_column_mappings(df, 'collateral_data')
                return df
        
        logger.warning("Collateral data file not found - this is required for risk analysis")
        return None
    
    def _load_csv_with_pattern(self, pattern: str) -> Optional[pd.DataFrame]:
        """Load CSV file matching pattern with robust error handling."""
        try:
            # Find matching files
            matching_files = sorted(
                [
                    path
                    for path in self.data_dir.glob("*.csv")
                    if pattern in path.name
                ]
            )

            if not matching_files:
                return None

            # Use most recent file if multiple matches
            file_path = matching_files[-1]

            # Read with proper encoding handling
            try:
                df = pd.read_csv(file_path, encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, encoding='latin-1')
            
            return df
            
        except Exception as e:
            logger.error(f"Error loading file with pattern '{pattern}': {str(e)}")
            return None
    
    def _apply_column_mappings(self, df: pd.DataFrame, dataset_key: str) -> pd.DataFrame:
        """Apply column mappings from configuration."""
        if dataset_key in self.column_maps:
            mappings = self.column_maps[dataset_key]
            # Create reverse mapping for renaming
            rename_dict = {v: k for k, v in mappings.items() if v in df.columns}
            if rename_dict:
                df = df.rename(columns=rename_dict)
        return df
    
    def _validate_required_columns(self, df: pd.DataFrame, required_columns: List[str]):
        """Validate that required columns exist and have data."""
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            error_msg = f"Missing required columns: {missing_columns}"
            logger.error(error_msg)
            self.validation_errors.append({
                'type': 'missing_columns',
                'columns': missing_columns,
                'timestamp': datetime.now()
            })
        
        # Check for empty required columns
        for col in required_columns:
            if col in df.columns and df[col].isna().all():
                logger.warning(f"Column '{col}' exists but contains only null values")
    
    def get_data_quality_report(self) -> Dict:
        """Generate comprehensive data quality report."""
        report = {
            'summary': {
                'total_datasets_loaded': len(self.datasets),
                'total_rows': sum(len(df) for df in self.datasets.values()),
                'validation_errors': len(self.validation_errors),
                'generated_at': datetime.now().isoformat()
            },
            'datasets': {}
        }
        
        for name, df in self.datasets.items():
            report['datasets'][name] = {
                'row_count': len(df),
                'column_count': len(df.columns),
                'null_counts': df.isnull().sum().to_dict(),
                'dtypes': df.dtypes.astype(str).to_dict(),
                'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024
            }
        
        report['validation_errors'] = self.validation_errors
        
        return report

# Usage example for immediate testing
if __name__ == "__main__":
    loader = DataLoader()
    datasets = loader.load_all_datasets()
    quality_report = loader.get_data_quality_report()
    print(f"Loaded {len(datasets)} datasets")
    print(f"Data quality issues: {quality_report['summary']['validation_errors']}")
