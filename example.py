"""
Example usage of the KPI Analyzer

This script demonstrates how to use the KPIAnalyzer class to compute
various business metrics.
"""

import pandas as pd
import numpy as np
from kpi_analyzer import KPIAnalyzer


def main():
    """Run example KPI calculations."""
    
    # Initialize the analyzer
    analyzer = KPIAnalyzer()
    
    print("=" * 60)
    print("KPI Analyzer - Example Usage")
    print("=" * 60)
    
    # Create sample data
    revenue_df = pd.DataFrame({
        "date": ["2023-01", "2023-02", "2023-03", "2023-04"],
        "revenue": [50000, 60000, 75000, 90000]
    })
    
    customer_df = pd.DataFrame({
        "date": ["2023-01", "2023-02", "2023-03", "2023-04"],
        "customer_id": [1, 2, 3, 4]
    })
    
    valuation_df = pd.DataFrame({
        "pre_money_valuation": [5000000],
        "investment_amount": [1000000],
        "market_cap": [7000000],
        "total_debt": [500000],
        "cash": [200000],
        "revenue": [300000],
        "ebitda": [50000],
        "marketing_expense": [20000]
    })
    
    loan_df = pd.DataFrame({
        "loan_id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "amount": [10000, 20000, 15000, 30000, 25000, 12000, 18000, 22000, 16000, 14000],
        "dpd": [0, 30, 90, 200, 150, 0, 45, 190, 60, 0],
        "status": ["active", "active", "active", "default", "npl", 
                   "active", "active", "default", "active", "active"]
    })
    
    payment_df = pd.DataFrame({
        "payment_id": [1, 2, 3, 4, 5],
        "amount": [5000, 10000, 7500, 8000, 6000]
    })
    
    user_df = pd.DataFrame({
        "user_id": [1, 2, 3, 4, 5, 6, 7, 8],
        "status": ["active", "active", "inactive", "active", "active", "active", "inactive", "active"]
    })
    
    # Compute KPIs
    print("\nComputing KPIs...")
    kpis = analyzer.compute_kpis(
        revenue_df=revenue_df,
        customer_df=customer_df,
        valuation_df=valuation_df,
        loan_df=loan_df,
        payment_df=payment_df,
        user_df=user_df,
        default_dpd_threshold=180
    )
    
    # Display results
    print("\n" + "=" * 60)
    print("STARTUP METRICS")
    print("=" * 60)
    for key, value in kpis["startup"].items():
        if isinstance(value, float):
            print(f"{key:.<40} {value:>15,.2f}")
        else:
            print(f"{key:.<40} {value:>15,}")
    
    print("\n" + "=" * 60)
    print("FINTECH METRICS")
    print("=" * 60)
    for key, value in kpis["fintech"].items():
        if isinstance(value, float):
            print(f"{key:.<40} {value:>15,.2f}")
        else:
            print(f"{key:.<40} {value:>15,}")
    
    print("\n" + "=" * 60)
    print("VALUATION METRICS")
    print("=" * 60)
    for key, value in kpis["valuation"].items():
        if isinstance(value, float) and not np.isnan(value):
            print(f"{key:.<40} {value:>15,.2f}")
        elif np.isnan(value):
            print(f"{key:.<40} {'N/A':>15}")
        else:
            print(f"{key:.<40} {value:>15,}")
    
    print("\n" + "=" * 60)
    print("VIABILITY INDEX")
    print("=" * 60)
    print(f"Score: {kpis['viability_index']:.1f}/100.0")
    
    # Interpret viability score
    score = kpis['viability_index']
    if score >= 80:
        interpretation = "Excellent - Strong viability"
    elif score >= 60:
        interpretation = "Good - Healthy business"
    elif score >= 40:
        interpretation = "Fair - Needs improvement"
    else:
        interpretation = "Poor - Significant challenges"
    
    print(f"Interpretation: {interpretation}")
    print("=" * 60)
    
    # Export results
    print("\nExporting results to kpis.json...")
    analyzer.compute_kpis(
        revenue_df=revenue_df,
        customer_df=customer_df,
        valuation_df=valuation_df,
        loan_df=loan_df,
        payment_df=payment_df,
        user_df=user_df,
        default_dpd_threshold=180,
        export=True
    )
    print("Export complete!")


if __name__ == "__main__":
    main()
