"""
Payment Analyzer Module
Handles payment timeline and DPD (Days Past Due) calculations for loan portfolios.
"""

import pandas as pd
from datetime import datetime
from typing import Optional, Tuple


class PaymentAnalyzer:
    """
    A class for analyzing payment schedules and calculating Days Past Due (DPD).
    """
    
    def __init__(self):
        """Initialize the PaymentAnalyzer."""
        pass
    
    def standardize_dataframes(
        self, 
        schedule_df: pd.DataFrame, 
        payments_df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Standardize schedule and payment dataframes to ensure consistent column names.
        
        Args:
            schedule_df: Raw schedule DataFrame with potentially varying column names
            payments_df: Raw payments DataFrame with potentially varying column names
            
        Returns:
            Tuple of (standardized_schedule_df, standardized_payments_df)
        """
        # Make copies to avoid modifying originals
        sched = schedule_df.copy()
        pays = payments_df.copy()
        
        # Standardize schedule columns
        schedule_column_mapping = {
            'LoanID': 'loan_id',
            'loan_ID': 'loan_id',
            'Loan_ID': 'loan_id',
            'DueDate': 'due_date',
            'due_Date': 'due_date',
            'Due_Date': 'due_date',
            'DueAmount': 'due_amount',
            'due_Amount': 'due_amount',
            'Due_Amount': 'due_amount',
            'Amount': 'due_amount',
        }
        
        for old_col, new_col in schedule_column_mapping.items():
            if old_col in sched.columns and new_col not in sched.columns:
                sched.rename(columns={old_col: new_col}, inplace=True)
        
        # Standardize payment columns
        payment_column_mapping = {
            'LoanID': 'loan_id',
            'loan_ID': 'loan_id',
            'Loan_ID': 'loan_id',
            'PaymentDate': 'payment_date',
            'payment_Date': 'payment_date',
            'Payment_Date': 'payment_date',
            'PaymentAmount': 'payment_amount',
            'payment_Amount': 'payment_amount',
            'Payment_Amount': 'payment_amount',
            'Amount': 'payment_amount',
        }
        
        for old_col, new_col in payment_column_mapping.items():
            if old_col in pays.columns and new_col not in pays.columns:
                pays.rename(columns={old_col: new_col}, inplace=True)
        
        # Ensure date columns are datetime
        if 'due_date' in sched.columns:
            sched['due_date'] = pd.to_datetime(sched['due_date'])
        if 'payment_date' in pays.columns:
            pays['payment_date'] = pd.to_datetime(pays['payment_date'])
        
        return sched, pays
    
    def calculate_payment_timeline(
        self,
        schedule_df: pd.DataFrame,
        payments_df: pd.DataFrame,
        reference_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Calculate payment timeline by matching payments to scheduled dues.
        
        This method has been refactored to avoid redundant standardization.
        It now checks if the data is already standardized before calling
        standardize_dataframes.
        
        Args:
            schedule_df: Schedule DataFrame (raw or already standardized)
            payments_df: Payments DataFrame (raw or already standardized)
            reference_date: Optional reference date for calculations
            
        Returns:
            DataFrame with payment timeline information
        """
        # Check if data is already standardized by looking for required columns
        raw = not {"loan_id", "due_date", "due_amount"}.issubset(schedule_df.columns)
        
        if raw:
            # Data needs standardization
            sched, pays = self.standardize_dataframes(schedule_df, payments_df)
        else:
            # Data is already standardized, just make copies
            sched, pays = schedule_df.copy(), payments_df.copy()
            # Ensure date columns are datetime, even if columns are present
            if 'due_date' in sched and not pd.api.types.is_datetime64_any_dtype(sched['due_date']):
                sched['due_date'] = pd.to_datetime(sched['due_date'])
            if 'payment_date' in sched and not pd.api.types.is_datetime64_any_dtype(sched['payment_date']):
                sched['payment_date'] = pd.to_datetime(sched['payment_date'])
            if 'payment_date' in pays and not pd.api.types.is_datetime64_any_dtype(pays['payment_date']):
                pays['payment_date'] = pd.to_datetime(pays['payment_date'])
        
        # Set reference date if not provided
        if reference_date is None:
            reference_date = datetime.now()
        
        # Proceed with timeline calculation on sched and pays
        # Sort both DataFrames for merge_asof
        sched_sorted = sched.sort_values(['loan_id', 'due_date']).reset_index(drop=True)
        pays_sorted = pays.sort_values(['loan_id', 'payment_date']).reset_index(drop=True)

        # Use merge_asof to match each due with the next payment for that loan
        timeline = pd.merge_asof(
            sched_sorted,
            pays_sorted,
            by='loan_id',
            left_on='due_date',
            right_on='payment_date',
            direction='forward',
            suffixes=('_schedule', '_payment')
        )

        # Calculate payment status
        timeline['days_difference'] = (
            timeline['payment_date'] - timeline['due_date']
        ).dt.days

        # Vectorized assignment for payment_status
        timeline['payment_status'] = 'unpaid'
        mask_paid = timeline['payment_date'].notna()
        timeline.loc[mask_paid & (timeline['days_difference'] <= 0), 'payment_status'] = 'paid_on_time'
        timeline.loc[mask_paid & (timeline['days_difference'] > 0), 'payment_status'] = 'paid_late'
        return timeline
    
    def calculate_dpd(
        self,
        schedule_df: pd.DataFrame,
        payments_df: pd.DataFrame,
        reference_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Calculate Days Past Due (DPD) for each loan.
        
        This method has been refactored to standardize data once and reuse it
        for both timeline and DPD calculations, avoiding redundant processing.
        
        Args:
            schedule_df: Raw schedule DataFrame
            payments_df: Raw payments DataFrame
            reference_date: Optional reference date for DPD calculation
            
        Returns:
            DataFrame with DPD information for each loan
        """
        # Standardize dataframes once at the start
        sched, pays = self.standardize_dataframes(schedule_df, payments_df)
        
        # Set reference date if not provided
        if reference_date is None:
            reference_date = datetime.now()
        
        # Use standardized data for timeline calculation
        # Pass already-standardized data to avoid re-standardization
        timeline = self.calculate_payment_timeline(sched, pays, reference_date)
        
        # Calculate DPD based on timeline
        dpd_data = []
        
        for loan_id in timeline['loan_id'].unique():
            loan_timeline = timeline[timeline['loan_id'] == loan_id]
            
            # Find unpaid dues
            unpaid = loan_timeline[loan_timeline['payment_status'] == 'unpaid']
            
            if len(unpaid) > 0:
                # Calculate DPD as days from earliest unpaid due date to reference date
                earliest_due = unpaid['due_date'].min()
                dpd = (reference_date - earliest_due).days
                dpd = max(0, dpd)  # DPD cannot be negative
            else:
                dpd = 0
            
            dpd_data.append({
                'loan_id': loan_id,
                'dpd': dpd,
                'reference_date': reference_date
            })
        
        dpd_df = pd.DataFrame(dpd_data)
        
        return dpd_df
