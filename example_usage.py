"""
Example usage of the LoanAnalytics calculate_weighted_stats method
"""

import pandas as pd
from loan_analytics import LoanAnalytics


def main():
    """Demonstrate usage of calculate_weighted_stats"""
    
    # Create a sample loan portfolio dataset
    loan_data = pd.DataFrame({
        'loan_id': [1, 2, 3, 4, 5],
        'outstanding_balance': [10000, 25000, 15000, 30000, 20000],
        'apr': [4.5, 5.5, 6.0, 5.0, 4.8],
        'eir': [4.6, 5.7, 6.2, 5.1, 4.9],
        'term': [360, 240, 300, 180, 360]
    })
    
    print("Sample Loan Portfolio:")
    print(loan_data)
    print("\n" + "="*80 + "\n")
    
    # Initialize the analytics class
    analytics = LoanAnalytics()
    
    # Example 1: Calculate weighted stats with default parameters
    print("Example 1: Calculate all default metrics (apr, eir, term)")
    print("-" * 80)
    result1 = analytics.calculate_weighted_stats(loan_data)
    print(result1)
    print("\n" + "="*80 + "\n")
    
    # Example 2: Calculate weighted stats for specific metrics only
    print("Example 2: Calculate only APR and term")
    print("-" * 80)
    result2 = analytics.calculate_weighted_stats(loan_data, metrics=['apr', 'term'])
    print(result2)
    print("\n" + "="*80 + "\n")
    
    # Example 3: Using different column names (aliases)
    loan_data_aliases = pd.DataFrame({
        'loan_id': [1, 2, 3],
        'current_balance': [10000, 25000, 15000],
        'annual_rate': [4.5, 5.5, 6.0],
        'effective_interest_rate': [4.6, 5.7, 6.2],
        'tenor_days': [360, 240, 300]
    })
    
    print("Example 3: Using column aliases")
    print("Loan data with different column names:")
    print(loan_data_aliases)
    print("\nCalculating weighted stats:")
    print("-" * 80)
    result3 = analytics.calculate_weighted_stats(
        loan_data_aliases, 
        weight_field='current_balance'
    )
    print(result3)
    print("\n" + "="*80 + "\n")
    
    # Example 4: Handling missing values
    loan_data_with_nans = pd.DataFrame({
        'outstanding_balance': [10000, None, 15000, 30000],
        'apr': [4.5, 5.5, 6.0, 5.0],
        'eir': [4.6, 5.7, None, 5.1],
        'term': [360, 240, 300, 180]
    })
    
    print("Example 4: Handling missing values")
    print("Loan data with NaN values:")
    print(loan_data_with_nans)
    print("\nCalculating weighted stats (NaN values are automatically excluded):")
    print("-" * 80)
    result4 = analytics.calculate_weighted_stats(loan_data_with_nans)
    print(result4)
    print("\n" + "="*80 + "\n")
    
    # Manual calculation verification for Example 1
    print("Verification of Example 1 calculations:")
    print("-" * 80)
    total_balance = loan_data['outstanding_balance'].sum()
    manual_apr = (
        loan_data['apr'] * loan_data['outstanding_balance']
    ).sum() / total_balance
    manual_eir = (
        loan_data['eir'] * loan_data['outstanding_balance']
    ).sum() / total_balance
    manual_term = (
        loan_data['term'] * loan_data['outstanding_balance']
    ).sum() / total_balance
    
    print(f"Manual calculation:")
    print(f"  Weighted APR:  {manual_apr:.6f}")
    print(f"  Weighted EIR:  {manual_eir:.6f}")
    print(f"  Weighted Term: {manual_term:.6f}")
    print(f"\nFunction result:")
    print(f"  Weighted APR:  {result1['weighted_apr'].iloc[0]:.6f}")
    print(f"  Weighted EIR:  {result1['weighted_eir'].iloc[0]:.6f}")
    print(f"  Weighted Term: {result1['weighted_term'].iloc[0]:.6f}")


if __name__ == '__main__':
    main()
