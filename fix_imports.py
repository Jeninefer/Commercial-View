#!/usr/bin/env python3
"""
Quick fix for Dict/Any import issues in feature_engineer.py and process_portfolio.py
"""

import os
from pathlib import Path

def fix_file(filepath: Path) -> bool:
    """Fix typing imports in a specific file"""
    path = Path(filepath)
    if not path.exists():
        print(f"❌ File not found: {path}")
        return False
        
    original_content = path.read_text()
    lines = original_content.splitlines()
    typing_lines = []
    clean_lines = []
    
    for line in lines:
        if line.strip().startswith('from typing import'):
            typing_lines.append(line.strip())
        else:
            clean_lines.append(line)
    
    if typing_lines:
        all_imports = set()
        for line in typing_lines:
            imports = line.replace('from typing import', '').strip()
            for imp in imports.split(','):
                all_imports.add(imp.strip())
        
        all_imports.update(['Any', 'Dict', 'Optional'])
        consolidated = f"from typing import {', '.join(sorted(all_imports))}"
        
        import_end = 0
        for i, line in enumerate(clean_lines):
            if line.startswith('import ') or (line.startswith('from ') and 'typing' not in line):
                import_end = i
        
        clean_lines.insert(import_end + 1, consolidated)
    
    fixed_content = '\n'.join(clean_lines)
    if fixed_content == original_content.rstrip('\n'):
        print(f"ℹ️ No changes needed: {path}")
        return False

    path.write_text(fixed_content + '\n')
    print(f"✅ Fixed {path}")
    return True

if __name__ == "__main__":
    files_to_fix = [
        Path("src/feature_engineer.py"),
        Path("src/process_portfolio.py")
    ]
    
    print("Fixing typing import issues...")
    for filepath in files_to_fix:
        fix_file(filepath)
    
    print("\n🔍 Run 'python test_modules.py' to verify the fixes.")
    
    print("Fixing typing import issues...")
    for filepath in files_to_fix:
        fix_file(filepath)
    
    print("\n🔍 Run 'python test_modules.py' to verify the fixes.")
