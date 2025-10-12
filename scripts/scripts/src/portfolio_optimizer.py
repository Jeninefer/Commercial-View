"""
Portfolio optimizer module extracted from PRs #26-30
Portfolio optimization and alert engine functionality
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any


class PortfolioOptimizer:
    """Portfolio optimization with alert engine capabilities"""

    def __init__(self):
        self.optimization_rules = {
            "max_concentration": 0.20,
            "target_yield": 0.15,
            "max_dpd_threshold": 90,
        }

    def optimize(self, portfolio_df: pd.DataFrame) -> Dict[str, Any]:
        """Optimize portfolio allocation and generate recommendations"""
        optimization_results = {
            "recommended_actions": [],
            "risk_alerts": [],
            "performance_metrics": {},
        }

        # Concentration analysis
        if (
            "customer_id" in portfolio_df.columns
            and "outstanding_balance" in portfolio_df.columns
        ):
            concentration = (
                portfolio_df.groupby("customer_id")["outstanding_balance"].sum()
                / portfolio_df["outstanding_balance"].sum()
            )

            high_concentration = concentration[
                concentration > self.optimization_rules["max_concentration"]
            ]
            if not high_concentration.empty:
                optimization_results["risk_alerts"].append(
                    f"High concentration risk: {len(high_concentration)} customers exceed 20% threshold"
                )

        return optimization_results

    def generate_alerts(self, portfolio_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate portfolio alerts based on risk thresholds"""
        alerts = []

        if "days_past_due" in portfolio_df.columns:
            high_dpd = portfolio_df[
                portfolio_df["days_past_due"]
                > self.optimization_rules["max_dpd_threshold"]
            ]
            if not high_dpd.empty:
                alerts.append(
                    {
                        "type": "DPD_ALERT",
                        "severity": "HIGH",
                        "message": f"{len(high_dpd)} loans exceed {self.optimization_rules['max_dpd_threshold']} days past due",
                        "count": len(high_dpd),
                    }
                )

        return alerts
