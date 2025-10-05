#!/usr/bin/env python3
"""
Test all Commercial-View modules for import errors
"""

import sys
sys.path.append('src')

def test_module_import(module_name):
    """Test importing a single module"""
    try:
        __import__(module_name)
        return True, None
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    modules_to_test = [
        'dpd_analyzer',
        'loan_analytics', 
        'metrics_calculator',
        'customer_analytics',
        'evergreen',
        'feature_engineer',
        'abaco_core',
        'portfolio_optimizer',
        'payment_processor',
        'pricing_enricher',
        'process_portfolio'
    ]
    
    print("Testing Commercial-View modules...")
    print("=" * 50)
    
    success_count = 0
    total_count = len(modules_to_test)
    
    for module in modules_to_test:
        success, error = test_module_import(module)
        if success:
            print(f"{module}: Imported successfully")
            success_count += 1
        else:
            print(f"{module}: Error - {error}")
    
    print("=" * 50)
    print(f"Test Results: {success_count}/{total_count} modules working correctly")
    
    if success_count == total_count:
        print("All modules working perfectly!")
    else:
        print("Some modules need attention.")
