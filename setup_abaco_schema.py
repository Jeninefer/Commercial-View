"""
Setup script to integrate the Abaco schema into Commercial-View
"""

import json
import shutil
from pathlib import Path
import logging

def setup_abaco_schema():
    """Setup Abaco schema integration."""
    
    # Source and destination paths
    source_path = Path.home() / 'Downloads' / 'abaco_schema_autodetected.json'
    dest_path = Path(__file__).parent.parent / 'config' / 'abaco_schema_autodetected.json'
    
    print("🏦 Setting up Abaco Schema Integration")
    print("=" * 50)
    
    # Check if source file exists
    if source_path.exists():
        # Copy schema file to config directory
        dest_path.parent.mkdir(exist_ok=True)
        shutil.copy2(source_path, dest_path)
        print(f"✅ Copied schema file to: {dest_path}")
        
        # Load and validate schema
        try:
            with open(dest_path, 'r') as f:
                schema = json.load(f)
            
            datasets = schema.get('datasets', {})
            available_datasets = [name for name, info in datasets.items() if info.get('exists')]
            
            print(f"📊 Schema contains {len(available_datasets)} available datasets:")
            for dataset_name in available_datasets:
                dataset_info = datasets[dataset_name]
                rows = dataset_info.get('rows', 0)
                cols = len(dataset_info.get('columns', []))
                print(f"  - {dataset_name}: {rows:,} rows, {cols} columns")
            
            print(f"\n🎯 Total loan records: {datasets.get('Loan Data', {}).get('rows', 0):,}")
            print(f"💰 Total payment records: {datasets.get('Historic Real Payment', {}).get('rows', 0):,}")
            print(f"📅 Total schedule records: {datasets.get('Payment Schedule', {}).get('rows', 0):,}")
            
            print("\n✅ Abaco schema integration complete!")
            print(f"📁 Schema available at: {dest_path}")
            
        except Exception as e:
            print(f"❌ Error validating schema: {e}")
            return False
    else:
        print(f"❌ Schema file not found at: {source_path}")
        print("Please ensure abaco_schema_autodetected.json is in your Downloads folder")
        return False
    
    return True

if __name__ == '__main__':
    setup_abaco_schema()
