"""Example usage of the FeatureEngineer.classify_client_type method"""

from datetime import datetime
import pandas as pd
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from commercial_view import FeatureEngineer


def main():
    """Demonstrate the classify_client_type functionality"""
    
    # Create sample data
    data = {
        'customer_id': [1, 2, 3, 4, 5],
        'customer_name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
        'loan_count': [1, 3, 2, 5, 0],
        'last_active_date': [
            '2023-12-15',  # New customer
            '2023-11-20',  # Recurrent (42 days)
            '2023-08-15',  # Recovered (139 days)
            '2023-12-28',  # Recurrent (4 days)
            '2023-10-01'   # New (0 loans)
        ]
    }
    
    df = pd.DataFrame(data)
    
    print("Original Data:")
    print(df)
    print("\n" + "="*80 + "\n")
    
    # Initialize FeatureEngineer
    fe = FeatureEngineer()
    
    # Classify customers
    reference_date = datetime(2024, 1, 1)
    result = fe.classify_client_type(df, reference_date=reference_date)
    
    print(f"Customer Classification (Reference Date: {reference_date.date()}):")
    print(result[['customer_id', 'customer_name', 'loan_count', 'days_since_last', 'customer_type']])
    print("\n" + "="*80 + "\n")
    
    # Summary statistics
    print("Classification Summary:")
    print(result['customer_type'].value_counts())
    print("\n" + "="*80 + "\n")
    
    print("Customer Type Definitions:")
    print(f"- {fe.CUSTOMER_TYPES['NEW']}: Customers with 1 or fewer loans")
    print(f"- {fe.CUSTOMER_TYPES['RECURRENT']}: Customers with >1 loan and last active ≤90 days ago")
    print(f"- {fe.CUSTOMER_TYPES['RECOVERED']}: Customers with >1 loan and last active >90 days ago")


if __name__ == '__main__':
    main()
