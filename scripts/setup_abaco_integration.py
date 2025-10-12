"""
Setup script for comprehensive Abaco integration
Copies schema file and validates integration
"""

import json
import shutil
from pathlib import Path
import logging
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

def setup_abaco_integration():
    """Complete Abaco integration setup."""
    
    print("🏦 Commercial-View Abaco Integration Setup")
    print("=" * 50)
    
    # Source and destination paths
    source_path = Path.home() / 'Downloads' / 'abaco_schema_autodetected.json'
    config_dir = Path(__file__).parent.parent / 'config'
    dest_path = config_dir / 'abaco_schema_autodetected.json'
    
    success_steps = 0
    total_steps = 4
    
    # Step 1: Check source file
    print("📂 Step 1: Checking schema file...")
    if source_path.exists():
        print(f"   ✅ Found schema file: {source_path}")
        success_steps += 1
    else:
        print(f"   ❌ Schema file not found: {source_path}")
        print("   📥 Please download abaco_schema_autodetected.json to Downloads folder")
        return False
    
    # Step 2: Copy to config directory
    print("📁 Step 2: Setting up config directory...")
    try:
        config_dir.mkdir(exist_ok=True)
        shutil.copy2(source_path, dest_path)
        print(f"   ✅ Schema copied to: {dest_path}")
        success_steps += 1
    except Exception as e:
        print(f"   ❌ Error copying schema: {e}")
        return False
    
    # Step 3: Validate schema content
    print("🔍 Step 3: Validating schema...")
    try:
        with open(dest_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        
        datasets = schema.get('datasets', {})
        available_datasets = {name: info for name, info in datasets.items() if info.get('exists')}
        
        print("   ✅ Schema loaded successfully")
        print(f"   📊 Available datasets: {len(available_datasets)}")
        
        # Display dataset details
        total_records = 0
        for dataset_name, dataset_info in available_datasets.items():
            rows = dataset_info.get('rows', 0)
            cols = len(dataset_info.get('columns', []))
            total_records += rows
            print(f"      - {dataset_name}: {rows:,} rows, {cols} columns")
        
        print(f"   📈 Total records: {total_records:,}")
        success_steps += 1
        
    except Exception as e:
        print(f"   ❌ Schema validation error: {e}")
        return False
    
    # Step 4: Test integration
    print("🧪 Step 4: Testing integration...")
    try:
        # Test import
        from src import get_abaco_schema_info, setup_abaco_integration as test_setup
        
        schema_info = get_abaco_schema_info()
        if schema_info.get('available'):
            print("   ✅ Integration test passed")
            print(f"   📍 Schema path: {schema_info.get('schema_path')}")
            success_steps += 1
        else:
            print(f"   ⚠️  Integration available but with issues: {schema_info.get('reason')}")
            success_steps += 0.5
            
    except Exception as e:
        print(f"   ❌ Integration test failed: {e}")
        return False
    
    # Summary
    print("\n" + "=" * 50)
    print(f"🎯 Setup Summary: {success_steps}/{total_steps} steps completed")
    
    if success_steps == total_steps:
        print("✅ Abaco integration setup COMPLETE!")
        print("\n🚀 You can now:")
        print("   • Load Abaco loan tape data with schema validation")
        print("   • Process 48,853+ loan records with automated risk scoring")
        print("   • Generate comprehensive portfolio analytics")
        print("   • Export validated results in multiple formats")
        
        # Show next steps
        print("\n📋 Next Steps:")
        print("   1. Place Abaco CSV files in data/ directory:")
        print("      - Abaco - Loan Tape_Loan Data_Table.csv")
        print("      - Abaco - Loan Tape_Historic Real Payment_Table.csv")
        print("      - Abaco - Loan Tape_Payment Schedule_Table.csv")
        print("   2. Run: python portfolio.py --abaco-only")
        print("   3. Check results in abaco_runtime/exports/")
        
        return True
    else:
        print("⚠️  Setup completed with some issues")
        print("   Review errors above and retry if needed")
        return False

if __name__ == '__main__':
    success = setup_abaco_integration()
    sys.exit(0 if success else 1)
