"""Loan Analyzer Module for Payment Timeline and DPD Calculations"""

import logging
from datetime import datetime, date
from typing import Optional, Union

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class LoanAnalyzer:
    """
    A class to analyze loan payment timelines and calculate Days Past Due (DPD).
    
    Attributes:
        dpd_threshold (int): The threshold in days to classify a loan as default.
    """
    
    def __init__(self, dpd_threshold: int = 90):
        """
        Initialize the LoanAnalyzer.
        
        Args:
            dpd_threshold (int): Days past due threshold for default classification.
                                Defaults to 90 days.
        """
        self.dpd_threshold = dpd_threshold
    
    def standardize_dataframes(self, schedule_df: pd.DataFrame, 
                               payments_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Standardize input DataFrames by ensuring proper column names and data types.
        
        Args:
            schedule_df: DataFrame with loan schedule data (loan_id, due_date, due_amount)
            payments_df: DataFrame with payment data (loan_id, payment_date, payment_amount)
        
        Returns:
            Tuple of standardized (schedule_df, payments_df)
        """
        schedule_df = schedule_df.copy()
        payments_df = payments_df.copy()
        
        # Convert date columns to datetime and then to date
        if "due_date" in schedule_df.columns:
            schedule_df["due_date"] = pd.to_datetime(schedule_df["due_date"], errors="coerce").dt.date
        
        if "payment_date" in payments_df.columns:
            payments_df["payment_date"] = pd.to_datetime(payments_df["payment_date"], errors="coerce").dt.date
        
        # Ensure numeric columns
        if "due_amount" in schedule_df.columns:
            schedule_df["due_amount"] = pd.to_numeric(schedule_df["due_amount"], errors="coerce")
        
        if "payment_amount" in payments_df.columns:
            payments_df["payment_amount"] = pd.to_numeric(payments_df["payment_amount"], errors="coerce")
        
        return schedule_df, payments_df
    
    def calculate_payment_timeline(self, schedule_df: pd.DataFrame, payments_df: pd.DataFrame,
                                   reference_date: Optional[Union[datetime, date]] = None) -> pd.DataFrame:
        """
        Calculate the payment timeline showing cumulative dues and payments over time.
        
        Args:
            schedule_df: DataFrame with columns [loan_id, due_date, due_amount]
            payments_df: DataFrame with columns [loan_id, payment_date, payment_amount]
            reference_date: Reference date for calculations. Defaults to current date.
        
        Returns:
            DataFrame with timeline of cumulative dues, payments, and gaps by loan and date.
        """
        schedule_df, payments_df = self.standardize_dataframes(schedule_df, payments_df)
        if reference_date is None:
            reference_date = datetime.now().date()
        elif isinstance(reference_date, datetime):
            reference_date = reference_date.date()

        sched = schedule_df.loc[schedule_df["due_date"] <= reference_date].copy()
        pays  = payments_df.loc[payments_df["payment_date"] <= reference_date].copy()

        # Aggregate by loan_id + date
        s = (sched.groupby(["loan_id","due_date"], as_index=False)
                   .agg(due_amount=("due_amount","sum"))
                   .rename(columns={"due_date":"date"}))
        p = (pays.groupby(["loan_id","payment_date"], as_index=False)
                  .agg(payment_amount=("payment_amount","sum"))
                  .rename(columns={"payment_date":"date"}))

        # Merge by loan_id+date, fillna, then calculate cumulative values per loan
        tl = (s.merge(p, on=["loan_id","date"], how="outer")
                .sort_values(["loan_id","date"]))
        tl["due_amount"] = pd.to_numeric(tl["due_amount"], errors="coerce").fillna(0)
        tl["payment_amount"] = pd.to_numeric(tl["payment_amount"], errors="coerce").fillna(0)

        tl["cumulative_due"]  = tl.groupby("loan_id")["due_amount"].cumsum()
        tl["cumulative_paid"] = tl.groupby("loan_id")["payment_amount"].cumsum()
        tl["cumulative_gap"]  = tl["cumulative_due"] - tl["cumulative_paid"]
        return tl
    
    def calculate_dpd(self, schedule_df: pd.DataFrame, payments_df: pd.DataFrame,
                      reference_date: Optional[Union[datetime, date]] = None) -> pd.DataFrame:
        """
        Calculate Days Past Due (DPD) for each loan.
        
        Args:
            schedule_df: DataFrame with columns [loan_id, due_date, due_amount]
            payments_df: DataFrame with columns [loan_id, payment_date, payment_amount]
            reference_date: Reference date for calculations. Defaults to current date.
        
        Returns:
            DataFrame with DPD information per loan including:
                - loan_id
                - past_due_amount
                - days_past_due
                - first_arrears_date
                - last_payment_date
                - last_due_date
                - is_default
                - reference_date
        """
        if reference_date is None:
            reference_date = datetime.now().date()
        elif isinstance(reference_date, datetime):
            reference_date = reference_date.date()

        schedule_df, payments_df = self.standardize_dataframes(schedule_df, payments_df)
        tl = self.calculate_payment_timeline(schedule_df, payments_df, reference_date)

        # Last state per loan
        idx = tl.groupby("loan_id")["date"].idxmax()
        last = tl.loc[idx].copy()

        # First arrears date (gap > 0) per loan
        arrears = tl.loc[tl["cumulative_gap"] > 0, ["loan_id","date"]].groupby("loan_id", as_index=False).min()
        arrears.rename(columns={"date":"first_arrears_date"}, inplace=True)

        out = last[["loan_id","cumulative_gap","date"]].rename(columns={"cumulative_gap":"past_due_amount",
                                                                        "date":"status_date"})
        out = out.merge(arrears, on="loan_id", how="left")

        # DPD calculation
        fad = pd.to_datetime(out["first_arrears_date"], errors="coerce")
        dpd = (pd.to_datetime(reference_date) - fad).dt.days
        out["days_past_due"] = np.where(fad.notna(), np.maximum(dpd, 0), 0).astype('int64')

        # Auxiliary dates
        last_pay = payments_df.groupby("loan_id")["payment_date"].max().reset_index().rename(columns={"payment_date":"last_payment_date"})
        last_due = schedule_df.groupby("loan_id")["due_date"].max().reset_index().rename(columns={"due_date":"last_due_date"})
        out = out.merge(last_pay, on="loan_id", how="left").merge(last_due, on="loan_id", how="left")

        out["is_default"] = out["days_past_due"] >= self.dpd_threshold
        out["reference_date"] = reference_date
        out["past_due_amount"] = out["past_due_amount"].clip(lower=0).fillna(0)

        # Compact logging
        logger.info(f"DPD done: loans={len(out)}, defaults={int(out['is_default'].sum())}, "
                    f"avg_dpd={out['days_past_due'].mean():.2f}, past_due={out['past_due_amount'].sum():.2f}")
        return out[["loan_id","past_due_amount","days_past_due","first_arrears_date",
                    "last_payment_date","last_due_date","is_default","reference_date"]]
