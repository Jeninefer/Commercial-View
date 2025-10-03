"""
Feature Engineering Module

Handles exposure segmentation, DPD buckets, client type classification, 
HHI (Herfindahl-Hirschman Index), and master enrichment.
"""

import logging
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class ExposureSegmentation:
    """Segment loan exposure into categories."""
    
    SEGMENTS = {
        'micro': (0, 10000),
        'small': (10000, 50000),
        'medium': (50000, 200000),
        'large': (200000, float('inf'))
    }
    
    @classmethod
    def segment_exposure(cls, amount: float) -> str:
        """
        Categorize exposure amount into segments.
        
        Args:
            amount: Exposure amount
        
        Returns:
            str: Segment category
        """
        for segment, (min_val, max_val) in cls.SEGMENTS.items():
            if min_val <= amount < max_val:
                return segment
        return 'unknown'
    
    @classmethod
    def segment_dataframe(cls, df: pd.DataFrame, amount_col: str = 'exposure') -> pd.DataFrame:
        """
        Add exposure segment column to dataframe.
        
        Args:
            df: DataFrame with exposure data
            amount_col: Name of the amount column
        
        Returns:
            pd.DataFrame: DataFrame with segment column
        """
        df = df.copy()
        df['exposure_segment'] = df[amount_col].apply(cls.segment_exposure)
        logger.info(f"Segmented {len(df)} exposures")
        return df


class ClientTypeClassifier:
    """Classify clients into types."""
    
    CLIENT_TYPES = ['individual', 'small_business', 'corporate', 'government']
    
    @staticmethod
    def classify_client(revenue: Optional[float] = None, employee_count: Optional[int] = None,
                       legal_form: Optional[str] = None) -> str:
        """
        Classify client type based on characteristics.
        
        Args:
            revenue: Annual revenue
            employee_count: Number of employees
            legal_form: Legal form of entity
        
        Returns:
            str: Client type
        """
        if legal_form and 'government' in legal_form.lower():
            return 'government'
        
        if revenue is None and employee_count is None:
            return 'individual'
        
        if revenue and revenue > 10_000_000:
            return 'corporate'
        
        if employee_count and employee_count > 50:
            return 'corporate'
        
        if revenue and revenue > 500_000:
            return 'small_business'
        
        if employee_count and employee_count > 5:
            return 'small_business'
        
        return 'individual'


class HHICalculator:
    """Calculate Herfindahl-Hirschman Index for portfolio concentration."""
    
    @staticmethod
    def calculate_hhi(market_shares: List[float]) -> float:
        """
        Calculate HHI from market shares.
        
        Args:
            market_shares: List of market shares (as percentages or decimals)
        
        Returns:
            float: HHI value (0-10000 scale if percentages, 0-1 if decimals)
        """
        if not market_shares:
            return 0.0
        
        # Normalize to ensure they're in percentage form
        total = sum(market_shares)
        if total > 0:
            normalized_shares = [share / total * 100 for share in market_shares]
        else:
            return 0.0
        
        hhi = sum(share ** 2 for share in normalized_shares)
        logger.debug(f"Calculated HHI: {hhi:.2f}")
        return hhi
    
    @staticmethod
    def calculate_portfolio_hhi(df: pd.DataFrame, group_col: str, amount_col: str) -> float:
        """
        Calculate HHI for a portfolio grouped by a specific column.
        
        Args:
            df: Portfolio dataframe
            group_col: Column to group by (e.g., 'client_id', 'sector')
            amount_col: Column with amounts
        
        Returns:
            float: Portfolio HHI
        """
        if df.empty:
            return 0.0
        
        grouped = df.groupby(group_col)[amount_col].sum()
        market_shares = grouped.values
        hhi = HHICalculator.calculate_hhi(market_shares)
        
        logger.info(f"Portfolio HHI by {group_col}: {hhi:.2f}")
        return hhi


def create_dpd_buckets(df: pd.DataFrame, dpd_col: str = 'dpd') -> pd.DataFrame:
    """
    Add DPD bucket column to dataframe.
    
    Args:
        df: DataFrame with DPD data
        dpd_col: Name of the DPD column
    
    Returns:
        pd.DataFrame: DataFrame with DPD bucket column
    """
    from .payment_logic import DPDCalculator
    
    df = df.copy()
    df['dpd_bucket'] = df[dpd_col].apply(DPDCalculator.get_dpd_bucket)
    logger.info(f"Created DPD buckets for {len(df)} records")
    return df


def master_enrichment(base_df: pd.DataFrame, enrichment_dfs: Dict[str, pd.DataFrame],
                     join_keys: Dict[str, str]) -> pd.DataFrame:
    """
    Enrich master dataframe with additional data sources.
    
    Args:
        base_df: Base dataframe to enrich
        enrichment_dfs: Dictionary of dataframes to join (name -> df)
        join_keys: Dictionary of join keys (enrichment_name -> key_column)
    
    Returns:
        pd.DataFrame: Enriched dataframe
    """
    enriched = base_df.copy()
    
    for name, enrich_df in enrichment_dfs.items():
        if name not in join_keys:
            logger.warning(f"No join key specified for {name}, skipping")
            continue
        
        join_key = join_keys[name]
        
        if join_key not in enriched.columns:
            logger.warning(f"Join key {join_key} not in base dataframe, skipping {name}")
            continue
        
        if join_key not in enrich_df.columns:
            logger.warning(f"Join key {join_key} not in {name} dataframe, skipping")
            continue
        
        enriched = enriched.merge(enrich_df, on=join_key, how='left', suffixes=('', f'_{name}'))
        logger.info(f"Enriched with {name} on key {join_key}")
    
    logger.info(f"Master enrichment complete: {len(base_df)} -> {len(enriched)} records")
    return enriched


def calculate_features(df: pd.DataFrame, feature_config: Dict[str, Any]) -> pd.DataFrame:
    """
    Calculate multiple features based on configuration.
    
    Args:
        df: Input dataframe
        feature_config: Configuration for features to calculate
    
    Returns:
        pd.DataFrame: DataFrame with calculated features
    """
    result = df.copy()
    
    if feature_config.get('exposure_segmentation'):
        amount_col = feature_config.get('exposure_col', 'exposure')
        if amount_col in result.columns:
            result = ExposureSegmentation.segment_dataframe(result, amount_col)
    
    if feature_config.get('dpd_buckets'):
        dpd_col = feature_config.get('dpd_col', 'dpd')
        if dpd_col in result.columns:
            result = create_dpd_buckets(result, dpd_col)
    
    if feature_config.get('client_type'):
        # Apply client type classification if relevant columns exist
        if all(col in result.columns for col in ['revenue', 'employee_count']):
            result['client_type'] = result.apply(
                lambda row: ClientTypeClassifier.classify_client(
                    row.get('revenue'), 
                    row.get('employee_count'),
                    row.get('legal_form')
                ), axis=1
            )
    
    logger.info(f"Feature calculation complete with {len(result.columns)} columns")
    return result
