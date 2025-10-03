"""
Example usage of the Commercial View DPD calculation.

This script demonstrates how to use the LoanPortfolio class to calculate
accurate Days Past Due (DPD) for a portfolio of commercial loans.
"""

import pandas as pd
from commercial_view import LoanPortfolio


def main():
    """Demonstrate DPD calculation with example data."""
    
    # Initialize portfolio with 90-day default threshold
    portfolio = LoanPortfolio(dpd_threshold=90)
    
    # Example payment schedule
    payment_schedule = pd.DataFrame({
        'loan_id': [
            'L001', 'L001', 'L001',
            'L002', 'L002', 'L002',
            'L003', 'L003', 'L003',
            'L004', 'L004', 'L004'
        ],
        'due_date': [
            '2024-01-01', '2024-02-01', '2024-03-01',
            '2024-01-01', '2024-02-01', '2024-03-01',
            '2024-01-01', '2024-02-01', '2024-03-01',
            '2024-01-01', '2024-02-01', '2024-03-01'
        ],
        'amount_due': [
            1000.0, 1000.0, 1000.0,
            2000.0, 2000.0, 2000.0,
            1500.0, 1500.0, 1500.0,
            3000.0, 3000.0, 3000.0
        ]
    })
    
    # Example payments
    payments = pd.DataFrame({
        'loan_id': [
            'L001', 'L001', 'L001',  # Fully paid on time
            'L002', 'L002',           # One payment missed
            'L003', 'L003', 'L003',   # Late but caught up
            'L004'                     # Only one payment made
        ],
        'payment_date': [
            '2024-01-01', '2024-02-01', '2024-03-01',
            '2024-01-01', '2024-02-01',
            '2024-01-01', '2024-03-15', '2024-03-15',
            '2024-01-05'
        ],
        'amount_paid': [
            1000.0, 1000.0, 1000.0,
            2000.0, 2000.0,
            1500.0, 1500.0, 1500.0,
            3000.0
        ]
    })
    
    # Calculate DPD as of March 20, 2024
    results = portfolio.calculate_dpd(
        payment_schedule=payment_schedule,
        payments=payments,
        reference_date='2024-03-20'
    )
    
    # Display results
    print("="*80)
    print("DPD Calculation Results")
    print("="*80)
    print(f"\nReference Date: 2024-03-20")
    print(f"Default Threshold: {portfolio.dpd_threshold} days")
    print("\n")
    
    # Sort by days_past_due descending
    results_sorted = results.sort_values('days_past_due', ascending=False)
    
    for _, row in results_sorted.iterrows():
        print(f"Loan ID: {row['loan_id']}")
        print(f"  Total Due:        ${row['total_due']:,.2f}")
        print(f"  Total Paid:       ${row['total_paid']:,.2f}")
        print(f"  Current Gap:      ${row['cumulative_gap']:,.2f}")
        print(f"  Days Past Due:    {row['days_past_due']} days")
        print(f"  Past Due Amount:  ${row['past_due_amount']:,.2f}")
        print(f"  In Default:       {'Yes' if row['is_default'] else 'No'}")
        if pd.notna(row['first_arrears_date']):
            print(f"  First Arrears:    {row['first_arrears_date'].strftime('%Y-%m-%d')}")
        print()
    
    # Summary statistics
    print("="*80)
    print("Portfolio Summary")
    print("="*80)
    print(f"Total Loans:        {len(results)}")
    print(f"Loans in Arrears:   {(results['days_past_due'] > 0).sum()}")
    print(f"Loans in Default:   {results['is_default'].sum()}")
    print(f"Default Rate:       {results['is_default'].mean() * 100:.1f}%")
    print(f"Total Past Due:     ${results['past_due_amount'].sum():,.2f}")
    print()


if __name__ == '__main__':
    main()
