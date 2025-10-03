"""
Test ingestion module.
"""

import pytest
import pandas as pd
from ingestion import load_sample_data, CSVDataReader
from pathlib import Path


def test_load_sample_data():
    """Test loading sample data."""
    data = load_sample_data()
    
    assert isinstance(data, dict)
    assert 'loan_tape' in data
    assert 'disbursement_requests' in data
    assert 'clients' in data
    
    # Check loan tape
    loan_tape = data['loan_tape']
    assert isinstance(loan_tape, pd.DataFrame)
    assert len(loan_tape) > 0
    assert 'loan_id' in loan_tape.columns
    assert 'principal' in loan_tape.columns
    assert 'apr' in loan_tape.columns
    
    # Check disbursement requests
    requests = data['disbursement_requests']
    assert isinstance(requests, pd.DataFrame)
    assert len(requests) > 0
    assert 'request_id' in requests.columns
    assert 'requested_amount' in requests.columns
    
    # Check clients
    clients = data['clients']
    assert isinstance(clients, pd.DataFrame)
    assert len(clients) > 0
    assert 'client_id' in clients.columns
    assert 'client_name' in clients.columns


def test_csv_reader():
    """Test CSV reader initialization."""
    data_dir = Path('/tmp/test_data')
    reader = CSVDataReader(data_dir)
    
    assert reader.data_dir == data_dir
    
    # Test list files (even if directory doesn't exist)
    files = reader.list_available_files()
    assert isinstance(files, list)
