"""KPI Calculator for startup, fintech, and valuation metrics"""

import logging
from typing import Dict, Any
import pandas as pd


class KPICalculator:
    """
    Calculator for startup, fintech, and valuation metrics.
    """

    def __init__(self):
        self.logger = logging.getLogger("abaco_dashboard")

    def compute_startup_metrics(
        self, 
        revenue_df: pd.DataFrame, 
        customer_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Compute startup-related metrics.
        
        Args:
            revenue_df: DataFrame containing revenue data
            customer_df: DataFrame containing customer data
            
        Returns:
            Dictionary containing startup metrics
        """
        if not isinstance(revenue_df, pd.DataFrame):
            raise ValueError("revenue_df must be a DataFrame")
        if not isinstance(customer_df, pd.DataFrame):
            raise ValueError("customer_df must be a DataFrame")

        metrics = {
            "total_customers": int(len(customer_df)) if not customer_df.empty else 0,
        }

        # Revenue metrics
        if not revenue_df.empty and "amount" in revenue_df.columns:
            metrics["total_revenue"] = float(revenue_df["amount"].sum())
            metrics["average_revenue"] = float(revenue_df["amount"].mean())
            
            # Monthly Recurring Revenue (MRR) if period column exists
            if "period" in revenue_df.columns:
                monthly_revenue = revenue_df[revenue_df["period"] == "monthly"]
                if not monthly_revenue.empty:
                    metrics["mrr"] = float(monthly_revenue["amount"].sum())

        # Customer metrics
        if not customer_df.empty:
            if "acquisition_date" in customer_df.columns:
                customer_df_copy = customer_df.copy()
                customer_df_copy["acquisition_date"] = pd.to_datetime(
                    customer_df_copy["acquisition_date"], errors="coerce"
                )
                recent_customers = customer_df_copy[
                    customer_df_copy["acquisition_date"] >= 
                    (pd.Timestamp.now() - pd.Timedelta(days=30))
                ]
                metrics["new_customers_last_30_days"] = int(len(recent_customers))

            # Customer Acquisition Cost (CAC) if available
            if "acquisition_cost" in customer_df.columns:
                metrics["average_cac"] = float(customer_df["acquisition_cost"].mean())

        self.logger.info("Computed startup metrics")
        return metrics

    def compute_fintech_metrics(self, transaction_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Compute fintech-related metrics.
        
        Args:
            transaction_df: DataFrame containing transaction data
            
        Returns:
            Dictionary containing fintech metrics
        """
        if not isinstance(transaction_df, pd.DataFrame):
            raise ValueError("transaction_df must be a DataFrame")

        metrics = {
            "total_transactions": int(len(transaction_df)) if not transaction_df.empty else 0,
        }

        if not transaction_df.empty:
            # Transaction volume
            if "amount" in transaction_df.columns:
                metrics["total_transaction_volume"] = float(transaction_df["amount"].sum())
                metrics["average_transaction_value"] = float(transaction_df["amount"].mean())

            # Transaction success rate
            if "status" in transaction_df.columns:
                total = len(transaction_df)
                successful = len(transaction_df[transaction_df["status"].isin(["success", "completed"])])
                metrics["transaction_success_rate"] = float(successful / total) if total > 0 else 0.0

            # Payment method distribution
            if "payment_method" in transaction_df.columns:
                method_counts = transaction_df["payment_method"].value_counts().to_dict()
                metrics["payment_method_distribution"] = {
                    str(k): int(v) for k, v in method_counts.items()
                }

        self.logger.info("Computed fintech metrics")
        return metrics

    def compute_valuation_metrics(
        self,
        revenue_df: pd.DataFrame,
        customer_df: pd.DataFrame,
        transaction_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Compute valuation-related metrics.
        
        Args:
            revenue_df: DataFrame containing revenue data
            customer_df: DataFrame containing customer data
            transaction_df: DataFrame containing transaction data
            
        Returns:
            Dictionary containing valuation metrics
        """
        if not all(isinstance(x, pd.DataFrame) for x in [revenue_df, customer_df, transaction_df]):
            raise ValueError("All inputs must be DataFrames")

        metrics = {}

        # Customer Lifetime Value (CLTV) approximation
        if not revenue_df.empty and not customer_df.empty:
            total_customers = len(customer_df)
            if total_customers > 0 and "amount" in revenue_df.columns:
                total_revenue = revenue_df["amount"].sum()
                metrics["average_cltv"] = float(total_revenue / total_customers)

        # ARR (Annual Recurring Revenue) if MRR can be calculated
        if not revenue_df.empty and "amount" in revenue_df.columns:
            if "period" in revenue_df.columns:
                monthly_revenue = revenue_df[revenue_df["period"] == "monthly"]
                if not monthly_revenue.empty:
                    mrr = monthly_revenue["amount"].sum()
                    metrics["arr"] = float(mrr * 12)

        # Revenue per transaction
        if not revenue_df.empty and not transaction_df.empty:
            if "amount" in revenue_df.columns:
                total_revenue = revenue_df["amount"].sum()
                total_transactions = len(transaction_df)
                if total_transactions > 0:
                    metrics["revenue_per_transaction"] = float(total_revenue / total_transactions)

        # Churn rate if available
        if not customer_df.empty:
            if "status" in customer_df.columns:
                total = len(customer_df)
                churned = len(customer_df[customer_df["status"].isin(["churned", "inactive"])])
                metrics["churn_rate"] = float(churned / total) if total > 0 else 0.0

        self.logger.info("Computed valuation metrics")
        return metrics
