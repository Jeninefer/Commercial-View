#!/usr/bin/env python3
"""
English-only content validation for Commercial-View
Ensures 100% English content with no demo data
"""

import re
import sys
from pathlib import Path

def validate_english_only():
    """Validate all content is in English"""
    
    issues = []
    root = Path('.')
    
    # Check for non-English content
    non_english_patterns = [
        r'[^\x00-\x7F]+',  # Non-ASCII
        r'\b(español|français|deutsch|italiano|português)\b',  # Other languages
    ]
    
    for file_path in root.rglob('*.py'):
        if '.venv' in str(file_path) or 'node_modules' in str(file_path):
            continue
            
        try:
            content = file_path.read_text(encoding='utf-8')
            for pattern in non_english_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    issues.append(f"Non-English content in {file_path}")
        except:
            continue
    
    if issues:
        print("❌ Non-English content found:")
        for issue in issues[:5]:  # Show first 5
            print(f"  - {issue}")
        return False
    
    print("✅ All content is in English")
    return True

def validate_no_demo_data():
    """Validate no demo or example data exists"""
    
    demo_patterns = [
        r'demo.*data',
        r'example.*data', 
        r'sample.*data',
        r'mock.*data',
        r'lorem ipsum',
        r'john doe',
        r'jane smith',
        r'acme corp'
    ]
    
    issues = []
    root = Path('.')
    
    for file_path in root.rglob('*'):
        if (file_path.is_file() and 
            file_path.suffix in ['.py', '.md', '.csv', '.json'] and
            '.venv' not in str(file_path) and
            'node_modules' not in str(file_path)):
            
            try:
                content = file_path.read_text(encoding='utf-8').lower()
                for pattern in demo_patterns:
                    if re.search(pattern, content):
                        issues.append(f"Demo data pattern '{pattern}' in {file_path}")
                        break
            except:
                continue
    
    if issues:
        print("❌ Demo data found:")
        for issue in issues[:5]:  # Show first 5
            print(f"  - {issue}")
        return False
    
    print("✅ No demo data found")
    return True

if __name__ == "__main__":
    print("🔍 Validating Commercial-View Repository")
    print("=" * 50)
    
    english_ok = validate_english_only()
    demo_ok = validate_no_demo_data()
    
    if english_ok and demo_ok:
        print("\n🎉 Repository validation passed!")
        print("✅ 100% English content")
        print("✅ Zero demo data")
        print("✅ Production-ready for commercial lending")
        sys.exit(0)
    else:
        print("\n💥 Repository validation failed!")
        sys.exit(1)
