#!/usr/bin/env python3
"""
Test to check the actual content of files and diagnose import issues
"""

import os

def check_file_content(filepath):
    """Check the actual content of a file"""
    print(f"\n=== Checking {filepath} ===")
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        print("First 15 lines:")
        for i, line in enumerate(lines[:15], 1):
            print(f"{i:2d}: {line.rstrip()}")
        
        # Check for typing imports
        typing_imports = [line for line in lines if 'typing import' in line or 'from typing' in line]
        if typing_imports:
            print(f"\nTyping imports found:")
            for imp in typing_imports:
                print(f"  {imp.strip()}")
        else:
            print("\n❌ No typing imports found!")
        
        # Check for duplicate imports
        import_lines = [line.strip() for line in lines if line.strip().startswith('from typing import')]
        if len(import_lines) > 1:
            print(f"\n⚠️  Found {len(import_lines)} typing import lines - possible duplicates:")
            for i, imp in enumerate(import_lines, 1):
                print(f"  {i}: {imp}")
                
    else:
        print(f"❌ File does not exist: {filepath}")

def check_module_import(module_name):
    """Test importing a module"""
    print(f"\n=== Testing import of {module_name} ===")
    try:
        import sys
        sys.path.insert(0, 'src')
        __import__(module_name)
        print(f"✅ {module_name} imported successfully")
    except Exception as e:
        print(f"❌ {module_name} import failed: {e}")

if __name__ == "__main__":
    # Check the problematic files
    files_to_check = [
        "src/feature_engineer.py",
        "src/process_portfolio.py",
        "src/metrics_calculator.py"
    ]
    
    for file_path in files_to_check:
        check_file_content(file_path)
    
    print("\n" + "="*60)
    print("TESTING MODULE IMPORTS")
    print("="*60)
    
    # Test module imports
    modules_to_test = [
        "feature_engineer",
        "process_portfolio", 
        "metrics_calculator"
    ]
    
    for module in modules_to_test:
        check_module_import(module)
