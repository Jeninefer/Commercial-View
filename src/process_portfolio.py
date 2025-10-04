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
from typing import Dict, Any

import yaml
import json
from datetime import datetime
import pandas as pd

from src.data_loader import (
    load_loan_data,
    load_historic_real_payment,
    load_payment_schedule,
    load_customer_data,
    load_collateral
)


def load_config(config_dir: str) -> Dict[str, Any]:
    """Load all configuration files from the config directory."""
    configs = {}
    
    config_files = [
        'column_maps.yml',
        'pricing_config.yml', 
        'dpd_policy.yml',
        'export_config.yml'
    ]
    
    for config_file in config_files:
        config_path = Path(config_dir) / config_file
        if config_path.exists():
            with open(config_path, 'r') as f:
                config_name = config_file.replace('.yml', '')
                configs[config_name] = yaml.safe_load(f)
        else:
            print(f"Warning: Configuration file {config_file} not found")
    
    return configs


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
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")


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
    
    # Load configurations
    print(f"Loading configurations from: {args.config}")
    configs = load_config(args.config)
    
    if not configs:
        print("Error: No valid configuration files found")
        sys.exit(1)
    
    # Create export directories
    print("\nCreating export directories...")
    create_export_directories(configs.get('export_config', {}))
    
    # Load data
    print("\nLoading data...")
    # Only pass base_path if CLI override is provided; otherwise, let loaders resolve internally
    if args.data_dir:
        loan_data = load_loan_data(args.data_dir)
        customer_data = load_customer_data(args.data_dir)
    else:
        loan_data = load_loan_data()
        customer_data = load_customer_data()
    print(f"Loaded {loan_data.shape[0]} rows and {loan_data.shape[1]} columns from loan_data.")
    print(f"Loaded {customer_data.shape[0]} rows and {customer_data.shape[1]} columns from customer_data.")

    # TODO: Implement the rest of the processing logic

    print("\n✅ Processing completed successfully!")
    print("\nNext steps:")
    print("1. Check the generated files in ./abaco_runtime/exports/")
    print("2. Customize the configuration files for your data")
    print("3. Implement actual data processing logic in this script")


if __name__ == '__main__':
    main()
