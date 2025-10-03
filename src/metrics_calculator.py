"""
Metrics Calculator for Startup KPIs
"""
import logging
from typing import Dict, Optional
import pandas as pd
import numpy as np

# Configure logger
logger = logging.getLogger(__name__)


class MetricsCalculator:
    """Calculator for various startup metrics including MRR, ARR, Churn, NRR, CAC, LTV, etc."""
    
    def safe_division(self, numerator: float, denominator: float, default: float = 0.0) -> float:
        """
        Safely divide two numbers, returning a default value if denominator is zero.
        
        Args:
            numerator: The numerator value
            denominator: The denominator value
            default: The default value to return if denominator is zero
            
        Returns:
            The division result or default value
        """
        if denominator == 0 or pd.isna(denominator):
            return default
        return numerator / denominator
    
    def compute_startup_metrics(self,
                                revenue_df: pd.DataFrame,
                                customer_df: pd.DataFrame,
                                expense_df: Optional[pd.DataFrame] = None) -> Dict[str, float]:
        """
        Compute comprehensive startup metrics from revenue, customer, and expense data.
        
        Args:
            revenue_df: DataFrame containing revenue data with columns like 'date', 
                       'recurring_revenue', 'start_revenue', 'end_revenue', etc.
            customer_df: DataFrame containing customer data with columns like 'churn_count',
                        'start_count', 'is_churned', 'new_customers', etc.
            expense_df: Optional DataFrame containing expense data with columns like 'date',
                       'total_expense', 'cash_balance', 'marketing_expense'
                       
        Returns:
            Dictionary containing calculated metrics such as:
            - mrr: Monthly Recurring Revenue
            - arr: Annual Recurring Revenue
            - churn_rate: Customer churn rate
            - nrr: Net Revenue Retention
            - cac: Customer Acquisition Cost
            - arpu: Average Revenue Per User
            - ltv: Lifetime Value
            - ltv_cac_ratio: LTV to CAC ratio
            - monthly_burn: Monthly burn rate
            - runway_months: Runway in months
        """
        m: Dict[str, float] = {}

        # MRR/ARR
        try:
            if {"date","recurring_revenue"}.issubset(revenue_df.columns):
                r = revenue_df[["date","recurring_revenue"]].copy()
                r["date"] = pd.to_datetime(r["date"], errors="coerce")
                r = r.sort_values("date").dropna(subset=["date"]).tail(1)
                mrr = float(r["recurring_revenue"].iloc[0]) if not r.empty else 0.0
                m["mrr"] = mrr
                m["arr"] = mrr * 12.0
            else:
                logger.warning("MRR/ARR: missing {'date','recurring_revenue'}")
        except Exception as e:
            logger.error(f"MRR/ARR error: {e}")

        # Churn
        try:
            if {"churn_count", "start_count"}.issubset(customer_df.columns):
                m["churn_rate"] = float(self.safe_division(customer_df["churn_count"].sum(),
                                                           customer_df["start_count"].sum(), 0.0))
            elif "is_churned" in customer_df.columns:
                m["churn_rate"] = float(self.safe_division(customer_df["is_churned"].sum(),
                                                           len(customer_df), 0.0))
        except Exception as e:
            logger.error(f"Churn error: {e}")

        # NRR
        try:
            if {"start_revenue", "end_revenue"}.issubset(revenue_df.columns):
                m["nrr"] = float(self.safe_division(revenue_df["end_revenue"].sum(),
                                                    revenue_df["start_revenue"].sum(), 0.0))
        except Exception as e:
            logger.error(f"NRR error: {e}")

        # CAC / LTV (ARPU from revenue_df if available)
        try:
            if expense_df is not None and "marketing_expense" in expense_df.columns:
                marketing = float(expense_df["marketing_expense"].sum())
                if "new_customers" in customer_df.columns:
                    new_cust = float(customer_df["new_customers"].sum())
                    m["cac"] = float(self.safe_division(marketing, new_cust, 0.0))
                    if "revenue" in revenue_df.columns and "customer_count" in revenue_df.columns:
                        arpu = float(self.safe_division(revenue_df["revenue"].sum(),
                                                        revenue_df["customer_count"].sum(), 0.0))
                        m["arpu"] = arpu
                    # LTV only if churn_rate > 0
                    if m.get("arpu", 0) > 0 and m.get("churn_rate", 0) > 0:
                        m["ltv"] = float(self.safe_division(m["arpu"], m["churn_rate"], np.inf))
                        if m.get("cac", 0) > 0:
                            m["ltv_cac_ratio"] = float(self.safe_division(m["ltv"], m["cac"], np.nan))
        except Exception as e:
            logger.error(f"CAC/LTV error: {e}")

        # Burn / Runway
        try:
            if expense_df is not None and {"date", "total_expense"}.issubset(expense_df.columns):
                e = expense_df[["date","total_expense","cash_balance"]].copy()
                e["date"] = pd.to_datetime(e["date"], errors="coerce")
                e = e.dropna(subset=["date"]).sort_values("date")
                if len(e) >= 3:
                    last3 = e.tail(3)
                    monthly_burn = float(last3["total_expense"].mean())
                    m["monthly_burn"] = monthly_burn
                    if "cash_balance" in e.columns and not e["cash_balance"].empty:
                        cash = float(e["cash_balance"].iloc[-1])
                        m["runway_months"] = float(self.safe_division(cash, monthly_burn, np.inf)) if monthly_burn > 0 else np.inf
        except Exception as e:
            logger.error(f"Burn/Runway error: {e}")

        return m
