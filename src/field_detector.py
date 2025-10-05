"""
Field detector module extracted from PRs #31-40
Patterns for Payment Date and Total Payment columns detection
"""

import pandas as pd
from typing import Dict, List

class FieldDetector:
    """Detect field patterns for Payment Date and Total Payment columns"""
    
    def __init__(self):
        self.payment_date_patterns = [
            'payment_date', 'pay_date', 'fecha_pago', 'payment_dt',
            'true_payment_date', 'actual_payment_date'
        ]
        
        self.total_payment_patterns = [
            'total_payment', 'payment_amount', 'monto_pago', 'total_paid',
            'amount_paid', 'payment_total'
        ]
    
    def detect_payment_fields(self, df: pd.DataFrame) -> Dict[str, str]:
        """Add field detection patterns for Payment Date and Total Payment columns"""
        detected_fields = {}
        
        # Payment Date detection
        for pattern in self.payment_date_patterns:
            matches = [col for col in df.columns if pattern.lower() in col.lower()]
            if matches:
                detected_fields['payment_date'] = matches[0]
                break
        
        # Total Payment detection  
        for pattern in self.total_payment_patterns:
            matches = [col for col in df.columns if pattern.lower() in col.lower()]
            if matches:
                detected_fields['total_payment'] = matches[0]
                break
        
        return detected_fields
