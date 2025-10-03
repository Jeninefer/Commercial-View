"""
Multi-objective optimization engine for disbursement decisions.
Balances multiple KPIs to recommend optimal loan disbursements.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from pulp import LpMaximize, LpProblem, LpVariable, lpSum, LpBinary, LpStatus, value

from config import (
    WEIGHT_APR,
    WEIGHT_ROTATION_SPEED,
    WEIGHT_CONCENTRATION_RISK,
    WEIGHT_MOM_GROWTH,
    WEIGHT_DPD_MINIMIZATION,
    MAX_CLIENT_CONCENTRATION,
    MAX_SECTOR_CONCENTRATION,
    MAX_DPD_TOLERANCE
)


class DisbursementOptimizer:
    """
    Multi-objective optimizer for loan disbursement decisions.
    """
    
    def __init__(
        self,
        disbursement_requests: pd.DataFrame,
        current_portfolio: pd.DataFrame,
        available_cash: float
    ):
        self.requests = disbursement_requests
        self.portfolio = current_portfolio
        self.available_cash = available_cash
        self.recommendations = []
        
    def _calculate_apr_score(self, selected_loans: pd.DataFrame) -> float:
        """
        Calculate APR score for selected loans.
        Higher APR is better (normalized 0-1).
        """
        if len(selected_loans) == 0:
            return 0.0
        
        avg_apr = selected_loans['proposed_apr'].mean()
        # Normalize assuming APR range 8-25%
        normalized = (avg_apr - 0.08) / (0.25 - 0.08)
        return max(0.0, min(1.0, normalized))
    
    def _calculate_rotation_score(self, selected_loans: pd.DataFrame) -> float:
        """
        Calculate rotation speed score.
        Shorter terms are better for faster rotation (normalized 0-1).
        """
        if len(selected_loans) == 0:
            return 0.0
        
        avg_term = selected_loans['proposed_term'].mean()
        # Normalize assuming term range 30-180 days (inverse: shorter is better)
        normalized = 1.0 - (avg_term - 30) / (180 - 30)
        return max(0.0, min(1.0, normalized))
    
    def _calculate_concentration_score(self, selected_loans: pd.DataFrame) -> float:
        """
        Calculate concentration risk score.
        Lower concentration is better (normalized 0-1).
        """
        if len(selected_loans) == 0:
            return 0.0
        
        # Combine selected loans with existing portfolio
        # Ensure selected_loans has a 'principal' column for consistency
        selected_loans_with_principal = selected_loans.copy()
        if 'principal' not in selected_loans_with_principal.columns and 'requested_amount' in selected_loans_with_principal.columns:
            selected_loans_with_principal['principal'] = selected_loans_with_principal['requested_amount']
        combined_portfolio = pd.concat([self.portfolio, selected_loans_with_principal], ignore_index=True)
        total_exposure = combined_portfolio['principal'].sum()
        
        # Client concentration
        client_concentration = 0.0
        if 'client_id' in combined_portfolio.columns:
            client_exposure = combined_portfolio.groupby('client_id').agg({
                'principal': 'sum'
            })
            if len(selected_loans) > 0:
                selected_by_client = selected_loans.groupby('client_id')['requested_amount'].sum()
                for client_id, amount in selected_by_client.items():
                    if client_id in client_exposure.index:
                        client_exposure.loc[client_id, 'principal'] += amount
                    else:
                        client_exposure.loc[client_id] = amount
            
            client_concentration = (client_exposure['principal'] / total_exposure).max()
        
        # Sector concentration
        sector_concentration = 0.0
        if 'sector' in combined_portfolio.columns:
            sector_exposure = combined_portfolio.groupby('sector')['principal'].sum()
            if len(selected_loans) > 0 and 'sector' in selected_loans.columns:
                selected_by_sector = selected_loans.groupby('sector')['requested_amount'].sum()
                for sector, amount in selected_by_sector.items():
                    if sector in sector_exposure.index:
                        sector_exposure[sector] += amount
                    else:
                        sector_exposure[sector] = amount
            
            sector_concentration = (sector_exposure / total_exposure).max()
        
        # Score is better when concentration is lower
        avg_concentration = (client_concentration + sector_concentration) / 2
        score = 1.0 - avg_concentration
        return max(0.0, min(1.0, score))
    
    def _calculate_growth_score(self, selected_loans: pd.DataFrame) -> float:
        """
        Calculate growth potential score.
        More disbursements contribute to growth (normalized 0-1).
        """
        if len(selected_loans) == 0:
            return 0.0
        
        disbursement_amount = selected_loans['requested_amount'].sum()
        current_portfolio_size = self.portfolio['principal'].sum()
        
        # Growth as percentage of current portfolio
        growth_rate = disbursement_amount / current_portfolio_size if current_portfolio_size > 0 else 1.0
        
        # Normalize assuming 0-50% growth
        normalized = min(growth_rate / 0.5, 1.0)
        return normalized
    
    def _calculate_dpd_score(self, selected_loans: pd.DataFrame) -> float:
        """
        Calculate DPD risk score.
        Lower expected DPD is better (normalized 0-1).
        """
        if len(selected_loans) == 0:
            return 0.0
        
        # Use credit score as proxy for DPD risk if available
        if 'credit_score' in selected_loans.columns:
            avg_credit_score = selected_loans['credit_score'].mean()
            # Normalize credit score (300-850 range)
            normalized = (avg_credit_score - 300) / (850 - 300)
            return max(0.0, min(1.0, normalized))
        
        # Default to neutral score if no credit data
        return 0.5
    
    def _calculate_objective_score(self, selected_loans: pd.DataFrame) -> float:
        """
        Calculate weighted multi-objective score.
        """
        apr_score = self._calculate_apr_score(selected_loans)
        rotation_score = self._calculate_rotation_score(selected_loans)
        concentration_score = self._calculate_concentration_score(selected_loans)
        growth_score = self._calculate_growth_score(selected_loans)
        dpd_score = self._calculate_dpd_score(selected_loans)
        
        total_score = (
            WEIGHT_APR * apr_score +
            WEIGHT_ROTATION_SPEED * rotation_score +
            WEIGHT_CONCENTRATION_RISK * concentration_score +
            WEIGHT_MOM_GROWTH * growth_score +
            WEIGHT_DPD_MINIMIZATION * dpd_score
        )
        
        return total_score
    
    def optimize_linear_programming(self) -> Dict[str, Any]:
        """
        Use linear programming to find optimal disbursement combination.
        """
        # Create the LP problem
        prob = LpProblem("Disbursement_Optimization", LpMaximize)
        
        # Create binary decision variables for each loan request
        n_requests = len(self.requests)
        loan_vars = [LpVariable(f"loan_{i}", cat=LpBinary) for i in range(n_requests)]
        
        # Objective: Maximize weighted score
        # Simplified: maximize APR contribution (can be extended with other factors)
        objective = lpSum([
            loan_vars[i] * self.requests.iloc[i]['requested_amount'] * self.requests.iloc[i]['proposed_apr']
            for i in range(n_requests)
        ])
        prob += objective
        
        # Constraint: Total disbursement <= available cash
        prob += lpSum([
            loan_vars[i] * self.requests.iloc[i]['requested_amount']
            for i in range(n_requests)
        ]) <= self.available_cash
        
        # Solve the problem
        prob.solve()
        
        # Extract solution
        selected_indices = [i for i in range(n_requests) if value(loan_vars[i]) == 1]
        selected_loans = self.requests.iloc[selected_indices].copy()
        
        return {
            'status': LpStatus[prob.status],
            'selected_loans': selected_loans,
            'total_disbursement': selected_loans['requested_amount'].sum() if len(selected_loans) > 0 else 0,
            'objective_value': value(prob.objective) if prob.status == 1 else 0
        }
    
    def optimize_greedy(self) -> Dict[str, Any]:
        """
        Use greedy algorithm to select loans.
        Faster alternative to LP, selects loans by score/cost ratio.
        """
        # Calculate score for each loan
        scores = []
        for idx, loan in self.requests.iterrows():
            loan_df = pd.DataFrame([loan])
            score = self._calculate_objective_score(loan_df)
            efficiency = score / loan['requested_amount']
            scores.append((idx, score, efficiency))
        
        # Sort by efficiency (score per dollar)
        scores.sort(key=lambda x: x[2], reverse=True)
        
        # Greedily select loans
        selected_indices = []
        total_disbursed = 0
        
        for idx, score, efficiency in scores:
            loan_amount = self.requests.loc[idx, 'requested_amount']
            if total_disbursed + loan_amount <= self.available_cash:
                selected_indices.append(idx)
                total_disbursed += loan_amount
        
        selected_loans = self.requests.loc[selected_indices].copy()
        
        return {
            'status': 'Optimal',
            'selected_loans': selected_loans,
            'total_disbursement': total_disbursed,
            'remaining_cash': self.available_cash - total_disbursed
        }
    
    def generate_recommendation(self, method: str = 'greedy') -> Dict[str, Any]:
        """
        Generate disbursement recommendation.
        
        Args:
            method: 'greedy' or 'lp' (linear programming)
            
        Returns:
            Dictionary with recommendations and analysis
        """
        if method == 'lp':
            result = self.optimize_linear_programming()
        else:
            result = self.optimize_greedy()
        
        selected_loans = result['selected_loans']
        
        # Calculate expected KPIs
        expected_kpis = {
            'apr_score': self._calculate_apr_score(selected_loans),
            'rotation_score': self._calculate_rotation_score(selected_loans),
            'concentration_score': self._calculate_concentration_score(selected_loans),
            'growth_score': self._calculate_growth_score(selected_loans),
            'dpd_score': self._calculate_dpd_score(selected_loans),
            'overall_score': self._calculate_objective_score(selected_loans)
        }
        
        return {
            'status': result['status'],
            'selected_loans': selected_loans,
            'total_disbursement': result['total_disbursement'],
            'remaining_cash': self.available_cash - result['total_disbursement'],
            'num_loans': len(selected_loans),
            'expected_kpis': expected_kpis,
            'cash_utilization': result['total_disbursement'] / self.available_cash if self.available_cash > 0 else 0
        }
    
    def format_recommendation(self, recommendation: Dict[str, Any]) -> str:
        """
        Format recommendation as human-readable text.
        """
        selected = recommendation['selected_loans']
        kpis = recommendation['expected_kpis']
        
        output = f"""
DISBURSEMENT RECOMMENDATION
===========================
Status: {recommendation['status']}
Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

Summary:
--------
Number of Loans to Approve: {recommendation['num_loans']}
Total Disbursement Amount: ${recommendation['total_disbursement']:,.2f}
Available Cash: ${self.available_cash:,.2f}
Cash Utilization: {recommendation['cash_utilization']*100:.1f}%
Remaining Cash: ${recommendation['remaining_cash']:,.2f}

Expected Portfolio Impact:
--------------------------
APR Score: {kpis['apr_score']*100:.1f}%
Rotation Speed Score: {kpis['rotation_score']*100:.1f}%
Concentration Risk Score: {kpis['concentration_score']*100:.1f}%
Growth Score: {kpis['growth_score']*100:.1f}%
Credit Quality Score: {kpis['dpd_score']*100:.1f}%
Overall Score: {kpis['overall_score']*100:.1f}%

Recommended Loans:
------------------
"""
        if len(selected) > 0:
            for idx, loan in selected.iterrows():
                output += f"\n  • Request ID: {loan.get('request_id', 'N/A')}"
                output += f"\n    Client: {loan.get('client_name', 'N/A')}"
                output += f"\n    Amount: ${loan['requested_amount']:,.2f}"
                output += f"\n    APR: {loan['proposed_apr']*100:.2f}%"
                output += f"\n    Term: {loan['proposed_term']} days"
                if 'sector' in loan:
                    output += f"\n    Sector: {loan['sector']}"
                output += "\n"
        else:
            output += "\n  No loans recommended with current constraints.\n"
        
        return output


def optimize_disbursements(
    requests: pd.DataFrame,
    portfolio: pd.DataFrame,
    available_cash: float,
    method: str = 'greedy'
) -> Dict[str, Any]:
    """
    Convenience function to optimize disbursements.
    """
    optimizer = DisbursementOptimizer(requests, portfolio, available_cash)
    return optimizer.generate_recommendation(method)
