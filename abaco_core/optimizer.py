"""
Portfolio optimizer for Commercial-View.

Pragmatic, dependency-light portfolio optimization that honors target mix
and hard limits defined in the manifest.
"""

import logging
from typing import Dict, Any, List, Tuple, Optional
import pandas as pd
import numpy as np

from .config import Config

logger = logging.getLogger("abaco_core.optimizer")


class PortfolioOptimizer:
    """
    Portfolio optimizer honoring target mix and hard limits.
    
    Uses a greedy algorithm with priority weighting to select deals
    that optimize the portfolio mix while respecting constraints.
    
    Example:
        >>> optimizer = PortfolioOptimizer()
        >>> selected = optimizer.optimize(deal_candidates, current_portfolio)
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize optimizer.
        
        Args:
            config: Configuration object. If None, loads default config.
        """
        self.cfg = config or Config()
        self.constraints = self.cfg.optimizer
        
    def optimize(
        self,
        candidates: pd.DataFrame,
        current_portfolio: pd.DataFrame,
        max_amount: float
    ) -> pd.DataFrame:
        """
        Select deals to optimize portfolio mix.
        
        Args:
            candidates: DataFrame with candidate deals.
                Required columns: deal_id, amount, apr_bucket, line_bucket,
                industry, payer_id, term_months
            current_portfolio: DataFrame with current portfolio.
                Same structure as candidates.
            max_amount: Maximum total amount to allocate.
        
        Returns:
            DataFrame with selected deals.
        """
        if candidates.empty:
            return pd.DataFrame()
        
        # Calculate current portfolio state
        current_total = current_portfolio["amount"].sum() if not current_portfolio.empty else 0.0
        target_total = current_total + max_amount
        
        # Score each candidate
        candidates = candidates.copy()
        candidates["score"] = candidates.apply(
            lambda row: self._score_deal(row, current_portfolio, target_total),
            axis=1
        )
        
        # Sort by score (descending)
        candidates = candidates.sort_values("score", ascending=False)
        
        # Greedy selection respecting constraints
        selected = []
        selected_amount = 0.0
        temp_portfolio = current_portfolio.copy() if not current_portfolio.empty else pd.DataFrame()
        
        for _, deal in candidates.iterrows():
            if selected_amount + deal["amount"] > max_amount:
                continue
            
            # Check if adding this deal violates hard limits
            temp_combined = pd.concat([temp_portfolio, pd.DataFrame([deal])], ignore_index=True)
            if self._check_hard_limits(temp_combined):
                selected.append(deal)
                selected_amount += deal["amount"]
                temp_portfolio = temp_combined
                
                if selected_amount >= max_amount:
                    break
        
        return pd.DataFrame(selected) if selected else pd.DataFrame()
    
    def _score_deal(
        self,
        deal: pd.Series,
        current_portfolio: pd.DataFrame,
        target_total: float
    ) -> float:
        """
        Score a deal based on how well it improves portfolio mix.
        
        Args:
            deal: Deal to score.
            current_portfolio: Current portfolio state.
            target_total: Target total portfolio size.
        
        Returns:
            Score (higher is better).
        """
        weights = self.constraints.get("priority_weights", {})
        w_apr = weights.get("apr", 0.6)
        w_term = weights.get("term_fit", 0.35)
        w_count = weights.get("origination_count", 0.05)
        
        # APR score: how close to target mix
        apr_score = self._calculate_apr_score(deal, current_portfolio, target_total)
        
        # Term fit score: prefer 12-18 month terms (normalized to 0-1)
        term_score = 0.0
        if "term_months" in deal:
            ideal_term = 15.0
            term_months = float(deal["term_months"])
            term_score = max(0.0, 1.0 - abs(term_months - ideal_term) / 12.0)
        
        # Count score: prefer smaller deals for diversification
        count_score = 1.0 / (1.0 + np.log1p(deal["amount"] / 10000.0))
        
        total_score = w_apr * apr_score + w_term * term_score + w_count * count_score
        return total_score
    
    def _calculate_apr_score(
        self,
        deal: pd.Series,
        current_portfolio: pd.DataFrame,
        target_total: float
    ) -> float:
        """
        Calculate APR mix score for a deal.
        
        Args:
            deal: Deal to score.
            current_portfolio: Current portfolio.
            target_total: Target portfolio total.
        
        Returns:
            Score from 0 to 1 (higher means closer to target).
        """
        if target_total <= 0:
            return 0.0
        
        apr_bucket = deal.get("apr_bucket", "")
        target_mix = self.constraints.get("target_mix", {}).get("apr", {})
        
        if not target_mix or apr_bucket not in target_mix:
            return 0.5  # Neutral score if bucket not in target
        
        # Calculate current share
        current_total = current_portfolio["amount"].sum() if not current_portfolio.empty else 0.0
        current_bucket_amt = 0.0
        if not current_portfolio.empty and "apr_bucket" in current_portfolio.columns:
            current_bucket_amt = current_portfolio[
                current_portfolio["apr_bucket"] == apr_bucket
            ]["amount"].sum()
        
        # Calculate projected share if we add this deal
        projected_bucket_amt = current_bucket_amt + deal["amount"]
        projected_share = projected_bucket_amt / target_total
        
        # Target share
        target_share = target_mix.get(apr_bucket, 0.0)
        
        # Score: 1.0 if at target, decreases as we move away
        deviation = abs(projected_share - target_share)
        score = max(0.0, 1.0 - deviation * 5.0)  # Scale deviation
        
        return score
    
    def _check_hard_limits(self, portfolio: pd.DataFrame) -> bool:
        """
        Check if portfolio respects hard limits.
        
        Args:
            portfolio: Portfolio to check.
        
        Returns:
            True if all limits are respected, False otherwise.
        """
        if portfolio.empty:
            return True
        
        total = portfolio["amount"].sum()
        if total <= 0:
            return True
        
        hard_limits = self.constraints.get("hard_limits", {})
        
        # Check APR limits
        apr_limits = hard_limits.get("apr", {})
        if "apr_bucket" in portfolio.columns:
            for bucket, limit in apr_limits.items():
                max_pct = limit.get("max_pct", 1.0)
                bucket_amt = portfolio[portfolio["apr_bucket"] == bucket]["amount"].sum()
                if bucket_amt / total > max_pct:
                    return False
        
        # Check payer concentration
        payer_limits = hard_limits.get("payer", {})
        if "payer_id" in portfolio.columns:
            any_anchor_max = payer_limits.get("any_anchor", {}).get("max_pct", 1.0)
            payer_shares = portfolio.groupby("payer_id")["amount"].sum() / total
            if payer_shares.max() > any_anchor_max:
                return False
        
        # Check industry concentration
        industry_limits = hard_limits.get("industry", {})
        if "industry" in portfolio.columns:
            any_sector_max = industry_limits.get("any_sector", {}).get("max_pct", 1.0)
            industry_shares = portfolio.groupby("industry")["amount"].sum() / total
            if industry_shares.max() > any_sector_max:
                return False
        
        return True
    
    def analyze_portfolio(self, portfolio: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze portfolio and compare against targets.
        
        Args:
            portfolio: Portfolio DataFrame to analyze.
        
        Returns:
            Dictionary with analysis results.
        """
        if portfolio.empty:
            return {"error": "Empty portfolio"}
        
        total = portfolio["amount"].sum()
        analysis = {
            "total_amount": float(total),
            "deal_count": len(portfolio),
            "apr_distribution": {},
            "line_distribution": {},
            "industry_distribution": {},
            "payer_concentration": {},
            "hard_limits_violations": []
        }
        
        # APR distribution
        if "apr_bucket" in portfolio.columns:
            apr_dist = portfolio.groupby("apr_bucket")["amount"].sum() / total
            analysis["apr_distribution"] = apr_dist.to_dict()
        
        # Line size distribution
        if "line_bucket" in portfolio.columns:
            line_dist = portfolio.groupby("line_bucket")["amount"].sum() / total
            analysis["line_distribution"] = line_dist.to_dict()
        
        # Industry distribution
        if "industry" in portfolio.columns:
            ind_dist = portfolio.groupby("industry")["amount"].sum() / total
            analysis["industry_distribution"] = ind_dist.to_dict()
        
        # Payer concentration
        if "payer_id" in portfolio.columns:
            payer_shares = portfolio.groupby("payer_id")["amount"].sum() / total
            analysis["payer_concentration"] = {
                "top1": float(payer_shares.max()),
                "top10": float(payer_shares.nlargest(10).sum()) if len(payer_shares) >= 10 else float(payer_shares.sum())
            }
        
        # Check hard limits
        if not self._check_hard_limits(portfolio):
            analysis["hard_limits_violations"].append("Portfolio violates hard limits")
        
        return analysis
