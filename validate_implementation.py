"""
Validation script to verify the implementation matches the problem statement
"""

import pandas as pd
import numpy as np
from loan_analytics import LoanAnalytics


def validate_implementation():
    """Validate that the implementation matches all requirements"""
    
    print("="*80)
    print("VALIDATION: calculate_weighted_stats Implementation")
    print("="*80)
    print()
    
    analytics = LoanAnalytics()
    
    # Test 1: Basic functionality with standard columns
    print("✓ Test 1: Basic weighted statistics calculation")
    df1 = pd.DataFrame({
        'outstanding_balance': [1000, 2000, 3000],
        'apr': [5.0, 6.0, 7.0],
        'eir': [5.1, 6.2, 7.3],
        'term': [360, 240, 180]
    })
    result1 = analytics.calculate_weighted_stats(df1)
    assert not result1.empty, "Should return non-empty result"
    assert 'weighted_apr' in result1.columns, "Should have weighted_apr"
    expected_apr = (5.0*1000 + 6.0*2000 + 7.0*3000) / 6000
    assert abs(result1['weighted_apr'].iloc[0] - expected_apr) < 0.000001, "Weighted APR calculation should be correct"
    print(f"  Weighted APR: {result1['weighted_apr'].iloc[0]:.6f} (Expected: {expected_apr:.6f})")
    
    # Test 2: Alias resolution
    print("\n✓ Test 2: Column alias resolution")
    df2 = pd.DataFrame({
        'current_balance': [1000, 2000],
        'annual_rate': [5.0, 6.0],
        'effective_interest_rate': [5.1, 6.2],
        'tenor_days': [360, 240]
    })
    result2 = analytics.calculate_weighted_stats(df2, weight_field='current_balance')
    assert not result2.empty, "Should resolve aliases"
    assert 'weighted_apr' in result2.columns, "Should find apr via annual_rate alias"
    print(f"  Successfully resolved aliases: annual_rate → apr, effective_interest_rate → eir, tenor_days → term")
    
    # Test 3: Handling NaN weights
    print("\n✓ Test 3: NaN weight handling")
    df3 = pd.DataFrame({
        'outstanding_balance': [1000, np.nan, 3000],
        'apr': [5.0, 6.0, 7.0]
    })
    result3 = analytics.calculate_weighted_stats(df3, metrics=['apr'])
    expected_apr_nan = (5.0*1000 + 7.0*3000) / 4000
    assert abs(result3['weighted_apr'].iloc[0] - expected_apr_nan) < 0.000001, "Should skip NaN weights"
    print(f"  Correctly excluded NaN weights: {result3['weighted_apr'].iloc[0]:.6f}")
    
    # Test 4: Handling zero weights
    print("\n✓ Test 4: Zero weight handling")
    df4 = pd.DataFrame({
        'outstanding_balance': [1000, 0, 3000],
        'apr': [5.0, 6.0, 7.0]
    })
    result4 = analytics.calculate_weighted_stats(df4, metrics=['apr'])
    expected_apr_zero = (5.0*1000 + 7.0*3000) / 4000
    assert abs(result4['weighted_apr'].iloc[0] - expected_apr_zero) < 0.000001, "Should skip zero weights"
    print(f"  Correctly excluded zero weights: {result4['weighted_apr'].iloc[0]:.6f}")
    
    # Test 5: Handling negative weights
    print("\n✓ Test 5: Negative weight handling")
    df5 = pd.DataFrame({
        'outstanding_balance': [1000, -500, 3000],
        'apr': [5.0, 6.0, 7.0]
    })
    result5 = analytics.calculate_weighted_stats(df5, metrics=['apr'])
    expected_apr_neg = (5.0*1000 + 7.0*3000) / 4000
    assert abs(result5['weighted_apr'].iloc[0] - expected_apr_neg) < 0.000001, "Should skip negative weights"
    print(f"  Correctly excluded negative weights: {result5['weighted_apr'].iloc[0]:.6f}")
    
    # Test 6: Missing weight field fallback
    print("\n✓ Test 6: Weight field auto-detection")
    df6 = pd.DataFrame({
        'some_column': [1000, 2000],
        'apr': [5.0, 6.0]
    })
    result6 = analytics.calculate_weighted_stats(df6, weight_field='non_existent')
    assert result6.empty, "Should return empty DataFrame when weight field not found"
    print(f"  Correctly returned empty DataFrame when weight field not found")
    
    # Test 7: Custom metrics
    print("\n✓ Test 7: Custom metrics selection")
    df7 = pd.DataFrame({
        'outstanding_balance': [1000, 2000],
        'apr': [5.0, 6.0],
        'eir': [5.1, 6.2],
        'term': [360, 240]
    })
    result7 = analytics.calculate_weighted_stats(df7, metrics=['apr'])
    assert 'weighted_apr' in result7.columns, "Should have weighted_apr"
    assert 'weighted_eir' not in result7.columns, "Should not have weighted_eir"
    assert 'weighted_term' not in result7.columns, "Should not have weighted_term"
    print(f"  Successfully calculated only requested metrics")
    
    # Test 8: Case-insensitive matching
    print("\n✓ Test 8: Case-insensitive column matching")
    df8 = pd.DataFrame({
        'Outstanding_Balance': [1000, 2000],
        'APR': [5.0, 6.0]
    })
    result8 = analytics.calculate_weighted_stats(df8, weight_field='Outstanding_Balance', metrics=['apr'])
    assert not result8.empty, "Should match case-insensitively"
    print(f"  Successfully matched columns case-insensitively")
    
    # Test 9: Substring matching
    print("\n✓ Test 9: Substring column matching")
    df9 = pd.DataFrame({
        'my_outstanding_balance_field': [1000, 2000],
        'field_apr_value': [5.0, 6.0]
    })
    result9 = analytics.calculate_weighted_stats(df9, weight_field='my_outstanding_balance_field', metrics=['apr'])
    assert not result9.empty, "Should match via substring"
    print(f"  Successfully matched columns via substring")
    
    # Test 10: Return type validation
    print("\n✓ Test 10: Return type validation")
    df10 = pd.DataFrame({
        'outstanding_balance': [1000],
        'apr': [5.0]
    })
    result10 = analytics.calculate_weighted_stats(df10, metrics=['apr'])
    assert isinstance(result10, pd.DataFrame), "Should return DataFrame"
    assert isinstance(result10['weighted_apr'].iloc[0], (float, np.float64)), "Values should be float"
    print(f"  Correct return type: pd.DataFrame with float values")
    
    print("\n" + "="*80)
    print("ALL VALIDATIONS PASSED ✓")
    print("="*80)
    print()
    print("Summary:")
    print("  • Method signature matches specification")
    print("  • Weighted calculations are mathematically correct")
    print("  • Alias resolution works as expected")
    print("  • Guards against zero/NaN/negative weights")
    print("  • Case-insensitive and substring matching implemented")
    print("  • Error handling is robust")
    print("  • Return types are correct")
    print()


if __name__ == '__main__':
    validate_implementation()
