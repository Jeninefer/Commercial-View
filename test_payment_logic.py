import unittest
from payment_logic import PaymentProcessor


class TestPaymentProcessor(unittest.TestCase):
    """Test cases for PaymentProcessor field detection."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = PaymentProcessor()
    
    def test_detect_loan_id_field(self):
        """Test loan ID field detection."""
        # Test various column name formats
        columns1 = ['Loan ID', 'Payment Date', 'Amount']
        self.assertEqual(self.processor.detect_loan_id_field(columns1), 'Loan ID')
        
        columns2 = ['loan_id', 'payment_date', 'amount']
        self.assertEqual(self.processor.detect_loan_id_field(columns2), 'loan_id')
        
        columns3 = ['Account Number', 'Date', 'Amount']
        self.assertEqual(self.processor.detect_loan_id_field(columns3), 'Account Number')
        
    def test_detect_schedule_date_field_with_payment_date(self):
        """Test schedule date field detection with 'Payment Date' (with space)."""
        # This is the key test for the new pattern
        columns = ['Loan ID', 'Payment Date', 'Total Payment']
        detected = self.processor.detect_schedule_date_field(columns)
        self.assertEqual(detected, 'Payment Date')
        
    def test_detect_schedule_date_field_existing_patterns(self):
        """Test schedule date field detection with existing patterns."""
        columns1 = ['Loan ID', 'Due Date', 'Amount']
        self.assertEqual(self.processor.detect_schedule_date_field(columns1), 'Due Date')
        
        columns2 = ['loan_id', 'schedule_date', 'amount']
        self.assertEqual(self.processor.detect_schedule_date_field(columns2), 'schedule_date')
        
    def test_detect_schedule_amount_field_with_total_payment(self):
        """Test schedule amount field detection with 'Total Payment' patterns."""
        # Test "Total Payment" with space
        columns1 = ['Loan ID', 'Payment Date', 'Total Payment']
        detected1 = self.processor.detect_schedule_amount_field(columns1)
        self.assertEqual(detected1, 'Total Payment')
        
        # Test "total_payment" with underscore
        columns2 = ['loan_id', 'payment_date', 'total_payment']
        detected2 = self.processor.detect_schedule_amount_field(columns2)
        self.assertEqual(detected2, 'total_payment')
        
    def test_detect_schedule_amount_field_existing_patterns(self):
        """Test schedule amount field detection with existing patterns."""
        columns1 = ['Loan ID', 'Due Date', 'Due Amount']
        self.assertEqual(self.processor.detect_schedule_amount_field(columns1), 'Due Amount')
        
        columns2 = ['loan_id', 'due_date', 'scheduled_amount']
        self.assertEqual(self.processor.detect_schedule_amount_field(columns2), 'scheduled_amount')
        
    def test_detect_payment_date_field(self):
        """Test payment date field detection."""
        # Test with "True Payment Date" - should match the generic "date" pattern
        columns1 = ['Loan ID', 'True Payment Date', 'True Total Payment']
        detected1 = self.processor.detect_payment_date_field(columns1)
        self.assertIn(detected1, ['True Payment Date'])  # Should match via "payment[_\s]*date" or "date"
        
        columns2 = ['loan_id', 'paid_date', 'amount']
        self.assertEqual(self.processor.detect_payment_date_field(columns2), 'paid_date')
        
    def test_detect_payment_amount_field_with_total_payment(self):
        """Test payment amount field detection with 'Total Payment' patterns."""
        # Test "True Total Payment" - should match via "total[_\s]*payment" pattern
        columns1 = ['Loan ID', 'True Payment Date', 'True Total Payment']
        detected1 = self.processor.detect_payment_amount_field(columns1)
        self.assertEqual(detected1, 'True Total Payment')
        
        # Test "total_payment" with underscore
        columns2 = ['loan_id', 'payment_date', 'total_payment']
        detected2 = self.processor.detect_payment_amount_field(columns2)
        self.assertEqual(detected2, 'total_payment')
        
    def test_detect_payment_amount_field_existing_patterns(self):
        """Test payment amount field detection with existing patterns."""
        columns1 = ['Loan ID', 'Payment Date', 'Paid Amount']
        self.assertEqual(self.processor.detect_payment_amount_field(columns1), 'Paid Amount')
        
        columns2 = ['loan_id', 'paid_date', 'payment_amount']
        self.assertEqual(self.processor.detect_payment_amount_field(columns2), 'payment_amount')
        
    def test_detect_field_returns_none_when_no_match(self):
        """Test that _detect_field returns None when no pattern matches."""
        columns = ['Unrelated1', 'Unrelated2', 'Unrelated3']
        self.assertIsNone(self.processor.detect_loan_id_field(columns))
        self.assertIsNone(self.processor.detect_schedule_date_field(columns))
        self.assertIsNone(self.processor.detect_schedule_amount_field(columns))
        
    def test_case_insensitive_matching(self):
        """Test that pattern matching is case-insensitive."""
        columns_upper = ['LOAN ID', 'PAYMENT DATE', 'TOTAL PAYMENT']
        self.assertEqual(self.processor.detect_loan_id_field(columns_upper), 'LOAN ID')
        self.assertEqual(self.processor.detect_schedule_date_field(columns_upper), 'PAYMENT DATE')
        self.assertEqual(self.processor.detect_schedule_amount_field(columns_upper), 'TOTAL PAYMENT')
        
        columns_lower = ['loan id', 'payment date', 'total payment']
        self.assertEqual(self.processor.detect_loan_id_field(columns_lower), 'loan id')
        self.assertEqual(self.processor.detect_schedule_date_field(columns_lower), 'payment date')
        self.assertEqual(self.processor.detect_schedule_amount_field(columns_lower), 'total payment')
        
    def test_mixed_separator_styles(self):
        """Test that both underscores and spaces are matched."""
        # Underscore style
        columns_underscore = ['loan_id', 'payment_date', 'total_payment']
        self.assertEqual(self.processor.detect_loan_id_field(columns_underscore), 'loan_id')
        self.assertEqual(self.processor.detect_schedule_date_field(columns_underscore), 'payment_date')
        self.assertEqual(self.processor.detect_schedule_amount_field(columns_underscore), 'total_payment')
        
        # Space style
        columns_space = ['Loan ID', 'Payment Date', 'Total Payment']
        self.assertEqual(self.processor.detect_loan_id_field(columns_space), 'Loan ID')
        self.assertEqual(self.processor.detect_schedule_date_field(columns_space), 'Payment Date')
        self.assertEqual(self.processor.detect_schedule_amount_field(columns_space), 'Total Payment')


if __name__ == '__main__':
    unittest.main()
