"""
Example usage of FintechMetricsCalculator

This script demonstrates how to use the FintechMetricsCalculator class
to compute various fintech metrics from sample data.
"""

import pandas as pd
from fintech_metrics import FintechMetricsCalculator


def main():
    # Initialize the calculator
    calculator = FintechMetricsCalculator()
    
    # Create sample loan data
    loan_df = pd.DataFrame({
        'loan_amount': [1000, 2000, 3000, 4000, 5000],
        'days_past_due': [0, 30, 90, 180, 200],
        'revenue': [50, 100, 150, 200, 250],
        'apr': [0.12, 0.15, 0.18, 0.20, 0.22],
        'eir': [0.10, 0.12, 0.15, 0.17, 0.19]
    })
    
    # Create sample user data
    user_df = pd.DataFrame({
        'user_id': [1, 2, 3, 4, 5],
        'is_active': [1, 1, 1, 0, 0]
    })
    
    # Compute metrics
    metrics = calculator.compute_fintech_metrics(loan_df, user_df=user_df)
    
    # Display results
    print("Fintech Metrics:")
    print("-" * 50)
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"{key}: {value:.4f}")
        else:
            print(f"{key}: {value}")
    
    print("\n" + "=" * 50)
    print("Metric Explanations:")
    print("-" * 50)
    print(f"GMV (Gross Merchandise Value): Total loan amount disbursed")
    print(f"Default Rate: Percentage of loans past due >= 180 days")
    print(f"Take Rate: Revenue as a percentage of GMV")
    print(f"Average EIR: Mean Effective Interest Rate")
    print(f"APR-EIR Spread: Average difference between APR and EIR")
    print(f"Active Users: Number of active users")
    print(f"Active Rate: Percentage of active users")


if __name__ == '__main__':
    main()
