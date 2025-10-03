"""
Feature Engineering Module for Commercial View
Contains the FeatureEngineer class and wrapper functions for data processing.
"""

import pandas as pd
import numpy as np
from datetime import datetime


class FeatureEngineer:
    """
    Feature engineering class for commercial data processing.
    Provides methods for client segmentation, classification, and metric calculation.
    """
    
    def segment_clients_by_exposure(self, df, exposure_col='outstanding_balance', segments=None):
        """
        Segment clients by exposure amount.
        
        Parameters:
        -----------
        df : pd.DataFrame
            Input dataframe
        exposure_col : str
            Column name for exposure/outstanding balance
        segments : list or None
            List of segment thresholds. If None, uses default [10000, 50000, 100000]
            
        Returns:
        --------
        pd.DataFrame
            DataFrame with added 'exposure_segment' column
        """
        if segments is None:
            segments = [10000, 50000, 100000]
        
        result_df = df.copy()
        
        # Create segment labels
        labels = []
        for i in range(len(segments) + 1):
            if i == 0:
                labels.append(f'0-{segments[0]}')
            elif i == len(segments):
                labels.append(f'{segments[-1]}+')
            else:
                labels.append(f'{segments[i-1]}-{segments[i]}')
        
        # Assign segments using pd.cut
        result_df['exposure_segment'] = pd.cut(
            result_df[exposure_col],
            bins=[-np.inf] + segments + [np.inf],
            labels=labels,
            include_lowest=True
        )
        
        return result_df
    
    def classify_dpd_buckets(self, df, dpd_col='days_past_due'):
        """
        Classify days past due into buckets.
        
        Parameters:
        -----------
        df : pd.DataFrame
            Input dataframe
        dpd_col : str
            Column name for days past due
            
        Returns:
        --------
        pd.DataFrame
            DataFrame with added 'dpd_bucket' column
        """
        result_df = df.copy()
        
        def get_dpd_bucket(dpd):
            if pd.isna(dpd):
                return 'Unknown'
            if dpd <= 0:
                return 'Current'
            elif dpd <= 30:
                return '1-30'
            elif dpd <= 60:
                return '31-60'
            elif dpd <= 90:
                return '61-90'
            elif dpd <= 180:
                return '91-180'
            else:
                return '180+'
        
        result_df['dpd_bucket'] = result_df[dpd_col].apply(get_dpd_bucket)
        
        return result_df
    
    def classify_client_type(self, df, customer_id_col='customer_id', 
                            loan_count_col='loan_count', last_active_col='last_active_date'):
        """
        Classify client type based on loan count and activity.
        
        Parameters:
        -----------
        df : pd.DataFrame
            Input dataframe
        customer_id_col : str
            Column name for customer ID
        loan_count_col : str
            Column name for loan count
        last_active_col : str
            Column name for last active date
            
        Returns:
        --------
        pd.DataFrame
            DataFrame with added 'client_type' column
        """
        result_df = df.copy()
        
        def get_client_type(row):
            loan_count = row[loan_count_col] if loan_count_col in row.index else 1
            last_active = row[last_active_col] if last_active_col in row.index else datetime.now()
            
            # Check if last_active is valid
            if pd.isna(last_active):
                days_inactive = 0
            else:
                # Convert to datetime if string
                if isinstance(last_active, str):
                    try:
                        last_active = pd.to_datetime(last_active)
                    except:
                        days_inactive = 0
                else:
                    last_active = pd.to_datetime(last_active)
                
                days_inactive = (datetime.now() - last_active).days
            
            # Classification logic
            if pd.isna(loan_count) or loan_count == 0:
                return 'Inactive'
            elif loan_count == 1 and days_inactive > 180:
                return 'Dormant'
            elif loan_count == 1:
                return 'New'
            elif loan_count <= 5:
                return 'Regular'
            else:
                return 'High-Value'
        
        result_df['client_type'] = result_df.apply(get_client_type, axis=1)
        
        return result_df
    
    def calculate_weighted_metrics(self, df, metrics, weight_col='outstanding_balance'):
        """
        Calculate weighted metrics.
        
        Parameters:
        -----------
        df : pd.DataFrame
            Input dataframe
        metrics : list
            List of metric column names to weight
        weight_col : str
            Column name for weights
            
        Returns:
        --------
        pd.DataFrame
            DataFrame with added weighted metric columns
        """
        result_df = df.copy()
        
        # Calculate total weight
        total_weight = result_df[weight_col].sum()
        
        if total_weight == 0:
            # Handle edge case where total weight is 0
            for metric in metrics:
                result_df[f'weighted_{metric}'] = 0
        else:
            # Calculate weighted metrics
            for metric in metrics:
                if metric in result_df.columns:
                    result_df[f'weighted_{metric}'] = (
                        result_df[metric] * result_df[weight_col] / total_weight
                    )
                else:
                    result_df[f'weighted_{metric}'] = 0
        
        return result_df
    
    def calculate_line_utilization(self, df, credit_line_field='line_amount', 
                                   loan_amount_field='outstanding_balance'):
        """
        Calculate line utilization ratio.
        
        Parameters:
        -----------
        df : pd.DataFrame
            Input dataframe
        credit_line_field : str
            Column name for credit line amount
        loan_amount_field : str
            Column name for loan/outstanding balance amount
            
        Returns:
        --------
        pd.DataFrame
            DataFrame with added 'line_utilization' column
        """
        result_df = df.copy()
        
        # Calculate utilization ratio
        def calculate_utilization(row):
            credit_line = row[credit_line_field]
            loan_amount = row[loan_amount_field]
            
            if pd.isna(credit_line) or pd.isna(loan_amount):
                return 0.0
            if credit_line == 0:
                return 0.0
            
            return (loan_amount / credit_line) * 100
        
        result_df['line_utilization'] = result_df.apply(calculate_utilization, axis=1)
        
        return result_df
    
    def enrich_master_dataframe(self, df):
        """
        Enrich master dataframe with all features.
        
        Parameters:
        -----------
        df : pd.DataFrame
            Input dataframe
            
        Returns:
        --------
        pd.DataFrame
            Enriched dataframe with all features
        """
        result_df = df.copy()
        
        # Apply all enrichment methods if columns exist
        if 'outstanding_balance' in result_df.columns:
            result_df = self.segment_clients_by_exposure(result_df)
        
        if 'days_past_due' in result_df.columns:
            result_df = self.classify_dpd_buckets(result_df)
        
        if 'customer_id' in result_df.columns:
            result_df = self.classify_client_type(result_df)
        
        if 'outstanding_balance' in result_df.columns and 'line_amount' in result_df.columns:
            result_df = self.calculate_line_utilization(result_df)
        
        return result_df


# Global instance
feature_engineer = FeatureEngineer()


def segment_clients_by_exposure(df, exposure_col='outstanding_balance', segments=None):
    """
    Wrapper function to segment clients by exposure.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    exposure_col : str
        Column name for exposure/outstanding balance
    segments : list or None
        List of segment thresholds
        
    Returns:
    --------
    pd.DataFrame
        DataFrame with added 'exposure_segment' column
    """
    assert isinstance(df, pd.DataFrame), "df must be a DataFrame"
    return feature_engineer.segment_clients_by_exposure(df, exposure_col, segments)


def classify_dpd_buckets(df, dpd_col='days_past_due'):
    """
    Wrapper function to classify days past due into buckets.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    dpd_col : str
        Column name for days past due
        
    Returns:
    --------
    pd.DataFrame
        DataFrame with added 'dpd_bucket' column
    """
    assert isinstance(df, pd.DataFrame), "df must be a DataFrame"
    return feature_engineer.classify_dpd_buckets(df, dpd_col)


def classify_client_type(df, customer_id_col='customer_id', loan_count_col='loan_count', last_active_col='last_active_date'):
    """
    Wrapper function to classify client type.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    customer_id_col : str
        Column name for customer ID
    loan_count_col : str
        Column name for loan count
    last_active_col : str
        Column name for last active date
        
    Returns:
    --------
    pd.DataFrame
        DataFrame with added 'client_type' column
    """
    assert isinstance(df, pd.DataFrame), "df must be a DataFrame"
    return feature_engineer.classify_client_type(df, customer_id_col, loan_count_col, last_active_col)


def calculate_weighted_metrics(df, metrics, weight_col='outstanding_balance'):
    """
    Wrapper function to calculate weighted metrics.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    metrics : list
        List of metric column names to weight
    weight_col : str
        Column name for weights
        
    Returns:
    --------
    pd.DataFrame
        DataFrame with added weighted metric columns
    """
    assert isinstance(df, pd.DataFrame), "df must be a DataFrame"
    assert isinstance(metrics, (list, tuple)) and metrics, "metrics must be a non-empty list"
    return feature_engineer.calculate_weighted_metrics(df, metrics, weight_col)


def calculate_line_utilization(df, balance_col='outstanding_balance', line_col='line_amount'):
    """
    Wrapper function to calculate line utilization.
    Note: The wrapper intentionally switches order to match (credit_line_field, loan_amount_field)
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    balance_col : str
        Column name for loan/outstanding balance
    line_col : str
        Column name for credit line amount
        
    Returns:
    --------
    pd.DataFrame
        DataFrame with added 'line_utilization' column
    """
    assert isinstance(df, pd.DataFrame), "df must be a DataFrame"
    return feature_engineer.calculate_line_utilization(df, line_col, balance_col)


def enrich_master_dataframe(df):
    """
    Wrapper function to enrich master dataframe with all features.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
        
    Returns:
    --------
    pd.DataFrame
        Enriched dataframe with all features
    """
    assert isinstance(df, pd.DataFrame), "df must be a DataFrame"
    return feature_engineer.enrich_master_dataframe(df)
