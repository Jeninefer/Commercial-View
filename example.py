"""Example usage of Commercial-View LoanAnalyzer"""

import sys
import os

# Add src to path for direct script execution
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pandas as pd
from datetime import date
from commercial_view import LoanAnalyzer


def main():
    """Demonstrate LoanAnalyzer functionality"""
    
    print("="*60)
    print("Commercial-View LoanAnalyzer Example")
    print("="*60)
    print()
    
    # Initialize analyzer with 90-day default threshold
    analyzer = LoanAnalyzer(dpd_threshold=90)
    print(f"Initialized LoanAnalyzer with DPD threshold: {analyzer.dpd_threshold} days")
    print()
    
    # Create sample loan schedule data
    schedule_df = pd.DataFrame({
        'loan_id': ['L001', 'L001', 'L001', 'L002', 'L002', 'L003', 'L003'],
        'due_date': [
            '2024-01-01', '2024-02-01', '2024-03-01',  # L001
            '2024-01-15', '2024-02-15',                # L002
            '2023-12-01', '2024-01-01'                 # L003 (older loan)
        ],
        'due_amount': [1000, 1000, 1000, 500, 500, 2000, 2000]
    })
    
    # Create sample payment data
    payments_df = pd.DataFrame({
        'loan_id': ['L001', 'L001', 'L002', 'L003'],
        'payment_date': ['2024-01-05', '2024-02-10', '2024-01-20', '2023-12-05'],
        'payment_amount': [1000, 500, 500, 1000]
    })
    
    print("Sample Data:")
    print("-" * 60)
    print("\nLoan Schedule:")
    print(schedule_df.to_string(index=False))
    print("\nPayments:")
    print(payments_df.to_string(index=False))
    print()
    
    # Calculate payment timeline
    reference_date = date(2024, 3, 15)
    print(f"\nCalculating payment timeline as of {reference_date}...")
    print("-" * 60)
    
    timeline = analyzer.calculate_payment_timeline(
        schedule_df, 
        payments_df, 
        reference_date=reference_date
    )
    
    print("\nPayment Timeline:")
    print(timeline.to_string(index=False))
    print()
    
    # Calculate DPD
    print(f"\nCalculating DPD as of {reference_date}...")
    print("-" * 60)
    
    dpd_result = analyzer.calculate_dpd(
        schedule_df, 
        payments_df, 
        reference_date=reference_date
    )
    
    print("\nDPD Analysis Results:")
    print(dpd_result.to_string(index=False))
    print()
    
    # Summary statistics
    print("\nSummary Statistics:")
    print("-" * 60)
    print(f"Total loans analyzed: {len(dpd_result)}")
    print(f"Loans in default: {dpd_result['is_default'].sum()}")
    print(f"Total past due amount: ${dpd_result['past_due_amount'].sum():.2f}")
    print(f"Average days past due: {dpd_result['days_past_due'].mean():.2f}")
    print()
    
    # Detailed analysis per loan
    print("\nDetailed Analysis by Loan:")
    print("-" * 60)
    for _, row in dpd_result.iterrows():
        print(f"\nLoan ID: {row['loan_id']}")
        print(f"  Past Due Amount: ${row['past_due_amount']:.2f}")
        print(f"  Days Past Due: {row['days_past_due']:.0f}")
        print(f"  Default Status: {'YES' if row['is_default'] else 'NO'}")
        if pd.notna(row['first_arrears_date']):
            print(f"  First Arrears Date: {row['first_arrears_date']}")
        if pd.notna(row['last_payment_date']):
            print(f"  Last Payment Date: {row['last_payment_date']}")
        print(f"  Last Due Date: {row['last_due_date']}")
    
    print("\n" + "="*60)
    print("Example completed successfully!")
    print("="*60)


if __name__ == "__main__":
    main()
