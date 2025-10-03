"""
Payment Processor module for DPD bucket classification.

This module provides DPD (Days Past Due) bucket classification with a focus on
default status determination. The default threshold is set at 180 days, which
represents the point at which a loan is considered in default status.
"""

from typing import Dict, Any
import pandas as pd


class PaymentProcessor:
    """
    Process payments and assign DPD (Days Past Due) buckets.
    
    The PaymentProcessor uses a configurable dpd_threshold (default 180 days) to mark
    default_flag. This represents the technical default status for accounting and
    regulatory purposes.
    
    Attributes:
        dpd_threshold (int): The number of days past due at which a loan is considered
                           in default status. Default is 180 days.
    """
    
    def __init__(self, dpd_threshold: int = 180):
        """
        Initialize the PaymentProcessor.
        
        Args:
            dpd_threshold (int): The threshold in days for marking default_flag.
                               Default is 180 days.
        """
        self.dpd_threshold = dpd_threshold
    
    def assign_dpd_buckets(self, df: pd.DataFrame, dpd_column: str = 'days_past_due') -> pd.DataFrame:
        """
        Assign DPD buckets with detailed labels and descriptions.
        
        This method categorizes loans based on their days past due into buckets and
        assigns a default_flag based on the dpd_threshold. The default_flag indicates
        loans that have reached the technical default status (>= dpd_threshold days).
        
        Bucket categories:
        - Current: 0-29 days
        - DPD 30-59: 30-59 days
        - DPD 60-89: 60-89 days
        - DPD 90-119: 90-119 days (High Risk, but not yet default by 180-day standard)
        - DPD 120-179: 120-179 days (High Risk, but not yet default by 180-day standard)
        - Default 180+ days: 180+ days (Technical default status)
        
        Args:
            df (pd.DataFrame): DataFrame containing loan data
            dpd_column (str): Name of the column containing days past due values
        
        Returns:
            pd.DataFrame: DataFrame with added columns:
                - dpd_bucket: Categorical bucket label
                - dpd_bucket_description: Detailed description of the bucket
                - default_flag: Boolean indicating if loan is in default (>= dpd_threshold)
        
        Note:
            The default_flag is set based on dpd_threshold (default 180 days), which
            represents the accounting/regulatory definition of default. Loans in the
            90-179 day range are considered "High Risk" but not yet "Default" by this
            strict definition.
        """
        df = df.copy()
        
        # Ensure dpd_column exists
        if dpd_column not in df.columns:
            raise ValueError(f"Column '{dpd_column}' not found in DataFrame")
        
        # Initialize columns
        df['dpd_bucket'] = None
        df['dpd_bucket_description'] = None
        df['default_flag'] = False
        
        # Assign buckets based on days past due
        conditions = [
            (df[dpd_column] >= 0) & (df[dpd_column] < 30),
            (df[dpd_column] >= 30) & (df[dpd_column] < 60),
            (df[dpd_column] >= 60) & (df[dpd_column] < 90),
            (df[dpd_column] >= 90) & (df[dpd_column] < 120),
            (df[dpd_column] >= 120) & (df[dpd_column] < self.dpd_threshold),
            (df[dpd_column] >= self.dpd_threshold)
        ]
        
        bucket_labels = [
            'Current',
            'DPD_30',
            'DPD_60',
            'DPD_90',
            'DPD_120',
            f'DPD_{self.dpd_threshold}'
        ]
        
        bucket_descriptions = [
            'Current (0-29 days)',
            'DPD 30-59 days',
            'DPD 60-89 days',
            'DPD 90-119 days (High Risk)',
            f'DPD 120-{self.dpd_threshold-1} days (High Risk)',
            f'Default {self.dpd_threshold}+ days (Technical Default)'
        ]
        
        # Apply conditions
        for condition, label, description in zip(conditions, bucket_labels, bucket_descriptions):
            df.loc[condition, 'dpd_bucket'] = label
            df.loc[condition, 'dpd_bucket_description'] = description
        
        # Set default_flag for loans >= dpd_threshold
        df['default_flag'] = df[dpd_column] >= self.dpd_threshold
        
        return df
