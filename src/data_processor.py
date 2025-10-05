"""
Data processor module extracted from PRs #31-40
Handles date conversions and loan schedule processing
"""

import pandas as pd
from datetime import datetime
from typing import Dict, Any

class DataProcessor:
    """Process loan schedules and payments with date conversion capabilities"""
    
    def __init__(self):
        # ...existing code...
        self.date_formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']
    
    def convert_dates_safely(self, df: pd.DataFrame, date_columns: list) -> pd.DataFrame:
        """Safely convert date columns with multiple format support"""
        result_df = df.copy()
        
        for col in date_columns:
            if col in result_df.columns:
                result_df[col] = pd.to_datetime(result_df[col], errors='coerce', infer_datetime_format=True)
        
        return result_df
    
    def process_loan_schedules(self, schedule_df: pd.DataFrame) -> pd.DataFrame:
        """Process loan payment schedules with date validation"""
        # ...existing code...
        processed_df = self.convert_dates_safely(schedule_df, ['payment_date', 'due_date'])
        
        if 'payment_amount' in processed_df.columns:
            processed_df['payment_amount'] = pd.to_numeric(processed_df['payment_amount'], errors='coerce')
        
        return processed_df