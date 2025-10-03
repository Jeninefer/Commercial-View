"""
Feature Engineer module for risk-based DPD classification.

This module provides DPD (Days Past Due) bucket classification with a focus on
risk segmentation. The is_default flag is set at 90 days, which represents the
point at which a loan is considered high risk for analytical purposes.
"""

from typing import Dict, Any
import pandas as pd


class FeatureEngineer:
    """
    Engineer features including risk-based DPD bucket classification.
    
    The FeatureEngineer uses a risk-based approach where loans >= 90 days past due
    are flagged as is_default for risk analysis purposes. This is distinct from the
    accounting/regulatory default definition (typically 180 days) used in
    PaymentProcessor.
    
    Key differences from PaymentProcessor:
    - is_default flag is set at 90+ days (high risk threshold)
    - default_flag in PaymentProcessor is set at 180+ days (accounting threshold)
    - This serves analytical and risk segmentation needs
    
    Attributes:
        risk_threshold (int): The number of days past due at which a loan is considered
                            high risk. Default is 90 days.
    """
    
    def __init__(self, risk_threshold: int = 90):
        """
        Initialize the FeatureEngineer.
        
        Args:
            risk_threshold (int): The threshold in days for marking is_default for
                                risk analysis purposes. Default is 90 days.
        """
        self.risk_threshold = risk_threshold
    
    def assign_dpd_buckets(self, df: pd.DataFrame, dpd_column: str = 'days_past_due') -> pd.DataFrame:
        """
        Assign DPD buckets with risk-based default classification.
        
        This method categorizes loans based on their days past due into buckets and
        assigns an is_default flag for risk analysis purposes. The is_default flag
        indicates loans that have reached the high risk threshold (>= risk_threshold days).
        
        Bucket categories:
        - Current: 0-29 days
        - DPD_30: 30-59 days
        - DPD_60: 60-89 days
        - DPD_90: 90-119 days (High Risk - is_default = True)
        - DPD_120: 120-179 days (High Risk - is_default = True)
        - DPD_180: 180+ days (Default - is_default = True)
        
        Args:
            df (pd.DataFrame): DataFrame containing loan data
            dpd_column (str): Name of the column containing days past due values
        
        Returns:
            pd.DataFrame: DataFrame with added columns:
                - dpd_bucket: Categorical bucket label
                - dpd_risk_category: Risk category (Current, Early Delinquency, High Risk, Default)
                - is_default: Boolean indicating if loan is in high risk category (>= risk_threshold)
        
        Note:
            The is_default flag (>= 90 days) is more aggressive than the accounting
            default definition (>= 180 days) and is used for risk segmentation and
            analytical purposes. This allows earlier identification of problematic loans
            for portfolio management and risk mitigation strategies.
        """
        df = df.copy()
        
        # Ensure dpd_column exists
        if dpd_column not in df.columns:
            raise ValueError(f"Column '{dpd_column}' not found in DataFrame")
        
        # Initialize columns
        df['dpd_bucket'] = None
        df['dpd_risk_category'] = None
        df['is_default'] = False
        
        # Assign buckets and risk categories based on days past due
        conditions = [
            (df[dpd_column] >= 0) & (df[dpd_column] < 30),
            (df[dpd_column] >= 30) & (df[dpd_column] < 60),
            (df[dpd_column] >= 60) & (df[dpd_column] < 90),
            (df[dpd_column] >= 90) & (df[dpd_column] < 120),
            (df[dpd_column] >= 120) & (df[dpd_column] < 180),
            (df[dpd_column] >= 180)
        ]
        
        bucket_labels = [
            'Current',
            'DPD_30',
            'DPD_60',
            'DPD_90',
            'DPD_120',
            'DPD_180'
        ]
        
        risk_categories = [
            'Current',
            'Early Delinquency',
            'Early Delinquency',
            'High Risk',
            'High Risk',
            'Default'
        ]
        
        # Apply conditions
        for condition, label, category in zip(conditions, bucket_labels, risk_categories):
            df.loc[condition, 'dpd_bucket'] = label
            df.loc[condition, 'dpd_risk_category'] = category
        
        # Set is_default flag for loans >= risk_threshold (90 days by default)
        # This is for risk analysis purposes and is more aggressive than the
        # accounting default definition (180 days)
        df['is_default'] = df[dpd_column] >= self.risk_threshold
        
        return df
