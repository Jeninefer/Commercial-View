"""Example usage of Commercial-View analytics package."""

import pandas as pd
import numpy as np
from commercial_view import PaymentAnalyzer
from commercial_view.analyzer import (
    calculate_revenue_metrics,
    calculate_line_utilization,
    calculate_customer_dpd_stats
)


def main():
    """Demonstrate the usage of Commercial-View analytics."""
    
    print("=" * 80)
    print("Commercial-View Analytics - Usage Examples")
    print("=" * 80)
    
    # Initialize analyzer
    analyzer = PaymentAnalyzer(dpd_threshold=90)
    
    # Example 1: DPD Bucketing
    print("\n1. DPD Bucketing Example")
    print("-" * 80)
    dpd_data = pd.DataFrame({
        "loan_id": [1, 2, 3, 4, 5, 6],
        "days_past_due": [0, 15, 45, 75, 120, 200]
    })
    
    dpd_result = analyzer.get_dpd_buckets(dpd_data)
    print(dpd_result[["loan_id", "days_past_due", "dpd_bucket", "default_flag"]])
    
    # Example 2: Customer Segmentation
    print("\n2. Customer Segmentation Example")
    print("-" * 80)
    loans_data = pd.DataFrame({
        "loan_id": range(1, 11),
        "customer_id": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"],
        "outstanding_balance": [10000, 25000, 15000, 50000, 30000, 8000, 45000, 20000, 35000, 12000]
    })
    
    segmented = analyzer.calculate_customer_segments(loans_data)
    print(segmented[["customer_id", "outstanding_balance", "segment"]].sort_values("outstanding_balance", ascending=False))
    
    # Example 3: Customer Type Determination
    print("\n3. Customer Type Classification Example")
    print("-" * 80)
    loans_history = pd.DataFrame({
        "loan_id": [1, 2, 3, 4, 5],
        "customer_id": ["A", "A", "B", "B", "C"],
        "origination_date": pd.to_datetime([
            "2023-01-01", "2023-02-15",  # Customer A: 45 days gap
            "2023-01-01", "2023-06-01",  # Customer B: 151 days gap
            "2023-01-01"                 # Customer C: first loan
        ])
    })
    dpd_history = pd.DataFrame({
        "loan_id": [1, 2, 3, 4, 5],
        "days_past_due": [0, 0, 0, 0, 0]
    })
    
    typed = analyzer.determine_customer_type(loans_history, dpd_history)
    print(typed[["loan_id", "customer_id", "origination_date", "customer_type"]])
    
    # Example 4: Weighted Statistics
    print("\n4. Weighted Statistics Example")
    print("-" * 80)
    loan_stats = pd.DataFrame({
        "loan_id": [1, 2, 3, 4],
        "apr": [8.5, 12.0, 15.5, 10.0],
        "term": [12, 24, 36, 18],
        "outstanding_balance": [10000, 25000, 15000, 30000]
    })
    
    weighted = analyzer.calculate_weighted_stats(loan_stats)
    print("Weighted Statistics:")
    for key, value in weighted.items():
        print(f"  {key}: {value:.2f}")
    
    # Example 5: HHI Calculation
    print("\n5. Herfindahl-Hirschman Index (Concentration) Example")
    print("-" * 80)
    portfolio = pd.DataFrame({
        "customer_id": ["A", "B", "C", "D", "E"],
        "outstanding_balance": [50000, 30000, 15000, 3000, 2000]
    })
    
    hhi = analyzer.calculate_hhi(portfolio)
    print(f"HHI Score: {hhi:.2f}")
    if hhi < 1500:
        print("Portfolio Concentration: Low (Diversified)")
    elif hhi < 2500:
        print("Portfolio Concentration: Moderate")
    else:
        print("Portfolio Concentration: High (Concentrated)")
    
    # Example 6: Revenue Metrics
    print("\n6. Revenue Metrics Example")
    print("-" * 80)
    revenue_data = pd.DataFrame({
        "loan_id": [1, 2, 3],
        "principal": [10000, 20000, 15000],
        "interest_rate": [10.0, 12.5, 15.0],
        "term": [12, 24, 36],
        "total_paid": [11000, 25000, 22000]
    })
    
    revenue_result = calculate_revenue_metrics(revenue_data)
    print(revenue_result[["loan_id", "principal", "expected_revenue", "effective_revenue", "revenue_efficiency"]])
    
    # Example 7: Line Utilization
    print("\n7. Credit Line Utilization Example")
    print("-" * 80)
    credit_lines = pd.DataFrame({
        "loan_id": [1, 2, 3, 4],
        "credit_line": [20000, 50000, 30000, 40000],
        "outstanding": [15000, 25000, 30000, 10000]
    })
    
    utilization = calculate_line_utilization(credit_lines)
    print(utilization[["loan_id", "credit_line", "outstanding", "line_utilization"]])
    
    # Example 8: Customer DPD Statistics
    print("\n8. Customer DPD Statistics Example")
    print("-" * 80)
    customer_loans = pd.DataFrame({
        "loan_id": [1, 2, 3, 4, 5, 6],
        "customer_id": ["A", "A", "A", "B", "B", "C"]
    })
    
    dpd_stats_data = pd.DataFrame({
        "loan_id": [1, 2, 3, 4, 5, 6],
        "days_past_due": [0, 30, 15, 60, 45, 90]
    })
    
    dpd_stats = calculate_customer_dpd_stats(customer_loans, dpd_stats_data)
    print(dpd_stats[["customer_id", "dpd_mean", "dpd_median", "dpd_max", "dpd_min"]].drop_duplicates())
    
    print("\n" + "=" * 80)
    print("All examples completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()
