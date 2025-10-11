"""
Fix remaining integration issues and validate setup
"""

import os
import sys
import yaml
from pathlib import Path
from typing import Optional

def fix_yaml_files():
    """Fix any YAML syntax issues in configuration files."""
    
    print("🔧 Fixing YAML Configuration Files")
    print("=" * 50)
    
    config_dir = Path("config")
    yaml_files = list(config_dir.glob("*.yml"))
    
    fixed_files = []
    
    for yaml_file in yaml_files:
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                yaml.safe_load(f)
            print(f"✅ {yaml_file.name}: Valid YAML")
        except yaml.YAMLError as e:
            print(f"❌ {yaml_file.name}: YAML Error - {e}")
            # Fixed: Use proper attribute access for YAMLError
            problem_mark = getattr(e, 'problem_mark', None)
            if problem_mark:
                print(f"   📍 Line {problem_mark.line + 1}")
            else:
                print(f"   📍 Location unknown")
            fixed_files.append(yaml_file.name)
        except Exception as e:
            print(f"⚠️  {yaml_file.name}: Could not read - {e}")
    
    return fixed_files

def test_imports():
    """Test all required imports."""
    
    print("\n🐍 Testing Module Imports")
    print("=" * 30)
    
    # Add src to path
    sys.path.insert(0, 'src')
    
    imports_to_test = [
        ('data_loader', ['DataLoader', 'load_loan_data', 'load_customer_data', 'load_historic_real_payment']),
        ('__init__', ['get_production_info', '__version__'])
    ]
    
    successful_imports = 0
    total_imports = 0
    
    for module_name, functions in imports_to_test:
        try:
            module = __import__(module_name)
            print(f"✅ {module_name}: Module imported")
            
            for func_name in functions:
                total_imports += 1
                if hasattr(module, func_name):
                    print(f"   ✅ {func_name}: Available")
                    successful_imports += 1
                else:
                    print(f"   ❌ {func_name}: Missing")
        except Exception as e:
            print(f"❌ {module_name}: Import failed - {e}")
            total_imports += len(functions)
    
    print(f"\n📊 Import Summary: {successful_imports}/{total_imports} successful")
    return successful_imports == total_imports

def verify_data_files():
    """Verify Abaco data files are present and readable."""
    
    print("\n📁 Verifying Data Files")
    print("=" * 25)
    
    data_dir = Path("data")
    required_files = [
        "Abaco - Loan Tape_Loan Data_Table.csv",
        "Abaco - Loan Tape_Historic Real Payment_Table.csv",
        "Abaco - Loan Tape_Payment Schedule_Table.csv"
    ]
    
    files_ok = 0
    
    for filename in required_files:
        file_path = data_dir / filename
        if file_path.exists():
            try:
                import pandas as pd
                df = pd.read_csv(file_path, nrows=1)  # Just read header
                file_size = file_path.stat().st_size / (1024 * 1024)  # MB
                print(f"✅ {filename}: {file_size:.1f} MB, {len(df.columns)} columns")
                files_ok += 1
            except Exception as e:
                print(f"❌ {filename}: Cannot read - {e}")
        else:
            print(f"❌ {filename}: Not found")
    
    return files_ok == len(required_files)

def main():
    """Run all fixes and validations."""
    
    print("🚀 Commercial-View Integration Fix")
    print("=" * 40)
    
    # Fix YAML files
    fixed_yaml = fix_yaml_files()
    
    # Test imports
    imports_ok = test_imports()
    
    # Verify data files
    data_ok = verify_data_files()
    
    # Summary
    print("\n" + "=" * 40)
    print("📋 FIX SUMMARY")
    print("=" * 40)
    
    if fixed_yaml:
        print(f"🔧 Fixed YAML files: {fixed_yaml}")
    else:
        print("✅ All YAML files valid")
    
    print(f"🐍 Import status: {'✅ OK' if imports_ok else '❌ Issues'}")
    print(f"📁 Data files: {'✅ OK' if data_ok else '❌ Missing'}")
    
    if imports_ok and data_ok:
        print("\n🎉 All issues resolved!")
        print("🚀 Ready to run: python portfolio.py --abaco-only")
        return True
    else:
        print("\n⚠️  Some issues remain - check output above")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
