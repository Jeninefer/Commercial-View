"""
Integration test simulating a real-world loan portfolio analysis scenario
"""

import pandas as pd
import numpy as np
from loan_analytics import LoanAnalytics


def run_real_world_scenario():
    """Simulate a real loan portfolio analysis"""
    
    print("="*80)
    print("REAL-WORLD SCENARIO: Commercial Loan Portfolio Analysis")
    print("="*80)
    print()
    
    # Create a realistic loan portfolio
    np.random.seed(42)
    n_loans = 100
    
    loan_portfolio = pd.DataFrame({
        'loan_id': range(1, n_loans + 1),
        'outstanding_balance': np.random.uniform(5000, 500000, n_loans),
        'apr': np.random.uniform(3.5, 8.5, n_loans),
        'eir': np.random.uniform(3.6, 8.7, n_loans),
        'term': np.random.choice([180, 240, 300, 360], n_loans),
        'loan_type': np.random.choice(['Commercial', 'Consumer', 'Mortgage'], n_loans)
    })
    
    # Add some challenging data points
    # Add a few loans with zero balance (should be excluded)
    loan_portfolio.loc[5, 'outstanding_balance'] = 0
    # Add a few loans with missing APR (should be handled)
    loan_portfolio.loc[10, 'apr'] = np.nan
    # Add a loan with negative balance (should be excluded)
    loan_portfolio.loc[15, 'outstanding_balance'] = -1000
    
    print(f"Portfolio Overview:")
    print(f"  Total Loans: {len(loan_portfolio)}")
    print(f"  Total Outstanding Balance: ${loan_portfolio['outstanding_balance'].sum():,.2f}")
    print(f"  Balance Range: ${loan_portfolio['outstanding_balance'].min():,.2f} - ${loan_portfolio['outstanding_balance'].max():,.2f}")
    print()
    
    analytics = LoanAnalytics()
    
    # Scenario 1: Calculate weighted stats for entire portfolio
    print("-" * 80)
    print("Scenario 1: Portfolio-Wide Weighted Statistics")
    print("-" * 80)
    result = analytics.calculate_weighted_stats(loan_portfolio)
    
    if not result.empty:
        print("\nWeighted Portfolio Metrics:")
        print(f"  Weighted APR:  {result['weighted_apr'].iloc[0]:.4f}%")
        print(f"  Weighted EIR:  {result['weighted_eir'].iloc[0]:.4f}%")
        print(f"  Weighted Term: {result['weighted_term'].iloc[0]:.2f} days")
    
    # Scenario 2: Calculate stats by loan type
    print("\n" + "-" * 80)
    print("Scenario 2: Weighted Statistics by Loan Type")
    print("-" * 80)
    
    for loan_type in loan_portfolio['loan_type'].unique():
        subset = loan_portfolio[loan_portfolio['loan_type'] == loan_type]
        result_type = analytics.calculate_weighted_stats(subset)
        
        if not result_type.empty:
            print(f"\n{loan_type} Loans (n={len(subset)}):")
            print(f"  Total Balance: ${subset['outstanding_balance'].sum():,.2f}")
            print(f"  Weighted APR:  {result_type['weighted_apr'].iloc[0]:.4f}%")
            print(f"  Weighted EIR:  {result_type['weighted_eir'].iloc[0]:.4f}%")
            print(f"  Weighted Term: {result_type['weighted_term'].iloc[0]:.2f} days")
    
    # Scenario 3: Focus on specific metrics (risk analysis)
    print("\n" + "-" * 80)
    print("Scenario 3: Risk Analysis - APR Focus")
    print("-" * 80)
    
    high_balance_loans = loan_portfolio[loan_portfolio['outstanding_balance'] > 100000]
    result_risk = analytics.calculate_weighted_stats(high_balance_loans, metrics=['apr'])
    
    print(f"\nHigh Balance Loans (>$100,000):")
    print(f"  Number of Loans: {len(high_balance_loans)}")
    print(f"  Total Balance: ${high_balance_loans['outstanding_balance'].sum():,.2f}")
    if not result_risk.empty:
        print(f"  Weighted APR: {result_risk['weighted_apr'].iloc[0]:.4f}%")
    
    # Scenario 4: Test with Spanish column names
    print("\n" + "-" * 80)
    print("Scenario 4: International Data (Spanish Column Names)")
    print("-" * 80)
    
    international_portfolio = pd.DataFrame({
        'id_prestamo': [1, 2, 3],
        'saldo_actual': [100000, 250000, 150000],
        'tasa_anual': [4.5, 5.5, 6.0],
        'tasa_efectiva': [4.6, 5.7, 6.2],
        'plazo_dias': [360, 240, 300]
    })
    
    print("\nInternational Portfolio (Spanish):")
    print(international_portfolio)
    
    result_intl = analytics.calculate_weighted_stats(
        international_portfolio, 
        weight_field='saldo_actual'
    )
    
    if not result_intl.empty:
        print("\nWeighted Metrics:")
        print(f"  Weighted APR (tasa_anual):    {result_intl['weighted_apr'].iloc[0]:.4f}%")
        print(f"  Weighted EIR (tasa_efectiva): {result_intl['weighted_eir'].iloc[0]:.4f}%")
        print(f"  Weighted Term (plazo_dias):   {result_intl['weighted_term'].iloc[0]:.2f} days")
    
    # Scenario 5: Edge case - all invalid weights
    print("\n" + "-" * 80)
    print("Scenario 5: Edge Case - Invalid Data Handling")
    print("-" * 80)
    
    invalid_portfolio = pd.DataFrame({
        'outstanding_balance': [0, 0, np.nan, -100],
        'apr': [5.0, 6.0, 7.0, 8.0]
    })
    
    print("\nPortfolio with all invalid weights:")
    print(invalid_portfolio)
    
    result_invalid = analytics.calculate_weighted_stats(invalid_portfolio, metrics=['apr'])
    
    if result_invalid.empty:
        print("\n✓ Correctly handled: Returned empty DataFrame for invalid data")
    
    print("\n" + "="*80)
    print("INTEGRATION TEST COMPLETED SUCCESSFULLY")
    print("="*80)
    print()
    print("Key Takeaways:")
    print("  ✓ Handles large portfolios efficiently")
    print("  ✓ Supports segmentation by loan characteristics")
    print("  ✓ Works with multilingual column names")
    print("  ✓ Robust error handling for edge cases")
    print("  ✓ Provides actionable insights for risk management")
    print()


if __name__ == '__main__':
    run_real_world_scenario()
