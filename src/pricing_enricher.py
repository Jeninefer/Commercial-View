"""
Pricing enricher module extracted from PR #26
Loan pricing enrichment with flexible join strategies
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple

class PricingEnricher:
    """Comprehensive pricing enrichment system with multi-stage matching"""
    
    def __init__(self, pricing_paths: Optional[List[str]] = None):
        self.pricing_paths = pricing_paths or ["./configs", "./pricing"]
        self.pricing_grid = None
        self.recommended_pricing = None
    
    def enrich_with_pricing(self,
                          loans_df: pd.DataFrame,
                          pricing_file: str,
                          join_keys: List[str],
                          band_keys: Optional[Dict[str, Tuple[str, str]]] = None,
                          rate_cols: Optional[Tuple[str, ...]] = None,
                          recommended_col: str = "recommended_rate") -> pd.DataFrame:
        """
        Exact keys only or Interval + exact keys enrichment
        """
        result = loans_df.copy()
        
        # Load pricing configuration
        if pricing_file.endswith('.parquet'):
            pricing_df = pd.read_parquet(pricing_file)
        elif pricing_file.endswith('.yaml'):
            import yaml
            with open(pricing_file, 'r') as f:
                config = yaml.safe_load(f)
            pricing_df = pd.DataFrame(config.get('pricing_grid', []))
        else:
            pricing_df = pd.read_csv(pricing_file)
        
        # Exact key joins
        merged = result.merge(pricing_df, on=join_keys, how='left')
        
        # Band-based matching if specified
        if band_keys:
            for loan_col, (min_col, max_col) in band_keys.items():
                if loan_col in merged.columns:
                    mask = (
                        (merged[loan_col] >= merged[min_col]) & 
                        (merged[loan_col] <= merged[max_col])
                    )
                    # Apply band-based filtering to ensure proper matching
                    merged.loc[~mask, rate_cols or [recommended_col]] = np.nan
        
        return merged
    
    def load_pricing_grid(self, pricing_file: str) -> pd.DataFrame:
        """Load pricing grid from various file formats"""
        if pricing_file.endswith('.parquet'):
            return pd.read_parquet(pricing_file)
        elif pricing_file.endswith('.yaml'):
            import yaml
            with open(pricing_file, 'r') as f:
                config = yaml.safe_load(f)
            return pd.DataFrame(config.get('pricing_grid', []))
        else:
            return pd.read_csv(pricing_file)
        
    def apply_fallback_pricing(self, df: pd.DataFrame, fallback_rules: Dict[str, float]) -> pd.DataFrame:
        """Apply fallback pricing rules for unmatched loans"""
        result = df.copy()
        for col, default_rate in fallback_rules.items():
            result[col] = result[col].fillna(default_rate)
        return result
    
    def to_json_safe(self, df: pd.DataFrame) -> list[dict]:
        """Convert DataFrame to JSON-safe list of dictionaries.
        
        Handles pandas/numpy types that are not JSON serializable:
        - Timestamps -> ISO format strings
        - NaT/NaN -> None
        - numpy int64/float64 -> Python int/float
        """
        if df is None or df.empty:
            return []
        
        # Convert to records, then handle special types
        records = df.copy()
        
        # Convert datetime columns to ISO format strings
        for col in records.columns:
            if pd.api.types.is_datetime64_any_dtype(records[col]):
                records[col] = records[col].dt.strftime('%Y-%m-%d %H:%M:%S').where(pd.notna(records[col]), None)
            # Replace NaN with None for JSON null
            elif pd.api.types.is_numeric_dtype(records[col]):
                records[col] = records[col].where(pd.notna(records[col]), None)
        
        # Convert to records and ensure native Python types
        result = records.to_dict(orient='records')
        
        # Convert numpy types to native Python types
        for record in result:
            for key, value in record.items():
                if pd.isna(value):
                    record[key] = None
                elif hasattr(value, 'item'):  # numpy scalar
                    record[key] = value.item()
        
        return result