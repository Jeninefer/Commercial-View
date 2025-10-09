#!/usr/bin/env python3
"""
Commercial-View Portfolio Processing Script

Main entry point for processing commercial lending portfolios and generating
DPD analysis, risk bucketing, and KPI reports.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

import yaml
import json
from datetime import datetime
import pandas as pd

# Add src to path if needed
sys.path.insert(0, str(Path(__file__).parent))

# Import data loader functions
try:
    from src.data_loader import DataLoader
    DATA_LOADER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import DataLoader: {e}")
    DATA_LOADER_AVAILABLE = False
    DataLoader = None


def _load_single_config(config_dir: Path, config_file: str) -> Optional[Dict[str, Any]]:
    """Load a single configuration file.
    
    Args:
        config_dir: Path to configuration directory
        config_file: Name of configuration file
        
    Returns:
        Configuration dictionary or None if file not found
    """
    config_path = config_dir / config_file
    if not config_path.exists():
        print(f"Warning: Configuration file {config_file} not found")
        return None
    
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading {config_file}: {e}")
        return None


def load_config(config_dir: str) -> Dict[str, Any]:
    """Load all configuration files from the config directory."""
    configs = {}
    config_path = Path(config_dir)
    
    config_files = [
        'column_maps.yml',
        'pricing_config.yml', 
        'dpd_policy.yml',
        'export_config.yml'
    ]
    
    for config_file in config_files:
        config_data = _load_single_config(config_path, config_file)
        if config_data:
            config_name = config_file.replace('.yml', '')
            configs[config_name] = config_data
    
    return configs


def _create_directory(directory: str) -> None:
    """Create a single directory if it doesn't exist.
    
    Args:
        directory: Path to directory to create
    """
    Path(directory).mkdir(parents=True, exist_ok=True)
    print(f"Created directory: {directory}")


def create_export_directories(export_config: Dict[str, Any]) -> None:
    """Create necessary export directories."""
    export_paths = export_config.get('export_paths', {})
    
    directories = [
        export_paths.get('base_path', './abaco_runtime/exports'),
        export_paths.get('kpi_json', './abaco_runtime/exports/kpi/json'),
        export_paths.get('kpi_csv', './abaco_runtime/exports/kpi/csv'),
        './abaco_runtime/exports/dpd',
        './abaco_runtime/exports/buckets'
    ]
    
    for directory in directories:
        _create_directory(directory)


def calculate_risk_score(loan_df: pd.DataFrame) -> pd.Series:
    """Calculate risk score for loans.
    
    Implementation strategy:
    1. Use credit score + payment history
    2. Integrate with external risk API
    3. Apply machine learning model for risk prediction
    
    Args:
        loan_df: DataFrame containing loan data
        
    Returns:
        Series of risk scores (0.0 to 1.0)
    """
    # Placeholder implementation - returns median risk score
    # Note: Implement full risk scoring logic based on:
    #   - Days in Default
    #   - Loan Status
    #   - Interest Rate APR
    #   - Outstanding Loan Value
    return pd.Series([0.5] * len(loan_df), index=loan_df.index)


def load_portfolio_data(data_loader: Optional[Any]) -> pd.DataFrame:
    """Load portfolio data using DataLoader.
    
    Args:
        data_loader: DataLoader instance
        
    Returns:
        DataFrame with loan data or None if loading fails
    """
    if not data_loader:
        print("Error: DataLoader not available")
        return None
    
    try:
        # Load loan data
        loan_data = data_loader.load_loan_data()
        
        if loan_data is not None:
            print(f"Loaded {loan_data.shape[0]} rows and {loan_data.shape[1]} columns from loan_data.")
        else:
            print("Warning: No loan data loaded")
            
        return loan_data
        
    except Exception as e:
        print(f"Error loading data: {e}")
        return None


def _validate_dependencies() -> bool:
    """Validate that required dependencies are available.
    
    Returns:
        True if dependencies are available, False otherwise
    """
    if not DATA_LOADER_AVAILABLE:
        print("Error: DataLoader not available. Please install required dependencies.")
        return False
    return True


def _initialize_data_loader() -> Optional[Any]:
    """Initialize the DataLoader instance.
    
    Returns:
        DataLoader instance or None if initialization fails
    """
    try:
        data_loader = DataLoader()
        print("✅ DataLoader initialized successfully")
        return data_loader
    except Exception as e:
        print(f"Error initializing DataLoader: {e}")
        return None


def _process_portfolio_data(loan_data: pd.DataFrame) -> None:
    """Process portfolio data and calculate metrics.
    
    Args:
        loan_data: DataFrame with loan data
    """
    print("\nCalculating risk scores...")
    risk_scores = calculate_risk_score(loan_data)
    loan_data['risk_score'] = risk_scores
    print(f"Risk scores calculated for {len(risk_scores)} loans")

    print("\nProcessing portfolio data...")
    # Note: Implement DPD bucketing based on dpd_policy config
    # Note: Implement KPI calculations
    # Note: Export results to configured locations


def _print_next_steps() -> None:
    """Print next steps for the user."""
    print("\n✅ Processing completed successfully!")
    print("\nNext steps:")
    print("1. Check the generated files in ./abaco_runtime/exports/")
    print("2. Customize the configuration files for your data")
    print("3. Implement actual data processing logic in this script")


def main():
    """Main processing function."""
    parser = argparse.ArgumentParser(description='Process commercial lending portfolio')
    parser.add_argument('--config', required=True, help='Configuration directory path')
    parser.add_argument('--data', help='Input data file path (optional for demo)')
    parser.add_argument(
        '--data-dir',
        help=(
            'Base directory containing the pricing CSV files. '
            'Defaults to the COMMERCIAL_VIEW_DATA_PATH environment variable or '
            'the repository data/pricing directory.'
        ),
    )

    args = parser.parse_args()
    
    print("Commercial-View Portfolio Processing")
    print("=" * 50)
    
    # Validate dependencies
    if not _validate_dependencies():
        sys.exit(1)
    
    # Load configurations
    print(f"Loading configurations from: {args.config}")
    configs = load_config(args.config)
    
    if not configs:
        print("Error: No valid configuration files found")
        sys.exit(1)
    
    # Create export directories
    print("\nCreating export directories...")
    create_export_directories(configs.get('export_config', {}))
    
    # Initialize data loader
    print("\nInitializing data loader...")
    data_loader = _initialize_data_loader()
    if not data_loader:
        sys.exit(1)
    
    # Load data
    print("\nLoading portfolio data...")
    loan_data = load_portfolio_data(data_loader)
    
    if loan_data is None:
        print("Error: Failed to load loan data")
        sys.exit(1)

    # Process data
    _process_portfolio_data(loan_data)
    
    # Print completion message
    _print_next_steps()


if __name__ == '__main__':
    main()
    
    # Print completion message
    _print_next_steps()


if __name__ == '__main__':
    main()
