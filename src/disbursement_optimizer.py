"""
Disbursement optimizer module extracted from PRs #26-30
Optimizes loan disbursement strategies
"""

import pandas as pd
from typing import Dict, List, Any

class DisbursementOptimizer:
    """Optimize loan disbursement timing and amounts"""
    
    def __init__(self):
        self.disbursement_limits = {
            'daily_limit': 1000000,    # $1M daily limit
            'monthly_target': 5000000,  # $5M monthly target
            'risk_adjustment': 0.1      # 10% risk buffer
        }
    
    def optimize_disbursements(self, loan_queue_df: pd.DataFrame) -> Dict[str, Any]:
        """Optimize disbursement schedule based on risk and capacity"""
        optimization = {
            'recommended_disbursements': [],
            'deferred_loans': [],
            'capacity_utilization': 0.0
        }
        
        if 'loan_amount' in loan_queue_df.columns:
            total_queue = loan_queue_df['loan_amount'].sum()
            daily_capacity = self.disbursement_limits['daily_limit']
            
            optimization['capacity_utilization'] = min(total_queue / daily_capacity, 1.0)
            
            # Priority-based disbursement
            if 'risk_score' in loan_queue_df.columns:
                sorted_loans = loan_queue_df.sort_values('risk_score')
                cumulative_amount = 0
                
                for idx, loan in sorted_loans.iterrows():
                    if cumulative_amount + loan['loan_amount'] <= daily_capacity:
                        optimization['recommended_disbursements'].append(loan.to_dict())
                        cumulative_amount += loan['loan_amount']
                    else:
                        optimization['deferred_loans'].append(loan.to_dict())
        
        return optimization