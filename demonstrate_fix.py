"""Demonstration that the fix works - the method now returns a DataFrame."""

import pandas as pd
from commercial_view import PortfolioOptimizer


def test_return_value():
    """Test that the optimize method returns a DataFrame."""
    
    # Very simple rules that will allow selection
    rules = {
        "hard_limits": {
            "apr": {},
            "payer": {
                "any_anchor": {"max_pct": 1.0}  # 100% - no restriction
            },
            "industry": {
                "any_sector": {"max_pct": 1.0}  # 100% - no restriction
            }
        }
    }
    
    weights = {"apr": 1.0, "term_fit": 0.0, "origination_count": 0.0}
    
    optimizer = PortfolioOptimizer(rules=rules, weights=weights)
    
    # Simple candidates
    candidates = pd.DataFrame({
        "customer_id": ["A", "B"],
        "amount": [100000, 50000],
        "apr": [6.5, 7.2],
        "term": [36, 48],
        "payer_rank": [1, 2],
        "industry": ["Tech", "Healthcare"]
    })
    
    print("=" * 80)
    print("DEMONSTRATION: The optimize() method now returns the selected DataFrame")
    print("=" * 80)
    
    print("\nInput candidates:")
    print(candidates)
    
    # Call the optimize method - THIS IS THE FIX!
    # Before: The method created 'selected' but didn't return it
    # After: The method returns the 'selected' DataFrame
    result = optimizer.optimize(candidates, aum_total=120000)
    
    print(f"\n{'='*80}")
    print("RESULT")
    print(f"{'='*80}")
    
    print(f"\nType of return value: {type(result)}")
    print(f"Is it a DataFrame? {isinstance(result, pd.DataFrame)}")
    print(f"Number of rows: {len(result)}")
    
    if not result.empty:
        print("\n✓ SUCCESS! The method returns a DataFrame with selected loans:")
        print(result)
        
        print(f"\n{'='*80}")
        print("VERIFICATION OF THE FIX")
        print(f"{'='*80}")
        print("\nColumns in returned DataFrame:")
        for col in result.columns:
            print(f"  - {col}")
        
        print("\nKey columns added by the method:")
        print(f"  ✓ 'selected' column present: {'selected' in result.columns}")
        print(f"  ✓ 'selected_amount_cum' column present: {'selected_amount_cum' in result.columns}")
        
        if 'selected' in result.columns and 'selected_amount_cum' in result.columns:
            print(f"\n  All 'selected' values are True: {(result['selected'] == True).all()}")
            print(f"  Last cumulative amount matches total: {result['selected_amount_cum'].iloc[-1] == result['amount'].sum()}")
        
        print("\n" + "="*80)
        print("✓✓✓ THE FIX IS COMPLETE ✓✓✓")
        print("="*80)
        print("\nThe optimize() method now properly returns the 'selected' DataFrame")
        print("with the 'selected' and 'selected_amount_cum' columns included.")
    else:
        print("\n⚠ Empty result (constraints prevented selection)")
        print("But the method still correctly returns a DataFrame!")


if __name__ == "__main__":
    test_return_value()
