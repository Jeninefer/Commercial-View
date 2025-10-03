"""
KPI Analyzer Module

This module provides functionality to compute various business metrics including
startup metrics, fintech metrics, valuation metrics, and viability indices.
"""

import json
import logging
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class KPIAnalyzer:
    """
    Analyzes and computes Key Performance Indicators (KPIs) for commercial businesses.
    
    This class provides methods to calculate metrics for:
    - Startup metrics (growth, retention, etc.)
    - Fintech metrics (loan performance, payment metrics)
    - Valuation metrics (enterprise value, multiples, etc.)
    - Viability indices
    """

    def __init__(self):
        """Initialize the KPI Analyzer."""
        pass

    def safe_division(self, numerator: float, denominator: float, default: float = 0.0) -> float:
        """
        Perform safe division with a default value for division by zero or invalid values.
        
        Args:
            numerator: The numerator value
            denominator: The denominator value
            default: The default value to return if division is not possible
            
        Returns:
            The result of division or the default value
        """
        if denominator and denominator != 0 and np.isfinite(numerator) and np.isfinite(denominator):
            return numerator / denominator
        return default

    def compute_startup_metrics(
        self,
        revenue_df: pd.DataFrame,
        customer_df: pd.DataFrame,
        valuation_df: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """
        Compute startup-related metrics.
        
        Args:
            revenue_df: DataFrame containing revenue data
            customer_df: DataFrame containing customer data
            valuation_df: Optional DataFrame containing valuation data (for marketing expenses)
            
        Returns:
            Dictionary containing startup metrics
        """
        metrics = {}
        
        try:
            # Revenue metrics
            if not revenue_df.empty:
                total_revenue = revenue_df.get("revenue", pd.Series([0])).sum()
                metrics["total_revenue"] = float(total_revenue)
                
                if "date" in revenue_df.columns:
                    revenue_df_sorted = revenue_df.sort_values("date")
                    if len(revenue_df_sorted) >= 2:
                        latest_revenue = revenue_df_sorted.iloc[-1].get("revenue", 0)
                        previous_revenue = revenue_df_sorted.iloc[-2].get("revenue", 0)
                        metrics["revenue_growth"] = self.safe_division(
                            latest_revenue - previous_revenue,
                            previous_revenue,
                            0.0
                        )
            
            # Customer metrics
            if not customer_df.empty:
                total_customers = len(customer_df)
                metrics["total_customers"] = total_customers
                
                if "date" in customer_df.columns:
                    customer_df_sorted = customer_df.sort_values("date")
                    if len(customer_df_sorted) >= 2:
                        # Calculate customer growth
                        latest_date = customer_df_sorted["date"].max()
                        previous_date = customer_df_sorted["date"].unique()[-2] if len(customer_df_sorted["date"].unique()) >= 2 else None
                        
                        if previous_date is not None:
                            latest_customers = len(customer_df_sorted[customer_df_sorted["date"] == latest_date])
                            previous_customers = len(customer_df_sorted[customer_df_sorted["date"] == previous_date])
                            metrics["customer_growth"] = self.safe_division(
                                latest_customers - previous_customers,
                                previous_customers,
                                0.0
                            )
                
                # Calculate ARPU (Average Revenue Per User)
                if "total_revenue" in metrics and total_customers > 0:
                    metrics["arpu"] = metrics["total_revenue"] / total_customers
            
            # Marketing efficiency
            if valuation_df is not None and not valuation_df.empty and "marketing_expense" in valuation_df.columns:
                marketing_expense = float(valuation_df.get("marketing_expense", pd.Series([0])).iloc[0])
                metrics["marketing_expense"] = marketing_expense
                
                if "total_customers" in metrics and marketing_expense > 0:
                    metrics["cac"] = marketing_expense / metrics["total_customers"]
                    
                    if "arpu" in metrics:
                        metrics["ltv_cac_ratio"] = self.safe_division(
                            metrics["arpu"] * 3,  # Simplified LTV calculation
                            metrics["cac"],
                            0.0
                        )
        
        except Exception as e:
            logger.error(f"Error computing startup metrics: {e}")
        
        return metrics

    def compute_fintech_metrics(
        self,
        loan_df: pd.DataFrame,
        payment_df: Optional[pd.DataFrame] = None,
        user_df: Optional[pd.DataFrame] = None,
        default_dpd_threshold: int = 180
    ) -> Dict[str, Any]:
        """
        Compute fintech-related metrics.
        
        Args:
            loan_df: DataFrame containing loan data
            payment_df: Optional DataFrame containing payment data
            user_df: Optional DataFrame containing user data
            default_dpd_threshold: Days past due threshold for defaults
            
        Returns:
            Dictionary containing fintech metrics
        """
        metrics = {}
        
        try:
            if loan_df.empty:
                return metrics
            
            # Loan portfolio metrics
            total_loans = len(loan_df)
            metrics["total_loans"] = total_loans
            
            if "amount" in loan_df.columns:
                total_loan_amount = float(loan_df["amount"].sum())
                metrics["total_loan_amount"] = total_loan_amount
                metrics["average_loan_amount"] = total_loan_amount / total_loans if total_loans > 0 else 0.0
            
            # Default rate calculation
            if "dpd" in loan_df.columns:
                defaulted_loans = len(loan_df[loan_df["dpd"] >= default_dpd_threshold])
                metrics["default_rate"] = self.safe_division(defaulted_loans, total_loans, 0.0)
            
            # NPL (Non-Performing Loans) ratio
            if "status" in loan_df.columns:
                npl_loans = len(loan_df[loan_df["status"].isin(["default", "npl"])])
                metrics["npl_ratio"] = self.safe_division(npl_loans, total_loans, 0.0)
            
            # Payment metrics
            if payment_df is not None and not payment_df.empty:
                if "amount" in payment_df.columns:
                    total_payments = float(payment_df["amount"].sum())
                    metrics["total_payments"] = total_payments
                    
                    if "total_loan_amount" in metrics:
                        metrics["collection_rate"] = self.safe_division(
                            total_payments,
                            metrics["total_loan_amount"],
                            0.0
                        )
            
            # User engagement metrics
            if user_df is not None and not user_df.empty:
                active_users = len(user_df[user_df.get("status", pd.Series()) == "active"]) if "status" in user_df.columns else len(user_df)
                metrics["active_users"] = active_users
        
        except Exception as e:
            logger.error(f"Error computing fintech metrics: {e}")
        
        return metrics

    def compute_viability_index(self, startup_metrics: Dict[str, Any]) -> float:
        """
        Compute a viability index based on startup metrics.
        
        Args:
            startup_metrics: Dictionary containing startup metrics
            
        Returns:
            Viability index score (0-100)
        """
        try:
            score = 0.0
            max_score = 100.0
            
            # Revenue contribution (30 points)
            if "total_revenue" in startup_metrics and startup_metrics["total_revenue"] > 0:
                score += 30.0
            
            # Growth contribution (30 points)
            if "revenue_growth" in startup_metrics:
                growth = startup_metrics["revenue_growth"]
                if growth > 0.5:  # 50% growth
                    score += 30.0
                elif growth > 0.2:  # 20% growth
                    score += 20.0
                elif growth > 0:
                    score += 10.0
            
            # Customer base contribution (20 points)
            if "total_customers" in startup_metrics:
                customers = startup_metrics["total_customers"]
                if customers > 1000:
                    score += 20.0
                elif customers > 100:
                    score += 15.0
                elif customers > 10:
                    score += 10.0
            
            # LTV/CAC contribution (20 points)
            if "ltv_cac_ratio" in startup_metrics:
                ratio = startup_metrics["ltv_cac_ratio"]
                if ratio > 3:
                    score += 20.0
                elif ratio > 1:
                    score += 10.0
            
            return min(score, max_score)
        
        except Exception as e:
            logger.error(f"Error computing viability index: {e}")
            return 0.0

    def _export_json(self, data: Dict[str, Any], filename: str) -> None:
        """
        Export data to a JSON file.
        
        Args:
            data: Dictionary to export
            filename: Base filename (without extension)
        """
        try:
            filepath = f"{filename}.json"
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            logger.info(f"Exported data to {filepath}")
        except Exception as e:
            logger.error(f"Error exporting JSON: {e}")

    def compute_kpis(
        self,
        revenue_df: pd.DataFrame,
        customer_df: pd.DataFrame,
        valuation_df: pd.DataFrame,
        *,
        loan_df: Optional[pd.DataFrame] = None,
        payment_df: Optional[pd.DataFrame] = None,
        user_df: Optional[pd.DataFrame] = None,
        default_dpd_threshold: int = 180,
        export: bool = False
    ) -> Dict[str, Any]:
        """
        Compute all KPIs for a business.
        
        Args:
            revenue_df: DataFrame containing revenue data
            customer_df: DataFrame containing customer data
            valuation_df: DataFrame containing valuation data
            loan_df: Optional DataFrame containing loan data (for fintech metrics)
            payment_df: Optional DataFrame containing payment data (for fintech metrics)
            user_df: Optional DataFrame containing user data (for fintech metrics)
            default_dpd_threshold: Days past due threshold for loan defaults
            export: Whether to export the results to a JSON file
            
        Returns:
            Dictionary containing all computed KPIs organized by category
        """
        out: Dict[str, Any] = {
            "startup": self.compute_startup_metrics(
                revenue_df, 
                customer_df, 
                valuation_df if (valuation_df is not None and isinstance(valuation_df, pd.DataFrame) and "marketing_expense" in valuation_df.columns) else None
            ),
            "fintech": self.compute_fintech_metrics(
                loan_df if loan_df is not None else pd.DataFrame(),
                payment_df, 
                user_df, 
                default_dpd_threshold=default_dpd_threshold
            ) if loan_df is not None else {},
            "valuation": {}
        }

        # Valuation block (reuse valuation_df columns if provided)
        try:
            v = valuation_df
            pre = float(v.get("pre_money_valuation", pd.Series([np.nan])).iloc[0]) if isinstance(v, pd.DataFrame) else float(v.get("pre_money_valuation", np.nan))
            inv = float(v.get("investment_amount", pd.Series([0])).iloc[0]) if isinstance(v, pd.DataFrame) else float(v.get("investment_amount", 0))
            mcap = float(v.get("market_cap", pd.Series([0])).iloc[0]) if isinstance(v, pd.DataFrame) else float(v.get("market_cap", 0))
            debt = float(v.get("total_debt", pd.Series([0])).iloc[0]) if isinstance(v, pd.DataFrame) else float(v.get("total_debt", 0))
            cash = float(v.get("cash", pd.Series([0])).iloc[0]) if isinstance(v, pd.DataFrame) else float(v.get("cash", 0))
            rev = float(v.get("revenue", pd.Series([0])).iloc[0]) if isinstance(v, pd.DataFrame) else float(v.get("revenue", 0))
            ebitda = float(v.get("ebitda", pd.Series([np.nan])).iloc[0]) if isinstance(v, pd.DataFrame) else float(v.get("ebitda", np.nan))

            post = pre + inv if np.isfinite(pre) else np.nan
            ev = mcap + debt - cash
            out["valuation"] = {
                "pre_money_valuation": pre,
                "post_money_valuation": post,
                "enterprise_value": ev,
                "revenue_multiple": self.safe_division(ev, rev, np.nan),
                "ebitda_multiple": self.safe_division(ev, ebitda, np.nan) if (ebitda is not None and np.isfinite(ebitda) and ebitda > 0) else np.nan,
                "dilution": self.safe_division(inv, post, 0.0) if (np.isfinite(post) and post > 0) else 0.0,
            }
        except Exception as e:
            logger.error(f"Valuation error: {e}")
            out["valuation"] = {}

        out["viability_index"] = self.compute_viability_index(out["startup"])

        if export:
            self._export_json(out, "kpis")

        return out
