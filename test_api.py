#!/usr/bin/env python3
"""Test script to demonstrate the package API changes."""

print("Testing Commercial View Package API")
print("=" * 50)

# Test 1: Import the exported classes
print("\n1. Testing exported classes:")
try:
    from commercial_view import ComprehensiveKPICalculator, KPIConfig
    print("   ✓ Successfully imported ComprehensiveKPICalculator")
    print("   ✓ Successfully imported KPIConfig")
except ImportError as e:
    print(f"   ✗ Failed to import: {e}")
    exit(1)

# Test 2: Verify create_sample_data is NOT exported
print("\n2. Verifying create_sample_data is not in public API:")
try:
    from commercial_view import create_sample_data
    print("   ✗ FAIL: create_sample_data should not be importable!")
    exit(1)
except ImportError:
    print("   ✓ create_sample_data is correctly NOT exported")

# Test 3: Verify create_sample_data is still in the module for internal use
print("\n3. Verifying create_sample_data still exists internally:")
try:
    from commercial_view.comprehensive_kpis import create_sample_data
    print("   ✓ create_sample_data is still available in comprehensive_kpis module")
except ImportError as e:
    print(f"   ✗ Failed: {e}")
    exit(1)

# Test 4: Test actual functionality
print("\n4. Testing KPI Calculator functionality:")
try:
    config1 = KPIConfig(metric_name="revenue", target_value=1000000.0, weight=2.0)
    config2 = KPIConfig(metric_name="customer_satisfaction", target_value=90.0, weight=1.0)
    
    calculator = ComprehensiveKPICalculator([config1, config2])
    
    # Use internal function for test data
    from commercial_view.comprehensive_kpis import create_sample_data
    sample_data = create_sample_data()
    
    results = calculator.calculate_kpi(sample_data)
    overall_score = calculator.get_overall_score(sample_data)
    
    print(f"   ✓ Calculated KPIs for {len(results)} metrics")
    print(f"   ✓ Overall score: {overall_score:.2f}%")
    print(f"   ✓ Revenue achievement: {results['revenue']['achievement_percent']:.2f}%")
    print(f"   ✓ Customer satisfaction achievement: {results['customer_satisfaction']['achievement_percent']:.2f}%")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    exit(1)

print("\n" + "=" * 50)
print("All tests passed! ✓")
print("\nSummary:")
print("- ComprehensiveKPICalculator and KPIConfig are in the public API")
print("- create_sample_data is removed from public API but still available internally")
print("- All functionality works as expected")
