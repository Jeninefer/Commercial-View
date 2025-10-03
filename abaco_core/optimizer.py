"""
ABACO Optimizer - Disbursement Planning with Target Mix and Hard Limits
"""
from typing import Dict, Optional, List, Tuple
import pandas as pd
import numpy as np
from .manifest import bucket_apr, bucket_line, bucket_payer, share


class DisbursementOptimizer:
    """
    Optimize disbursement allocation to meet target portfolio mix while respecting hard limits.
    """
    
    def __init__(
        self,
        target_apr_mix: Optional[Dict[str, float]] = None,
        target_line_mix: Optional[Dict[str, float]] = None,
        target_industry_mix: Optional[Dict[str, float]] = None,
        payer_a_min: float = 0.30,
        payer_d_max: float = 0.15,
        industry_max_share: float = 0.25,
        top_client_max: float = 0.15,
    ):
        """
        Initialize optimizer with target mix and hard limits.
        
        Args:
            target_apr_mix: Target percentage distribution by APR bucket
            target_line_mix: Target percentage distribution by line bucket
            target_industry_mix: Target percentage distribution by industry
            payer_a_min: Minimum share for A-grade payers (default 30%)
            payer_d_max: Maximum share for D-grade payers (default 15%)
            industry_max_share: Maximum share for any single industry (default 25%)
            top_client_max: Maximum share for top client (default 15%)
        """
        self.target_apr_mix = target_apr_mix or {}
        self.target_line_mix = target_line_mix or {}
        self.target_industry_mix = target_industry_mix or {}
        self.payer_a_min = payer_a_min
        self.payer_d_max = payer_d_max
        self.industry_max_share = industry_max_share
        self.top_client_max = top_client_max
    
    def score_request(
        self,
        amount: float,
        apr: float,
        industry: str,
        payer_grade: str,
        customer_id: str,
        current_portfolio: pd.DataFrame,
    ) -> float:
        """
        Score a disbursement request based on how it improves portfolio mix.
        
        Args:
            amount: Requested disbursement amount
            apr: APR for the request
            industry: Industry of the customer
            payer_grade: Payer quality grade (A, B, C, D)
            customer_id: Customer identifier
            current_portfolio: Current portfolio DataFrame with columns:
                             amount, apr, industry, payer_grade, customer_id
        
        Returns:
            Score (higher is better, negative if violates hard limits)
        """
        score = 0.0
        
        # Calculate current portfolio metrics
        total_current = current_portfolio["amount"].sum() if len(current_portfolio) > 0 else 0.0
        total_with_new = total_current + amount
        
        # Check hard limits
        
        # 1. Top client concentration
        if len(current_portfolio) > 0:
            customer_totals = current_portfolio.groupby("customer_id")["amount"].sum()
            if customer_id in customer_totals.index:
                customer_new_total = customer_totals[customer_id] + amount
            else:
                customer_new_total = amount
            
            if customer_new_total / total_with_new > self.top_client_max:
                return -1000.0  # Hard reject
        
        # 2. Industry concentration
        if len(current_portfolio) > 0:
            industry_totals = current_portfolio.groupby("industry")["amount"].sum()
            if industry in industry_totals.index:
                industry_new_total = industry_totals[industry] + amount
            else:
                industry_new_total = amount
            
            if industry_new_total / total_with_new > self.industry_max_share:
                return -900.0  # Hard reject
        
        # 3. Payer quality limits
        if len(current_portfolio) > 0:
            payer_totals = current_portfolio.groupby("payer_grade")["amount"].sum()
            
            # Check payer A minimum
            payer_a_total = payer_totals.get("A", 0.0)
            if payer_grade == "A":
                payer_a_total += amount
            payer_a_share = payer_a_total / total_with_new
            
            # Check payer D maximum
            payer_d_total = payer_totals.get("D", 0.0)
            if payer_grade == "D":
                payer_d_total += amount
            payer_d_share = payer_d_total / total_with_new
            
            if payer_d_share > self.payer_d_max:
                return -800.0  # Hard reject
        
        # Score based on target mix alignment
        
        # APR mix score
        if self.target_apr_mix:
            apr_bucket = bucket_apr(apr)
            current_apr_mix = share(current_portfolio.groupby(
                current_portfolio["apr"].apply(bucket_apr)
            )["amount"].sum()) if len(current_portfolio) > 0 else {}
            
            target_share = self.target_apr_mix.get(apr_bucket, 0.0)
            current_share = current_apr_mix.get(apr_bucket, 0.0)
            
            # Reward if below target
            if current_share < target_share:
                score += 10.0 * (target_share - current_share)
        
        # Line mix score
        if self.target_line_mix:
            line_bucket = bucket_line(amount)
            current_line_mix = share(current_portfolio.groupby(
                current_portfolio["amount"].apply(bucket_line)
            )["amount"].sum()) if len(current_portfolio) > 0 else {}
            
            target_share = self.target_line_mix.get(line_bucket, 0.0)
            current_share = current_line_mix.get(line_bucket, 0.0)
            
            if current_share < target_share:
                score += 8.0 * (target_share - current_share)
        
        # Industry mix score
        if self.target_industry_mix:
            target_share = self.target_industry_mix.get(industry, 0.0)
            current_industry_mix = share(
                current_portfolio.groupby("industry")["amount"].sum()
            ) if len(current_portfolio) > 0 else {}
            current_share = current_industry_mix.get(industry, 0.0)
            
            if current_share < target_share:
                score += 12.0 * (target_share - current_share)
        
        # Bonus for A-grade payers
        if payer_grade == "A":
            score += 5.0
        
        # Penalty for D-grade payers
        if payer_grade == "D":
            score -= 5.0
        
        return score
    
    def optimize(
        self,
        requests: pd.DataFrame,
        current_portfolio: pd.DataFrame,
        aum_target: float,
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        Select optimal disbursements from pending requests.
        
        Args:
            requests: DataFrame with columns: amount, apr, industry, payer_grade, customer_id
            current_portfolio: Current portfolio DataFrame (same schema)
            aum_target: Target total AUM after disbursements
        
        Returns:
            Tuple of (selected_requests DataFrame, report Dict)
        """
        # Calculate available budget
        current_aum = current_portfolio["amount"].sum() if len(current_portfolio) > 0 else 0.0
        budget = aum_target - current_aum
        
        if budget <= 0:
            return pd.DataFrame(), {"budget": 0.0, "message": "No budget available"}
        
        # Score all requests
        requests = requests.copy()
        requests["score"] = requests.apply(
            lambda row: self.score_request(
                row["amount"],
                row["apr"],
                row["industry"],
                row["payer_grade"],
                row["customer_id"],
                current_portfolio,
            ),
            axis=1,
        )
        
        # Filter out hard-rejected requests
        eligible = requests[requests["score"] > -100].sort_values("score", ascending=False)
        
        # Greedy selection
        selected = []
        selected_amount = 0.0
        working_portfolio = current_portfolio.copy()
        
        for idx, row in eligible.iterrows():
            if selected_amount + row["amount"] <= budget:
                # Re-score with updated portfolio
                new_score = self.score_request(
                    row["amount"],
                    row["apr"],
                    row["industry"],
                    row["payer_grade"],
                    row["customer_id"],
                    working_portfolio,
                )
                
                if new_score > -100:
                    selected.append(idx)
                    selected_amount += row["amount"]
                    working_portfolio = pd.concat([
                        working_portfolio,
                        pd.DataFrame([row.to_dict()])
                    ], ignore_index=True)
        
        selected_df = requests.loc[selected].copy() if selected else pd.DataFrame()
        
        # Generate report
        if len(selected_df) > 0:
            report = {
                "selected_count": len(selected_df),
                "selected_amount": float(selected_amount),
                "budget": float(budget),
                "utilization": float(selected_amount / budget * 100),
                "apr_mix": share(selected_df.groupby(selected_df["apr"].apply(bucket_apr))["amount"].sum()),
                "line_mix": share(selected_df.groupby(selected_df["amount"].apply(bucket_line))["amount"].sum()),
                "industry_mix": share(selected_df.groupby("industry")["amount"].sum()),
                "payer_mix": share(selected_df.groupby("payer_grade")["amount"].sum()),
            }
        else:
            report = {
                "selected_count": 0,
                "selected_amount": 0.0,
                "budget": float(budget),
                "utilization": 0.0,
                "message": "No eligible requests found",
            }
        
        return selected_df, report
