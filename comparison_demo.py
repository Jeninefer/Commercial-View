"""
Comparison: Before and After Refactoring
This script demonstrates what would have happened BEFORE the refactoring
versus what happens AFTER the refactoring.
"""

import pandas as pd
from datetime import datetime


class PaymentAnalyzerBeforeRefactoring:
    """
    This represents the OLD implementation BEFORE refactoring.
    Both methods call standardize_dataframes causing redundancy.
    """
    
    def standardize_dataframes(self, schedule_df, payments_df):
        """Standardize column names - called redundantly in old implementation."""
        print("    [BEFORE] standardize_dataframes called")
        sched = schedule_df.copy()
        pays = payments_df.copy()
        
        # Column mapping
        schedule_mapping = {'LoanID': 'loan_id', 'DueDate': 'due_date', 'DueAmount': 'due_amount'}
        payment_mapping = {'LoanID': 'loan_id', 'PaymentDate': 'payment_date', 'PaymentAmount': 'payment_amount'}
        
        for old, new in schedule_mapping.items():
            if old in sched.columns:
                sched.rename(columns={old: new}, inplace=True)
        
        for old, new in payment_mapping.items():
            if old in pays.columns:
                pays.rename(columns={old: new}, inplace=True)
        
        sched['due_date'] = pd.to_datetime(sched['due_date'])
        pays['payment_date'] = pd.to_datetime(pays['payment_date'])
        
        return sched, pays
    
    def calculate_payment_timeline(self, schedule_df, payments_df, reference_date=None):
        """OLD: Always calls standardize_dataframes regardless of input."""
        # PROBLEM: Always standardizes, even if already standardized
        sched, pays = self.standardize_dataframes(schedule_df, payments_df)
        
        if reference_date is None:
            reference_date = datetime.now()
        
        timeline = sched.merge(pays, on='loan_id', how='left')
        return timeline
    
    def calculate_dpd(self, schedule_df, payments_df, reference_date=None):
        """OLD: Standardizes data, then calls calculate_payment_timeline which standardizes again."""
        # PROBLEM: Standardizes here...
        sched, pays = self.standardize_dataframes(schedule_df, payments_df)
        
        if reference_date is None:
            reference_date = datetime.now()
        
        # PROBLEM: ...and standardizes again inside calculate_payment_timeline!
        timeline = self.calculate_payment_timeline(sched, pays, reference_date)
        
        dpd_data = []
        for loan_id in timeline['loan_id'].unique():
            dpd_data.append({'loan_id': loan_id, 'dpd': 0})
        
        return pd.DataFrame(dpd_data)


class PaymentAnalyzerAfterRefactoring:
    """
    This represents the NEW implementation AFTER refactoring.
    Smart detection avoids redundant standardization.
    """
    
    def standardize_dataframes(self, schedule_df, payments_df):
        """Standardize column names - called only once after refactoring."""
        print("    [AFTER] standardize_dataframes called")
        sched = schedule_df.copy()
        pays = payments_df.copy()
        
        # Column mapping
        schedule_mapping = {'LoanID': 'loan_id', 'DueDate': 'due_date', 'DueAmount': 'due_amount'}
        payment_mapping = {'LoanID': 'loan_id', 'PaymentDate': 'payment_date', 'PaymentAmount': 'payment_amount'}
        
        for old, new in schedule_mapping.items():
            if old in sched.columns:
                sched.rename(columns={old: new}, inplace=True)
        
        for old, new in payment_mapping.items():
            if old in pays.columns:
                pays.rename(columns={old: new}, inplace=True)
        
        sched['due_date'] = pd.to_datetime(sched['due_date'])
        pays['payment_date'] = pd.to_datetime(pays['payment_date'])
        
        return sched, pays
    
    def calculate_payment_timeline(self, schedule_df, payments_df, reference_date=None):
        """NEW: Checks if data is standardized before calling standardize_dataframes."""
        # SOLUTION: Check if data is already standardized
        raw = not {"loan_id", "due_date", "due_amount"}.issubset(schedule_df.columns)
        
        if raw:
            print("    [AFTER] Data needs standardization")
            sched, pays = self.standardize_dataframes(schedule_df, payments_df)
        else:
            print("    [AFTER] Data already standardized, skipping")
            sched, pays = schedule_df.copy(), payments_df.copy()
        
        if reference_date is None:
            reference_date = datetime.now()
        
        timeline = sched.merge(pays, on='loan_id', how='left')
        return timeline
    
    def calculate_dpd(self, schedule_df, payments_df, reference_date=None):
        """NEW: Standardizes once, then passes standardized data."""
        # SOLUTION: Standardize once here...
        sched, pays = self.standardize_dataframes(schedule_df, payments_df)
        
        if reference_date is None:
            reference_date = datetime.now()
        
        # SOLUTION: ...and calculate_payment_timeline detects it's already standardized!
        timeline = self.calculate_payment_timeline(sched, pays, reference_date)
        
        dpd_data = []
        for loan_id in timeline['loan_id'].unique():
            dpd_data.append({'loan_id': loan_id, 'dpd': 0})
        
        return pd.DataFrame(dpd_data)


def main():
    """Compare the two implementations."""
    
    print("=" * 80)
    print("COMPARISON: Before vs After Refactoring")
    print("=" * 80)
    
    # Sample data
    schedule = pd.DataFrame({
        'LoanID': ['L001', 'L002'],
        'DueDate': ['2025-01-01', '2025-01-15'],
        'DueAmount': [1000, 500]
    })
    
    payments = pd.DataFrame({
        'LoanID': ['L001'],
        'PaymentDate': ['2025-01-01'],
        'PaymentAmount': [1000]
    })
    
    print("\n1. BEFORE REFACTORING (Redundant Standardization):")
    print("-" * 80)
    before = PaymentAnalyzerBeforeRefactoring()
    print("   Calling calculate_dpd...")
    dpd_before = before.calculate_dpd(schedule, payments, datetime(2025, 3, 1))
    
    print("\n2. AFTER REFACTORING (Optimized):")
    print("-" * 80)
    after = PaymentAnalyzerAfterRefactoring()
    print("   Calling calculate_dpd...")
    dpd_after = after.calculate_dpd(schedule, payments, datetime(2025, 3, 1))
    
    print("\n" + "=" * 80)
    print("SUMMARY:")
    print("=" * 80)
    print("BEFORE: standardize_dataframes called TWICE")
    print("        1st call: in calculate_dpd")
    print("        2nd call: in calculate_payment_timeline")
    print("")
    print("AFTER:  standardize_dataframes called ONCE")
    print("        Only call: in calculate_dpd")
    print("        calculate_payment_timeline detected already-standardized data")
    print("=" * 80)
    print("\n✓ Refactoring eliminates redundant processing!")
    print("✓ Performance improvement especially significant for large datasets")
    print("=" * 80)


if __name__ == "__main__":
    main()
