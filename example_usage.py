"""
Example usage of the LoanAnalyzer class to calculate weighted statistics
"""

import logging
import pandas as pd
from loan_analyzer import LoanAnalyzer

# Configure logging to see info messages
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def main():
    """Demonstrate the calculate_weighted_stats functionality"""
    
    # Create a sample loan portfolio
    loan_data = pd.DataFrame({
        'loan_id': ['L001', 'L002', 'L003', 'L004', 'L005'],
        'outstanding_balance': [10000, 25000, 15000, 30000, 20000],
        'apr': [5.5, 6.0, 5.75, 6.25, 5.9],
        'eir': [5.65, 6.17, 5.91, 6.42, 6.06],
        'term': [12, 24, 18, 36, 24]
    })
    
    print("Sample Loan Portfolio:")
    print(loan_data)
    print("\n" + "="*60 + "\n")
    
    # Create analyzer instance
    analyzer = LoanAnalyzer()
    
    # Calculate weighted statistics
    print("Calculating weighted statistics...")
    weighted_stats = analyzer.calculate_weighted_stats(loan_data)
    
    print("\nWeighted Statistics:")
    print(weighted_stats)
    print("\n" + "="*60 + "\n")
    
    # Example with Spanish column names
    loan_data_spanish = pd.DataFrame({
        'prestamo_id': ['L001', 'L002', 'L003'],
        'saldo_actual': [10000, 25000, 15000],
        'tasa_anual': [5.5, 6.0, 5.75],
        'tasa_efectiva': [5.65, 6.17, 5.91],
        'plazo_dias': [365, 730, 547]
    })
    
    print("Sample Loan Portfolio (Spanish):")
    print(loan_data_spanish)
    print("\n" + "="*60 + "\n")
    
    print("Calculating weighted statistics with Spanish column names...")
    weighted_stats_spanish = analyzer.calculate_weighted_stats(loan_data_spanish)
    
    print("\nWeighted Statistics (Spanish):")
    print(weighted_stats_spanish)
    print("\n" + "="*60 + "\n")
    
    # Example with custom metrics
    print("Calculating only APR and EIR (custom metrics list)...")
    weighted_stats_custom = analyzer.calculate_weighted_stats(
        loan_data, 
        metrics=['apr', 'eir']
    )
    
    print("\nWeighted Statistics (Custom Metrics):")
    print(weighted_stats_custom)


if __name__ == '__main__':
    main()
