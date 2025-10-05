"""
KPI Calculator module extracted from PR #6
Core KPI calculation functions for startup and commercial metrics
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
import pandas as pd

@dataclass
class StartupSnapshot:
    """Dataclass for startup metrics snapshot"""
    mrr: float
    total_customers: int
    pre_money: Optional[float] = None
    post_money: Optional[float] = None

def compute_arr(mrr: float) -> float:
    """Calculate Annual Recurring Revenue from Monthly Recurring Revenue"""
    return float(mrr) * 12.0

def compute_post_money(pre_money: float, new_money: float) -> float:
    """Calculate post-money valuation"""
    return float(pre_money) + float(new_money)

def update_snapshot(snap: Dict[str, Any], new_money: Optional[float] = None) -> Dict[str, Any]:
    """Update snapshot with calculated KPIs"""
    if "startup" in snap and "mrr" in snap["startup"]:
        mrr = snap["startup"]["mrr"]
        snap["startup"]["arr"] = compute_arr(mrr)
    
    if (new_money is not None and 
        "valuation" in snap and 
        snap["valuation"].get("pre_money")):
        snap["valuation"]["post_money"] = compute_post_money(
            snap["valuation"]["pre_money"], new_money
        )
    
    return snap

def calculate_weighted_apr(portfolio_data: Dict[str, Any]) -> float:
    """Calculate portfolio-weighted APR: sum(APR × balance) / sum(balance)"""
    total_weighted = 0.0
    total_balance = 0.0
    
    # ...existing code for calculation logic...
    
    return total_weighted / total_balance if total_balance > 0 else 0.0

def calculate_progress_percentage(current: float, target: float) -> int:
    """Calculate progress percentage with proper rounding"""
    if target == 0:
        return 0
    return round((current / target) * 100)

class KPICalculator:
    """Enhanced KPI calculator with additional metrics from PRs #20-25"""
    
    def __init__(self):
        self.advanced_metrics = ['portfolio_yield', 'cost_of_funds', 'net_interest_margin']
    
    def calculate_portfolio_yield(self, loan_df: pd.DataFrame) -> float:
        """Calculate portfolio yield from interest income"""
        if 'interest_income' in loan_df.columns and 'outstanding_balance' in loan_df.columns:
            total_income = loan_df['interest_income'].sum()
            total_balance = loan_df['outstanding_balance'].sum()
            return total_income / total_balance if total_balance > 0 else 0.0
        return 0.0
    
    def calculate_collection_efficiency(self, payment_df: pd.DataFrame) -> float:
        """Calculate collection efficiency ratio"""
        if 'collected_amount' in payment_df.columns and 'scheduled_amount' in payment_df.columns:
            total_collected = payment_df['collected_amount'].sum()
            total_scheduled = payment_df['scheduled_amount'].sum()
            return total_collected / total_scheduled if total_scheduled > 0 else 0.0
        return 0.0
