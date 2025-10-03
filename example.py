"""
Example usage of the Commercial-View PaymentProcessor
"""

from abaco_core import PaymentProcessor
import pandas as pd
from datetime import date

def main():
    print("=" * 70)
    print("Commercial-View Payment Processor Example")
    print("=" * 70)
    
    # Create payment processor with default 180-day threshold
    processor = PaymentProcessor()
    print(f"\n1. Created PaymentProcessor with {processor.dpd_threshold}-day default threshold")
    
    # Sample schedule data
    schedule = pd.DataFrame({
        "loan_id": ["L001", "L001", "L001", "L002", "L002", "L003"],
        "due_date": ["2024-01-01", "2024-02-01", "2024-03-01", 
                     "2024-01-15", "2024-02-15", "2024-01-10"],
        "due_amount": [100, 100, 100, 200, 200, 150]
    })
    
    # Sample payment data
    payments = pd.DataFrame({
        "loan_id": ["L001", "L001", "L002", "L003"],
        "payment_date": ["2024-01-05", "2024-02-10", "2024-01-20", "2024-01-10"],
        "payment_amount": [100, 50, 150, 150]
    })
    
    print("\n2. Sample Data:")
    print("\nSchedule:")
    print(schedule.to_string(index=False))
    print("\nPayments:")
    print(payments.to_string(index=False))
    
    # Calculate payment timeline
    ref_date = date(2024, 3, 15)
    print(f"\n3. Reference Date: {ref_date}")
    
    timeline = processor.calculate_payment_timeline(schedule, payments, ref_date)
    print("\n4. Payment Timeline (last 5 entries):")
    print(timeline.tail().to_string(index=False))
    
    # Calculate DPD
    dpd = processor.calculate_dpd(schedule, payments, ref_date)
    print("\n5. DPD Calculation:")
    print(dpd.to_string(index=False))
    
    # Assign DPD buckets
    dpd_with_buckets = processor.assign_dpd_buckets(dpd)
    print("\n6. DPD with Buckets:")
    cols_to_show = ["loan_id", "days_past_due", "dpd_bucket", "dpd_bucket_description", "default_flag"]
    print(dpd_with_buckets[cols_to_show].to_string(index=False))
    
    # Summary statistics
    print("\n7. Summary Statistics:")
    print(f"   Total loans: {len(dpd_with_buckets)}")
    print(f"   Current loans: {len(dpd_with_buckets[dpd_with_buckets['dpd_bucket'] == 'Current'])}")
    print(f"   Delinquent loans: {len(dpd_with_buckets[dpd_with_buckets['days_past_due'] > 0])}")
    print(f"   Defaulted loans (180+ days): {dpd_with_buckets['default_flag'].sum()}")
    print(f"   Total past due amount: ${dpd_with_buckets['past_due_amount'].sum():.2f}")
    
    print("\n" + "=" * 70)
    print("Example completed successfully!")
    print("=" * 70)

if __name__ == "__main__":
    main()
