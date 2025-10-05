#!/usr/bin/env python3
"""
Quick diagnostic and fix for the Dict/Any import issues
"""

import os
import sys

def fix_typing_imports():
    """Fix typing imports in problematic files"""
    
    files_to_fix = [
        "src/feature_engineer.py",
        "src/process_portfolio.py"
    ]
    
    for filepath in files_to_fix:
        if not os.path.exists(filepath):
            print(f"❌ File not found: {filepath}")
            continue
            
        print(f"🔧 Fixing {filepath}...")
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Remove duplicate typing imports first
        lines = content.split('\n')
        typing_imports = []
        cleaned_lines = []
        
        for line in lines:
            if line.strip().startswith('from typing import'):
                if line not in typing_imports:
                    typing_imports.append(line)
            else:
                cleaned_lines.append(line)
        
        # Rebuild content with single typing import
        if typing_imports:
            # Find the right place to insert the consolidated import
            import_end = 0
            for i, line in enumerate(cleaned_lines):
                if line.startswith('import ') or line.startswith('from ') and not line.startswith('from typing'):
                    import_end = i
            
            # Create consolidated typing import
            consolidated_import = 'from typing import Dict, Any, Optional'
            cleaned_lines.insert(import_end + 1, consolidated_import)
        
        # Write back the fixed content
        content = '\n'.join(cleaned_lines)
        with open(filepath, 'w') as f:
            f.write(content)
        
        print(f"  ✅ Fixed {filepath}")

def test_imports():
    """Test if the fixed files can be imported"""
    print("\n🔍 Testing imports...")
    sys.path.insert(0, 'src')
    
    modules_to_test = ['feature_engineer', 'process_portfolio']
    
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"  ✅ {module} imported successfully")
        except Exception as e:
            print(f"  ❌ {module} failed: {e}")

if __name__ == "__main__":
    print("Fixing typing import issues...")
    fix_typing_imports()
    test_imports()
    print("\n✅ All fixes applied. Try running the tests again.")
