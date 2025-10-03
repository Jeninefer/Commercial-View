"""
Pricing enrichment functionality for loan data.
"""

import pandas as pd
import yaml
from pathlib import Path
from typing import Union, List, Dict, Optional, Tuple


def enrich_with_pricing(
    df: pd.DataFrame,
    pricing_config_path: str,
    join_keys: List[str],
    band_keys: Optional[Dict[str, List[str]]] = None,
    rate_cols: Optional[Tuple[str, ...]] = None,
    recommended_col: Optional[str] = None
) -> pd.DataFrame:
    """
    Enrich a loans DataFrame with pricing information from a configuration file.
    
    Supports two modes:
    1. Exact key joins (typically from .parquet files)
    2. Interval/band joins + exact keys (typically from .yaml files)
    
    Parameters
    ----------
    df : pd.DataFrame
        The loans DataFrame to enrich
    pricing_config_path : str
        Path to the pricing configuration file (.parquet or .yaml)
    join_keys : List[str]
        Exact key columns to join on (e.g., ["country", "sector", "risk_band"])
    band_keys : Optional[Dict[str, List[str]]], default=None
        Dictionary mapping columns in df to [min_col, max_col] in pricing config.
        Example: {"tenor_days": ["tenor_min", "tenor_max"], "ticket_usd": ["ticket_min", "ticket_max"]}
    rate_cols : Optional[Tuple[str, ...]], default=None
        Tuple of rate column names to include from pricing config (e.g., ("apr", "eir"))
    recommended_col : Optional[str], default=None
        Name of the recommended rate column to include from pricing config
    
    Returns
    -------
    pd.DataFrame
        Enriched DataFrame with pricing information
    
    Examples
    --------
    # Exact keys only
    loans = enrich_with_pricing(
        loans_df,
        "configs/pricing_grid.parquet",
        join_keys=["country","sector","risk_band"]
    )
    
    # Interval + exact keys
    loans = enrich_with_pricing(
        loans_df,
        "configs/pricing_grid.yaml",
        join_keys=["country","risk_band"],
        band_keys={"tenor_days": ["tenor_min","tenor_max"], "ticket_usd": ["ticket_min","ticket_max"]},
        rate_cols=("apr","eir"),
        recommended_col="recommended_rate"
    )
    """
    pricing_path = Path(pricing_config_path)
    
    # Load pricing configuration based on file type
    if pricing_path.suffix == '.parquet':
        pricing_df = pd.read_parquet(pricing_config_path)
    elif pricing_path.suffix in ['.yaml', '.yml']:
        with open(pricing_config_path, 'r') as f:
            pricing_data = yaml.safe_load(f)
        pricing_df = pd.DataFrame(pricing_data)
    else:
        raise ValueError(f"Unsupported file format: {pricing_path.suffix}. Use .parquet or .yaml/.yml")
    
    # If no band_keys, perform simple exact join
    if band_keys is None:
        result_df = df.merge(pricing_df, on=join_keys, how='left')
        return result_df
    
    # Perform interval/band join
    result_df = _interval_join(df, pricing_df, join_keys, band_keys)
    
    # Filter columns if rate_cols and/or recommended_col are specified
    if rate_cols is not None or recommended_col is not None:
        # Keep original df columns + join_keys + specified rate/recommended columns
        cols_to_keep = list(df.columns)
        
        if rate_cols:
            for rate_col in rate_cols:
                if rate_col in result_df.columns and rate_col not in cols_to_keep:
                    cols_to_keep.append(rate_col)
        
        if recommended_col:
            if recommended_col in result_df.columns and recommended_col not in cols_to_keep:
                cols_to_keep.append(recommended_col)
        
        # Keep only the specified columns
        result_df = result_df[[col for col in cols_to_keep if col in result_df.columns]]
    
    return result_df


def _interval_join(
    df: pd.DataFrame,
    pricing_df: pd.DataFrame,
    join_keys: List[str],
    band_keys: Dict[str, List[str]]
) -> pd.DataFrame:
    """
    Perform an interval join between df and pricing_df.
    
    This joins on exact keys first, then filters based on interval conditions.
    """
    # Create a copy to avoid modifying the original
    result_df = df.copy()
    
    # Add a temporary index to preserve order
    result_df['_temp_idx'] = range(len(result_df))
    
    # Perform exact join on join_keys (cross join effect for each matching key combination)
    merged = result_df.merge(pricing_df, on=join_keys, how='left', suffixes=('', '_pricing'))
    
    # Apply interval conditions
    mask = pd.Series([True] * len(merged))
    
    for df_col, (min_col, max_col) in band_keys.items():
        if df_col in merged.columns and min_col in merged.columns and max_col in merged.columns:
            # Check if value is within [min, max] range
            mask &= (merged[df_col] >= merged[min_col]) & (merged[df_col] <= merged[max_col])
    
    # Filter to only matching intervals
    filtered = merged[mask].copy()
    
    # Handle multiple matches - take the first match per original row
    if len(filtered) > 0:
        filtered = filtered.sort_values('_temp_idx').groupby('_temp_idx', as_index=False).first()
    
    # Get columns to keep from pricing_df (exclude join_keys as they're already in df)
    pricing_cols = [col for col in pricing_df.columns if col not in join_keys]
    
    # Merge back to ensure we have all original rows (even those without matches)
    # Only merge the pricing columns
    if len(filtered) > 0:
        cols_to_merge = ['_temp_idx'] + pricing_cols
        cols_to_merge = [col for col in cols_to_merge if col in filtered.columns]
        final_result = result_df.merge(
            filtered[cols_to_merge],
            on='_temp_idx',
            how='left'
        )
    else:
        # No matches, just add NaN columns
        final_result = result_df.copy()
        for col in pricing_cols:
            final_result[col] = pd.NA
    
    # Remove temporary index
    final_result = final_result.drop(columns=['_temp_idx'])
    
    return final_result
