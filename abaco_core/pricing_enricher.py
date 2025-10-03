"""
PricingEnricher module for enriching loan data with pricing band information.

This module provides functionality to match loans against pricing bands
and enrich loan data with pricing grid information.
"""

import pandas as pd
from typing import List, Dict, Optional, Any


class PricingEnricher:
    """
    Enriches loan data with pricing band information.
    
    The PricingEnricher matches loan attributes against pricing bands
    and adds corresponding pricing grid data to each loan record.
    """
    
    def __init__(self, pricing_bands: pd.DataFrame):
        """
        Initialize the PricingEnricher with pricing bands.
        
        Args:
            pricing_bands: DataFrame containing pricing band definitions.
                          Expected to have columns defining ranges/bands.
        """
        self.pricing_bands = pricing_bands
    
    def _match_loan_to_band(self, loan: Dict[str, Any], band_keys: List[str]) -> Optional[Dict[str, Any]]:
        """
        Match a single loan to a pricing band based on band keys.
        
        Args:
            loan: Dictionary containing loan attributes
            band_keys: List of column names to use for band matching
        
        Returns:
            Dictionary of matched band data, or None if no match found
        """
        # Implementation would match loan attributes against band ranges
        # For now, return None as placeholder for non-matching case
        for _, band in self.pricing_bands.iterrows():
            match = True
            for key in band_keys:
                if key in loan and key in band:
                    # Simple equality check - in practice, this would include
                    # range/interval matching logic
                    if loan[key] != band[key]:
                        match = False
                        break
            if match:
                return band.to_dict()
        return None
    
    def enrich_loan_data(self, loans_df: pd.DataFrame, band_keys: List[str]) -> pd.DataFrame:
        """
        Enrich loan data with pricing band information.
        
        This method matches each loan against pricing bands using the specified
        band_keys for interval matching. If a loan doesn't match any pricing band,
        the pricing grid columns will contain NaN values.
        
        Implementation detail: To avoid errors when creating the matched DataFrame,
        None entries are replaced with empty dictionaries, producing NaN values for
        loans that didn't match any pricing band.
        
        Args:
            loans_df: DataFrame containing loan data to enrich
            band_keys: List of column names to use for band matching (e.g., 
                      ['loan_term', 'credit_score_band', 'ltv_band'])
        
        Returns:
            DataFrame with original loan data plus pricing grid columns
            (suffixed with '_grid'). Unmatched loans will have NaN values
            in the grid columns.
        
        Example:
            >>> enricher = PricingEnricher(pricing_bands_df)
            >>> enriched = enricher.enrich_loan_data(loans_df, ['term', 'score'])
            >>> # Loans without matches will have NaN in *_grid columns
        """
        # Convert loans to list of dictionaries for processing
        loans_list = loans_df.to_dict('records')
        
        # Match each loan to a pricing band
        matched = [self._match_loan_to_band(loan, band_keys) for loan in loans_list]
        
        # Replace None with empty dict to avoid errors when creating DataFrame
        # This produces NaNs for loans that didn't match any pricing band
        matched_records = [r or {} for r in matched]
        matched_df = pd.DataFrame(matched_records)
        
        # If matched_df is empty (all loans didn't match and pricing_bands is empty),
        # we still need to add the _grid suffix to maintain consistency
        if not matched_df.empty:
            matched_df = matched_df.add_suffix("_grid")
        else:
            # Create empty dataframe with grid columns from pricing_bands
            grid_columns = [col + '_grid' for col in self.pricing_bands.columns]
            matched_df = pd.DataFrame(columns=grid_columns, index=loans_df.index)
        
        # Combine original loan data with matched pricing grid data
        result_df = pd.concat([loans_df.reset_index(drop=True), matched_df.reset_index(drop=True)], axis=1)
        
        return result_df
