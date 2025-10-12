"""
Comprehensive KPI Engine Test Suite
31+ test cases covering all commercial lending analytics
"""

import pytest
import pandas as pd
import numpy as np
rng = np.random.default_rng(seed=42)  # Modern NumPy random generator
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from src.analytics.kpi_engine import CommercialLendingKPIEngine, KPIResult
from src.core.production_data_manager import ProductionDataManager
from src.core.enterprise_config import EnterpriseConfigManager

class TestCommercialLendingKPIEngine:
    """Test suite for KPI calculation engine"""
    
    @pytest.fixture
    def mock_data_loader(self):
        """Mock data loader with test datasets"""
        loader = Mock(spec=ProductionDataManager)
        loader.load_dataset.return_value = self._create_test_loan_data()
        return loader
    
    @pytest.fixture
    def mock_config(self):
        """Mock configuration manager"""
        config = Mock(spec=EnterpriseConfigManager)
        config.get_kpi_targets.return_value = {
            "outstanding_portfolio": 7800000,
            "weighted_apr": 0.185,
            "npl_rate": 0.025,
            "collection_rate": 0.95
        }
        return config
    
    @pytest.fixture
    def kpi_engine(self, mock_data_loader, mock_config):
        """KPI engine instance with mocked dependencies"""
        return CommercialLendingKPIEngine(mock_data_loader, mock_config)
    
    def _create_test_loan_data(self, num_loans=100):
        """Create realistic test loan dataset"""
        np.random.seed(42)
        return pd.DataFrame({
            'loan_id': [f'CL{i:06d}' for i in range(1, num_loans + 1)],
            'customer_id': [f'CUST{(i % 30) + 1:04d}' for i in range(num_loans)],
            'principal_amount': np.random.lognormal(13, 0.8, num_loans),
            'interest_rate': rng.normal(0.18, 0.05, num_loans).clip(0.08, 0.35),
            'loan_status': rng.choice(['active', 'paid_of', 'delinquent'], num_loans, p=[0.8, 0.15, 0.05]),
            'origination_date': pd.date_range(start='2023-01-01', periods=num_loans, freq='D').strftime('%Y-%m-%d'),
            'risk_grade': rng.choice(['A', 'B', 'C', 'D', 'E'], num_loans, p=[0.3, 0.3, 0.25, 0.1, 0.05])
        })
    
    # Test Case 1-5: Outstanding Portfolio Calculations
    def test_outstanding_portfolio_calculation_basic(self, kpi_engine, mock_data_loader):
        """Test basic outstanding portfolio calculation"""
        test_data = self._create_test_loan_data(50)
        mock_data_loader.load_dataset.return_value = test_data
        
        result = kpi_engine._calculate_outstanding_portfolio({"loan_portfolio": test_data})
        
        assert isinstance(result, KPIResult)
        assert result.value > 0
        assert result.name == "Outstanding Portfolio"
        assert result.unit == "$"
        assert result.confidence_level >= 0.9
    
    def test_outstanding_portfolio_empty_dataset(self, kpi_engine, mock_data_loader):
        """Test outstanding portfolio with empty dataset"""
        empty_data = pd.DataFrame(columns=['loan_id', 'customer_id', 'principal_amount', 'loan_status'])
        mock_data_loader.load_dataset.return_value = empty_data
        
        result = kpi_engine._calculate_outstanding_portfolio({"loan_portfolio": empty_data})
        
        assert result.value == 0
        assert result.status == "critical"
    
    def test_outstanding_portfolio_only_inactive_loans(self, kpi_engine, mock_data_loader):
        """Test portfolio calculation with only inactive loans"""
        test_data = self._create_test_loan_data(20)
        test_data['loan_status'] = 'paid_off'
        mock_data_loader.load_dataset.return_value = test_data
        
        result = kpi_engine._calculate_outstanding_portfolio({"loan_portfolio": test_data})
        
        assert result.value == 0
    
    def test_outstanding_portfolio_with_payment_schedule(self, kpi_engine, mock_data_loader):
        """Test portfolio calculation using payment schedule balances"""
        loan_data = self._create_test_loan_data(10)
        payment_data = pd.DataFrame({
            'loan_id': ['CL000001', 'CL000002', 'CL000003'],
            'remaining_balance': [50000, 75000, 100000]
        })
        
        datasets = {"loan_portfolio": loan_data, "payment_schedule": payment_data}
        result = kpi_engine._calculate_outstanding_portfolio(datasets)
        
        assert result.value == 225000  # Sum of remaining balances
    
    def test_outstanding_portfolio_status_determination(self, kpi_engine, mock_data_loader):
        """Test status determination based on target comparison"""
        test_data = self._create_test_loan_data(10)
        test_data['principal_amount'] = [1000000] * 10  # Total: 10M
        mock_data_loader.load_dataset.return_value = test_data
        
        result = kpi_engine._calculate_outstanding_portfolio({"loan_portfolio": test_data})
        
        # Should be "excellent" as 10M > 7.8M target
        assert result.status == "excellent"
    
    # Test Case 6-10: Weighted APR Calculations
    def test_weighted_apr_calculation_accuracy(self, kpi_engine, mock_data_loader):
        """Test weighted APR calculation accuracy"""
        # Create precise test data
        test_data = pd.DataFrame({
            'loan_id': ['CL000001', 'CL000002'],
            'principal_amount': [1000000, 500000],  # 2:1 ratio
            'interest_rate': [0.20, 0.10],  # 20% and 10%
            'loan_status': ['active', 'active'],
            'customer_id': ['CUST001', 'CUST002']
        })
        
        result = kpi_engine._calculate_weighted_apr({"loan_portfolio": test_data})
        
        # Expected: (0.20 * 1M + 0.10 * 0.5M) / 1.5M = 0.1667
        expected_apr = (0.20 * 1000000 + 0.10 * 500000) / 1500000
        assert abs(result.value - expected_apr) < 0.0001
    
    def test_weighted_apr_single_loan(self, kpi_engine, mock_data_loader):
        """Test weighted APR with single loan"""
        test_data = pd.DataFrame({
            'loan_id': ['CL000001'],
            'principal_amount': [1000000],
            'interest_rate': [0.15],
            'loan_status': ['active'],
            'customer_id': ['CUST001']
        })
        
        result = kpi_engine._calculate_weighted_apr({"loan_portfolio": test_data})
        
        assert result.value == 0.15
    
    def test_weighted_apr_no_active_loans(self, kpi_engine, mock_data_loader):
        """Test weighted APR with no active loans"""
        test_data = pd.DataFrame({
            'loan_id': ['CL000001'],
            'principal_amount': [1000000],
            'interest_rate': [0.15],
            'loan_status': ['paid_of'],
            'customer_id': ['CUST001']
        })
        
        result = kpi_engine._calculate_weighted_apr({"loan_portfolio": test_data})
        
        assert result.value == 0.0
        assert result.status == "critical"
    
    def test_weighted_apr_extreme_values(self, kpi_engine, mock_data_loader):
        """Test weighted APR with extreme interest rates"""
        test_data = pd.DataFrame({
            'loan_id': ['CL000001', 'CL000002'],
            'principal_amount': [1000000, 1000000],
            'interest_rate': [0.05, 0.35],  # 5% and 35%
            'loan_status': ['active', 'active'],
            'customer_id': ['CUST001', 'CUST002']
        })
        
        result = kpi_engine._calculate_weighted_apr({"loan_portfolio": test_data})
        
        assert result.value == 0.20  # Average of 5% and 35%
    
    def test_weighted_apr_tolerance_checking(self, kpi_engine, mock_data_loader):
        """Test APR tolerance-based status determination"""
        test_data = self._create_test_loan_data(10)
        test_data['interest_rate'] = 0.187  # Close to 18.5% target
        mock_data_loader.load_dataset.return_value = test_data
        
        result = kpi_engine._calculate_weighted_apr({"loan_portfolio": test_data})
        
        # Should be "good" as within tolerance
        assert result.status in ["good", "excellent"]
    
    # Test Case 11-15: NPL Rate Calculations
    def test_npl_rate_calculation_basic(self, kpi_engine, mock_data_loader):
        """Test basic NPL rate calculation"""
        loan_data = self._create_test_loan_data(10)
        historic_data = pd.DataFrame({
            'loan_id': ['CL000001', 'CL000002', 'CL000003'],
            'days_past_due': [200, 150, 90]  # 1 NPL, 2 current
        })
        
        datasets = {"loan_portfolio": loan_data, "historic_payments": historic_data}
        result = kpi_engine._calculate_npl_rate(datasets)
        
        # 1 NPL out of 10 active loans = 10%
        expected_npl = 1 / 8  # 8 active loans in test data
        assert abs(result.value - expected_npl) < 0.01
    
    def test_npl_rate_no_npls(self, kpi_engine, mock_data_loader):
        """Test NPL rate with no NPL loans"""
        loan_data = self._create_test_loan_data(5)
        historic_data = pd.DataFrame({
            'loan_id': ['CL000001', 'CL000002'],
            'days_past_due': [30, 60]  # All current
        })
        
        datasets = {"loan_portfolio": loan_data, "historic_payments": historic_data}
        result = kpi_engine._calculate_npl_rate(datasets)
        
        assert result.value == 0.0
        assert result.status == "excellent"
    
    def test_npl_rate_all_npls(self, kpi_engine, mock_data_loader):
        """Test NPL rate with all loans NPL"""
        loan_data = self._create_test_loan_data(3)
        historic_data = pd.DataFrame({
            'loan_id': ['CL000001', 'CL000002', 'CL000003'],
            'days_past_due': [200, 300, 250]  # All NPL
        })
        
        datasets = {"loan_portfolio": loan_data, "historic_payments": historic_data}
        result = kpi_engine._calculate_npl_rate(datasets)
        
        # Adjust for active loans in test data
        assert result.value > 0.8  # Should be very high
        assert result.status == "critical"
    
    def test_npl_rate_boundary_conditions(self, kpi_engine, mock_data_loader):
        """Test NPL rate at exactly 180 DPD boundary"""
        loan_data = self._create_test_loan_data(4)
        historic_data = pd.DataFrame({
            'loan_id': ['CL000001', 'CL000002', 'CL000003', 'CL000004'],
            'days_past_due': [179, 180, 181, 90]  # 2 NPL (>=180), 2 current
        })
        
        datasets = {"loan_portfolio": loan_data, "historic_payments": historic_data}
        result = kpi_engine._calculate_npl_rate(datasets)
        
        # 2 NPLs out of active loans
        active_loans = len(loan_data[loan_data['loan_status'] == 'active'])
        expected_npl = 2 / active_loans if active_loans > 0 else 0
        assert abs(result.value - expected_npl) < 0.1
    
    def test_npl_rate_missing_payment_data(self, kpi_engine, mock_data_loader):
        """Test NPL rate with missing payment history"""
        loan_data = self._create_test_loan_data(5)
        historic_data = pd.DataFrame(columns=['loan_id', 'days_past_due'])
        
        datasets = {"loan_portfolio": loan_data, "historic_payments": historic_data}
        result = kpi_engine._calculate_npl_rate(datasets)
        
        assert result.value == 0.0
    
    # Test Case 16-20: Concentration Risk Analysis
    def test_concentration_risk_single_dominant_client(self, kpi_engine, mock_data_loader):
        """Test concentration risk with one dominant client"""
        test_data = pd.DataFrame({
            'loan_id': ['CL000001', 'CL000002', 'CL000003'],
            'customer_id': ['CUST001', 'CUST001', 'CUST002'],  # CUST001 has 2 loans
            'principal_amount': [5000000, 3000000, 1000000],  # Total: 9M, CUST001: 8M
            'loan_status': ['active', 'active', 'active']
        })
        
        result = kpi_engine._calculate_concentration_risk({"loan_portfolio": test_data})
        
        # CUST001: 8M / 9M = 88.9%
        expected_concentration = 8000000 / 9000000
        assert abs(result.value - expected_concentration) < 0.01
        assert result.status == "critical"  # Well above 15% limit
    
    def test_concentration_risk_equal_distribution(self, kpi_engine, mock_data_loader):
        """Test concentration risk with equal client distribution"""
        test_data = pd.DataFrame({
            'loan_id': ['CL000001', 'CL000002', 'CL000003', 'CL000004'],
            'customer_id': ['CUST001', 'CUST002', 'CUST003', 'CUST004'],
            'principal_amount': [1000000, 1000000, 1000000, 1000000],
            'loan_status': ['active', 'active', 'active', 'active']
        })
        
        result = kpi_engine._calculate_concentration_risk({"loan_portfolio": test_data})
        
        # Each client: 25%
        assert result.value == 0.25
        assert result.status in ["warning", "critical"]  # Above 15% limit
    
    def test_concentration_risk_within_limits(self, kpi_engine, mock_data_loader):
        """Test concentration risk within acceptable limits"""
        test_data = pd.DataFrame({
            'loan_id': [f'CL{i:06d}' for i in range(1, 11)],
            'customer_id': [f'CUST{i:03d}' for i in range(1, 11)],  # 10 different clients
            'principal_amount': [1000000] * 10,  # Equal amounts
            'loan_status': ['active'] * 10
        })
        
        result = kpi_engine._calculate_concentration_risk({"loan_portfolio": test_data})
        
        # Each client: 10%
        assert result.value == 0.10
        assert result.status == "excellent"  # Below 15% limit
    
    def test_concentration_risk_no_loans(self, kpi_engine, mock_data_loader):
        """Test concentration risk with no loans"""
        test_data = pd.DataFrame(columns=['loan_id', 'customer_id', 'principal_amount', 'loan_status'])
        
        result = kpi_engine._calculate_concentration_risk({"loan_portfolio": test_data})
        
        assert result.value == 0.0
    
    def test_concentration_risk_single_loan(self, kpi_engine, mock_data_loader):
        """Test concentration risk with single loan"""
        test_data = pd.DataFrame({
            'loan_id': ['CL000001'],
            'customer_id': ['CUST001'],
            'principal_amount': [1000000],
            'loan_status': ['active']
        })
        
        result = kpi_engine._calculate_concentration_risk({"loan_portfolio": test_data})
        
        assert result.value == 1.0  # 100% concentration
        assert result.status == "critical"

    # Test Case 21-25: Collection Rate Analysis
    def test_collection_rate_perfect_collections(self, kpi_engine, mock_data_loader):
        """Test collection rate with 100% collections"""
        payment_schedule = pd.DataFrame({
            'due_date': ['2024-01-15', '2024-01-15'],
            'total_amount': [10000, 15000]
        })
        historic_payments = pd.DataFrame({
            'payment_date': ['2024-01-15', '2024-01-16'],
            'amount_paid': [10000, 15000]
        })
        
        # Mock current month
        with patch('src.analytics.kpi_engine.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "2024-01"
            
            datasets = {"payment_schedule": payment_schedule, "historic_payments": historic_payments}
            result = kpi_engine._calculate_collection_rate(datasets)
            
            assert result.value == 1.0  # 100%
            assert result.status == "excellent"

    def test_collection_rate_partial_collections(self, kpi_engine, mock_data_loader):
        """Test collection rate with partial collections"""
        payment_schedule = pd.DataFrame({
            'due_date': ['2024-01-15', '2024-01-15'],
            'total_amount': [10000, 20000]  # Total: 30K scheduled
        })
        historic_payments = pd.DataFrame({
            'payment_date': ['2024-01-15', '2024-01-16'],
            'amount_paid': [10000, 15000]  # Total: 25K collected
        })
        
        with patch('src.analytics.kpi_engine.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "2024-01"
            
            datasets = {"payment_schedule": payment_schedule, "historic_payments": historic_payments}
            result = kpi_engine._calculate_collection_rate(datasets)
            
            expected_rate = 25000 / 30000  # 83.33%
            assert abs(result.value - expected_rate) < 0.01
            assert result.status in ["warning", "good"]

    def test_collection_rate_no_scheduled_payments(self, kpi_engine, mock_data_loader):
        """Test collection rate with no scheduled payments"""
        payment_schedule = pd.DataFrame(columns=['due_date', 'total_amount'])
        historic_payments = pd.DataFrame(columns=['payment_date', 'amount_paid'])
        
        datasets = {"payment_schedule": payment_schedule, "historic_payments": historic_payments}
        result = kpi_engine._calculate_collection_rate(datasets)
        
        assert result.value == 0.0

    def test_collection_rate_excess_collections(self, kpi_engine, mock_data_loader):
        """Test collection rate with collections exceeding scheduled amounts"""
        payment_schedule = pd.DataFrame({
            'due_date': ['2024-01-15'],
            'total_amount': [10000]
        })
        historic_payments = pd.DataFrame({
            'payment_date': ['2024-01-15'],
            'amount_paid': [15000]  # 150% of scheduled
        })
        
        with patch('src.analytics.kpi_engine.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "2024-01"
            
            datasets = {"payment_schedule": payment_schedule, "historic_payments": historic_payments}
            result = kpi_engine._calculate_collection_rate(datasets)
            
            assert result.value == 1.5  # 150%
            assert result.status == "excellent"

    def test_collection_rate_zero_collections(self, kpi_engine, mock_data_loader):
        """Test collection rate with zero collections"""
        payment_schedule = pd.DataFrame({
            'due_date': ['2024-01-15'],
            'total_amount': [10000]
        })
        historic_payments = pd.DataFrame(columns=['payment_date', 'amount_paid'])
        
        with patch('src.analytics.kpi_engine.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "2024-01"
            
            datasets = {"payment_schedule": payment_schedule, "historic_payments": historic_payments}
            result = kpi_engine._calculate_collection_rate(datasets)
            
            assert result.value == 0.0
            assert result.status == "critical"

    # Test Case 26-31: Integration and Edge Cases
    def test_calculate_all_kpis_integration(self, kpi_engine, mock_data_loader):
        """Test complete KPI calculation integration"""
        # Setup comprehensive test data
        loan_data = self._create_test_loan_data(100)
        payment_schedule = pd.DataFrame({
            'loan_id': ['CL000001', 'CL000002'],
            'remaining_balance': [50000, 75000]
        })
        historic_payments = pd.DataFrame({
            'loan_id': ['CL000001', 'CL000002'],
            'days_past_due': [30, 200]
        })
        
        def mock_load_dataset(name):
            if name == "loan_portfolio":
                return loan_data
            elif name == "payment_schedule":
                return payment_schedule
            elif name == "historic_payments":
                return historic_payments
            else:
                return pd.DataFrame()
        
        mock_data_loader.load_dataset.side_effect = mock_load_dataset
        
        results = kpi_engine.calculate_all_kpis()
        
        # Verify all KPIs are calculated
        expected_kpis = [
            "outstanding_portfolio", "weighted_apr", "npl_rate",
            "concentration_risk", "active_clients", "collection_rate"
        ]
        
        for kpi in expected_kpis:
            assert kpi in results
            assert isinstance(results[kpi], KPIResult)
            assert results[kpi].value is not None

    def test_kpi_engine_error_handling(self, kpi_engine, mock_data_loader):
        """Test KPI engine error handling with corrupted data"""
        # Create corrupted dataset
        corrupted_data = pd.DataFrame({
            'loan_id': ['CL000001', None, 'CL000003'],
            'principal_amount': [100000, 'invalid', -50000],
            'interest_rate': [0.15, None, 'bad_rate'],
            'loan_status': ['active', '', None]
        })
        
        mock_data_loader.load_dataset.return_value = corrupted_data
        
        # Should handle errors gracefully
        with pytest.raises((ValueError, TypeError)):
            kpi_engine._calculate_outstanding_portfolio({"loan_portfolio": corrupted_data})
    
    # ... existing code ...
