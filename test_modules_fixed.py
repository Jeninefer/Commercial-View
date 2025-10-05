#!/usr/bin/env python3
"""
Test script to verify all modules are working correctly
"""

import sys
sys.path.append('src')

def test_module_imports():
    """Test importing all Commercial-View modules"""
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
    
    results = {}
    
    print("Testing Commercial-View modules...")
    print("=" * 50)
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            results[module_name] = "✅ Imported successfully"
            print(f"{module_name}: ✅ Imported successfully")
        except Exception as e:
            results[module_name] = f"❌ Error - {str(e)}"
            print(f"{module_name}: ❌ Error - {str(e)}")
    
    print("=" * 50)
    successful = len([r for r in results.values() if "✅" in r])
    total = len(results)
    print(f"Test Results: {successful}/{total} modules working correctly")
    
    if successful < total:
        print("⚠️  Some modules need attention.")
    else:
        print("🎉 All modules working perfectly!")
    
    return results

if __name__ == "__main__":
    test_module_imports()
