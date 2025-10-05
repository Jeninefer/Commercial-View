#!/usr/bin/env python3
"""
Fix missing Dict and Any imports in feature_engineer.py and process_portfolio.py
"""

import os
import re

def fix_typing_imports(filepath):
    """Fix typing imports in a file"""
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    print(f"🔧 Fixing {filepath}...")
    
    # Remove any typing imports inside classes first
    content = re.sub(r'^\s+from typing import.*\n', '', content, flags=re.MULTILINE)
    
    # Check current typing imports at module level
    typing_pattern = r'from typing import ([^\n]+)'
    match = re.search(typing_pattern, content)
    
    if match:
        current_imports = match.group(1)
        # Parse existing imports
        imports = [imp.strip() for imp in current_imports.split(',')]
        
        # Add missing imports
        if 'Dict' not in imports:
            imports.append('Dict')
        if 'Any' not in imports:
            imports.append('Any')
        if 'List' not in imports:
            imports.append('List')
        
        # Update the import line
        new_import_line = f"from typing import {', '.join(sorted(set(imports)))}"
        content = re.sub(typing_pattern, new_import_line, content)
        
    else:
        # Add typing import after pandas/numpy imports
        lines = content.split('\n')
        insert_idx = 0
        
        for i, line in enumerate(lines):
            if line.startswith('import pandas') or line.startswith('import numpy') or line.startswith('from datetime'):
                insert_idx = i + 1
        
        lines.insert(insert_idx, 'from typing import Dict, Any, List')
        content = '\n'.join(lines)
    
    # Write back the fixed content
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"✅ Fixed typing imports in {filepath}")
    return True

if __name__ == "__main__":
    files_to_fix = [
        "src/feature_engineer.py", 
        "src/process_portfolio.py",
        "src/customer_analytics.py"
    ]
    
    print("Fixing missing Dict/Any imports...\n")
    
    for filepath in files_to_fix:
        fix_typing_imports(filepath)
    
    print(f"\n🔍 Run 'python test_modules.py' to verify the fixes.")
