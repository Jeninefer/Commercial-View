"""
Tests for PaymentAnalyzer module to verify the refactoring that avoids redundant standardization.
"""

import pandas as pd
import pytest
from datetime import datetime, timedelta
from payment_analyzer import PaymentAnalyzer


class TestPaymentAnalyzer:
    """Test suite for PaymentAnalyzer class."""
    
    @pytest.fixture
    def analyzer(self):
        """Create a PaymentAnalyzer instance for testing."""
        return PaymentAnalyzer()
    
    @pytest.fixture
    def raw_schedule_data(self):
        """Sample raw schedule data with non-standardized column names."""
        return pd.DataFrame({
            'LoanID': ['L001', 'L001', 'L002', 'L002'],
            'DueDate': [
                '2025-01-01',
                '2025-02-01',
                '2025-01-15',
                '2025-02-15'
            ],
            'DueAmount': [1000, 1000, 500, 500]
        })
    
    @pytest.fixture
    def raw_payments_data(self):
        """Sample raw payments data with non-standardized column names."""
        return pd.DataFrame({
            'LoanID': ['L001', 'L002'],
            'PaymentDate': ['2025-01-01', '2025-01-20'],
            'PaymentAmount': [1000, 500]
        })
    
    @pytest.fixture
    def standardized_schedule_data(self):
        """Sample standardized schedule data."""
        return pd.DataFrame({
            'loan_id': ['L001', 'L001', 'L002', 'L002'],
            'due_date': pd.to_datetime([
                '2025-01-01',
                '2025-02-01',
                '2025-01-15',
                '2025-02-15'
            ]),
            'due_amount': [1000, 1000, 500, 500]
        })
    
    @pytest.fixture
    def standardized_payments_data(self):
        """Sample standardized payments data."""
        return pd.DataFrame({
            'loan_id': ['L001', 'L002'],
            'payment_date': pd.to_datetime(['2025-01-01', '2025-01-20']),
            'payment_amount': [1000, 500]
        })
    
    def test_standardize_dataframes(self, analyzer, raw_schedule_data, raw_payments_data):
        """Test that standardize_dataframes correctly renames columns."""
        sched, pays = analyzer.standardize_dataframes(raw_schedule_data, raw_payments_data)
        
        # Check schedule columns
        assert 'loan_id' in sched.columns
        assert 'due_date' in sched.columns
        assert 'due_amount' in sched.columns
        
        # Check payment columns
        assert 'loan_id' in pays.columns
        assert 'payment_date' in pays.columns
        assert 'payment_amount' in pays.columns
        
        # Check data types
        assert pd.api.types.is_datetime64_any_dtype(sched['due_date'])
        assert pd.api.types.is_datetime64_any_dtype(pays['payment_date'])
    
    def test_calculate_payment_timeline_with_raw_data(
        self, analyzer, raw_schedule_data, raw_payments_data
    ):
        """
        Test that calculate_payment_timeline works with raw data 
        and standardizes it internally.
        """
        timeline = analyzer.calculate_payment_timeline(
            raw_schedule_data,
            raw_payments_data,
            reference_date=datetime(2025, 3, 1)
        )
        
        # Timeline should have merged data
        assert len(timeline) > 0
        assert 'loan_id' in timeline.columns
        assert 'payment_status' in timeline.columns
        
    def test_calculate_payment_timeline_with_standardized_data(
        self, analyzer, standardized_schedule_data, standardized_payments_data
    ):
        """
        Test that calculate_payment_timeline works with already-standardized data
        without re-standardizing it.
        """
        timeline = analyzer.calculate_payment_timeline(
            standardized_schedule_data,
            standardized_payments_data,
            reference_date=datetime(2025, 3, 1)
        )
        
        # Timeline should have merged data
        assert len(timeline) > 0
        assert 'loan_id' in timeline.columns
        assert 'payment_status' in timeline.columns
    
    def test_calculate_dpd(self, analyzer, raw_schedule_data, raw_payments_data):
        """
        Test that calculate_dpd standardizes data once and reuses it,
        avoiding redundant standardization.
        """
        reference_date = datetime(2025, 3, 1)
        dpd_df = analyzer.calculate_dpd(
            raw_schedule_data,
            raw_payments_data,
            reference_date=reference_date
        )
        
        # DPD should be calculated for both loans
        assert len(dpd_df) == 2
        assert 'loan_id' in dpd_df.columns
        assert 'dpd' in dpd_df.columns
        assert 'reference_date' in dpd_df.columns
        
        # Verify the DPD values are non-negative
        assert all(dpd_df['dpd'] >= 0)
    
    def test_no_redundant_standardization(
        self, analyzer, raw_schedule_data, raw_payments_data, monkeypatch
    ):
        """
        Test that standardize_dataframes is called only once in calculate_dpd flow.
        This is the key test for the refactoring.
        """
        call_count = 0
        original_standardize = analyzer.standardize_dataframes
        
        def counting_standardize(sched_df, pay_df):
            nonlocal call_count
            call_count += 1
            return original_standardize(sched_df, pay_df)
        
        # Monkeypatch to count calls
        monkeypatch.setattr(analyzer, 'standardize_dataframes', counting_standardize)
        
        # Call calculate_dpd which internally calls calculate_payment_timeline
        dpd_df = analyzer.calculate_dpd(
            raw_schedule_data,
            raw_payments_data,
            reference_date=datetime(2025, 3, 1)
        )
        
        # standardize_dataframes should be called exactly once (in calculate_dpd)
        # and NOT again in calculate_payment_timeline because it receives standardized data
        assert call_count == 1, (
            f"Expected standardize_dataframes to be called once, but it was called {call_count} times. "
            "This indicates redundant standardization is still happening."
        )
