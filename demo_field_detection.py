#!/usr/bin/env python3
"""
Demonstration script showing the PaymentProcessor field detection in action.
This demonstrates the updated patterns that were added per the problem statement.
"""

from payment_logic import PaymentProcessor


def main():
    processor = PaymentProcessor()
    
    print("=" * 70)
    print("PaymentProcessor Field Detection Demonstration")
    print("=" * 70)
    print()
    
    # Example 1: Schedule data with "Payment Date" and "Total Payment"
    print("Example 1: Schedule Dataset")
    print("-" * 70)
    schedule_columns = ['Loan ID', 'Payment Date', 'Total Payment']
    print(f"Columns: {schedule_columns}")
    print(f"  Detected Loan ID field:     {processor.detect_loan_id_field(schedule_columns)}")
    print(f"  Detected Schedule Date:     {processor.detect_schedule_date_field(schedule_columns)}")
    print(f"  Detected Schedule Amount:   {processor.detect_schedule_amount_field(schedule_columns)}")
    print()
    
    # Example 2: Payment data with "True Payment Date" and "True Total Payment"
    print("Example 2: Actual Payment Dataset")
    print("-" * 70)
    payment_columns = ['Loan ID', 'True Payment Date', 'True Total Payment']
    print(f"Columns: {payment_columns}")
    print(f"  Detected Loan ID field:     {processor.detect_loan_id_field(payment_columns)}")
    print(f"  Detected Payment Date:      {processor.detect_payment_date_field(payment_columns)}")
    print(f"  Detected Payment Amount:    {processor.detect_payment_amount_field(payment_columns)}")
    print()
    
    # Example 3: Underscore-separated columns (alternative format)
    print("Example 3: Alternative Format with Underscores")
    print("-" * 70)
    underscore_columns = ['loan_id', 'payment_date', 'total_payment']
    print(f"Columns: {underscore_columns}")
    print(f"  Detected Loan ID field:     {processor.detect_loan_id_field(underscore_columns)}")
    print(f"  Detected Schedule Date:     {processor.detect_schedule_date_field(underscore_columns)}")
    print(f"  Detected Schedule Amount:   {processor.detect_schedule_amount_field(underscore_columns)}")
    print(f"  Detected Payment Date:      {processor.detect_payment_date_field(underscore_columns)}")
    print(f"  Detected Payment Amount:    {processor.detect_payment_amount_field(underscore_columns)}")
    print()
    
    # Example 4: Mixed case testing
    print("Example 4: Mixed Case Columns")
    print("-" * 70)
    mixed_columns = ['LOAN ID', 'payment Date', 'TOTAL payment']
    print(f"Columns: {mixed_columns}")
    print(f"  Detected Loan ID field:     {processor.detect_loan_id_field(mixed_columns)}")
    print(f"  Detected Schedule Date:     {processor.detect_schedule_date_field(mixed_columns)}")
    print(f"  Detected Schedule Amount:   {processor.detect_schedule_amount_field(mixed_columns)}")
    print()
    
    print("=" * 70)
    print("Key Updates Made:")
    print("=" * 70)
    print("1. SCHEDULE_DATE_PATTERNS: Added 'payment[_\\s]*date' to match 'Payment Date'")
    print("2. SCHEDULE_AMOUNT_PATTERNS: Added 'total[_\\s]*payment' to match 'Total Payment'")
    print("3. PAYMENT_AMOUNT_PATTERNS: Added 'total[_\\s]*payment' to match 'True Total Payment'")
    print()
    print("All patterns support both underscores (_) and spaces in column names.")
    print("All patterns are case-insensitive for flexible matching.")
    print("=" * 70)


if __name__ == '__main__':
    main()
