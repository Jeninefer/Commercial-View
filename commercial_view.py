"""
Commercial View - Principal KPI Module
Provides loan portfolio analytics including accurate Days Past Due (DPD) calculations.
"""

import pandas as pd
from datetime import datetime
from typing import Optional


class LoanPortfolio:
    """
    A class for managing and analyzing commercial loan portfolios.
    
    This class provides methods to calculate key performance indicators (KPIs)
    including Days Past Due (DPD) for loans based on payment schedules and
    actual payments received.
    """
    
    def __init__(self, dpd_threshold: int = 90):
        """
        Initialize the LoanPortfolio.
        
        Args:
            dpd_threshold: Number of days past due before a loan is considered in default.
                          Defaults to 90 days.
        """
        self.dpd_threshold = dpd_threshold
    
    def calculate_dpd(
        self,
        payment_schedule: pd.DataFrame,
        payments: pd.DataFrame,
        reference_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Calculate Days Past Due (DPD) for loans based on accurate current arrears logic.
        
        This method computes DPD by:
        1. Calculating cumulative gap (total due - total paid) as of reference date
        2. Determining first arrears date only for current arrears period
        3. Setting days_past_due = 0 for loans not currently in arrears (cumulative_gap <= 0)
        4. Calculating days_past_due from first arrears date for loans with active arrears
        5. Updating is_default flag based on dpd_threshold
        
        Args:
            payment_schedule: DataFrame with columns ['loan_id', 'due_date', 'amount_due']
            payments: DataFrame with columns ['loan_id', 'payment_date', 'amount_paid']
            reference_date: Date to calculate DPD as of (defaults to today if not provided)
        
        Returns:
            DataFrame with columns:
                - loan_id: Unique loan identifier
                - total_due: Total amount due as of reference date
                - total_paid: Total amount paid
                - cumulative_gap: Current arrears amount (total_due - total_paid)
                - first_arrears_date: First date when current arrears period started
                - days_past_due: Number of days past due (0 if current)
                - past_due_amount: Amount currently past due
                - is_default: Whether loan is in default (days_past_due >= dpd_threshold)
        """
        # Set reference date to today if not provided
        if reference_date is None:
            reference_date = datetime.now().strftime('%Y-%m-%d')
        
        reference_date = pd.Timestamp(reference_date)
        
        # Filter payment schedule up to reference date
        schedule = payment_schedule.copy()
        schedule['due_date'] = pd.to_datetime(schedule['due_date'])
        schedule = schedule[schedule['due_date'] <= reference_date]
        
        # Calculate total due per loan as of reference date
        total_due = schedule.groupby('loan_id')['amount_due'].sum().reset_index()
        total_due.columns = ['loan_id', 'total_due']
        
        # Filter payments up to reference date
        pmts = payments.copy()
        pmts['payment_date'] = pd.to_datetime(pmts['payment_date'])
        pmts = pmts[pmts['payment_date'] <= reference_date]
        
        # Calculate total paid per loan
        total_paid = pmts.groupby('loan_id')['amount_paid'].sum().reset_index()
        total_paid.columns = ['loan_id', 'total_paid']
        
        # Merge and calculate cumulative gap
        last = total_due.merge(total_paid, on='loan_id', how='left')
        # If a loan has no payments, total_paid will be NaN after the merge; fill with 0.0 to indicate no payments made.
        last['total_paid'] = last['total_paid'].fillna(0.0)
        last['cumulative_gap'] = last['total_due'] - last['total_paid']
        
        # Calculate arrears information
        arrears = self._calculate_first_arrears_date(
            payment_schedule=schedule,
            payments=pmts,
            reference_date=reference_date
        )
        
        # Merge arrears information
        out = last.merge(arrears, on='loan_id', how='left')
        out['first_arrears_date'] = pd.to_datetime(out['first_arrears_date'], errors='coerce')
        
        # Initialize days_past_due to 0
        out['days_past_due'] = 0
        
        # For loans still in arrears (positive gap), calculate days since first arrears
        mask = out['cumulative_gap'] > 0
        out.loc[mask, 'days_past_due'] = (
            pd.Timestamp(reference_date) - out.loc[mask, 'first_arrears_date']
        ).dt.days.clip(lower=0)
        
        out['days_past_due'] = out['days_past_due'].fillna(0).astype(int)
        out['past_due_amount'] = out['cumulative_gap'].clip(lower=0).fillna(0.0)
        out['is_default'] = out['days_past_due'] >= self.dpd_threshold
        
        return out
    
    def _calculate_first_arrears_date(
        self,
        payment_schedule: pd.DataFrame,
        payments: pd.DataFrame,
        reference_date: pd.Timestamp
    ) -> pd.DataFrame:
        """
        Calculate the first arrears date for the current arrears period for each loan.
        
        This identifies when each loan entered its current delinquency period by finding
        the earliest date where the cumulative gap became positive and remained positive
        up to the reference date.
        
        Args:
            payment_schedule: Filtered payment schedule up to reference date
            payments: Filtered payments up to reference date
            reference_date: Reference date for calculations
        
        Returns:
            DataFrame with columns ['loan_id', 'first_arrears_date']
        """
        # Get all unique loan IDs
        all_loans = pd.DataFrame({'loan_id': payment_schedule['loan_id'].unique()})
        
        # Combine schedule and payments into a single timeline
        schedule_events = payment_schedule[['loan_id', 'due_date', 'amount_due']].copy()
        schedule_events['event_date'] = schedule_events['due_date']
        schedule_events['type'] = 'due'
        
        payment_events = payments[['loan_id', 'payment_date', 'amount_paid']].copy()
        payment_events['event_date'] = payment_events['payment_date']
        payment_events['type'] = 'payment'
        payment_events['amount_due'] = 0
        payment_events = payment_events.rename(columns={'amount_paid': 'amount'})
        
        schedule_events['amount'] = schedule_events['amount_due']
        schedule_events = schedule_events[['loan_id', 'event_date', 'type', 'amount']]
        payment_events = payment_events[['loan_id', 'event_date', 'type', 'amount']]
        
        # Combine all events
        all_events = pd.concat([schedule_events, payment_events], ignore_index=True)
        all_events = all_events.sort_values(['loan_id', 'event_date'])
        
        # Calculate cumulative gap over time for each loan
        first_arrears_dates = []
        
        for loan_id, group in all_events.groupby('loan_id'):
            cumulative_due = 0
            cumulative_paid = 0
            first_arrears_date = None
            last_gap = 0
            
            for _, row in group.iterrows():
                if row['type'] == 'due':
                    cumulative_due += row['amount']
                else:  # payment
                    cumulative_paid += row['amount']
                
                current_gap = cumulative_due - cumulative_paid
                
                # Track when loan enters arrears (gap becomes positive from zero/negative)
                if current_gap > 0 and last_gap <= 0:
                    first_arrears_date = row['event_date']
                # If loan becomes current again, reset
                elif current_gap <= 0 and last_gap > 0:
                    first_arrears_date = None
                
                last_gap = current_gap
            
            # Only keep first_arrears_date if loan is still in arrears at the end
            if last_gap > 0 and first_arrears_date is not None:
                first_arrears_dates.append({
                    'loan_id': loan_id,
                    'first_arrears_date': first_arrears_date
                })
        
        if first_arrears_dates:
            result = pd.DataFrame(first_arrears_dates)
        else:
            result = pd.DataFrame({'loan_id': [], 'first_arrears_date': []})
        
        # Ensure all loans are included (with null first_arrears_date if not in arrears)
        result = all_loans.merge(result, on='loan_id', how='left')
        
        return result
