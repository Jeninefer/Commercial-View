"""Debug script to understand why no loans are being selected."""

import pandas as pd
import numpy as np
from commercial_view import PortfolioOptimizer


def main():
    """Debug the optimization."""
    
    # More relaxed rules
    rules = {
        "hard_limits": {
            "apr": {
                "0-5": {"max_pct": 0.5},
                "5-7": {"max_pct": 0.6},
                "7-10": {"max_pct": 0.7},
                "10+": {"max_pct": 0.3}
            },
            "payer": {
                "any_anchor": {"max_pct": 0.25}  # Max 25% per customer
            },
            "industry": {
                "any_sector": {"max_pct": 0.5}  # Max 50% per industry
            }
        }
    }
    
    weights = {
        "apr": 0.6,
        "term_fit": 0.35,
        "origination_count": 0.05
    }
    
    optimizer = PortfolioOptimizer(rules=rules, weights=weights)
    
    # Simpler test case
    candidates = pd.DataFrame({
        "customer_id": ["A", "B", "C"],
        "amount": [100000, 200000, 150000],
        "apr": [6.5, 7.2, 5.8],
        "term": [36, 48, 36],
        "payer_rank": [1, 2, 1],
        "industry": ["Tech", "Healthcare", "Finance"]
    })
    
    print("Test candidates:")
    print(candidates)
    
    selected = optimizer.optimize(candidates, aum_total=400000, target_term=48)
    
    print(f"\nSelected {len(selected)} loans")
    if not selected.empty:
        print("\nSelected loans:")
        print(selected[["customer_id", "amount", "apr", "selected", "selected_amount_cum"]])
        print(f"\nTotal: ${selected['amount'].sum():,.0f}")
        print("\n✓ SUCCESS: The method returns the selected DataFrame with required columns!")
    else:
        print("\nNo loans selected - constraints may be too strict")
        print("But the method still returns a DataFrame (even if empty)")
        print(f"Return type: {type(selected)}")
        print(f"Is DataFrame: {isinstance(selected, pd.DataFrame)}")


if __name__ == "__main__":
    main()
