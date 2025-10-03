"""
Payment Logic Module

Handles schedule/payments standardization, timeline, DPD (Days Past Due), and buckets.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pandas as pd

logger = logging.getLogger(__name__)


class PaymentSchedule:
    """Handles payment schedule standardization and timeline management."""
    
    def __init__(self, loan_id: str, start_date: datetime, payment_amount: float, frequency: str = 'monthly'):
        """
        Initialize payment schedule.
        
        Args:
            loan_id: Unique loan identifier
            start_date: Start date of the loan
            payment_amount: Expected payment amount
            frequency: Payment frequency (monthly, weekly, biweekly)
        """
        self.loan_id = loan_id
        self.start_date = start_date
        self.payment_amount = payment_amount
        self.frequency = frequency
        self.payments = []
        
    def add_payment(self, payment_date: datetime, amount: float, payment_type: str = 'regular'):
        """Add a payment to the schedule."""
        self.payments.append({
            'date': payment_date,
            'amount': amount,
            'type': payment_type
        })
        logger.debug(f"Added payment for loan {self.loan_id}: {amount} on {payment_date}")
    
    def get_timeline(self) -> pd.DataFrame:
        """Generate payment timeline as DataFrame."""
        if not self.payments:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.payments)
        df['loan_id'] = self.loan_id
        return df.sort_values('date')


class DPDCalculator:
    """Calculate Days Past Due (DPD) for loans."""
    
    @staticmethod
    def calculate_dpd(due_date: datetime, payment_date: Optional[datetime] = None, 
                      reference_date: Optional[datetime] = None) -> int:
        """
        Calculate days past due.
        
        Args:
            due_date: When payment was due
            payment_date: When payment was made (if made)
            reference_date: Reference date for calculation (default: today)
        
        Returns:
            int: Days past due (0 if not overdue)
        """
        if payment_date and payment_date <= due_date:
            return 0
        
        ref_date = reference_date or datetime.now()
        compare_date = payment_date if payment_date else ref_date
        
        dpd = (compare_date - due_date).days
        return max(0, dpd)
    
    @staticmethod
    def get_dpd_bucket(dpd: int) -> str:
        """
        Categorize DPD into buckets.
        
        Args:
            dpd: Days past due
        
        Returns:
            str: Bucket category
        """
        if dpd == 0:
            return 'Current'
        elif dpd <= 30:
            return '1-30'
        elif dpd <= 60:
            return '31-60'
        elif dpd <= 90:
            return '61-90'
        elif dpd <= 120:
            return '91-120'
        elif dpd <= 180:
            return '121-180'
        else:
            return '180+'


def standardize_payment_data(payment_data: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize payment data format.
    
    Args:
        payment_data: Raw payment data
    
    Returns:
        pd.DataFrame: Standardized payment data
    """
    logger.info("Standardizing payment data")
    
    df = payment_data.copy()
    
    # Ensure required columns exist
    required_cols = ['loan_id', 'payment_date', 'amount']
    for col in required_cols:
        if col not in df.columns:
            logger.warning(f"Missing required column: {col}")
    
    # Standardize date format
    if 'payment_date' in df.columns:
        df['payment_date'] = pd.to_datetime(df['payment_date'])
    
    # Standardize amount format
    if 'amount' in df.columns:
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    
    logger.info(f"Standardized {len(df)} payment records")
    return df


def calculate_payment_timeline(schedules: List[PaymentSchedule]) -> pd.DataFrame:
    """
    Calculate consolidated payment timeline from multiple schedules.
    
    Args:
        schedules: List of PaymentSchedule objects
    
    Returns:
        pd.DataFrame: Consolidated timeline
    """
    timelines = [schedule.get_timeline() for schedule in schedules]
    
    if not timelines:
        return pd.DataFrame()
    
    consolidated = pd.concat(timelines, ignore_index=True)
    consolidated = consolidated.sort_values(['loan_id', 'date'])
    
    logger.info(f"Generated consolidated timeline with {len(consolidated)} records")
    return consolidated
