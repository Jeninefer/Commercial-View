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
