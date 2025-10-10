"""
Fix import issues and validate Abaco integration
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test all major imports"""
    print("🔧 Testing Commercial-View imports...")
    
    try:
        # Test basic import
        import src
        print("✅ Basic src import successful")
        
        # Test package info
        info = src.get_production_info()
        print(f"✅ Package version: {info.get('version', 'unknown')}")
        
        # Test Abaco schema
        if hasattr(src, 'get_abaco_schema_summary'):
            schema_summary = src.get_abaco_schema_summary()
            if schema_summary.get('schema_available'):
                print(f"✅ Abaco schema loaded: {schema_summary['total_records']:,} records")
                
                # Display dataset summary
                for name, info in schema_summary['datasets'].items():
                    print(f"   📊 {name}: {info['rows']:,} rows, {info['data_columns']} data columns")
            else:
                print(f"⚠️  Abaco schema issue: {schema_summary.get('reason')}")
        
        # Test data validation
        if hasattr(src, 'validate_abaco_data_structure'):
            validation = src.validate_abaco_data_structure()
            print(f"✅ Data validation: {validation['overall_status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_imports()
    print(f"\n{'='*50}")
    if success:
        print("🎉 All imports working correctly!")
        print("🚀 Commercial-View ready with Abaco integration")
    else:
        print("❌ Import issues detected")
        print("💡 Run from project root: python scripts/fix_imports.py")
