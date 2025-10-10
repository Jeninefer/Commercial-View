"""
Data Loader Module for Commercial-View

Handles loading and processing of commercial lending data from various sources
including Abaco loan tapes, CSV files, and Google Drive integration.
"""

import os
import logging
from typing import Dict, Any, Optional, List, Tuple, Union
from pathlib import Path
import pandas as pd
from datetime import datetime
import numpy as np
import json

logger = logging.getLogger(__name__)

# Constants for better maintainability
ABACO_LOAN_DATA_FILE = 'Abaco - Loan Tape_Loan Data_Table.csv'
ABACO_PAYMENT_HISTORY_FILE = 'Abaco - Loan Tape_Historic Real Payment_Table.csv'
ABACO_PAYMENT_SCHEDULE_FILE = 'Abaco - Loan Tape_Payment Schedule_Table.csv'

# Abaco-specific column constants
DAYS_IN_DEFAULT_COLUMN = 'Days in Default'
LOAN_STATUS_COLUMN = 'Loan Status'
INTEREST_RATE_APR_COLUMN = 'Interest Rate APR'
CUSTOMER_ID_COLUMN = 'Customer ID'
LOAN_ID_COLUMN = 'Loan ID'

class AbacoSchemaValidator:
    """Validates Abaco data against the autodetected schema."""
    
    def __init__(self, schema_path: Optional[str] = None):
        """Initialize with schema from JSON file."""
        self.schema = {}
        if schema_path and os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                self.schema = json.load(f)
    
    def validate_table_structure(self, df: pd.DataFrame, table_name: str) -> Tuple[bool, List[str]]:
        """Validate DataFrame structure against schema."""
        issues = []
        
        if table_name not in self.schema.get('datasets', {}):
            issues.append(f"Table {table_name} not found in schema")
            return False, issues
        
        table_schema = self.schema['datasets'][table_name]
        expected_columns = {col['name']: col for col in table_schema.get('columns', [])}
        
        # Check for missing required columns (non-null columns)
        for col_name, col_info in expected_columns.items():
            if col_info.get('non_null', 0) > 0 and col_name not in df.columns:
                issues.append(f"Missing required column: {col_name}")
        
        # Check data types
        for col_name in df.columns:
            if col_name in expected_columns:
                expected_dtype = expected_columns[col_name].get('dtype')
                actual_dtype = str(df[col_name].dtype)
                
                # Type mapping for validation
                type_mapping = {
                    'string': ['object', 'string'],
                    'float': ['float64', 'float32', 'int64', 'int32'],
                    'int': ['int64', 'int32', 'float64', 'float32'],
                    'datetime': ['datetime64[ns]', 'object']
                }
                
                if expected_dtype in type_mapping:
                    if not any(dtype in actual_dtype for dtype in type_mapping[expected_dtype]):
                        issues.append(f"Column {col_name}: expected {expected_dtype}, got {actual_dtype}")
        
        return len(issues) == 0, issues

class DataLoader:
    """
    Data loader for Commercial-View platform with full Abaco schema support.
    
    Supports multiple data sources including:
    - Abaco loan tape CSV files with schema validation
    - Generic CSV files
    - Google Drive integration (future)
    """
    
    def __init__(self, config_dir: Optional[str] = None, data_dir: Optional[str] = None, schema_path: Optional[str] = None):
        """
        Initialize DataLoader with enhanced Abaco support.
        
        Args:
            config_dir: Directory containing configuration files
            data_dir: Directory containing data files
            schema_path: Path to Abaco schema JSON file
        """
        self.config_dir = config_dir or os.path.join(os.getcwd(), 'config')
        self.data_dir = data_dir or os.path.join(os.getcwd(), 'data')
        
        # Initialize schema validator
        self.schema_validator = AbacoSchemaValidator(schema_path)
        
        # Ensure directories exist
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        
        logger.info(f"DataLoader initialized with config_dir: {self.config_dir}, data_dir: {self.data_dir}")
        if schema_path:
            logger.info(f"Abaco schema loaded from: {schema_path}")
    
    def load_csv(self, filepath: str, encoding: str = 'utf-8') -> Optional[pd.DataFrame]:
        """
        Load a single CSV file with enhanced error handling.
        
        Args:
            filepath: Path to CSV file
            encoding: File encoding (default: utf-8)
            
        Returns:
            DataFrame or None if loading fails
        """
        try:
            if not os.path.exists(filepath):
                logger.warning(f"File not found: {filepath}")
                return None
            
            # Try different encodings if utf-8 fails
            encodings_to_try = [encoding, 'utf-8', 'latin-1', 'iso-8859-1']
            
            for enc in encodings_to_try:
                try:
                    df = pd.read_csv(filepath, encoding=enc)
                    logger.info(f"✅ Loaded CSV: {filepath} ({len(df)} rows, {len(df.columns)} columns) with encoding: {enc}")
                    return df
                except UnicodeDecodeError:
                    continue
                    
            logger.error(f"Failed to load CSV with any encoding: {filepath}")
            return None
            
        except Exception as e:
            logger.error(f"Error loading CSV {filepath}: {e}")
            return None
    
    def validate_abaco_data_quality(self, df: pd.DataFrame, table_type: str) -> Tuple[bool, List[str]]:
        """
        Validate data quality for Abaco tables.
        
        Args:
            df: DataFrame to validate
            table_type: Type of table ('loan_data', 'payment_history', 'payment_schedule')
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Common validations
        if df.empty:
            issues.append("DataFrame is empty")
            return False, issues
        
        # Check for required columns based on table type
        required_columns = {
            'loan_data': ['Customer ID', 'Loan ID', 'Company'],
            'payment_history': ['Customer ID', 'Loan ID', 'True Payment Date'],
            'payment_schedule': ['Customer ID', 'Loan ID', 'Payment Date']
        }
        
        if table_type in required_columns:
            missing_cols = [col for col in required_columns[table_type] if col not in df.columns]
            if missing_cols:
                issues.append(f"Missing required columns: {missing_cols}")
        
        # Check for excessive null values
        null_percentages = df.isnull().sum() / len(df) * 100
        high_null_cols = null_percentages[null_percentages > 50].index.tolist()
        if high_null_cols:
            issues.append(f"Columns with >50% null values: {high_null_cols}")
        
        # Check for duplicate IDs in loan data
        if table_type == 'loan_data' and 'Loan ID' in df.columns:
            duplicates = df['Loan ID'].duplicated().sum()
            if duplicates > 0:
                issues.append(f"Found {duplicates} duplicate Loan IDs")
        
        is_valid = len(issues) == 0
        return is_valid, issues
    
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
    
    def load_abaco_data(self, config_path: Optional[str] = None) -> Dict[str, pd.DataFrame]:
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
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                logger.info(f"✅ Loaded Abaco config from {config_path}")
            else:
                logger.warning(f"Config file not found: {config_path} - using defaults")
            
            data = {}
            
            # Load Loan Data
            loan_data_path = os.path.join(self.data_dir, ABACO_LOAN_DATA_FILE)
            if os.path.exists(loan_data_path):
                df = self.load_csv(loan_data_path)
                if df is not None:
                    # Validate data quality
                    is_valid, issues = self.validate_abaco_data_quality(df, 'loan_data')
                    if issues:
                        logger.warning(f"Data quality issues in loan data: {issues}")
                    
                    df = self._apply_abaco_transformations(df, config, 'loan_data')
                    data['loan_data'] = df
                    logger.info(f"✅ Loaded {len(df)} loan records")
            
            # Load Payment History  
            payment_history_path = os.path.join(self.data_dir, ABACO_PAYMENT_HISTORY_FILE)
            if os.path.exists(payment_history_path):
                df = self.load_csv(payment_history_path)
                if df is not None:
                    # Validate data quality
                    is_valid, issues = self.validate_abaco_data_quality(df, 'payment_history')
                    if issues:
                        logger.warning(f"Data quality issues in payment history: {issues}")
                    
                    df = self._apply_abaco_transformations(df, config, 'payment_history')
                    data['payment_history'] = df
                    logger.info(f"✅ Loaded {len(df)} payment history records")
            
            # Load Payment Schedule
            payment_schedule_path = os.path.join(self.data_dir, ABACO_PAYMENT_SCHEDULE_FILE)
            if os.path.exists(payment_schedule_path):
                df = self.load_csv(payment_schedule_path)
                if df is not None:
                    # Validate data quality
                    is_valid, issues = self.validate_abaco_data_quality(df, 'payment_schedule')
                    if issues:
                        logger.warning(f"Data quality issues in payment schedule: {issues}")
                    
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
        """Apply data transformations for Abaco data with enhanced error handling."""
        try:
            df_copy = df.copy()  # Work on a copy to avoid modifying original
            
            # Convert datetime columns
            datetime_cols = config.get('data_types', {}).get('datetime_columns', [])
            for col in datetime_cols:
                if col in df_copy.columns:
                    df_copy[col] = pd.to_datetime(df_copy[col], errors='coerce')
                    null_count = df_copy[col].isnull().sum()
                    if null_count > 0:
                        logger.warning(f"Failed to parse {null_count} dates in column {col}")
            
            # Add delinquency buckets for loan data
            if table_type == 'loan_data' and DAYS_IN_DEFAULT_COLUMN in df_copy.columns:
                bucket_config = config.get('delinquency_buckets', {})
                df_copy['delinquency_bucket'] = df_copy[DAYS_IN_DEFAULT_COLUMN].apply(
                    lambda x: self._get_delinquency_bucket(x, bucket_config)
                )
            
            # Calculate derived fields
            if table_type == 'loan_data':
                # Risk score calculation
                df_copy['risk_score'] = self._calculate_abaco_risk_score(df_copy)
                
                # Add data quality score
                df_copy['data_quality_score'] = self._calculate_data_quality_score(df_copy)
                
            logger.info(f"✅ Applied transformations to {table_type}")
            return df_copy
            
        except Exception as e:
            logger.error(f"Error applying transformations: {e}")
            return df
    
    def _calculate_data_quality_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate data quality score for each row."""
        scores = pd.Series([1.0] * len(df), index=df.index)
        
        # Penalize for missing critical fields
        critical_fields = ['Customer ID', 'Loan ID', 'Disbursement Amount']
        for field in critical_fields:
            if field in df.columns:
                scores -= df[field].isnull() * 0.3
        
        # Penalize for invalid values
        if DAYS_IN_DEFAULT_COLUMN in df.columns:
            scores -= (df[DAYS_IN_DEFAULT_COLUMN] < 0) * 0.2
        
        return scores.clip(0.0, 1.0)
    
    def _get_delinquency_bucket(self, days: Union[int, float], bucket_config: Dict) -> str:
        """Map days in default to delinquency bucket with improved handling."""
        # Handle NaN values
        if pd.isna(days):
            return 'unknown'
        
        try:
            days = int(days)
        except (ValueError, TypeError):
            return 'unknown'
        
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
            elif len(day_ranges) >= 2:
                if day_ranges[0] <= days <= day_ranges[1]:
                    return bucket_name
        return 'unknown'
    
    def _calculate_abaco_risk_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate risk score for Abaco loans with improved handling."""
        risk_scores = pd.Series([0.0] * len(df), index=df.index)
        
        # Days in Default component (0-1 scale)
        if DAYS_IN_DEFAULT_COLUMN in df.columns:
            days_col = df[DAYS_IN_DEFAULT_COLUMN].fillna(0)
            max_days = days_col.max() or 1
            risk_scores += 0.4 * (days_col / max_days)
        
        # Loan Status component
        if LOAN_STATUS_COLUMN in df.columns:
            status_risk = df[LOAN_STATUS_COLUMN].map({
                'Current': 0.0,
                'Complete': 0.0,
                'Default': 1.0
            }).fillna(0.5)  # Unknown status gets medium risk
            risk_scores += 0.3 * status_risk
        
        # Interest Rate component (higher rate = higher risk)
        if INTEREST_RATE_APR_COLUMN in df.columns:
            rate_col = df[INTEREST_RATE_APR_COLUMN].fillna(0)
            max_rate = rate_col.max() or 1
            risk_scores += 0.1 * (rate_col / max_rate)
        
        # Outstanding balance component (larger loans = higher risk)
        if 'Outstanding Loan Value' in df.columns:
            balance_col = df['Outstanding Loan Value'].fillna(0)
            max_balance = balance_col.max() or 1
            risk_scores += 0.2 * (balance_col / max_balance)
        
        return risk_scores.clip(0.0, 1.0)

    def get_data_summary(self, data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Generate comprehensive summary of loaded data."""
        summary = {
            'total_tables': len(data),
            'total_rows': sum(len(df) for df in data.values()),
            'total_columns': sum(len(df.columns) for df in data.values()),
            'tables': {},
            'generated_at': datetime.now().isoformat()
        }
        
        for table_name, df in data.items():
            table_summary = {
                'rows': len(df),
                'columns': len(df.columns),
                'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024,
                'null_percentage': (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
            }
            
            # Add table-specific metrics
            if table_name == 'loan_data':
                if 'risk_score' in df.columns:
                    table_summary['avg_risk_score'] = df['risk_score'].mean()
                    table_summary['high_risk_loans'] = (df['risk_score'] > 0.7).sum()
                if 'delinquency_bucket' in df.columns:
                    table_summary['delinquency_distribution'] = df['delinquency_bucket'].value_counts().to_dict()
            
            summary['tables'][table_name] = table_summary
        
        return summary

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
