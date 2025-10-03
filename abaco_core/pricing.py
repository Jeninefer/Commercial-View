"""
Pricing Module

Handles auto-discovery of pricing files, joins, interval matching, 
and APR-EIR spread calculations.
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)


class PricingFileDiscovery:
    """Auto-discover and load pricing files."""
    
    SUPPORTED_FORMATS = ['.csv', '.xlsx', '.xls', '.parquet']
    
    @classmethod
    def discover_pricing_files(cls, directory: Path, pattern: str = '*pricing*') -> List[Path]:
        """
        Discover pricing files in a directory.
        
        Args:
            directory: Directory to search
            pattern: Glob pattern to match files
        
        Returns:
            List[Path]: List of discovered pricing files
        """
        if not isinstance(directory, Path):
            directory = Path(directory)
        
        if not directory.exists():
            logger.warning(f"Directory {directory} does not exist")
            return []
        
        files = []
        for ext in cls.SUPPORTED_FORMATS:
            files.extend(directory.glob(f'{pattern}{ext}'))
        
        logger.info(f"Discovered {len(files)} pricing files in {directory}")
        return sorted(files)
    
    @classmethod
    def load_pricing_file(cls, file_path: Path) -> Optional[pd.DataFrame]:
        """
        Load a pricing file based on its extension.
        
        Args:
            file_path: Path to pricing file
        
        Returns:
            Optional[pd.DataFrame]: Loaded dataframe or None
        """
        if not isinstance(file_path, Path):
            file_path = Path(file_path)
        
        if not file_path.exists():
            logger.error(f"File {file_path} does not exist")
            return None
        
        ext = file_path.suffix.lower()
        
        try:
            if ext == '.csv':
                df = pd.read_csv(file_path)
            elif ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            elif ext == '.parquet':
                df = pd.read_parquet(file_path)
            else:
                logger.error(f"Unsupported file format: {ext}")
                return None
            
            logger.info(f"Loaded pricing file {file_path.name} with {len(df)} records")
            return df
        
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return None


class IntervalMatcher:
    """Match values to pricing intervals."""
    
    @staticmethod
    def match_to_interval(value: float, intervals: pd.DataFrame, 
                         lower_col: str = 'min', upper_col: str = 'max',
                         closed: str = 'left') -> Optional[int]:
        """
        Match a value to an interval.
        
        Args:
            value: Value to match
            intervals: DataFrame with interval definitions
            lower_col: Column name for lower bound
            upper_col: Column name for upper bound
            closed: Which side of interval is closed ('left', 'right', 'both')
        
        Returns:
            Optional[int]: Index of matching interval or None
        """
        for idx, row in intervals.iterrows():
            lower = row[lower_col]
            upper = row[upper_col]
            
            if closed == 'left':
                match = lower <= value < upper
            elif closed == 'right':
                match = lower < value <= upper
            elif closed == 'both':
                match = lower <= value <= upper
            else:
                match = lower < value < upper
            
            if match:
                return idx
        
        return None
    
    @staticmethod
    def match_dataframe_to_intervals(df: pd.DataFrame, value_col: str,
                                    intervals: pd.DataFrame,
                                    lower_col: str = 'min', upper_col: str = 'max',
                                    closed: str = 'left') -> pd.DataFrame:
        """
        Match all values in a dataframe to intervals.
        
        Args:
            df: Input dataframe
            value_col: Column with values to match
            intervals: DataFrame with interval definitions
            lower_col: Column name for lower bound
            upper_col: Column name for upper bound
            closed: Which side of interval is closed
        
        Returns:
            pd.DataFrame: DataFrame with matched interval index
        """
        result = df.copy()
        
        result['interval_index'] = result[value_col].apply(
            lambda x: IntervalMatcher.match_to_interval(
                x, intervals, lower_col, upper_col, closed
            )
        )
        
        matched_count = result['interval_index'].notna().sum()
        logger.info(f"Matched {matched_count}/{len(result)} records to intervals")
        
        return result


class APRCalculator:
    """Calculate APR (Annual Percentage Rate) and EIR (Effective Interest Rate)."""
    
    @staticmethod
    def calculate_apr(principal: float, total_interest: float, term_months: int) -> float:
        """
        Calculate Annual Percentage Rate.
        
        Args:
            principal: Loan principal amount
            total_interest: Total interest paid
            term_months: Loan term in months
        
        Returns:
            float: APR as a decimal (e.g., 0.15 for 15%)
        """
        if principal <= 0 or term_months <= 0:
            return 0.0
        
        term_years = term_months / 12
        apr = (total_interest / principal) / term_years
        
        return apr
    
    @staticmethod
    def calculate_eir(nominal_rate: float, compounding_periods: int = 12) -> float:
        """
        Calculate Effective Interest Rate from nominal rate.
        
        Args:
            nominal_rate: Nominal annual rate (as decimal)
            compounding_periods: Number of compounding periods per year
        
        Returns:
            float: EIR as a decimal
        """
        if nominal_rate <= 0 or compounding_periods <= 0:
            return 0.0
        
        eir = (1 + nominal_rate / compounding_periods) ** compounding_periods - 1
        
        return eir
    
    @staticmethod
    def calculate_apr_eir_spread(apr: float, eir: float) -> float:
        """
        Calculate the spread between APR and EIR.
        
        Args:
            apr: Annual Percentage Rate
            eir: Effective Interest Rate
        
        Returns:
            float: Spread (EIR - APR)
        """
        return eir - apr


def join_pricing_data(base_df: pd.DataFrame, pricing_df: pd.DataFrame,
                     join_keys: List[str], how: str = 'left') -> pd.DataFrame:
    """
    Join base data with pricing information.
    
    Args:
        base_df: Base dataframe
        pricing_df: Pricing dataframe
        join_keys: List of column names to join on
        how: Type of join ('left', 'inner', 'outer', 'right')
    
    Returns:
        pd.DataFrame: Joined dataframe
    """
    result = base_df.merge(pricing_df, on=join_keys, how=how, suffixes=('', '_pricing'))
    
    logger.info(f"Joined pricing data: {len(base_df)} -> {len(result)} records")
    return result


def enrich_with_pricing(df: pd.DataFrame, pricing_directory: Optional[Path] = None) -> pd.DataFrame:
    """
    Enrich dataframe with pricing information from discovered files.
    
    Args:
        df: Base dataframe to enrich
        pricing_directory: Directory to search for pricing files
    
    Returns:
        pd.DataFrame: Enriched dataframe
    """
    if pricing_directory is None:
        logger.warning("No pricing directory specified, returning original dataframe")
        return df
    
    # Discover pricing files
    files = PricingFileDiscovery.discover_pricing_files(pricing_directory)
    
    if not files:
        logger.warning("No pricing files found, returning original dataframe")
        return df
    
    enriched = df.copy()
    
    # Load and join each pricing file (simplified - in practice would need more logic)
    for file in files:
        pricing_df = PricingFileDiscovery.load_pricing_file(file)
        if pricing_df is not None and 'loan_id' in enriched.columns and 'loan_id' in pricing_df.columns:
            enriched = join_pricing_data(enriched, pricing_df, ['loan_id'])
    
    return enriched


def calculate_pricing_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate pricing metrics including APR, EIR, and spreads.
    
    Args:
        df: DataFrame with loan data
    
    Returns:
        pd.DataFrame: DataFrame with calculated metrics
    """
    result = df.copy()
    
    # Calculate APR if we have the necessary columns
    if all(col in result.columns for col in ['principal', 'total_interest', 'term_months']):
        result['apr'] = result.apply(
            lambda row: APRCalculator.calculate_apr(
                row['principal'], row['total_interest'], row['term_months']
            ), axis=1
        )
    
    # Calculate EIR if we have nominal rate
    if 'nominal_rate' in result.columns:
        result['eir'] = result['nominal_rate'].apply(
            lambda x: APRCalculator.calculate_eir(x)
        )
    
    # Calculate spread if we have both APR and EIR
    if 'apr' in result.columns and 'eir' in result.columns:
        result['apr_eir_spread'] = result.apply(
            lambda row: APRCalculator.calculate_apr_eir_spread(row['apr'], row['eir']),
            axis=1
        )
    
    logger.info(f"Calculated pricing metrics for {len(result)} records")
    return result
