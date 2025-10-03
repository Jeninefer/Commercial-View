"""
Pricing Enrichment Module

This module provides functionality to enrich loan data with pricing information
and calculate APR-EIR spreads.
"""

import logging
from typing import Optional, Dict, Tuple, List
import pandas as pd
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)


class PricingEnricher:
    """
    A class to handle pricing data enrichment for loan dataframes.
    
    Attributes:
        pricing_paths: List of paths to pricing data files
        pricing_grid: DataFrame containing pricing grid data
        recommended_pricing: DataFrame containing recommended pricing data
    """
    
    def __init__(self, pricing_paths: Optional[List[str]] = None):
        """
        Initialize the PricingEnricher.
        
        Args:
            pricing_paths: Optional list of paths to pricing data files
        """
        self.pricing_paths = pricing_paths or []
        self.pricing_grid = None
        self.recommended_pricing = None
        logger.debug(f"PricingEnricher initialized with paths: {self.pricing_paths}")
    
    def load_pricing_data(self):
        """
        Load pricing data from configured paths.
        
        This method attempts to load pricing grid and recommended pricing data
        from the configured paths. If no paths are configured, it will look for
        default files in common locations.
        """
        logger.info("Loading pricing data...")
        
        if not self.pricing_paths:
            # Look for default pricing files
            default_paths = [
                "data/pricing_grid.csv",
                "data/recommended_pricing.csv",
                "pricing_grid.csv",
                "recommended_pricing.csv"
            ]
            self.pricing_paths = default_paths
        
        # Try to load pricing grid
        for path in self.pricing_paths:
            path_obj = Path(path)
            if path_obj.exists():
                if 'grid' in path.lower():
                    try:
                        self.pricing_grid = pd.read_csv(path)
                        logger.info(f"Loaded pricing grid from {path}")
                    except Exception as e:
                        logger.warning(f"Failed to load pricing grid from {path}: {e}")
                elif 'recommended' in path.lower():
                    try:
                        self.recommended_pricing = pd.read_csv(path)
                        logger.info(f"Loaded recommended pricing from {path}")
                    except Exception as e:
                        logger.warning(f"Failed to load recommended pricing from {path}: {e}")
        
        if self.pricing_grid is None and self.recommended_pricing is None:
            logger.warning("No pricing data files found. Enrichment will use empty data.")
    
    def _identify_rate_columns(
        self,
        df: pd.DataFrame,
        apr_col_hint: Optional[str] = None,
        eir_col_hint: Optional[str] = None
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Identify APR and EIR columns in the dataframe.
        
        Args:
            df: Input DataFrame
            apr_col_hint: Explicit APR column name
            eir_col_hint: Explicit EIR column name
            
        Returns:
            Tuple of (apr_column, eir_column) names, or (None, None) if not found
        """
        apr_col = None
        eir_col = None
        
        if apr_col_hint and apr_col_hint in df.columns:
            apr_col = apr_col_hint
        else:
            # Search for APR column
            apr_candidates = [col for col in df.columns if 'apr' in col.lower()]
            if len(apr_candidates) == 1:
                apr_col = apr_candidates[0]
            elif len(apr_candidates) > 1:
                logger.warning(f"Multiple APR candidates found: {apr_candidates}. Use apr_col_hint to specify.")
        
        if eir_col_hint and eir_col_hint in df.columns:
            eir_col = eir_col_hint
        else:
            # Search for EIR column
            eir_candidates = [col for col in df.columns if 'eir' in col.lower()]
            if len(eir_candidates) == 1:
                eir_col = eir_candidates[0]
            elif len(eir_candidates) > 1:
                logger.warning(f"Multiple EIR candidates found: {eir_candidates}. Use eir_col_hint to specify.")
        
        return apr_col, eir_col
    
    def _apply_band_matching(
        self,
        loan_df: pd.DataFrame,
        pricing_df: pd.DataFrame,
        band_keys: Dict[str, Tuple[str, str]]
    ) -> pd.DataFrame:
        """
        Apply band/interval matching between loan data and pricing data.
        
        Args:
            loan_df: Loan DataFrame
            pricing_df: Pricing DataFrame with band columns
            band_keys: Dict mapping loan column to (min_col, max_col) in pricing
            
        Returns:
            Merged DataFrame with band matching applied
        """
        result = loan_df.copy()
        
        # Get all columns from pricing_df that we want to add
        pricing_cols_to_add = [col for col in pricing_df.columns]
        
        # Create a merge key for each row
        for loan_col, (min_col, max_col) in band_keys.items():
            if loan_col not in loan_df.columns:
                logger.warning(f"Band key column '{loan_col}' not found in loan data")
                continue
            
            if min_col not in pricing_df.columns or max_col not in pricing_df.columns:
                logger.warning(f"Band columns '{min_col}' or '{max_col}' not found in pricing data")
                continue
            
            # Remove min/max columns from the list of columns to add
            pricing_cols_to_add = [col for col in pricing_cols_to_add if col not in [min_col, max_col]]
            
            # Add columns if they don't exist
            for col in pricing_cols_to_add:
                if col not in result.columns:
                    result[col] = pd.NA
            
            # Perform interval matching for each row
            for idx, row in result.iterrows():
                value = row[loan_col]
                matching_rows = pricing_df[
                    (pricing_df[min_col] <= value) & (pricing_df[max_col] >= value)
                ]
                if not matching_rows.empty:
                    pricing_row = matching_rows.iloc[0]
                    for col in pricing_cols_to_add:
                        result.loc[idx, col] = pricing_row[col]
        
        return result
    
    def enrich_loan_data(
        self,
        loan_df: pd.DataFrame,
        *,
        join_keys: Optional[List[str]] = None,
        band_keys: Optional[Dict[str, Tuple[str, str]]] = None,
        apr_col_hint: Optional[str] = None,
        eir_col_hint: Optional[str] = None,
        recommended_rate_col: str = "recommended_rate"
    ) -> pd.DataFrame:
        """
        Enrich loan data with pricing information and calculate APR-EIR spread.
        
        Args:
            loan_df: Input loan DataFrame
            join_keys: List of columns for exact matching between datasets
            band_keys: Dict mapping loan column to (min_col, max_col) in pricing grid
            apr_col_hint: Explicit APR column name
            eir_col_hint: Explicit EIR column name
            recommended_rate_col: Name for recommended rate column in output
            
        Returns:
            Enriched DataFrame with pricing information and spread calculations
        """
        result = loan_df.copy()
        
        # Merge with recommended pricing using join keys
        if join_keys and self.recommended_pricing is not None:
            valid_keys = [k for k in join_keys if k in loan_df.columns and k in self.recommended_pricing.columns]
            if valid_keys:
                logger.info(f"Merging on join keys: {valid_keys}")
                result = result.merge(
                    self.recommended_pricing,
                    on=valid_keys,
                    how='left',
                    suffixes=('', '_pricing')
                )
                # Add recommended rate column if it exists in pricing data
                if recommended_rate_col in self.recommended_pricing.columns:
                    pricing_col = f"{recommended_rate_col}_pricing"
                    if pricing_col in result.columns:
                        result[recommended_rate_col] = result[pricing_col]
                        result = result.drop(columns=[pricing_col])
        
        # Apply band matching with pricing grid
        if band_keys and self.pricing_grid is not None:
            logger.info(f"Applying band matching with keys: {band_keys}")
            result = self._apply_band_matching(result, self.pricing_grid, band_keys)
        
        # Calculate APR-EIR spread
        apr_col, eir_col = self._identify_rate_columns(result, apr_col_hint, eir_col_hint)
        
        if apr_col and eir_col:
            spread_col = "apr_eir_spread"
            result[spread_col] = result[apr_col] - result[eir_col]
            logger.info(f"Calculated {spread_col} from {apr_col} and {eir_col}")
        else:
            if not apr_col:
                logger.warning("APR column not identified, cannot calculate spread")
            if not eir_col:
                logger.warning("EIR column not identified, cannot calculate spread")
        
        return result


# Ensure a single global instance
try:
    pricing_enricher
except NameError:
    pricing_enricher = PricingEnricher()  # or PricingEnricher(pricing_paths=[...])


def enrich_pricing(
    loan_df: pd.DataFrame,
    *,
    join_keys: Optional[List[str]] = None,
    band_keys: Optional[Dict[str, Tuple[str, str]]] = None,  # e.g. {"tenor_days": ("tenor_min","tenor_max")}
    apr_col_hint: Optional[str] = None,
    eir_col_hint: Optional[str] = None,
    recommended_rate_col: str = "recommended_rate",
    autoload: bool = True
) -> pd.DataFrame:
    """
    Enrich loan data with pricing info and APR–EIR spread.
    
    Args:
        loan_df: Input loan DataFrame
        join_keys: exact-match columns present in BOTH datasets.
        band_keys: interval mapping feature -> (low_col, high_col) in grid.
        apr_col_hint: force APR column if multiple candidates exist.
        eir_col_hint: force EIR column if multiple candidates exist.
        recommended_rate_col: Name for recommended rate column in output
        autoload: auto-find/load pricing files if not already loaded.
        
    Returns:
        Enriched DataFrame with pricing information
        
    Raises:
        ValueError: If loan_df is None or empty
    """
    if loan_df is None or loan_df.empty:
        raise ValueError("loan_df must be a non-empty DataFrame")

    # Optionally load pricing files once
    if autoload and (
        pricing_enricher.pricing_grid is None and pricing_enricher.recommended_pricing is None
    ):
        pricing_enricher.load_pricing_data()

    return pricing_enricher.enrich_loan_data(
        loan_df,
        join_keys=join_keys,
        band_keys=band_keys,
        apr_col_hint=apr_col_hint,
        eir_col_hint=eir_col_hint,
        recommended_rate_col=recommended_rate_col,
    )


logger.info("Pricing Enrichment Module loaded successfully")
