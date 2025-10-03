"""
PaymentProcessor module for handling loan payment calculations and default detection.

This module provides functionality to process loan payments and identify
defaults based on configurable Days Past Due (DPD) thresholds.
"""

import pandas as pd
from typing import Optional


class PaymentProcessor:
    """
    Processes loan payments and determines default status.
    
    The PaymentProcessor handles payment calculations and identifies loans
    in default based on configurable DPD (Days Past Due) thresholds.
    """
    
    def __init__(self, default_threshold: int = 180):
        """
        Initialize the PaymentProcessor with a default threshold.
        
        Args:
            default_threshold: Days Past Due threshold for considering a loan
                             in default. Common thresholds:
                             - 90 days: Technical default (Basel II/III standard)
                             - 180 days: Write-off threshold (common in US)
                             - 360 days: Full write-off
                             Default is 180 days.
        
        Note:
            The default threshold should align with your organization's
            credit policies and regulatory requirements. For example:
            - 90+ days is often used for regulatory reporting (technical default)
            - 180+ days might be used for write-off decisions
            - Different jurisdictions may have different standards
        """
        self.default_threshold = default_threshold
    
    def is_default(self, days_past_due: int, threshold: Optional[int] = None) -> bool:
        """
        Determine if a loan is in default based on Days Past Due.
        
        A loan is considered in default if the days past due meets or exceeds
        the threshold. This method uses the instance's default_threshold unless
        a specific threshold is provided.
        
        Args:
            days_past_due: Number of days the loan payment is past due
            threshold: Optional override threshold. If not provided, uses
                      the instance's default_threshold set during initialization.
        
        Returns:
            True if the loan is in default (DPD >= threshold), False otherwise
        
        Example:
            >>> processor = PaymentProcessor(default_threshold=180)
            >>> processor.is_default(185)  # Returns True
            >>> processor.is_default(175)  # Returns False
            >>> processor.is_default(95, threshold=90)  # Returns True (custom threshold)
        
        Note:
            What "default" means in your context:
            - 90+ day DPD: Technical default per Basel standards
            - 180+ day DPD: Common write-off threshold in US markets
            - Your organization may have different policies
        """
        effective_threshold = threshold if threshold is not None else self.default_threshold
        return days_past_due >= effective_threshold
    
    def process_payments(self, payments_df: pd.DataFrame, 
                        dpd_column: str = 'days_past_due') -> pd.DataFrame:
        """
        Process a DataFrame of payments and add default status.
        
        Args:
            payments_df: DataFrame containing payment data
            dpd_column: Name of the column containing days past due values
        
        Returns:
            DataFrame with an additional 'is_default' column
        """
        result_df = payments_df.copy()
        result_df['is_default'] = result_df[dpd_column].apply(self.is_default)
        return result_df
    
    def calculate_default_rate(self, payments_df: pd.DataFrame,
                              dpd_column: str = 'days_past_due') -> float:
        """
        Calculate the default rate for a portfolio.
        
        Args:
            payments_df: DataFrame containing payment data
            dpd_column: Name of the column containing days past due values
        
        Returns:
            Default rate as a decimal (0.0 to 1.0)
        """
        if len(payments_df) == 0:
            return 0.0
        
        defaults = payments_df[dpd_column].apply(self.is_default).sum()
        return defaults / len(payments_df)
