"""
Pricing enrichment functionality (production-safe)
"""
import os
import json
from typing import Sequence, Mapping, Optional
import pandas as pd
import numpy as np
import yaml


def _load_pricing_grid(path: str) -> pd.DataFrame:
    """
    Load pricing grid from various file formats.
    
    Args:
        path: Path to the pricing grid file
        
    Returns:
        DataFrame containing the pricing grid
        
    Raises:
        ValueError: If file format is not supported
    """
    ext = os.path.splitext(path)[1].lower()
    if ext in (".csv",):
        return pd.read_csv(path)
    if ext in (".parquet", ".pq"):
        return pd.read_parquet(path)
    if ext in (".json",):
        return pd.read_json(path)
    if ext in (".yml", ".yaml"):
        with open(path, "r") as f:
            cfg = yaml.safe_load(f)
        # Expect cfg to contain a list under key "pricing_grid"
        # If cfg is already a list, use it directly; otherwise try to get "pricing_grid" key
        if isinstance(cfg, list):
            grid = cfg
        else:
            grid = cfg.get("pricing_grid", cfg)
        return pd.DataFrame(grid)
    raise ValueError(f"Unsupported pricing grid format: {ext}")


def enrich_with_pricing(
    loans_df: pd.DataFrame,
    pricing_grid_path: str,
    *,
    join_keys: Optional[Sequence[str]] = None,
    band_keys: Optional[Mapping[str, Sequence[str]]] = None,
    # Example band_keys:
    # {"tenor_days": ["tenor_min","tenor_max"], "ticket_usd": ["ticket_min","ticket_max"]}
    rate_cols: Sequence[str] = ("apr", "eir"),
    recommended_col: str = "recommended_rate",
) -> pd.DataFrame:
    """
    Enrich loan rows with pricing rules. Supports:
      - Exact join on explicit keys (join_keys)
      - Interval (band) matching via band_keys for ranges (e.g., tenor, ticket)
      - CSV/Parquet/JSON/YAML pricing sources

    Hard requirements:
      - You MUST pass explicit `join_keys` that exist in BOTH DataFrames,
        or a non-empty `band_keys`. We never join on "all common columns".
        
    Args:
        loans_df: DataFrame containing loan data
        pricing_grid_path: Path to pricing grid file
        join_keys: Columns to join on (exact match)
        band_keys: Dictionary mapping feature columns to [min_col, max_col] for range matching
        rate_cols: Tuple of rate column names (default: ("apr", "eir"))
        recommended_col: Name of the recommended rate column
        
    Returns:
        Enriched DataFrame with pricing information
        
    Raises:
        ValueError: If loans_df is not a valid DataFrame or required keys are missing
    """
    if not isinstance(loans_df, pd.DataFrame) or loans_df.empty:
        raise ValueError("loans_df must be a non-empty DataFrame")

    grid = _load_pricing_grid(pricing_grid_path)
    if grid.empty:
        return loans_df.copy()

    df = loans_df.copy()

    # Validate explicit joins
    if join_keys:
        missing_loans = [k for k in join_keys if k not in df.columns]
        missing_grid = [k for k in join_keys if k not in grid.columns]
        if missing_loans or missing_grid:
            raise ValueError(
                f"Missing join keys. loans_df:{missing_loans} grid:{missing_grid}"
            )
        df = df.merge(grid, on=list(join_keys), how="left")

    # Interval/band matching (post exact join or alone)
    if band_keys:
        for feat, (lo_col, hi_col) in band_keys.items():
            if feat not in df.columns:
                raise ValueError(f"Band feature '{feat}' not in loans_df")
            if lo_col not in grid.columns or hi_col not in grid.columns:
                raise ValueError(
                    f"Band bounds '{lo_col}/{hi_col}' not in pricing grid"
                )

            # Prepare intervals as categorical for vectorized match
            bounds = grid[[lo_col, hi_col]].copy()
            bounds[lo_col] = pd.to_numeric(bounds[lo_col], errors="coerce").fillna(
                -np.inf
            )
            bounds[hi_col] = pd.to_numeric(bounds[hi_col], errors="coerce").fillna(
                np.inf
            )
            # Build IntervalIndex and map row-wise via merge with condition
            # Efficient approach: explode bands into non-overlapping buckets if your grid overlaps.
            # Here we do a safe left join via boolean mask partitioned per unique bands:
            vals = pd.to_numeric(df[feat], errors="coerce")
            match_idx = pd.Series([-1] * len(df), dtype=int)

            # Simple linear scan over rows in grid (works if grid small/moderate)
            # For large grids, pre-index by ranges.
            for i, (lo, hi) in bounds.iterrows():
                mask = (vals >= lo) & (vals <= hi) & (match_idx.eq(-1))
                match_idx[mask] = i

            # Attach matched rows
            matched = grid.loc[match_idx.clip(lower=0)].reset_index(drop=True)
            # Only add columns not already present from exact join
            add_cols = [c for c in matched.columns if c not in df.columns]
            df = pd.concat([df.reset_index(drop=True), matched[add_cols]], axis=1)

    # Compute spreads if both rate columns exist
    if len(rate_cols) >= 2:
        apr_col, eir_col = rate_cols[0], rate_cols[1]
    elif len(rate_cols) == 1:
        apr_col, eir_col = rate_cols[0], None
    else:
        apr_col, eir_col = None, None
    if apr_col in df.columns and eir_col in df.columns:
        df["apr_eir_spread"] = pd.to_numeric(
            df[apr_col], errors="coerce"
        ) - pd.to_numeric(df[eir_col], errors="coerce")

    # Fast boolean flag for pricing availability
    has_col = recommended_col if recommended_col in df.columns else None
    df["has_pricing"] = False if has_col is None else df[has_col].notna()

    # Optional sanity checks
    # Ensure recommended_rate in % if you store bps in grid; adapt if needed:
    # if "recommended_rate_bps" in df.columns and "recommended_rate" not in df.columns:
    #     df["recommended_rate"] = pd.to_numeric(df["recommended_rate_bps"], errors="coerce") / 100.0

    return df
