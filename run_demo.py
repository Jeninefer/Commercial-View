#!/usr/bin/env python3
"""
Demo runner for Commercial-View portfolio processing
Creates configuration and runs the analysis
"""

import os
import subprocess
import sys
from pathlib import Path

def create_demo_config():
    """Create a minimal configuration for demo"""
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    # Create minimal export config
    export_config = """export_paths:
  base_path: './abaco_runtime/exports'
  kpi_json: './abaco_runtime/exports/kpi/json'
  kpi_csv: './abaco_runtime/exports/kpi/csv'
"""
    
    with open(config_dir / "export_config.yml", 'w') as f:
        f.write(export_config)
    
    # Create minimal column maps config
    column_config = """loan_columns:
  customer_id: customer_id
  outstanding_balance: outstanding_balance
  apr: apr
"""
    
    with open(config_dir / "column_maps.yml", 'w') as f:
        f.write(column_config)
    
    print("✅ Created demo configuration files")
    return str(config_dir)

def check_prerequisites():
    """Check if all required modules can be imported"""
    print("🔍 Checking prerequisites...")
    sys.path.insert(0, 'src')
    
    required_modules = [
        'feature_engineer',
        'loan_analytics', 
        'metrics_calculator',
        'google_drive_exporter'
    ]
    
    failed_modules = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except Exception as e:
            print(f"  ❌ {module}: {e}")
            failed_modules.append(module)
    
    if failed_modules:
        print(f"⚠️  {len(failed_modules)} modules failed to import")
        return False
    else:
        print("✅ All prerequisites satisfied")
        return True

if __name__ == "__main__":
    print("🔧 Setting up Commercial-View demo...")
    
    # Check prerequisites first
    if not check_prerequisites():
        print("❌ Prerequisites not met. Please fix import issues first.")
        sys.exit(1)
    
    config_path = create_demo_config()
    
    print("🚀 Running Commercial-View portfolio processing...")
    try:
        # Use sys.executable to ensure we use the same Python interpreter
        result = subprocess.run([
            sys.executable, "src/process_portfolio.py", 
            "--config", config_path
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        print("=" * 60)
        print("ANALYSIS OUTPUT:")
        print("=" * 60)
        print(result.stdout)
        
        if result.stderr:
            print("=" * 60)
            print("WARNINGS/ERRORS:")
            print("=" * 60)
            print(result.stderr)
            
        if result.returncode != 0:
            print(f"❌ Process failed with return code: {result.returncode}")
        else:
            print("\n" + "=" * 60)
            print("✅ Commercial-View analysis completed successfully!")
            print("✅ Check ./abaco_runtime/exports/ for generated files")
            print("📊 Analysis includes:")
            print("   • Customer segmentation (New/Recurrent/Recovered)")
            print("   • Cohort retention analysis")
            print("   • Weighted portfolio metrics")
            print("   • Google Drive export manifests")
            print("=" * 60)
            
    except Exception as e:
        print(f"❌ Error running analysis: {e}")
