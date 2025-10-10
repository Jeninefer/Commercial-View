"""
Data Loader Module for Commercial-View

Handles loading and processing of commercial lending data from various sources
including Abaco loan tapes, CSV files, and Google Drive integration.
"""

import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import pandas as pd
from typing import Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)

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
