from __future__ import annotations
from pathlib import Path
from typing import Union, Dict, Optional, Any, List
import pandas as pd
import logging
import json

logger = logging.getLogger(__name__)

_DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def _resolve_base_path(base: Union[str, Path, None] = None) -> Path:
    return Path(base).resolve() if base else _DEFAULT_DATA_DIR

PRICING_FILENAMES: Dict[str, str] = {
    "loan_data": "Abaco - Loan Tape_Loan Data_Table.csv",
    "historic_real_payment": "Abaco - Loan Tape_Historic Real Payment_Table.csv",
    "payment_schedule": "Abaco - Loan Tape_Payment Schedule_Table.csv",
    "customer_data": "customer_data.csv",
    "collateral": "collateral.csv",
}

def _read_csv(path_or_dir: Union[str, Path], default_name: str | None = None) -> pd.DataFrame:
    p = Path(path_or_dir)
    if p.is_dir():
        if not default_name:
            raise ValueError("Directory provided without default_name.")
        p = p / default_name
    return pd.read_csv(p)

class DataLoader:
    """
    Enhanced DataLoader class for Abaco loan tape data.
    Supports the exact 48,853 record structure from your schema:
    - Loan Data: 16,205 records (28 columns)
    - Historic Real Payment: 16,443 records (18 columns)  
    - Payment Schedule: 16,205 records (16 columns)
    """
    
    def __init__(self, config_dir: Optional[str] = None, data_dir: Optional[str] = None, schema_path: Optional[str] = None):
        """Initialize DataLoader with Abaco schema support."""
        self.config_dir = config_dir or "config"
        self.data_dir = Path(data_dir) if data_dir else _DEFAULT_DATA_DIR
        self.schema_path = schema_path
        self.schema = None
        
        # Load schema if available
        if schema_path and Path(schema_path).exists():
            self._load_schema(schema_path)
        else:
            # Try to find schema in common locations
            potential_paths = [
                Path(self.config_dir) / "abaco_schema_autodetected.json",
                Path.home() / "Downloads" / "abaco_schema_autodetected.json"
            ]
            for path in potential_paths:
                if path.exists():
                    self._load_schema(str(path))
                    break
    
    def _load_schema(self, schema_path: str):
        """Load the Abaco schema from JSON file."""
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                self.schema = json.load(f)
            logger.info(f"Loaded Abaco schema: {len(self.schema.get('datasets', {}))} datasets")
        except Exception as e:
            logger.warning(f"Failed to load schema: {e}")
    
    def load_loan_data(self, path: Optional[Union[str, Path]] = None) -> pd.DataFrame:
        """
        Load loan data from CSV file.
        Expected: 16,205 records with 28 columns including Spanish client names.
        """
        file_path = path or (self.data_dir / PRICING_FILENAMES["loan_data"])
        try:
            df = pd.read_csv(file_path)
            logger.info(f"Loaded loan data: {len(df)} records, {len(df.columns)} columns")
            return df
        except FileNotFoundError:
            logger.warning(f"Loan data file not found: {file_path}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error loading loan data: {e}")
            return pd.DataFrame()
    
    def load_historic_real_payment(self, path: Optional[Union[str, Path]] = None) -> pd.DataFrame:
        """
        Load historic real payment data from CSV file.
        Expected: 16,443 records with 18 columns including payment status.
        """
        file_path = path or (self.data_dir / PRICING_FILENAMES["historic_real_payment"])
        try:
            df = pd.read_csv(file_path)
            logger.info(f"Loaded payment history: {len(df)} records, {len(df.columns)} columns")
            return df
        except FileNotFoundError:
            logger.warning(f"Payment history file not found: {file_path}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error loading payment history: {e}")
            return pd.DataFrame()
    
    def load_payment_schedule(self, path: Optional[Union[str, Path]] = None) -> pd.DataFrame:
        """
        Load payment schedule data from CSV file.
        Expected: 16,205 records with 16 columns for scheduled payments.
        """
        file_path = path or (self.data_dir / PRICING_FILENAMES["payment_schedule"])
        try:
            df = pd.read_csv(file_path)
            logger.info(f"Loaded payment schedule: {len(df)} records, {len(df.columns)} columns")
            return df
        except FileNotFoundError:
            logger.warning(f"Payment schedule file not found: {file_path}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error loading payment schedule: {e}")
            return pd.DataFrame()
    
    def load_abaco_data(self) -> Dict[str, pd.DataFrame]:
        """
        Load all available Abaco data tables with enhancement.
        Returns dict with keys: loan_data, payment_history, payment_schedule
        """
        data = {}
        
        # Load and enhance Loan Data
        loan_df = self.load_loan_data()
        if not loan_df.empty:
            loan_df = self._enhance_loan_data(loan_df)
            data['loan_data'] = loan_df
        
        # Load and enhance Historic Real Payment  
        payment_df = self.load_historic_real_payment()
        if not payment_df.empty:
            payment_df = self._enhance_payment_data(payment_df)
            data['payment_history'] = payment_df
        
        # Load and enhance Payment Schedule
        schedule_df = self.load_payment_schedule()
        if not schedule_df.empty:
            schedule_df = self._enhance_schedule_data(schedule_df)
            data['payment_schedule'] = schedule_df
        
        return data
    
    def _enhance_loan_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Enhance loan data with derived fields based on Abaco schema."""
        enhanced_df = df.copy()
        
        # Add delinquency buckets based on Days in Default
        if 'Days in Default' in enhanced_df.columns:
            enhanced_df['delinquency_bucket'] = enhanced_df['Days in Default'].apply(self._get_delinquency_bucket)
        
        # Add comprehensive risk scoring
        enhanced_df['risk_score'] = enhanced_df.apply(self._calculate_risk_score, axis=1)
        
        # Calculate advance rate (Disbursement Amount / TPV) 
        if 'Disbursement Amount' in enhanced_df.columns and 'TPV' in enhanced_df.columns:
            enhanced_df['advance_rate'] = enhanced_df['Disbursement Amount'] / enhanced_df['TPV']
            enhanced_df['advance_rate'] = enhanced_df['advance_rate'].fillna(0).clip(0, 1)
        
        return enhanced_df
    
    def _enhance_payment_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Enhance payment data with calculated fields."""
        enhanced_df = df.copy()
        
        # Calculate payment efficiency (Principal / Total Payment)
        if 'True Principal Payment' in enhanced_df.columns and 'True Total Payment' in enhanced_df.columns:
            enhanced_df['payment_efficiency'] = enhanced_df['True Principal Payment'] / enhanced_df['True Total Payment']
            enhanced_df['payment_efficiency'] = enhanced_df['payment_efficiency'].fillna(0).clip(0, 1)
        
        return enhanced_df
    
    def _enhance_schedule_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Enhance schedule data with calculated fields."""
        enhanced_df = df.copy()
        
        # Calculate interest burden (Interest / Total Payment)
        if 'Interest Payment' in enhanced_df.columns and 'Total Payment' in enhanced_df.columns:
            enhanced_df['interest_burden'] = enhanced_df['Interest Payment'] / enhanced_df['Total Payment']
            enhanced_df['interest_burden'] = enhanced_df['interest_burden'].fillna(0).clip(0, 1)
        
        return enhanced_df
    
    def _get_delinquency_bucket(self, days_in_default: int) -> str:
        """
        Categorize loans into delinquency buckets.
        Based on your schema samples: [0, 1, 3] days in default.
        """
        if pd.isna(days_in_default) or days_in_default == 0:
            return 'current'
        elif 1 <= days_in_default <= 30:
            return 'early_delinquent'
        elif 31 <= days_in_default <= 60:
            return 'moderate_delinquent'
        elif 61 <= days_in_default <= 90:
            return 'late_delinquent'
        elif 91 <= days_in_default <= 120:
            return 'severe_delinquent'
        elif 121 <= days_in_default <= 180:
            return 'default'
        else:
            return 'npl'
    
    def _calculate_risk_score(self, row: pd.Series) -> float:
        """
        Calculate risk score based on your exact schema values.
        Uses Interest Rate APR range: 0.2947 - 0.3699 (29.47% - 36.99%)
        """
        risk_score = 0.0
        
        # Days in Default factor (40% weight)
        if 'Days in Default' in row and pd.notna(row['Days in Default']):
            days_risk = min(row['Days in Default'] / 180.0, 1.0)
            risk_score += days_risk * 0.4
        
        # Loan Status factor (30% weight) - from your samples: Current, Complete, Default
        if 'Loan Status' in row:
            status_risk = {'Current': 0.0, 'Complete': 0.0, 'Default': 1.0}.get(row['Loan Status'], 0.5)
            risk_score += status_risk * 0.3
        
        # Interest Rate factor (20% weight) - your range: 29.47% - 36.99%
        if 'Interest Rate APR' in row and pd.notna(row['Interest Rate APR']):
            rate_risk = (row['Interest Rate APR'] - 0.2947) / (0.3699 - 0.2947)
            risk_score += max(min(rate_risk, 1.0), 0) * 0.2
        
        # Loan Size factor (10% weight) - your range: $88.48 - $77,175
        if 'Outstanding Loan Value' in row and pd.notna(row['Outstanding Loan Value']):
            size_risk = min(row['Outstanding Loan Value'] / 100000.0, 1.0)
            risk_score += size_risk * 0.1
        
        return min(risk_score, 1.0)

def load_loan_data(path: Union[str, Path]) -> pd.DataFrame:
    return _read_csv(path, PRICING_FILENAMES["loan_data"])

def load_historic_real_payment(path: Union[str, Path]) -> pd.DataFrame:
    return _read_csv(path, PRICING_FILENAMES["historic_real_payment"])

def load_payment_schedule(path: Union[str, Path]) -> pd.DataFrame:
    return _read_csv(path, PRICING_FILENAMES["payment_schedule"])

def load_customer_data(path: Union[str, Path]) -> pd.DataFrame:
    return _read_csv(path, PRICING_FILENAMES["customer_data"])

def load_collateral(path: Union[str, Path]) -> pd.DataFrame:
    return _read_csv(path, PRICING_FILENAMES["collateral"])

def load_abaco_portfolio(data_dir: str = "data") -> Dict[str, pd.DataFrame]:
    """Load complete Abaco portfolio data (backward compatibility)."""
    loader = DataLoader(data_dir=data_dir)
    return loader.load_abaco_data()

class AbacoSchemaValidator:
    """Validator for Abaco schema compliance based on your 48,853 record structure."""
    
    def __init__(self, schema_path: str):
        """Initialize with your schema file."""
        with open(schema_path, 'r') as f:
            self.schema = json.load(f)
    
    def validate_table_structure(self, df: pd.DataFrame, table_name: str) -> tuple[bool, List[str]]:
        """Validate DataFrame against your exact schema structure."""
        issues = []
        
        if table_name not in self.schema['datasets']:
            issues.append(f"Table {table_name} not found in schema")
            return False, issues
        
        expected_schema = self.schema['datasets'][table_name]
        expected_columns = {col['name']: col for col in expected_schema['columns']}
        
        # Check required columns (non_null > 0)
        required_cols = [name for name, info in expected_columns.items() if info.get('non_null', 0) > 0]
        missing_required = [col for col in required_cols if col not in df.columns]
        
        if missing_required:
            issues.append(f"Missing required columns: {missing_required}")
        
        # Check for unexpected columns
        unexpected = [col for col in df.columns if col not in expected_columns]
        if unexpected:
            issues.append(f"Unexpected columns: {unexpected}")
        
        return len(issues) == 0, issues

# Updated __all__ to include DataLoader and AbacoSchemaValidator
__all__ = [
    "DataLoader",
    "AbacoSchemaValidator",
    "load_loan_data",
    "load_historic_real_payment",
    "load_payment_schedule",
    "load_customer_data",
    "load_collateral", 
    "load_abaco_portfolio",
    "_resolve_base_path",
    "PRICING_FILENAMES",
]
