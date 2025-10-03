"""
Analytics module for calculating customer and loan statistics.
"""

import logging
import pandas as pd

logger = logging.getLogger(__name__)


class CustomerAnalytics:
    """
    Class for computing customer-level analytics from loan and DPD data.
    """

    def calculate_customer_dpd_stats(
        self,
        dpd_df: pd.DataFrame,
        loan_df: pd.DataFrame,
        customer_id_field: str,
        loan_id_field: str = "loan_id"
    ) -> pd.DataFrame:
        """
        Median/mean/max/min/count DPD by customer. Safe merges and flat columns.
        """
        if "days_past_due" not in dpd_df.columns or loan_id_field not in loan_df.columns or customer_id_field not in loan_df.columns:
            logger.error("Required columns missing for DPD stats.")
            return pd.DataFrame()

        merged = dpd_df[[loan_id_field, "days_past_due"]].merge(
            loan_df[[loan_id_field, customer_id_field]], on=loan_id_field, how="left"
        )

        agg = (merged
               .dropna(subset=["days_past_due"])
               .groupby(customer_id_field)["days_past_due"]
               .agg(mean="mean", median="median", max="max", min="min", count="count")
               .reset_index())
        agg.columns = [customer_id_field, "dpd_mean", "dpd_median", "dpd_max", "dpd_min", "dpd_count"]
        logger.info(f"Customer DPD stats computed: {len(agg)} rows")
        return agg
