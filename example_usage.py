"""
Example usage of PaymentAnalyzer showing the refactored code in action.
This demonstrates how the refactoring avoids redundant standardization.
"""

import pandas as pd
from datetime import datetime
from payment_analyzer import PaymentAnalyzer


def main():
    """Demonstrate the PaymentAnalyzer usage."""
    
    print("=" * 70)
    print("PaymentAnalyzer Example - Avoiding Redundant Standardization")
    print("=" * 70)
    
    # Create sample data with non-standardized column names
    schedule_df = pd.DataFrame({
        'LoanID': ['L001', 'L001', 'L001', 'L002', 'L002'],
        'DueDate': ['2025-01-01', '2025-02-01', '2025-03-01', '2025-01-15', '2025-02-15'],
        'DueAmount': [1000, 1000, 1000, 500, 500]
    })
    
    payments_df = pd.DataFrame({
        'LoanID': ['L001', 'L001', 'L002'],
        'PaymentDate': ['2025-01-01', '2025-02-05', '2025-01-20'],
        'PaymentAmount': [1000, 1000, 500]
    })
    
    print("\n1. Raw Schedule Data (non-standardized column names):")
    print(schedule_df)
    
    print("\n2. Raw Payments Data (non-standardized column names):")
    print(payments_df)
    
    # Create analyzer instance
    analyzer = PaymentAnalyzer()
    
    # Calculate DPD - this will standardize once and reuse for timeline
    print("\n3. Calculating DPD (standardizes data once)...")
    reference_date = datetime(2025, 3, 15)
    dpd_df = analyzer.calculate_dpd(schedule_df, payments_df, reference_date)
    
    print("\n4. DPD Results:")
    print(dpd_df)
    
    print("\n" + "=" * 70)
    print("Key Points about the Refactoring:")
    print("=" * 70)
    print("✓ standardize_dataframes is called ONCE in calculate_dpd")
    print("✓ calculate_payment_timeline detects already-standardized data")
    print("✓ No redundant column renaming or date conversions")
    print("✓ More efficient for large datasets")
    print("=" * 70)
    
    # Also demonstrate direct timeline calculation with raw data
    print("\n5. Direct Timeline Calculation with Raw Data:")
    timeline = analyzer.calculate_payment_timeline(schedule_df, payments_df, reference_date)
    print(f"\nTimeline has {len(timeline)} records with payment status information")
    print("\nSample timeline records:")
    print(timeline[['loan_id', 'due_date', 'payment_date', 'payment_status']].head())


if __name__ == "__main__":
    main()
