"""Example usage of FeatureEngineer.classify_client_type method."""

import pandas as pd
from datetime import datetime
import sys
import os

# Import FeatureEngineer from src package
from src.feature_engineer import FeatureEngineer
def main():
    """Demonstrate customer classification."""
    # Create instance
    fe = FeatureEngineer()
    
    # Sample data
    print("=" * 80)
    print("Customer Classification Example")
    print("=" * 80)
    print()
    
    # Create sample DataFrame
    df = pd.DataFrame({
        'customer_id': [1, 2, 3, 4, 5],
        'loan_count': [0, 1, 2, 3, 5],
        'last_active_date': [
            '2023-12-01',  # 31 days before reference
            '2023-12-15',  # 17 days before reference
            '2023-10-20',  # 73 days before reference
            '2023-09-01',  # 122 days before reference
            '2023-12-25'   # 7 days before reference
        ]
    })
    
    print("Input Data:")
    print(df.to_string(index=False))
    print()
    
    # Classify customers
    reference_date = datetime(2024, 1, 1)
    result = fe.classify_client_type(
        df,
        reference_date=reference_date
    )
    
    print(f"Reference Date: {reference_date.date()}")
    print()
    print("Classification Results:")
    print(result[['customer_id', 'loan_count', 'days_since_last', 'customer_type']].to_string(index=False))
    print()
    
    print("Classification Summary:")
    print("-" * 40)
    summary = result['customer_type'].value_counts()
    for customer_type, count in summary.items():
        print(f"  {customer_type}: {count}")
    print()
    
    print("Classification Rules:")
    print("-" * 40)
    print("  • New: loan_count <= 1")
    print("  • Recurrent: loan_count > 1 and days_since_last <= 90")
    print("  • Recovered: loan_count > 1 and days_since_last > 90")
    print()


if __name__ == '__main__':
    main()
