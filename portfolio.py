#!/usr/bin/env python3
"""
Commercial-View Portfolio Processing Script

Main entry point for processing commercial lending portfolios and generating
DPD analysis, risk bucketing, and KPI reports with full Abaco integration.
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

# Import the DataLoader with Abaco support
from src.data_loader import DataLoader


def load_config(config_dir: str) -> Dict[str, Any]:
    """Load all configuration files from the config directory."""
    configs = {}
    
    config_files = [
        'column_maps.yml',
        'abaco_column_maps.yml',
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
                print(f"✅ Loaded {config_file}")
        else:
            print(f"⚠️  Warning: Configuration file {config_file} not found")
    
    return configs


def create_export_directories(export_config: Dict[str, Any]) -> None:
    """Create necessary export directories."""
    export_paths = export_config.get('export_paths', {})
    
    directories = [
        export_paths.get('base_path', './abaco_runtime/exports'),
        export_paths.get('kpi_json', './abaco_runtime/exports/kpi/json'),
        export_paths.get('kpi_csv', './abaco_runtime/exports/kpi/csv'),
        './abaco_runtime/exports/dpd',
        './abaco_runtime/exports/buckets',
        './abaco_runtime/exports/abaco'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {directory}")


def process_abaco_portfolio(data_loader: DataLoader, configs: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
    """Process Abaco loan tape data with risk scoring and analytics."""
    print("\n🏦 Processing Abaco loan tape data...")
    
    # Load Abaco data using the enhanced DataLoader
    abaco_data = data_loader.load_abaco_data()
    
    if not abaco_data:
        print("❌ No Abaco data found. Please ensure CSV files are in the data/ directory:")
        print("   - Abaco - Loan Tape_Loan Data_Table.csv")
        print("   - Abaco - Loan Tape_Historic Real Payment_Table.csv")
        print("   - Abaco - Loan Tape_Payment Schedule_Table.csv")
        return {}
    
    # Generate analytics summary
    analytics_summary = {}
    
    for table_name, df in abaco_data.items():
        print(f"📊 {table_name}: {len(df):,} rows, {len(df.columns)} columns")
        
        # Table-specific analytics
        if table_name == 'loan_data':
            analytics_summary['total_loans'] = len(df)
            analytics_summary['total_exposure'] = df['Outstanding Loan Value'].sum()
            analytics_summary['currency'] = df['Loan Currency'].iloc[0] if not df.empty else 'USD'
            
            # Delinquency analysis
            if 'delinquency_bucket' in df.columns:
                delinquency_dist = df['delinquency_bucket'].value_counts()
                analytics_summary['delinquency_distribution'] = delinquency_dist.to_dict()
                print(f"   🎯 Delinquency buckets: {len(delinquency_dist)} categories")
            
            # Risk scoring analysis
            if 'risk_score' in df.columns:
                analytics_summary['avg_risk_score'] = df['risk_score'].mean()
                analytics_summary['high_risk_loans'] = (df['risk_score'] > 0.7).sum()
                print(f"   ⚠️  High risk loans (>0.7): {analytics_summary['high_risk_loans']:,}")
        
        elif table_name == 'payment_history':
            analytics_summary['total_payments'] = len(df)
            analytics_summary['total_payment_amount'] = df['True Total Payment'].sum()
            
            # Payment performance
            if 'True Payment Status' in df.columns:
                payment_status_dist = df['True Payment Status'].value_counts()
                analytics_summary['payment_performance'] = payment_status_dist.to_dict()
                print(f"   💰 Payment statuses: {dict(payment_status_dist)}")
    
    return abaco_data, analytics_summary


def export_results(
    abaco_data: Dict[str, pd.DataFrame], 
    analytics_summary: Dict[str, Any], 
    export_config: Dict[str, Any]
) -> None:
    """Export processed results to various formats."""
    print("\n📤 Exporting results...")
    
    export_paths = export_config.get('export_paths', {})
    base_path = Path(export_paths.get('base_path', './abaco_runtime/exports'))
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Export Abaco data tables
    for table_name, df in abaco_data.items():
        # CSV export
        csv_path = base_path / 'abaco' / f'{table_name}_{timestamp}.csv'
        df.to_csv(csv_path, index=False)
        print(f"✅ Exported {table_name} to {csv_path}")
        
        # JSON export (sample for large datasets)
        if len(df) > 1000:
            sample_df = df.head(100)
            json_path = base_path / 'abaco' / f'{table_name}_sample_{timestamp}.json'
            sample_df.to_json(json_path, indent=2, date_format='iso')
            print(f"✅ Exported {table_name} sample to {json_path}")
    
    # Export analytics summary
    summary_path = base_path / 'kpi' / 'json' / f'abaco_summary_{timestamp}.json'
    with open(summary_path, 'w') as f:
        # Convert numpy types to native Python types for JSON serialization
        serializable_summary = {}
        for key, value in analytics_summary.items():
            if isinstance(value, (pd.Series, pd.DataFrame)):
                serializable_summary[key] = value.to_dict()
            elif hasattr(value, 'item'):  # numpy scalar
                serializable_summary[key] = value.item()
            else:
                serializable_summary[key] = value
        
        json.dump(serializable_summary, f, indent=2, default=str)
    print(f"✅ Exported analytics summary to {summary_path}")


def main():
    """Main processing function."""
    parser = argparse.ArgumentParser(description='Process commercial lending portfolio with Abaco integration')
    parser.add_argument('--config', default='config', help='Configuration directory path')
    parser.add_argument('--data-dir', help='Input data directory path')
    parser.add_argument('--abaco-only', action='store_true', help='Process only Abaco loan tape data')
    
    args = parser.parse_args()
    
    print("🏢 Commercial-View Portfolio Processing")
    print("=" * 50)
    print(f"🔧 Abaco Integration: {'Enabled' if args.abaco_only else 'Full Pipeline'}")
    
    # Load configurations
    print(f"\n📋 Loading configurations from: {args.config}")
    configs = load_config(args.config)
    
    if not configs:
        print("❌ Error: No valid configuration files found")
        sys.exit(1)
    
    # Create export directories
    print("\n📁 Creating export directories...")
    create_export_directories(configs.get('export_config', {}))
    
    # Initialize DataLoader with Abaco support
    data_loader = DataLoader(
        config_dir=args.config,
        data_dir=args.data_dir or 'data'
    )
    
    # Process Abaco portfolio data
    try:
        abaco_data, analytics_summary = process_abaco_portfolio(data_loader, configs)
        
        if abaco_data:
            # Export results
            export_results(abaco_data, analytics_summary, configs.get('export_config', {}))
            
            # Display summary
            print(f"\n📈 Portfolio Summary:")
            print(f"   💼 Total Loans: {analytics_summary.get('total_loans', 0):,}")
            print(f"   💰 Total Exposure: ${analytics_summary.get('total_exposure', 0):,.2f}")
            print(f"   💸 Total Payments: {analytics_summary.get('total_payments', 0):,}")
            print(f"   🎯 Average Risk Score: {analytics_summary.get('avg_risk_score', 0):.3f}")
            
        else:
            print("⚠️  No Abaco data processed. Check data directory and file formats.")
            
    except Exception as e:
        print(f"❌ Error processing portfolio: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print(f"\n✅ Processing completed successfully!")
    print(f"\n📋 Next steps:")
    print(f"1. 📂 Check generated files in ./abaco_runtime/exports/")
    print(f"2. ⚙️  Customize configuration files for your specific data schema")
    print(f"3. 🔍 Review analytics summary and risk scoring results")
    print(f"4. 📊 Import results into your preferred analytics platform")


if __name__ == '__main__':
    main()
