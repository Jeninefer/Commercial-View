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

# Constants for better maintainability - Fixed based on actual Abaco schema
ABACO_LOAN_DATA_FILE = 'Abaco - Loan Tape_Loan Data_Table.csv'
ABACO_PAYMENT_HISTORY_FILE = 'Abaco - Loan Tape_Historic Real Payment_Table.csv'
ABACO_PAYMENT_SCHEDULE_FILE = 'Abaco - Loan Tape_Payment Schedule_Table.csv'

# Abaco-specific column constants - Exact names from schema
DAYS_IN_DEFAULT_COLUMN = 'Days in Default'
LOAN_STATUS_COLUMN = 'Loan Status'
INTEREST_RATE_APR_COLUMN = 'Interest Rate APR'
CUSTOMER_ID_COLUMN = 'Customer ID'
LOAN_ID_COLUMN = 'Loan ID'
DISBURSEMENT_DATE_COLUMN = 'Disbursement Date'
TRUE_PAYMENT_DATE_COLUMN = 'True Payment Date'
DISBURSEMENT_AMOUNT_COLUMN = 'Disbursement Amount'
OUTSTANDING_LOAN_VALUE_COLUMN = 'Outstanding Loan Value'

class AbacoSchemaValidator:
    """Validates Abaco data against the autodetected schema."""
    
    def __init__(self, schema_path: Optional[str] = None):
        """Initialize with schema from JSON file."""
        self.schema = {}
        if not schema_path:
            # Try to find schema file in standard locations
            potential_paths = [
                os.path.join(os.getcwd(), 'config', 'abaco_schema_autodetected.json'),
                os.path.join(Path.home(), 'Downloads', 'abaco_schema_autodetected.json')
            ]
            for path in potential_paths:
                if os.path.exists(path):
                    schema_path = path
                    break
        
        if schema_path and os.path.exists(schema_path):
            try:
                with open(schema_path, 'r', encoding='utf-8') as f:
                    self.schema = json.load(f)
                logger.info(f"✅ Loaded Abaco schema from {schema_path}")
            except Exception as e:
                logger.error(f"Error loading schema from {schema_path}: {e}")
        else:
            logger.warning("Abaco schema file not found. Validation will be limited.")
    
    def validate_table_structure(self, df: pd.DataFrame, table_name: str) -> Tuple[bool, List[str]]:
        """Validate DataFrame structure against schema."""
        issues = []
        
        if not self.schema:
            issues.append("No schema loaded for validation")
            return False, issues
            
        datasets = self.schema.get('datasets', {})
        if table_name not in datasets:
            issues.append(f"Table {table_name} not found in schema")
            return False, issues
        
        table_schema = datasets[table_name]
        expected_columns = {col['name']: col for col in table_schema.get('columns', [])}
        
        # Check for missing required columns (non-null > 0)
        required_cols = [name for name, info in expected_columns.items() if info.get('non_null', 0) > 0]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            issues.append(f"Missing required columns: {missing_cols}")
        
        # Check expected row count (with tolerance)
        expected_rows = table_schema.get('rows', 0)
        actual_rows = len(df)
        if expected_rows > 0:
            tolerance = 0.05  # 5% tolerance
            if abs(actual_rows - expected_rows) / expected_rows > tolerance:
                issues.append(f"Row count mismatch: expected ~{expected_rows}, got {actual_rows}")
        
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
                    logger.info(f"✅ Loaded CSV: {os.path.basename(filepath)} ({len(df)} rows, {len(df.columns)} columns)")
                    return df
                except UnicodeDecodeError:
                    continue
                    
            logger.error(f"Failed to load CSV with any encoding: {filepath}")
            return None
            
        except Exception as e:
            logger.error(f"Error loading CSV {filepath}: {e}")
            return None
    
    def load_abaco_data(self, config_path: Optional[str] = None) -> Dict[str, pd.DataFrame]:
        """
        Load Abaco loan data with comprehensive validation and processing.
        
        Args:
            config_path: Path to abaco_column_maps.yml config file
            
        Returns:
            Dictionary containing loaded and processed DataFrames
        """
        logger.info("🏦 Starting Abaco loan tape data loading...")
        
        # Load configuration if available
        config = self._load_config(config_path)
        
        data = {}
        
        # Define Abaco table mappings based on schema
        abaco_tables = {
            'Loan Data': {
                'file': ABACO_LOAN_DATA_FILE,
                'key': 'loan_data',
                'expected_rows': 16205,
                'description': 'Core loan information and status'
            },
            'Historic Real Payment': {
                'file': ABACO_PAYMENT_HISTORY_FILE, 
                'key': 'payment_history',
                'expected_rows': 16443,
                'description': 'Historical payment records and performance'
            },
            'Payment Schedule': {
                'file': ABACO_PAYMENT_SCHEDULE_FILE,
                'key': 'payment_schedule', 
                'expected_rows': 16205,
                'description': 'Scheduled payment projections'
            }
        }
        
        # Load each table
        for schema_name, table_info in abaco_tables.items():
            file_path = os.path.join(self.data_dir, table_info['file'])
            
            if os.path.exists(file_path):
                logger.info(f"📊 Loading {table_info['description']}...")
                
                # Load CSV
                df = self.load_csv(file_path)
                if df is not None:
                    # Validate against schema
                    is_valid, issues = self.schema_validator.validate_table_structure(df, schema_name)
                    
                    if not is_valid:
                        logger.warning(f"⚠️  Schema validation issues for {schema_name}: {issues}")
                    else:
                        logger.info(f"✅ Schema validation passed for {schema_name}")
                    
                    # Apply transformations
                    df_processed = self._apply_abaco_transformations(df, config, table_info['key'])
                    data[table_info['key']] = df_processed
                    
                    # Log results
                    logger.info(f"✅ Processed {len(df_processed)} {table_info['key']} records")
                    
                    # Log key statistics
                    self._log_table_statistics(df_processed, table_info['key'])
            else:
                logger.warning(f"📁 File not found: {table_info['file']}")
        
        # Generate summary
        if data:
            total_records = sum(len(df) for df in data.values())
            logger.info(f"🎯 Abaco loading complete: {len(data)} tables, {total_records:,} total records")
        else:
            logger.warning("❌ No Abaco data loaded. Check file locations and formats.")
            
        return data
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration with fallback."""
        if not config_path:
            config_path = os.path.join(self.config_dir, 'abaco_column_maps.yml')
        
        config = {}
        if os.path.exists(config_path):
            try:
                import yaml
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                logger.info(f"✅ Loaded configuration from {config_path}")
            except Exception as e:
                logger.warning(f"Error loading config {config_path}: {e}")
        else:
            logger.info("Using default configuration (no config file found)")
        
        return config
    
    def _apply_abaco_transformations(self, df: pd.DataFrame, config: Dict, table_type: str) -> pd.DataFrame:
        """Apply comprehensive Abaco-specific transformations."""
        df_processed = df.copy()
        
        try:
            # Apply datetime conversions based on schema
            datetime_columns = {
                'loan_data': [DISBURSEMENT_DATE_COLUMN],
                'payment_history': [TRUE_PAYMENT_DATE_COLUMN],
                'payment_schedule': ['Payment Date']
            }
            
            for col in datetime_columns.get(table_type, []):
                if col in df_processed.columns:
                    df_processed[col] = pd.to_datetime(df_processed[col], errors='coerce')
                    null_count = df_processed[col].isnull().sum()
                    if null_count > 0:
                        logger.warning(f"⚠️  Failed to parse {null_count} dates in {col}")
            
            # Table-specific transformations
            if table_type == 'loan_data':
                df_processed = self._transform_loan_data(df_processed, config)
            elif table_type == 'payment_history':
                df_processed = self._transform_payment_history(df_processed, config)
            elif table_type == 'payment_schedule':
                df_processed = self._transform_payment_schedule(df_processed, config)
            
            return df_processed
            
        except Exception as e:
            logger.error(f"Error in transformations for {table_type}: {e}")
            return df_processed
    
    def _transform_loan_data(self, df: pd.DataFrame, config: Dict) -> pd.DataFrame:
        """Apply loan data specific transformations."""
        # Add delinquency buckets
        if DAYS_IN_DEFAULT_COLUMN in df.columns:
            df['delinquency_bucket'] = df[DAYS_IN_DEFAULT_COLUMN].apply(self._get_delinquency_bucket)
        
        # Calculate risk scores
        df['risk_score'] = self._calculate_risk_score(df)
        
        # Add derived fields
        if 'TPV' in df.columns and DISBURSEMENT_AMOUNT_COLUMN in df.columns:
            df['advance_rate'] = df[DISBURSEMENT_AMOUNT_COLUMN] / df['TPV']
            df['advance_rate'] = df['advance_rate'].fillna(0).clip(0, 1)
        
        return df
    
    def _transform_payment_history(self, df: pd.DataFrame, config: Dict) -> pd.DataFrame:
        """Apply payment history specific transformations."""
        # Calculate payment efficiency
        if 'True Total Payment' in df.columns and 'True Principal Payment' in df.columns:
            df['payment_efficiency'] = df['True Principal Payment'] / df['True Total Payment']
            df['payment_efficiency'] = df['payment_efficiency'].fillna(0).clip(0, 1)
        
        return df
    
    def _transform_payment_schedule(self, df: pd.DataFrame, config: Dict) -> pd.DataFrame:
        """Apply payment schedule specific transformations."""
        # Calculate interest burden
        if 'Total Payment' in df.columns and 'Principal Payment' in df.columns:
            df['interest_burden'] = 1 - (df['Principal Payment'] / df['Total Payment'])
            df['interest_burden'] = df['interest_burden'].fillna(0).clip(0, 1)
        
        return df
    
    def _get_delinquency_bucket(self, days: Union[int, float]) -> str:
        """Map days in default to delinquency bucket."""
        if pd.isna(days):
            return 'unknown'
        
        try:
            days = int(days)
        except (ValueError, TypeError):
            return 'unknown'
        
        # Standard Abaco delinquency buckets
        if days == 0:
            return 'current'
        elif 1 <= days <= 30:
            return 'early_delinquent'
        elif 31 <= days <= 60:
            return 'moderate_delinquent'
        elif 61 <= days <= 90:
            return 'late_delinquent'
        elif 91 <= days <= 120:
            return 'severe_delinquent'
        elif 121 <= days <= 180:
            return 'default'
        else:
            return 'npl'  # Non-performing loan
    
    def _calculate_risk_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate comprehensive risk score for Abaco loans."""
        risk_scores = pd.Series([0.0] * len(df), index=df.index)
        
        # Days in Default (40% weight)
        if DAYS_IN_DEFAULT_COLUMN in df.columns:
            days_normalized = np.minimum(df[DAYS_IN_DEFAULT_COLUMN].fillna(0) / 180.0, 1.0)
            risk_scores += 0.4 * days_normalized
        
        # Loan Status (30% weight)
        if LOAN_STATUS_COLUMN in df.columns:
            status_risk = df[LOAN_STATUS_COLUMN].map({
                'Current': 0.0,
                'Complete': 0.0,
                'Default': 1.0
            }).fillna(0.5)
            risk_scores += 0.3 * status_risk
        
        # Interest Rate (20% weight) - normalize to 0-1 range
        if INTEREST_RATE_APR_COLUMN in df.columns:
            rate_normalized = np.minimum(df[INTEREST_RATE_APR_COLUMN].fillna(0) / 0.5, 1.0)  # Assume max 50%
            risk_scores += 0.2 * rate_normalized
        
        # Loan Size relative risk (10% weight)
        if OUTSTANDING_LOAN_VALUE_COLUMN in df.columns:
            balance_col = df[OUTSTANDING_LOAN_VALUE_COLUMN].fillna(0)
            if balance_col.max() > 0:
                balance_percentile = balance_col.rank(pct=True)
                risk_scores += 0.1 * balance_percentile
        
        return risk_scores.clip(0.0, 1.0)
    
    def _log_table_statistics(self, df: pd.DataFrame, table_type: str) -> None:
        """Log key statistics for loaded table."""
        if table_type == 'loan_data':
            if 'Company' in df.columns:
                companies = df['Company'].value_counts()
                logger.info(f"   📈 Companies: {dict(companies)}")
            
            if LOAN_STATUS_COLUMN in df.columns:
                statuses = df[LOAN_STATUS_COLUMN].value_counts()
                logger.info(f"   📊 Loan Status: {dict(statuses)}")
            
            if 'delinquency_bucket' in df.columns:
                buckets = df['delinquency_bucket'].value_counts()
                logger.info(f"   🎯 Delinquency: {dict(buckets)}")
        
        elif table_type == 'payment_history':
            if 'True Payment Status' in df.columns:
                payment_statuses = df['True Payment Status'].value_counts()
                logger.info(f"   💰 Payment Status: {dict(payment_statuses)}")

    def load_loan_data(self) -> Optional[pd.DataFrame]:
        """
        Load generic loan data from data directory.
        
        Returns:
            DataFrame with loan data or None
        """
        loan_files = [
            'loan_data.csv',
            'loans.csv',
            ABACO_LOAN_DATA_FILE
        ]
        
        for filename in loan_files:
            filepath = os.path.join(self.data_dir, filename)
            df = self.load_csv(filepath)
            if df is not None:
                logger.info(f"✅ Loaded generic loan data from {filename}")
                return df
        
        logger.warning("No loan data files found")
        return None

    def load_customer_data(self) -> Optional[pd.DataFrame]:
        """
        Load customer data from data directory.
        
        Returns:
            DataFrame with customer data or None
        """
        customer_files = [
            'customer_data.csv',
            'customers.csv',
            'clients.csv'
        ]
        
        for filename in customer_files:
            filepath = os.path.join(self.data_dir, filename)
            df = self.load_csv(filepath)
            if df is not None:
                logger.info(f"✅ Loaded customer data from {filename}")
                return df
        
        logger.warning("No customer data files found")
        return None

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

def load_loan_data(data_dir: str = None) -> Optional[pd.DataFrame]:
    """
    Convenience function to load loan data.
    
    Args:
        data_dir: Directory containing data files
        
    Returns:
        DataFrame with loan data or None
    """
    loader = DataLoader(data_dir=data_dir)
    return loader.load_loan_data()

def load_customer_data(data_dir: str = None) -> Optional[pd.DataFrame]:
    """
    Convenience function to load customer data.
    
    Args:
        data_dir: Directory containing data files
        
    Returns:
        DataFrame with customer data or None
    """
    loader = DataLoader(data_dir=data_dir)
    return loader.load_customer_data()
