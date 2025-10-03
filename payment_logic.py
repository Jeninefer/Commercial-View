import re
from typing import Optional, List


class PaymentProcessor:
    """
    A processor for handling payment and schedule data with automatic field detection.
    """
    
    # Loan ID Patterns - existing patterns suffice
    LOAN_ID_PATTERNS = [
        r'\bloan(?:[_\s]*)id\b',
        r'\bloan(?:[_\s]*)number\b',
        r'\bloan(?:[_\s]*)no\b',
        r'\baccount(?:[_\s]*)id\b',
        r'\baccount(?:[_\s]*)number\b',
    ]
    
    # Schedule Date Patterns - added "Payment Date" with space
    SCHEDULE_DATE_PATTERNS = [
        r'due[_\s]*date',
        r'payment[_\s]*date',  # Added to match "Payment Date"
        r'schedule[_\s]*date',
        r'expected[_\s]*date',
    ]
    
    # Schedule Amount Patterns - added "Total Payment" and "total_payment"
    SCHEDULE_AMOUNT_PATTERNS = [
        r'due[_\s]*amount',
        r'scheduled[_\s]*amount',
        r'expected[_\s]*amount',
        r'(?:^|[_\s])total(?:[_\s]*)payment(?:$|[_\s])',  # Anchored to avoid matching substrings like 'subtotal_payment'
        r'installment[_\s]*amount',
    ]
    
    # Payment Date Patterns - already includes generic "date" which matched "True Payment Date"
    PAYMENT_DATE_PATTERNS = [
        r'payment[_\s]*date',
        r'paid[_\s]*date',
        r'actual[_\s]*date',
        r'transaction[_\s]*date',
        r'(?:^|[_\s])date(?:$|[_\s])',  # Anchored pattern to avoid matching substrings like 'updated'
    ]
    
    # Payment Amount Patterns - added "Total Payment"/"total_payment"
    PAYMENT_AMOUNT_PATTERNS = [
        r'paid[_\s]*amount',
        r'payment[_\s]*amount',
        r'actual[_\s]*amount',
        r'total[_\s]*payment',  # Added to match "True Total Payment" and "total_payment"
        r'transaction[_\s]*amount',
        r'amount',
    ]
    
    def __init__(self):
        """Initialize the PaymentProcessor."""
        pass
    
    def _detect_field(self, columns: List[str], patterns: List[str]) -> Optional[str]:
        """
        Detect which column matches the given patterns.
        
        Args:
            columns: List of column names to search through
            patterns: List of regex patterns to match against
            
        Returns:
            The first matching column name, or None if no match found
        """
        for pattern in patterns:
            compiled_pattern = re.compile(pattern, re.IGNORECASE)
            for col in columns:
                if compiled_pattern.search(col):
                    return col
        return None
    
    def detect_loan_id_field(self, columns: List[str]) -> Optional[str]:
        """Detect the loan ID field from the given columns."""
        return self._detect_field(columns, self.LOAN_ID_PATTERNS)
    
    def detect_schedule_date_field(self, columns: List[str]) -> Optional[str]:
        """Detect the schedule date field from the given columns."""
        return self._detect_field(columns, self.SCHEDULE_DATE_PATTERNS)
    
    def detect_schedule_amount_field(self, columns: List[str]) -> Optional[str]:
        """Detect the schedule amount field from the given columns."""
        return self._detect_field(columns, self.SCHEDULE_AMOUNT_PATTERNS)
    
    def detect_payment_date_field(self, columns: List[str]) -> Optional[str]:
        """Detect the payment date field from the given columns."""
        return self._detect_field(columns, self.PAYMENT_DATE_PATTERNS)
    
    def detect_payment_amount_field(self, columns: List[str]) -> Optional[str]:
        """Detect the payment amount field from the given columns."""
        return self._detect_field(columns, self.PAYMENT_AMOUNT_PATTERNS)
