"""
Unit tests for data_processor module
"""

import pandas as pd
import unittest
from datetime import date
from data_processor import process_loan_data


class TestDataProcessor(unittest.TestCase):
    
    def test_date_conversion(self):
        """Test that dates are converted properly"""
        schedule_df = pd.DataFrame({
            'loan_id': [1, 2],
            'due_date': ['2024-01-15', '2024-02-20']
        })
        payments_df = pd.DataFrame({
            'loan_id': [1, 2],
            'payment_date': ['2024-01-14', '2024-02-19']
        })
        
        processed_schedule, processed_payments = process_loan_data(schedule_df, payments_df)
        
        # Check that dates are converted to date objects
        self.assertIsInstance(processed_schedule['due_date'].iloc[0], date)
        self.assertIsInstance(processed_payments['payment_date'].iloc[0], date)
    
    def test_null_removal_schedule(self):
        """Test that rows with null loan_id or due_date are removed from schedule"""
        schedule_df = pd.DataFrame({
            'loan_id': [1, 2, None, 4],
            'due_date': ['2024-01-15', None, '2024-03-10', '2024-04-20']
        })
        payments_df = pd.DataFrame({
            'loan_id': [1],
            'payment_date': ['2024-01-14']
        })
        
        processed_schedule, _ = process_loan_data(schedule_df, payments_df)
        
        # Should only have 2 valid rows (loan_id=1 and loan_id=4)
        self.assertEqual(len(processed_schedule), 2)
        self.assertEqual(list(processed_schedule['loan_id']), [1.0, 4.0])
    
    def test_null_removal_payments(self):
        """Test that rows with null loan_id or payment_date are removed from payments"""
        schedule_df = pd.DataFrame({
            'loan_id': [1],
            'due_date': ['2024-01-15']
        })
        payments_df = pd.DataFrame({
            'loan_id': [1, None, 3, 4],
            'payment_date': ['2024-01-14', '2024-02-19', None, '2024-04-09']
        })
        
        _, processed_payments = process_loan_data(schedule_df, payments_df)
        
        # Should only have 2 valid rows (loan_id=1 and loan_id=4)
        self.assertEqual(len(processed_payments), 2)
        self.assertEqual(list(processed_payments['loan_id']), [1.0, 4.0])
    
    def test_invalid_dates_coerced(self):
        """Test that invalid dates are coerced to NaT and then removed"""
        schedule_df = pd.DataFrame({
            'loan_id': [1, 2, 3],
            'due_date': ['2024-01-15', 'invalid-date', '2024-03-10']
        })
        payments_df = pd.DataFrame({
            'loan_id': [1, 2],
            'payment_date': ['2024-01-14', '2024-02-19']
        })
        
        processed_schedule, _ = process_loan_data(schedule_df, payments_df)
        
        # Row with 'invalid-date' should be removed
        self.assertEqual(len(processed_schedule), 2)
        self.assertEqual(list(processed_schedule['loan_id']), [1.0, 3.0])
    
    def test_empty_dataframes(self):
        """Test handling of empty dataframes"""
        schedule_df = pd.DataFrame({
            'loan_id': [],
            'due_date': []
        })
        payments_df = pd.DataFrame({
            'loan_id': [],
            'payment_date': []
        })
        
        processed_schedule, processed_payments = process_loan_data(schedule_df, payments_df)
        
        self.assertEqual(len(processed_schedule), 0)
        self.assertEqual(len(processed_payments), 0)


if __name__ == '__main__':
    unittest.main()
