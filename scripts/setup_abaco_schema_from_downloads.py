"""
Setup Abaco schema from Downloads and create comprehensive integration test
"""

import os
import sys
import json
import shutil
from pathlib import Path

def setup_abaco_schema_integration():
    """Setup complete Abaco schema integration from Downloads folder."""
    
    print("🏦 Abaco Schema Integration Setup")
    print("=" * 50)
    
    # Paths
    project_root = Path(__file__).parent.parent
    downloads_schema = Path.home() / 'Downloads' / 'abaco_schema_autodetected.json'
    config_schema = project_root / 'config' / 'abaco_schema_autodetected.json'
    
    # Step 1: Copy schema from Downloads
    if downloads_schema.exists():
        config_schema.parent.mkdir(exist_ok=True)
        shutil.copy2(downloads_schema, config_schema)
        print(f"✅ Copied schema from Downloads to config/")
        
        # Validate the schema content
        with open(config_schema, 'r') as f:
            schema = json.load(f)
        
        datasets = schema.get('datasets', {})
        available_datasets = [name for name, info in datasets.items() if info.get('exists', False)]
        total_records = sum(info.get('rows', 0) for info in datasets.values() if info.get('exists'))
        
        print(f"📊 Schema loaded successfully:")
        print(f"   • Available datasets: {len(available_datasets)}")
        print(f"   • Total records: {total_records:,}")
        
        for name in available_datasets:
            info = datasets[name]
            rows = info.get('rows', 0)
            cols = len(info.get('columns', []))
            print(f"   • {name}: {rows:,} rows, {cols} columns")
        
        return True
    else:
        print(f"❌ Schema file not found at: {downloads_schema}")
        return False

if __name__ == '__main__':
    success = setup_abaco_schema_integration()
    if success:
        print(f"\n🎉 Abaco schema integration ready!")
        print(f"Now you can run: python scripts/complete_integration_test.py")
    else:
        print(f"\n❌ Setup failed. Please check file locations.")
    sys.exit(0 if success else 1)
