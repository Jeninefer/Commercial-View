"""
Example usage of CustomerAnalytics.calculate_customer_dpd_stats method.
"""

import logging
import pandas as pd
from commercial_view.analytics import CustomerAnalytics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Demonstrate the calculate_customer_dpd_stats method."""
    
    # Initialize analytics
    analytics = CustomerAnalytics()
    
    # Create sample DPD (Days Past Due) data
    dpd_df = pd.DataFrame({
        "loan_id": ["L001", "L002", "L003", "L004", "L005", "L006"],
        "days_past_due": [0, 15, 30, 10, 20, 45]
    })
    
    # Create sample loan data with customer information
    loan_df = pd.DataFrame({
        "loan_id": ["L001", "L002", "L003", "L004", "L005", "L006"],
        "customer_id": ["CUST_A", "CUST_A", "CUST_B", "CUST_B", "CUST_C", "CUST_C"]
    })
    
    print("DPD Data:")
    print(dpd_df)
    print("\nLoan Data:")
    print(loan_df)
    
    # Calculate customer DPD statistics
    stats = analytics.calculate_customer_dpd_stats(
        dpd_df=dpd_df,
        loan_df=loan_df,
        customer_id_field="customer_id",
        loan_id_field="loan_id"
    )
    
    print("\nCustomer DPD Statistics:")
    print(stats)
    print("\nColumn descriptions:")
    print("  - dpd_mean: Average days past due for the customer")
    print("  - dpd_median: Median days past due for the customer")
    print("  - dpd_max: Maximum days past due for the customer")
    print("  - dpd_min: Minimum days past due for the customer")
    print("  - dpd_count: Number of loans for the customer")

if __name__ == "__main__":
    main()
