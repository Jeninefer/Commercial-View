"""
Customer analytics module extracted from PR #13
DPD statistics calculations aggregated by customer
"""

import pandas as pd
import logging

logger = logging.getLogger(__name__)

class CustomerAnalytics:
    """Analytics class for customer-level DPD calculations"""
    
    def calculate_customer_dpd_stats(self,
                                   dpd_df: pd.DataFrame,
                                   loan_df: pd.DataFrame,
                                   customer_id_field: str,
                                   loan_id_field: str = "loan_id") -> pd.DataFrame:
        """
        Median/mean/max/min/count DPD by customer. Safe merges and flat columns.
        """
        if ("days_past_due" not in dpd_df.columns or 
            loan_id_field not in loan_df.columns or 
            customer_id_field not in loan_df.columns):
            logger.error("Required columns missing for DPD stats.")
            return pd.DataFrame()

        merged: pd.DataFrame = dpd_df[[loan_id_field, "days_past_due"]].merge(
            loan_df[[loan_id_field, customer_id_field]], 
            on=loan_id_field, 
            how="left"
        )

        agg: pd.DataFrame = (merged
               .dropna(subset=["days_past_due"])  # type: ignore
               .groupby(customer_id_field)["days_past_due"]
               .agg(mean="mean", median="median", max="max", min="min", count="count")
               .reset_index())
        
        agg.columns = [customer_id_field, "dpd_mean", "dpd_median", "dpd_max", "dpd_min", "dpd_count"]
        logger.info(f"Customer DPD stats computed for {len(agg)} customers.")
        return agg
