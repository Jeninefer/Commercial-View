"""DPD (Days Past Due) Analysis Module

This module provides functionality for analyzing days past due data for loans and customers.
"""

import numpy as np
import pandas as pd


def add_dpd_bucket_descriptions(dpd_df: pd.DataFrame) -> pd.DataFrame:
    """Add descriptive text for DPD buckets.
    
    Args:
        dpd_df: DataFrame containing a 'dpd_bucket' column
        
    Returns:
        DataFrame with added 'dpd_bucket_description' column
        
    Raises:
        ValueError: If 'dpd_bucket' column is not present
    """
    if "dpd_bucket" not in dpd_df.columns:
        raise ValueError("dpd_bucket is required")
    desc_map = {
        "Current": "No payment due",
        "1-29": "Early delinquency",
        "30-59": "Delinquent 30 days",
        "60-89": "Delinquent 60 days",
        "90-119": "Default 90 days",
        "120-149": "Default 120 days",
        "150-179": "Default 150 days",
        "180+": "Default 180+ days",
    }
    out = dpd_df.copy()
    out["dpd_bucket_description"] = out["dpd_bucket"].map(desc_map).fillna("Unknown")
    return out


class DPDAnalyzer:
    """Analyzer for Days Past Due (DPD) data and customer payment status."""
    
    def classify_customer_payment_status(
        self,
        loan_df: pd.DataFrame,
        customer_df: pd.DataFrame,
        dpd_df: pd.DataFrame,
        customer_id_field: str = "customer_id",
        threshold_days: int = 90
    ) -> pd.DataFrame:
        """Classify customer payment status based on loan and DPD data.
        
        Args:
            loan_df: DataFrame with loan information including customer_id and loan_id
            customer_df: DataFrame with customer information
            dpd_df: DataFrame with DPD metrics per loan
            customer_id_field: Name of the customer ID column (default: "customer_id")
            threshold_days: Days threshold for recovery classification (default: 90)
            
        Returns:
            DataFrame with customer data enriched with payment status and DPD metrics
            
        Raises:
            ValueError: If required columns are missing
        """
        if "loan_id" not in loan_df.columns:
            raise ValueError("loan_df must contain 'loan_id'")
        if customer_id_field not in loan_df.columns or customer_id_field not in customer_df.columns:
            raise ValueError(f"'{customer_id_field}' must exist in both loan_df and customer_df")

        # Merge loans with DPD outputs
        lw = loan_df[[customer_id_field, "loan_id"]].merge(
            dpd_df[
                ["loan_id", "days_past_due", "is_default", "first_arrears_date", "last_payment_date"]
            ],
            on="loan_id",
            how="left",
        )

        # Aggregate per customer
        agg = lw.groupby(customer_id_field, as_index=False).agg(
            max_dpd=("days_past_due", "max"),
            mean_dpd=("days_past_due", "mean"),
            median_dpd=("days_past_due", "median"),
            has_defaulted=("is_default", "max"),
            loan_count=("loan_id", "count"),
            first_arrears_date=("first_arrears_date", "min"),
            last_payment_date=("last_payment_date", "max"),
        )

        # Coerce dates
        for c in ["first_arrears_date", "last_payment_date"]:
            agg[c] = pd.to_datetime(agg[c], errors="coerce").dt.date

        # Vectorized recovery calc
        d1 = pd.to_datetime(agg["last_payment_date"], errors="coerce")
        d0 = pd.to_datetime(agg["first_arrears_date"], errors="coerce")
        day_gap = (d1 - d0).dt.days
        recovered = agg["has_defaulted"].fillna(False) & d1.notna() & d0.notna() & (day_gap > threshold_days)

        # Payment status
        status = np.where(
            recovered,
            "Recovered",
            np.where(agg["loan_count"].fillna(0) > 1, "Recurrent", "New"),
        )

        out = customer_df.merge(agg, on=customer_id_field, how="left")
        if "payment_status" in out.columns:
            out["payment_status"] = np.where(out["payment_status"].isna(), status, out["payment_status"])
        else:
            out["payment_status"] = status
        # Fill NaNs for metrics where useful
        fill_zero = ["max_dpd", "mean_dpd", "median_dpd", "loan_count"]
        for c in fill_zero:
            if c in out.columns:
                out[c] = out[c].fillna(0)
        if "has_defaulted" in out.columns:
            out["has_defaulted"] = out["has_defaulted"].fillna(False)

        return out

    def calculate_per_customer_dpd_stats(
        self,
        loan_df: pd.DataFrame,
        dpd_df: pd.DataFrame,
        customer_id_field: str = "customer_id"
    ) -> pd.DataFrame:
        """Calculate comprehensive DPD statistics per customer.
        
        Args:
            loan_df: DataFrame with loan information including customer_id and loan_id
            dpd_df: DataFrame with DPD metrics per loan
            customer_id_field: Name of the customer ID column (default: "customer_id")
            
        Returns:
            DataFrame with DPD statistics aggregated per customer
            
        Raises:
            ValueError: If required columns are missing
        """
        if customer_id_field not in loan_df.columns:
            raise ValueError(f"Customer ID field '{customer_id_field}' not found in loan DataFrame")
        if "loan_id" not in loan_df.columns or "loan_id" not in dpd_df.columns:
            raise ValueError("Both DataFrames must contain 'loan_id'")

        merged = loan_df[[customer_id_field, "loan_id"]].merge(
            dpd_df[["loan_id", "days_past_due", "is_default", "past_due_amount"]],
            on="loan_id",
            how="inner"
        )
        merged["days_past_due"] = pd.to_numeric(merged["days_past_due"], errors="coerce")
        merged["past_due_amount"] = pd.to_numeric(merged["past_due_amount"], errors="coerce").fillna(0)

        stats = merged.groupby(customer_id_field).agg(
            dpd_mean=("days_past_due", "mean"),
            dpd_median=("days_past_due", "median"),
            dpd_min=("days_past_due", "min"),
            dpd_max=("days_past_due", "max"),
            dpd_std=("days_past_due", "std"),
            default_count=("is_default", "sum"),
            default_rate=("is_default", "mean"),
            past_due_amount_sum=("past_due_amount", "sum"),
            past_due_amount_mean=("past_due_amount", "mean"),
            past_due_amount_max=("past_due_amount", "max"),
            loan_count=("loan_id", "count"),
        ).reset_index()

        # Weighted DPD by past-due amount (fallback weight=1 if zero)
        weighted_dpd_list = []
        for cust_id, group in merged.groupby(customer_id_field):
            w = np.where(group["past_due_amount"] > 0, group["past_due_amount"], 1.0)
            x = group["days_past_due"].fillna(0)
            weighted_dpd_list.append({
                customer_id_field: cust_id,
                "weighted_dpd": float(np.average(x, weights=w))
            })
        w = pd.DataFrame(weighted_dpd_list)
        stats = stats.merge(w, on=customer_id_field, how="left")
        return stats
