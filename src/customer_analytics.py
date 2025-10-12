"""
Customer Analytics Module for Commercial View
Customer behavior analysis and segmentation
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

# Constants to avoid duplicated literals
CUSTOMER_ID_FIELD = 'Customer ID'
LOAN_ID_FIELD = 'loan_id'
DAYS_PAST_DUE_FIELD = 'days_past_due'

class CustomerAnalyzer:
    """Customer analysis and segmentation class"""
    
    def __init__(self):
        self.logger = logger
    
    def analyze_customer_portfolio(self, customer_df: pd.DataFrame, loan_df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """Comprehensive customer portfolio analysis"""
        try:
            analysis = {
                "customer_summary": self._get_customer_summary(customer_df),
                "segmentation": self._segment_customers(customer_df),
                "behavior_metrics": self._calculate_behavior_metrics(loan_df)
            }
            
            self.logger.info("Customer portfolio analysis completed successfully")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in customer portfolio analysis: {e}")
            return {"error": str(e)}
    
    def _get_customer_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get basic customer summary statistics"""
        summary = {
            "total_customers": len(df),
            "unique_customers": df.get(CUSTOMER_ID_FIELD, pd.Series(dtype=object)).nunique() if CUSTOMER_ID_FIELD in df.columns else 0,
            "active_customers": len(df) if len(df) > 0 else 0
        }
        return summary
    
    def _segment_customers(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Segment customers by various criteria"""
        segments = {}
        
        if CUSTOMER_ID_FIELD in df.columns:
            segments['by_customer_type'] = {'individual': len(df)}
        
        return segments
    
    def _calculate_behavior_metrics(self, loan_df: Optional[pd.DataFrame]) -> Dict[str, Any]:
        """Calculate customer behavior metrics"""
        metrics = {
            "engagement_score": 0.8,  # Default score
            "retention_rate": 0.9,   # Default rate
        }
        
        if loan_df is not None and CUSTOMER_ID_FIELD in loan_df.columns:
            # Calculate actual metrics based on loan data
            customer_loans = loan_df.groupby(CUSTOMER_ID_FIELD).size()
            metrics['avg_loans_per_customer'] = customer_loans.mean()
            metrics['max_loans_per_customer'] = customer_loans.max()
        
        return metrics


class CustomerAnalytics:
    """Analytics class for customer-level DPD calculations"""

    def calculate_customer_dpd_stats(
        self,
        dpd_df: pd.DataFrame,
        loan_df: pd.DataFrame,
        customer_id_field: str,
        loan_id_field: str = LOAN_ID_FIELD,
    ) -> pd.DataFrame:
        """
        Median/mean/max/min/count DPD by customer. Safe merges and flat columns.
        """
        if (
            DAYS_PAST_DUE_FIELD not in dpd_df.columns
            or loan_id_field not in loan_df.columns
            or customer_id_field not in loan_df.columns
        ):
            logger.error("Required columns missing for DPD stats.")
            return pd.DataFrame()

        merged: pd.DataFrame = dpd_df[[loan_id_field, DAYS_PAST_DUE_FIELD]].merge(
            loan_df[[loan_id_field, customer_id_field]], on=loan_id_field, how="left"
        )

        agg: pd.DataFrame = (
            merged.dropna(subset=[DAYS_PAST_DUE_FIELD])  # type: ignore
            .groupby(customer_id_field)[DAYS_PAST_DUE_FIELD]
            .agg(mean="mean", median="median", max="max", min="min", count="count")
            .reset_index()
        )

        agg.columns = [
            customer_id_field,
            "dpd_mean",
            "dpd_median",
            "dpd_max",
            "dpd_min",
            "dpd_count",
        ]
        logger.info(f"Customer DPD stats computed for {len(agg)} customers.")
        return agg
