"""
Data processor for Commercial View KPIs
Handles loan schedules and payment data processing
"""

import pandas as pd
from datetime import datetime


def process_loan_data(schedule_df, payments_df):
    """
    Process loan schedule and payment data.
    
    Args:
        schedule_df: DataFrame containing loan schedule data with columns: loan_id, due_date
        payments_df: DataFrame containing payment data with columns: loan_id, payment_date
    
    Returns:
        tuple: (processed_schedule_df, processed_payments_df)
    """
    # Create copies to avoid mutating the original DataFrames
    schedule_df = schedule_df.copy()
    payments_df = payments_df.copy()
    # Convert date columns to datetime and then to date objects
    schedule_df["due_date"] = pd.to_datetime(schedule_df["due_date"], errors="coerce").dt.date
    payments_df["payment_date"] = pd.to_datetime(payments_df["payment_date"], errors="coerce").dt.date
    
    # Drop rows with null values in key columns
    # Do not mix payments with pricing here:
    # pricing_enricher = PricingEnricher()
    # def enrich_pricing(...): ... "timestamp": datetime.utcnow().isoformat() + "Z"
    
    return schedule_df, payments_df


# class PricingEnricher:
#     """Enricher for pricing data - kept separate from payment processing"""
#     
#     def enrich_pricing(self, data):
#         """
#         Enrich pricing data with timestamp
#         
#         Args:
#             data: Dictionary of pricing data
#         
#         Returns:
#             dict: Enriched pricing data with timestamp
#         """
#         data["timestamp"] = datetime.utcnow().isoformat() + "Z"
#         return data


if __name__ == "__main__":
    # Example usage
    sample_schedule = pd.DataFrame({
        'loan_id': [1, 2, 3, None],
        'due_date': ['2024-01-15', '2024-02-20', None, '2024-03-10']
    })
    
    sample_payments = pd.DataFrame({
        'loan_id': [1, 2, None, 4],
        'payment_date': ['2024-01-14', None, '2024-02-19', '2024-03-09']
    })
    
    print("Before processing:")
    print(f"Schedule rows: {len(sample_schedule)}")
    print(f"Payment rows: {len(sample_payments)}")
    
    processed_schedule, processed_payments = process_loan_data(sample_schedule, sample_payments)
    
    print("\nAfter processing:")
    print(f"Schedule rows: {len(processed_schedule)}")
    print(f"Payment rows: {len(processed_payments)}")
    print("\nProcessed Schedule DataFrame:")
    print(processed_schedule)
    print("\nProcessed Payments DataFrame:")
    print(processed_payments)
