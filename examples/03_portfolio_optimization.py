"""
Example: Portfolio optimization

Demonstrates how to use the PortfolioOptimizer to select deals that optimize
the portfolio mix while respecting constraints.
"""

import pandas as pd
from abaco_core.optimizer import PortfolioOptimizer


def main():
    # Initialize optimizer
    optimizer = PortfolioOptimizer()
    print("Portfolio Optimizer initialized\n")
    
    # ===== Current Portfolio =====
    print("=== Current Portfolio ===")
    current_portfolio = pd.DataFrame({
        "deal_id": ["D100", "D101", "D102", "D103", "D104"],
        "amount": [100000, 150000, 75000, 50000, 125000],
        "apr_bucket": ["35-40", "40-45", "30-35", "45-50", "35-40"],
        "line_bucket": ["<=100k", ">100k", "<=50k", "<=50k", ">100k"],
        "industry": ["Manufacturing", "Services", "Retail", "Manufacturing", "Services"],
        "payer_id": ["P10", "P11", "P12", "P13", "P14"],
        "term_months": [12, 15, 18, 12, 15]
    })
    
    print(f"Current portfolio: {len(current_portfolio)} deals, ${current_portfolio['amount'].sum():,.0f} total")
    
    # ===== Candidate Deals =====
    print("\n=== Candidate Deals ===")
    candidates = pd.DataFrame({
        "deal_id": ["D001", "D002", "D003", "D004", "D005", "D006", "D007"],
        "amount": [25000, 50000, 75000, 30000, 60000, 40000, 55000],
        "apr_bucket": ["35-40", "40-45", "30-35", "45-50", "40-45", "35-40", "50-60"],
        "line_bucket": ["<=50k", "<=100k", ">100k", "<=50k", "<=100k", "<=50k", "<=100k"],
        "industry": ["Manufacturing", "Retail", "Services", "Other", "Retail", "Services", "Manufacturing"],
        "payer_id": ["P1", "P2", "P3", "P4", "P5", "P6", "P7"],
        "term_months": [12, 18, 15, 12, 15, 18, 12]
    })
    
    print(f"Candidate deals: {len(candidates)} available, ${candidates['amount'].sum():,.0f} total")
    
    # ===== Optimize Selection =====
    print("\n=== Running Optimization ===")
    max_amount = 150000
    print(f"Maximum allocation: ${max_amount:,.0f}")
    
    selected = optimizer.optimize(candidates, current_portfolio, max_amount)
    
    if not selected.empty:
        print(f"\nSelected {len(selected)} deals:")
        for _, deal in selected.iterrows():
            print(f"  {deal['deal_id']}: ${deal['amount']:,.0f} @ {deal['apr_bucket']} APR, "
                  f"{deal['industry']}, {deal['term_months']}mo")
        print(f"\nTotal selected: ${selected['amount'].sum():,.0f}")
    else:
        print("\nNo deals selected (all candidates violate constraints)")
    
    # ===== Analyze Portfolio =====
    print("\n=== Portfolio Analysis ===")
    
    # Current portfolio analysis
    print("\nCurrent Portfolio:")
    current_analysis = optimizer.analyze_portfolio(current_portfolio)
    print(f"  Total: ${current_analysis['total_amount']:,.0f}")
    print(f"  Deals: {current_analysis['deal_count']}")
    print(f"  Top-1 concentration: {current_analysis['payer_concentration']['top1']:.1%}")
    
    print("\n  APR Distribution:")
    for bucket, pct in sorted(current_analysis['apr_distribution'].items()):
        print(f"    {bucket}: {pct:.1%}")
    
    print("\n  Industry Distribution:")
    for industry, pct in sorted(current_analysis['industry_distribution'].items()):
        print(f"    {industry}: {pct:.1%}")
    
    # Combined portfolio analysis (if deals were selected)
    if not selected.empty:
        print("\nProjected Portfolio (with selected deals):")
        combined = pd.concat([current_portfolio, selected], ignore_index=True)
        combined_analysis = optimizer.analyze_portfolio(combined)
        print(f"  Total: ${combined_analysis['total_amount']:,.0f}")
        print(f"  Deals: {combined_analysis['deal_count']}")
        print(f"  Top-1 concentration: {combined_analysis['payer_concentration']['top1']:.1%}")
        
        print("\n  APR Distribution:")
        for bucket, pct in sorted(combined_analysis['apr_distribution'].items()):
            print(f"    {bucket}: {pct:.1%}")
        
        print("\n  Industry Distribution:")
        for industry, pct in sorted(combined_analysis['industry_distribution'].items()):
            print(f"    {industry}: {pct:.1%}")
    
    # ===== Compare to Targets =====
    print("\n=== Comparison to Target Mix ===")
    target_mix = optimizer.constraints["target_mix"]["apr"]
    
    current_dist = current_analysis['apr_distribution']
    print("\nAPR Buckets vs Target:")
    print(f"{'Bucket':<10} {'Current':<10} {'Target':<10} {'Delta':<10}")
    print("-" * 40)
    for bucket in sorted(set(list(target_mix.keys()) + list(current_dist.keys()))):
        curr = current_dist.get(bucket, 0.0)
        tgt = target_mix.get(bucket, 0.0)
        delta = curr - tgt
        print(f"{bucket:<10} {curr:>8.1%} {tgt:>8.1%} {delta:>+8.1%}")


if __name__ == "__main__":
    main()
