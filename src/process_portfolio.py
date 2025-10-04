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
            print(
                f"Warning: Configuration file '{config_file}' not found at '{config_path}'.\n"
                f"Please ensure this file exists in the configuration directory ('{config_dir}'),\n"
                "or create it based on the sample templates provided."
            )
    
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


def generate_sample_output(export_config: Dict[str, Any]) -> None:
    """Generate sample output files to demonstrate the system."""
    export_paths = export_config.get('export_paths', {})
    base_path = export_paths.get('base_path', './abaco_runtime/exports')
    
    # Sample DPD data
    dpd_data = {
        "analysis_date": datetime.now().isoformat(),
        "portfolio_summary": {
            "total_loans": 1000,
            "total_exposure": 50000000,
            "default_rate": 0.05
        },
        "dpd_analysis": {
            "current": {"count": 850, "amount": 42500000},
            "1_30_days": {"count": 100, "amount": 5000000},
            "31_60_days": {"count": 30, "amount": 1500000},
            "61_90_days": {"count": 15, "amount": 750000},
            "90_plus_days": {"count": 5, "amount": 250000}
        }
    }
    
    # Sample KPI data
    kpi_data = {
        "generated_at": datetime.now().isoformat(),
        "kpis": {
            "portfolio_at_risk": 0.15,
            "default_rate": 0.05,
            "recovery_rate": 0.75,
            "provision_coverage": 0.12,
            "net_charge_off_rate": 0.03
        }
    }
    
    # Write sample files
    dpd_json_path = export_paths.get('dpd_json', './abaco_runtime/exports/dpd/json')
    Path(dpd_json_path).mkdir(parents=True, exist_ok=True)
    with open(f"{dpd_json_path}/dpd_analysis.json", 'w') as f:
        json.dump(dpd_data, f, indent=2)
    
    kpi_json_path = export_paths.get('kpi_json', './abaco_runtime/exports/kpi/json')
    Path(kpi_json_path).mkdir(parents=True, exist_ok=True)
    with open(f"{kpi_json_path}/kpi_report.json", 'w') as f:
        json.dump(kpi_data, f, indent=2)
    
    print("Generated sample output files:")
    print(f"  - {dpd_json_path}/dpd_analysis.json")
    print(f"  - {kpi_json_path}/kpi_report.json")


def main():
    """Main processing function."""
    parser = argparse.ArgumentParser(description='Process commercial lending portfolio')
    parser.add_argument('--config', required=True, help='Configuration directory path')
    parser.add_argument('--data', help='Input data file path (optional for demo)')
    
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
    
    # For now, generate sample output
    print("\nGenerating sample analysis (demo mode)...")
    generate_sample_output(configs.get('export_config', {}))
    
    print("\n✅ Processing completed successfully!")
    print("\nNext steps:")
    print("1. Check the generated files in ./abaco_runtime/exports/")
    print("2. Customize the configuration files for your data")
    print("3. Implement actual data processing logic in this script")


if __name__ == '__main__':
    main()
