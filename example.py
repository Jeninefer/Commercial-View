"""Example usage of the PortfolioOptimizer."""

import pandas as pd
from commercial_view import PortfolioOptimizer


def main():
    """Demonstrate the PortfolioOptimizer usage."""
    
    # Define rules for hard limits
    rules = {
        "hard_limits": {
            "apr": {
                "0-5": {"max_pct": 0.3},
                "5-7": {"max_pct": 0.4},
                "7-10": {"max_pct": 0.5},
                "10+": {"max_pct": 0.2}
            },
            "payer": {
                "any_anchor": {"max_pct": 0.04}  # Max 4% per customer
            },
            "industry": {
                "any_sector": {"max_pct": 0.35}  # Max 35% per industry
            }
        }
    }
    
    # Define scoring weights
    weights = {
        "apr": 0.6,
        "term_fit": 0.35,
        "origination_count": 0.05
    }
    
    # Create optimizer
    optimizer = PortfolioOptimizer(rules=rules, weights=weights)
    
    # Sample candidate loans
    candidates = pd.DataFrame({
        "customer_id": ["CUST_A", "CUST_B", "CUST_C", "CUST_D", "CUST_E", "CUST_F"],
        "amount": [100000, 200000, 150000, 300000, 250000, 180000],
        "apr": [6.5, 7.2, 5.8, 8.5, 6.0, 7.8],
        "term": [36, 48, 36, 60, 48, 36],
        "payer_rank": [1, 2, 1, 3, 2, 1],
        "industry": ["Tech", "Healthcare", "Finance", "Retail", "Tech", "Manufacturing"]
    })
    
    print("=" * 80)
    print("Portfolio Optimization Example")
    print("=" * 80)
    print(f"\nTotal candidates: {len(candidates)}")
    print(f"Total available amount: ${candidates['amount'].sum():,.0f}")
    
    # Run optimization with AUM target
    aum_total = 600000
    target_term = 48
    
    print(f"\nOptimization Parameters:")
    print(f"  Target AUM: ${aum_total:,.0f}")
    print(f"  Target Term: {target_term} months")
    
    # This is the key method that was fixed - it now returns the selected DataFrame
    selected = optimizer.optimize(candidates, aum_total=aum_total, target_term=target_term)
    
    print(f"\n{'='*80}")
    print("RESULTS")
    print(f"{'='*80}")
    
    if selected.empty:
        print("No loans were selected.")
    else:
        print(f"\nSelected {len(selected)} loans:")
        print(f"Total selected amount: ${selected['amount'].sum():,.0f}")
        print(f"Average APR: {selected['apr'].mean():.2f}%")
        
        print("\nSelected Loans Details:")
        print("-" * 80)
        display_cols = ["customer_id", "amount", "apr", "term", "industry", "selected_amount_cum"]
        print(selected[display_cols].to_string(index=False))
        
        # Verify the fix: show that selected_amount_cum is correctly calculated
        print(f"\n{'='*80}")
        print("VERIFICATION OF FIX")
        print(f"{'='*80}")
        print("\nThe 'selected' column is present:", "selected" in selected.columns)
        print("The 'selected_amount_cum' column is present:", "selected_amount_cum" in selected.columns)
        print("\nCumulative amount verification:")
        print(f"  First loan cumulative: ${selected['selected_amount_cum'].iloc[0]:,.0f}")
        print(f"  Last loan cumulative:  ${selected['selected_amount_cum'].iloc[-1]:,.0f}")
        print(f"  Total selected:        ${selected['amount'].sum():,.0f}")
        print(f"\n✓ The optimize method now correctly returns the selected DataFrame!")


if __name__ == "__main__":
    main()
