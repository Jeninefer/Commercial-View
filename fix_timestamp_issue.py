#!/usr/bin/env python3
"""
Fix the Timestamp serialization issue in process_portfolio.py
"""

import os
import re

def fix_comprehensive_analysis():
    """Add datetime conversion to comprehensive_analysis function"""
    filepath = "src/process_portfolio.py"
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Check if fix is already applied
    if "pd.api.types.is_datetime64_any_dtype" in content:
        print("✅ Timestamp fix already applied")
        return True
    
    # Find the comprehensive_analysis function
    func_start = content.find("def comprehensive_analysis(")
    if func_start == -1:
        print("❌ Could not find comprehensive_analysis function")
        return False
    
    # Find where cohort_dict is defined
    pattern = r"(\s+)cohort_dict = cohort_retention\.to_dict\(\) if not cohort_retention\.empty else \{\}"
    match = re.search(pattern, content)
    
    if not match:
        # Try alternative pattern
        pattern = r"(\s+)'cohort_retention_matrix': cohort_retention\.to_dict\(\) if not cohort_retention\.empty else \{\},"
        match = re.search(pattern, content)
        
        if match:
            # Inline version - need to extract and fix
            indent = match.group(1)
            
            new_code = f'''{indent}# Convert cohort retention matrix to JSON-serializable format
{indent}cohort_dict = {{}}
{indent}if not cohort_retention.empty:
{indent}    cohort_retention_reset = cohort_retention.reset_index()
{indent}    for col in cohort_retention_reset.columns:
{indent}        if pd.api.types.is_datetime64_any_dtype(cohort_retention_reset[col]):
{indent}            cohort_retention_reset[col] = cohort_retention_reset[col].astype(str)
{indent}    cohort_dict = cohort_retention_reset.to_dict('records')
{indent}
{indent}'cohort_retention_matrix': cohort_dict,'''
            
            content = content.replace(match.group(0), new_code)
        else:
            print("❌ Could not find cohort_retention code pattern")
            print("\nSearching for 'cohort_retention' in file...")
            if 'cohort_retention' in content:
                print("Found 'cohort_retention' - manual inspection needed")
                # Show context around cohort_retention
                idx = content.find('cohort_retention')
                print(content[max(0, idx-200):idx+200])
            return False
    else:
        indent = match.group(1)
        
        new_code = f'''{indent}# Convert cohort retention matrix to JSON-serializable format
{indent}cohort_dict = {{}}
{indent}if not cohort_retention.empty:
{indent}    cohort_retention_reset = cohort_retention.reset_index()
{indent}    for col in cohort_retention_reset.columns:
{indent}        if pd.api.types.is_datetime64_any_dtype(cohort_retention_reset[col]):
{indent}            cohort_retention_reset[col] = cohort_retention_reset[col].astype(str)
{indent}    cohort_dict = cohort_retention_reset.to_dict('records')'''
        
        content = content.replace(match.group(0), new_code)
    
    # Write back
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"✅ Fixed Timestamp serialization in {filepath}")
    return True

if __name__ == "__main__":
    print("Fixing Timestamp serialization issue...")
    print("=" * 50)
    if fix_comprehensive_analysis():
        print("\n🎉 Fix applied successfully!")
        print("\nNow run:")
        print("   python src/process_portfolio.py --config ./configs")
    else:
        print("\n⚠️  Automatic fix failed")
        print("\nPlease manually add this code to comprehensive_analysis():")
        print("""
    # Convert cohort retention matrix to JSON-serializable format
    cohort_dict = {}
    if not cohort_retention.empty:
        cohort_retention_reset = cohort_retention.reset_index()
        for col in cohort_retention_reset.columns:
            if pd.api.types.is_datetime64_any_dtype(cohort_retention_reset[col]):
                cohort_retention_reset[col] = cohort_retention_reset[col].astype(str)
        cohort_dict = cohort_retention_reset.to_dict('records')
        """)
