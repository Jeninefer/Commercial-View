"""
Test suite for Commercial View DPD calculations.

Tests the accurate Days Past Due (DPD) calculation logic to ensure:
1. DPD is 0 for loans that are current (no arrears)
2. DPD is correctly calculated for loans in arrears
3. DPD resets to 0 when loans catch up after being in arrears
4. Default flag is set correctly based on dpd_threshold
"""

import pandas as pd
import pytest
from datetime import datetime, timedelta
from commercial_view import LoanPortfolio


class TestDPDCalculation:
    """Test suite for accurate DPD calculation."""
    
    def test_loan_never_in_arrears(self):
        """Test that a loan that is always current has DPD = 0."""
        portfolio = LoanPortfolio(dpd_threshold=90)
        
        # Loan with payments on time
        payment_schedule = pd.DataFrame({
            'loan_id': ['L001', 'L001'],
            'due_date': ['2024-01-01', '2024-02-01'],
            'amount_due': [1000.0, 1000.0]
        })
        
        payments = pd.DataFrame({
            'loan_id': ['L001', 'L001'],
            'payment_date': ['2024-01-01', '2024-02-01'],
            'amount_paid': [1000.0, 1000.0]
        })
        
        result = portfolio.calculate_dpd(
            payment_schedule=payment_schedule,
            payments=payments,
            reference_date='2024-02-15'
        )
        
        assert len(result) == 1
        assert result.iloc[0]['loan_id'] == 'L001'
        assert result.iloc[0]['days_past_due'] == 0
        assert result.iloc[0]['cumulative_gap'] == 0.0
        assert result.iloc[0]['is_default'] == False
        assert result.iloc[0]['past_due_amount'] == 0.0
    
    def test_loan_currently_in_arrears(self):
        """Test that a loan in arrears has correct DPD calculation."""
        portfolio = LoanPortfolio(dpd_threshold=90)
        
        # Loan with missed payment
        payment_schedule = pd.DataFrame({
            'loan_id': ['L002', 'L002'],
            'due_date': ['2024-01-01', '2024-02-01'],
            'amount_due': [1000.0, 1000.0]
        })
        
        payments = pd.DataFrame({
            'loan_id': ['L002'],
            'payment_date': ['2024-01-01'],
            'amount_paid': [1000.0]
        })
        
        # Reference date is 30 days after second payment due
        result = portfolio.calculate_dpd(
            payment_schedule=payment_schedule,
            payments=payments,
            reference_date='2024-03-02'
        )
        
        assert len(result) == 1
        assert result.iloc[0]['loan_id'] == 'L002'
        assert result.iloc[0]['cumulative_gap'] == 1000.0
        assert result.iloc[0]['days_past_due'] == 30  # 30 days since 2024-02-01
        assert result.iloc[0]['is_default'] == False  # Not yet over 90 days
        assert result.iloc[0]['past_due_amount'] == 1000.0
    
    def test_loan_caught_up_after_arrears(self):
        """Test that DPD resets to 0 when a loan catches up after being in arrears."""
        portfolio = LoanPortfolio(dpd_threshold=90)
        
        # Loan that went into arrears then caught up
        payment_schedule = pd.DataFrame({
            'loan_id': ['L003', 'L003', 'L003'],
            'due_date': ['2024-01-01', '2024-02-01', '2024-03-01'],
            'amount_due': [1000.0, 1000.0, 1000.0]
        })
        
        payments = pd.DataFrame({
            'loan_id': ['L003', 'L003', 'L003'],
            'payment_date': ['2024-01-01', '2024-03-15', '2024-03-15'],
            'amount_paid': [1000.0, 1000.0, 1000.0]
        })
        
        # Reference date is after catching up
        result = portfolio.calculate_dpd(
            payment_schedule=payment_schedule,
            payments=payments,
            reference_date='2024-03-20'
        )
        
        assert len(result) == 1
        assert result.iloc[0]['loan_id'] == 'L003'
        assert result.iloc[0]['cumulative_gap'] == 0.0
        assert result.iloc[0]['days_past_due'] == 0  # Reset to 0 after catching up
        assert result.iloc[0]['is_default'] == False
        assert result.iloc[0]['past_due_amount'] == 0.0
    
    def test_default_flag_threshold(self):
        """Test that is_default flag is set correctly based on dpd_threshold."""
        portfolio = LoanPortfolio(dpd_threshold=90)
        
        # Loan that is 100 days past due
        payment_schedule = pd.DataFrame({
            'loan_id': ['L004'],
            'due_date': ['2024-01-01'],
            'amount_due': [1000.0]
        })
        
        payments = pd.DataFrame({
            'loan_id': [],
            'payment_date': [],
            'amount_paid': []
        })
        
        # Reference date is 100 days after due date
        result = portfolio.calculate_dpd(
            payment_schedule=payment_schedule,
            payments=payments,
            reference_date='2024-04-10'
        )
        
        assert len(result) == 1
        assert result.iloc[0]['loan_id'] == 'L004'
        assert result.iloc[0]['cumulative_gap'] == 1000.0
        assert result.iloc[0]['days_past_due'] == 100
        assert result.iloc[0]['is_default'] == True  # Over 90 days threshold
        assert result.iloc[0]['past_due_amount'] == 1000.0
    
    def test_multiple_loans_mixed_status(self):
        """Test portfolio with multiple loans in different states."""
        portfolio = LoanPortfolio(dpd_threshold=90)
        
        # Three loans: current, in arrears, caught up
        payment_schedule = pd.DataFrame({
            'loan_id': ['L001', 'L001', 'L002', 'L002', 'L003', 'L003'],
            'due_date': ['2024-01-01', '2024-02-01', '2024-01-01', '2024-02-01', 
                        '2024-01-01', '2024-02-01'],
            'amount_due': [1000.0, 1000.0, 1000.0, 1000.0, 1000.0, 1000.0]
        })
        
        payments = pd.DataFrame({
            'loan_id': ['L001', 'L001', 'L002', 'L003', 'L003', 'L003'],
            'payment_date': ['2024-01-01', '2024-02-01', '2024-01-01', 
                           '2024-01-01', '2024-02-10', '2024-02-10'],
            'amount_paid': [1000.0, 1000.0, 1000.0, 1000.0, 500.0, 500.0]
        })
        
        result = portfolio.calculate_dpd(
            payment_schedule=payment_schedule,
            payments=payments,
            reference_date='2024-03-02'
        )
        
        assert len(result) == 3
        
        # L001 should be current
        l001 = result[result['loan_id'] == 'L001'].iloc[0]
        assert l001['days_past_due'] == 0
        assert l001['is_default'] == False
        
        # L002 should be in arrears (30 days)
        l002 = result[result['loan_id'] == 'L002'].iloc[0]
        assert l002['days_past_due'] == 30
        assert l002['cumulative_gap'] == 1000.0
        assert l002['is_default'] == False
        
        # L003 should be current (caught up)
        l003 = result[result['loan_id'] == 'L003'].iloc[0]
        assert l003['days_past_due'] == 0
        assert l003['cumulative_gap'] == 0.0
        assert l003['is_default'] == False
    
    def test_partial_payment_in_arrears(self):
        """Test loan with partial payment still shows correct arrears."""
        portfolio = LoanPortfolio(dpd_threshold=90)
        
        payment_schedule = pd.DataFrame({
            'loan_id': ['L005', 'L005'],
            'due_date': ['2024-01-01', '2024-02-01'],
            'amount_due': [1000.0, 1000.0]
        })
        
        payments = pd.DataFrame({
            'loan_id': ['L005', 'L005'],
            'payment_date': ['2024-01-01', '2024-02-01'],
            'amount_paid': [1000.0, 500.0]  # Partial payment
        })
        
        result = portfolio.calculate_dpd(
            payment_schedule=payment_schedule,
            payments=payments,
            reference_date='2024-03-02'
        )
        
        assert len(result) == 1
        assert result.iloc[0]['loan_id'] == 'L005'
        assert result.iloc[0]['cumulative_gap'] == 500.0
        assert result.iloc[0]['days_past_due'] == 30  # Since 2024-02-01
        assert result.iloc[0]['past_due_amount'] == 500.0
    
    def test_reference_date_defaults_to_today(self):
        """Test that reference_date defaults to today when not provided."""
        portfolio = LoanPortfolio(dpd_threshold=90)
        
        payment_schedule = pd.DataFrame({
            'loan_id': ['L006'],
            'due_date': ['2024-01-01'],
            'amount_due': [1000.0]
        })
        
        payments = pd.DataFrame({
            'loan_id': ['L006'],
            'payment_date': ['2024-01-01'],
            'amount_paid': [1000.0]
        })
        
        # Should not raise an error when reference_date is not provided
        result = portfolio.calculate_dpd(
            payment_schedule=payment_schedule,
            payments=payments
        )
        
        assert len(result) == 1
        assert 'days_past_due' in result.columns
        assert 'is_default' in result.columns
    
    def test_first_arrears_date_reflects_current_period(self):
        """Test that first_arrears_date reflects the current arrears period."""
        portfolio = LoanPortfolio(dpd_threshold=90)
        
        # Loan goes into arrears, catches up, then goes into arrears again
        payment_schedule = pd.DataFrame({
            'loan_id': ['L007'] * 4,
            'due_date': ['2024-01-01', '2024-02-01', '2024-03-01', '2024-04-01'],
            'amount_due': [1000.0, 1000.0, 1000.0, 1000.0]
        })
        
        payments = pd.DataFrame({
            'loan_id': ['L007', 'L007', 'L007'],
            'payment_date': ['2024-01-01', '2024-02-15', '2024-03-01'],
            'amount_paid': [1000.0, 1000.0, 1000.0]
        })
        
        # Check when in second arrears period
        result = portfolio.calculate_dpd(
            payment_schedule=payment_schedule,
            payments=payments,
            reference_date='2024-04-30'
        )
        
        assert len(result) == 1
        assert result.iloc[0]['cumulative_gap'] == 1000.0
        # First arrears date should be 2024-04-01 (current period), not 2024-02-01
        assert pd.to_datetime(result.iloc[0]['first_arrears_date']) == pd.Timestamp('2024-04-01')
        assert result.iloc[0]['days_past_due'] == 29  # Days from 2024-04-01 to 2024-04-30
    
    def test_custom_dpd_threshold(self):
        """Test that custom dpd_threshold is respected."""
        portfolio = LoanPortfolio(dpd_threshold=30)  # 30-day threshold
        
        payment_schedule = pd.DataFrame({
            'loan_id': ['L008'],
            'due_date': ['2024-01-01'],
            'amount_due': [1000.0]
        })
        
        payments = pd.DataFrame({
            'loan_id': [],
            'payment_date': [],
            'amount_paid': []
        })
        
        result = portfolio.calculate_dpd(
            payment_schedule=payment_schedule,
            payments=payments,
            reference_date='2024-02-15'
        )
        
        assert len(result) == 1
        assert result.iloc[0]['days_past_due'] == 45
        assert result.iloc[0]['is_default'] == True  # Over 30-day threshold
    
    def test_overpayment(self):
        """Test loan with overpayment shows negative gap but correct DPD of 0."""
        portfolio = LoanPortfolio(dpd_threshold=90)
        
        payment_schedule = pd.DataFrame({
            'loan_id': ['L009'],
            'due_date': ['2024-01-01'],
            'amount_due': [1000.0]
        })
        
        payments = pd.DataFrame({
            'loan_id': ['L009'],
            'payment_date': ['2024-01-01'],
            'amount_paid': [1500.0]  # Overpayment
        })
        
        result = portfolio.calculate_dpd(
            payment_schedule=payment_schedule,
            payments=payments,
            reference_date='2024-02-01'
        )
        
        assert len(result) == 1
        assert result.iloc[0]['cumulative_gap'] == -500.0  # Negative gap
        assert result.iloc[0]['days_past_due'] == 0
        assert result.iloc[0]['past_due_amount'] == 0.0  # Clipped at 0
        assert result.iloc[0]['is_default'] == False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
