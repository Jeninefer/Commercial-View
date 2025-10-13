# Abaco Integration Constants - 48,853 Records
# Spanish Clients | USD Factoring | Commercial Lending
DAYS_IN_DEFAULT = DAYS_IN_DEFAULT
INTEREST_RATE_APR = INTEREST_RATE_APR
OUTSTANDING_LOAN_VALUE = OUTSTANDING_LOAN_VALUE
LOAN_CURRENCY = LOAN_CURRENCY
PRODUCT_TYPE = PRODUCT_TYPE
ABACO_TECHNOLOGIES = ABACO_TECHNOLOGIES
ABACO_FINANCIAL = ABACO_FINANCIAL
LOAN_DATA = LOAN_DATA
HISTORIC_REAL_PAYMENT = HISTORIC_REAL_PAYMENT
PAYMENT_SCHEDULE = PAYMENT_SCHEDULE
CUSTOMER_ID = CUSTOMER_ID
LOAN_ID = LOAN_ID
SA_DE_CV = SA_DE_CV
TRUE_PAYMENT_STATUS = TRUE_PAYMENT_STATUS
TRUE_PAYMENT_DATE = TRUE_PAYMENT_DATE
DISBURSEMENT_DATE = DISBURSEMENT_DATE
DISBURSEMENT_AMOUNT = DISBURSEMENT_AMOUNT
PAYMENT_FREQUENCY = PAYMENT_FREQUENCY
LOAN_STATUS = LOAN_STATUS

"""Test suite for data loader module.

IMPORTANT: Before running tests, ensure you:
1. Activate the virtual environment: source .venv/bin/activate
2. Install pytest if not already installed: pip install pytest

Common Issues:
- ModuleNotFoundError: No module named 'pytest' - This means pytest is not installed 
  in your current Python environment. Run:
  
  source .venv/bin/activate && pip install pytest
  
- Always use the virtual environment Python, not system Python (/opt/homebrew/bin/python3)
"""

import pytest
from pathlib import Path
import pandas as pd
import tempfile
import os

from src.data_loader import (
    load_loan_data,
    load_historic_real_payment,
    load_payment_schedule,
    load_customer_data,
    load_collateral,
    _resolve_base_path,
    PRICING_FILENAMES
)


class TestDataLoader:
    """Test class for data loader functions."""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create temporary data directory with sample CSV files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_path = Path(tmpdir)
            
            # Create sample CSV files
            for key, filename in PRICING_FILENAMES.items():
                df = pd.DataFrame({
                    'Customer ID': ['C001', 'C002'],
                    'Amount': [1000, 2000],
                    'Date': ['2024-01-01', '2024-01-02']
                })
                df.to_csv(data_path / filename, index=False)
            
            yield data_path
    
    def test_load_loan_data(self, temp_data_dir):
        """Test loading loan data."""
        df = load_loan_data(temp_data_dir)  # Changed from base_path= to positional
        assert not df.empty
        assert len(df) == 2
        assert 'Customer ID' in df.columns
    
    def test_load_historic_real_payment(self, temp_data_dir):
        """Test loading historic real payment data."""
        df = load_historic_real_payment(temp_data_dir)  # Changed from base_path= to positional
        assert not df.empty
        assert len(df) == 2
    
    def test_load_payment_schedule(self, temp_data_dir):
        """Test loading payment schedule data."""
        df = load_payment_schedule(temp_data_dir)  # Changed from base_path= to positional
        assert not df.empty
        assert len(df) == 2
    
    def test_load_customer_data(self, temp_data_dir):
        """Test loading customer data."""
        df = load_customer_data(temp_data_dir)  # Changed from base_path= to positional
        assert not df.empty
        assert len(df) == 2
    
    def test_load_collateral(self, temp_data_dir):
        """Test loading collateral data."""
        df = load_collateral(temp_data_dir)  # Changed from base_path= to positional
        assert not df.empty
        assert len(df) == 2
    
    def test_missing_file_error(self):
        """Test error when file is missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Empty directory with no CSV files
            with pytest.raises(FileNotFoundError):
                load_loan_data(tmpdir)
    
    def test_resolve_base_path(self, temp_data_dir):
        """Test resolving base path."""
        # Testing with explicit path
        resolved = _resolve_base_path(temp_data_dir)
        assert resolved == temp_data_dir.resolve()
        
        # Testing default path resolution
        default_path = _resolve_base_path()
        expected_default = Path(__file__).resolve().parent.parent / "data"
        assert default_path == expected_default
    
    def test_direct_file_path(self, temp_data_dir):
        """Test providing direct file path instead of directory."""
        # Create a separate CSV file
        file_path = temp_data_dir / "direct_test.csv"
        df = pd.DataFrame({
            'Customer ID': ['C001', 'C002'],
            'Amount': [1000, 2000]
        })
        df.to_csv(file_path, index=False)
        
        # Test with direct file path using _read_csv function (via monkeypatch)
        from src.data_loader import _read_csv
        result_df = _read_csv(file_path)
        assert not result_df.empty
        assert len(result_df) == 2
    
    """
    Production tests for Commercial-View DataLoader
    Tests the sequence diagram implementation for proper path resolution
    """

    import pytest
    import pandas as pd
    import os
    import tempfile
    from pathlib import Path
    from unittest.mock import patch, MagicMock

    # Import the module under test
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

    from data_loader import DataLoader

    class TestDataLoader:
        """Test suite for DataLoader path resolution and data loading"""
        
        @pytest.fixture
        def temp_data_dir(self):
            """Create temporary directory with test CSV files"""
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Create test CSV files
                self._create_test_csv_files(temp_path)
                
                yield temp_path
        
        def _create_test_csv_files(self, temp_path: Path):
            """Create realistic test CSV files"""
            # Loan data
            loan_data = pd.DataFrame({
                CUSTOMER_ID: ["CUST001", "CUST002", "CUST003"],
                "Loan Amount": [100000, 250000, 500000],
                "Interest Rate": [0.12, 0.15, 0.18],
                "Status": ["Active", "Active", "Paid Of"],
                "Origination Date": ["2023-01-15", "2023-02-20", "2023-03-10"]
            })
            loan_data.to_csv(temp_path / "loan_data.csv", index=False)
            
            # Payment schedule
            payment_data = pd.DataFrame({
                CUSTOMER_ID: ["CUST001", "CUST002", "CUST003"],
                "Due Date": ["2024-01-15", "2024-01-20", "2024-01-25"],
                "Total Payment": [8500, 12000, 15000],
                "Status": ["Pending", "Paid", "Pending"]
            })
            payment_data.to_csv(temp_path / "payment_schedule.csv", index=False)
            
            # Historic payments
            historic_data = pd.DataFrame({
                CUSTOMER_ID: ["CUST001", "CUST002"],
                "Payment Date": ["2023-12-15", "2023-12-20"],
                "Amount Paid": [8500, 12000],
                "Days Past Due": [0, 5]
            })
            historic_data.to_csv(temp_path / "historic_real_payment.csv", index=False)
            
            # Customer data
            customer_data = pd.DataFrame({
                CUSTOMER_ID: ["CUST001", "CUST002", "CUST003"],
                "Customer Name": ["ABC Manufacturing", "XYZ Services", "DEF Construction"],
                "Industry": ["Manufacturing", "Services", "Construction"],
                "Credit Score": [720, 680, 750]
            })
            customer_data.to_csv(temp_path / "customer_data.csv", index=False)
        
        def test_path_resolution_cli_argument(self, temp_data_dir):
            """Test path resolution when CLI argument is provided"""
            # Test sequence: U->>P: Run with --data-dir provided
            loader = DataLoader(base_path=temp_data_dir)
            
            assert loader.base_path == temp_data_dir
            
            # Verify data can be loaded
            loan_df = loader.load_loan_data()
            assert loan_df is not None
            assert len(loan_df) == 3
            assert CUSTOMER_ID in loan_df.columns
        
        @patch.dict(os.environ, {"COMMERCIAL_VIEW_DATA_PATH": "/test/env/path"})
        def test_path_resolution_environment_variable(self):
            """Test path resolution using environment variable"""
            # Test sequence: DL->>ENV: read COMMERCIAL_VIEW_DATA_PATH
            loader = DataLoader(base_path=None)
            
            assert str(loader.base_path) == "/test/env/path"
        
        @patch.dict(os.environ, {}, clear=True)
        def test_path_resolution_default_path(self):
            """Test path resolution falls back to default"""
            # Test sequence: DL->>DL: resolve DEFAULT_BASE_PATH if needed
            loader = DataLoader(base_path=None)
            
            assert loader.base_path == DataLoader.DEFAULT_BASE_PATH
            assert loader.base_path == Path("data")
        
        def test_load_loan_data_success(self, temp_data_dir):
            """Test successful loan data loading"""
            loader = DataLoader(base_path=temp_data_dir)
            
            # Test sequence: DL->>FS: open `loan_data.csv` -> FS-->>DL: CSV content -> DataFrame
            loan_df = loader.load_loan_data()
            
            assert loan_df is not None
            assert len(loan_df) == 3
            assert list(loan_df.columns) == [CUSTOMER_ID, "Loan Amount", "Interest Rate", "Status", "Origination Date"]
            assert loan_df.iloc[0][CUSTOMER_ID] == "CUST001"
        
        def test_load_loan_data_file_not_found(self, temp_data_dir):
            """Test loan data loading when file doesn't exist"""
            # Remove the loan data file
            (temp_data_dir / "loan_data.csv").unlink()
            
            loader = DataLoader(base_path=temp_data_dir)
            
            # Test sequence: DL->>FS: open `loan_data.csv` -> DL-->>P: raise FileNotFoundError
            with pytest.raises(FileNotFoundError) as exc_info:
                loader.load_loan_data()
            
            assert "Loan data file not found" in str(exc_info.value)
            assert "Production data source:" in str(exc_info.value)
        
        def test_load_payment_schedule_success(self, temp_data_dir):
            """Test successful payment schedule loading"""
            loader = DataLoader(base_path=temp_data_dir)
            
            payment_df = loader.load_payment_schedule()
            
            assert payment_df is not None
            assert len(payment_df) == 3
            assert CUSTOMER_ID in payment_df.columns
            assert "Due Date" in payment_df.columns
            assert "Total Payment" in payment_df.columns
        
        def test_load_historic_real_payment_success(self, temp_data_dir):
            """Test successful historic payment loading"""
            loader = DataLoader(base_path=temp_data_dir)
            
            historic_df = loader.load_historic_real_payment()
            
            assert historic_df is not None
            assert len(historic_df) == 2
            assert "Payment Date" in historic_df.columns
            assert "Amount Paid" in historic_df.columns
            assert "Days Past Due" in historic_df.columns
        
        def test_load_customer_data_success(self, temp_data_dir):
            """Test successful customer data loading"""
            loader = DataLoader(base_path=temp_data_dir)
            
            customer_df = loader.load_customer_data()
            
            assert customer_df is not None
            assert len(customer_df) == 3
            assert CUSTOMER_ID in customer_df.columns
            assert "Customer Name" in customer_df.columns
        
        def test_override_base_path_in_load_methods(self, temp_data_dir):
            """Test overriding base path in individual load methods"""
            # Initialize with default path
            loader = DataLoader()
            
            # Override path in load method (CLI --data-dir behavior)
            loan_df = loader.load_loan_data(base_path=temp_data_dir)
            
            assert loan_df is not None
            assert len(loan_df) == 3
        
        def test_data_validation_missing_columns(self, temp_data_dir):
            """Test data validation with missing required columns"""
            # Create invalid loan data
            invalid_data = pd.DataFrame({
                "Invalid Column": ["value1", "value2"]
            })
            invalid_data.to_csv(temp_data_dir / "loan_data.csv", index=False)
            
            loader = DataLoader(base_path=temp_data_dir)
            
            with pytest.raises(ValueError) as exc_info:
                loader.load_loan_data()
            
            assert "Missing required columns" in str(exc_info.value)
        
        def test_data_validation_empty_file(self, temp_data_dir):
            """Test data validation with empty CSV file"""
            # Create empty loan data
            empty_data = pd.DataFrame()
            empty_data.to_csv(temp_data_dir / "loan_data.csv", index=False)
            
            loader = DataLoader(base_path=temp_data_dir)
            
            with pytest.raises(ValueError) as exc_info:
                loader.load_loan_data()
            
            assert "file is empty" in str(exc_info.value)
        
        def test_get_data_status(self, temp_data_dir):
            """Test data status reporting"""
            loader = DataLoader(base_path=temp_data_dir)
            
            status = loader.get_data_status()
            
            assert status["data_source"] == "Production Google Drive"
            assert status["resolved_path"] == str(temp_data_dir.absolute())
            assert status["google_drive_url"] == loader.google_drive_url
            
            # Check dataset status
            assert "loan_data" in status["datasets"]
            assert status["datasets"]["loan_data"]["available"] is True
            assert status["datasets"]["loan_data"]["records"] == 3
        
        def test_sequence_diagram_complete_flow(self, temp_data_dir):
            """Test complete sequence diagram flow"""
            # Step 1: U->>P: Run with --data-dir provided
            # Step 2: P->>DL: load_*_data(base_path=CLI_path)
            loader = DataLoader(base_path=temp_data_dir)
            
            # Step 3: DL->>FS: open `<name>.csv`
            # Step 4: FS-->>DL: CSV content -> DataFrame  
            # Step 5: DL-->>P: return DataFrame
            loan_df = loader.load_loan_data()
            
            # Verify complete flow
            assert loan_df is not None
            assert len(loan_df) == 3
            assert loader.base_path == temp_data_dir
            
            # Test the alternative flow (file missing)
            (temp_data_dir / "payment_schedule.csv").unlink()
            
            # Should raise FileNotFoundError with guidance message
            with pytest.raises(FileNotFoundError) as exc_info:
                loader.load_payment_schedule()
            
            error_message = str(exc_info.value)
            assert "Payment schedule file not found" in error_message
            assert "Expected location:" in error_message
            assert "COMMERCIAL_VIEW_DATA_PATH" in error_message
            assert loader.google_drive_url in error_message

        @patch.dict(os.environ, {"COMMERCIAL_VIEW_DATA_PATH": ""}, clear=True)
        def test_environment_variable_priority(self, temp_data_dir):
            """Test that CLI argument takes priority over environment variable"""
            # Set environment variable to different path
            with patch.dict(os.environ, {"COMMERCIAL_VIEW_DATA_PATH": "/different/path"}):
                # CLI argument should take priority
                loader = DataLoader(base_path=temp_data_dir)
                
                assert loader.base_path == temp_data_dir
                # Should be able to load data from CLI path, not env path
                loan_df = loader.load_loan_data()
                assert loan_df is not None


"""Tests for data loader functionality."""

import pytest
from pathlib import Path
from src.data_loader import (
    load_loan_data,
    load_historic_real_payment,
    load_payment_schedule
)
# Import constants from abaco_schema
from src.abaco_schema import (
    DAYS_IN_DEFAULT_COLUMN,
    INTEREST_RATE_APR_COLUMN,
    OUTSTANDING_LOAN_VALUE_COLUMN,
    LOAN_CURRENCY_COLUMN,
    PRODUCT_TYPE_COLUMN,
    CUSTOMER_ID_COLUMN,
    LOAN_ID_COLUMN
)


class TestDataLoader:
    """Test data loading functionality."""
    
    def test_column_constants_defined(self):
        """Test that all column constants are defined."""
        assert DAYS_IN_DEFAULT_COLUMN == "Days in Default"
        assert INTEREST_RATE_APR_COLUMN == "Interest Rate APR"
        assert OUTSTANDING_LOAN_VALUE_COLUMN == "Outstanding Loan Value"
        assert LOAN_CURRENCY_COLUMN == "Loan Currency"
        assert PRODUCT_TYPE_COLUMN == "Product Type"
    
    def test_load_functions_exist(self):
        """Test that load functions are callable."""
        assert callable(load_loan_data)
        assert callable(load_historic_real_payment)
        assert callable(load_payment_schedule)
