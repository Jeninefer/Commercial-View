"""
CSV data reader for local fallback and testing.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Any


class CSVDataReader:
    """Reader for CSV data files."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        
    def read_csv(self, filename: str) -> pd.DataFrame:
        """
        Read a CSV file and return as pandas DataFrame.
        
        Args:
            filename: Name of the CSV file
            
        Returns:
            pandas DataFrame
        """
        file_path = self.data_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")
        
        return pd.read_csv(file_path)
    
    def read_loan_tape(self, filename: str = "loan_tape.csv") -> pd.DataFrame:
        """
        Read loan tape data with specific parsing.
        """
        df = self.read_csv(filename)
        
        # Parse date columns if present
        date_columns = ['disbursement_date', 'maturity_date', 'last_payment_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        return df
    
    def read_disbursement_requests(self, filename: str = "disbursement_requests.csv") -> pd.DataFrame:
        """
        Read pending disbursement requests.
        """
        df = self.read_csv(filename)
        
        # Parse request date if present
        if 'request_date' in df.columns:
            df['request_date'] = pd.to_datetime(df['request_date'], errors='coerce')
        
        return df
    
    def read_client_data(self, filename: str = "clients.csv") -> pd.DataFrame:
        """
        Read client master data.
        """
        return self.read_csv(filename)
    
    def list_available_files(self) -> List[str]:
        """
        List all CSV files in the data directory.
        """
        if not self.data_dir.exists():
            return []
        
        return [f.name for f in self.data_dir.glob("*.csv")]


def load_sample_data() -> Dict[str, pd.DataFrame]:
    """
    Always creates and returns mock (synthetic) data for testing and development.
    This function does not load data from files.
    """
    import numpy as np
    from datetime import datetime, timedelta
    
    # Create sample loan tape
    n_loans = 100
    loan_tape = pd.DataFrame({
        'loan_id': [f'L{i:05d}' for i in range(1, n_loans + 1)],
        'client_id': [f'C{np.random.randint(1, 31):03d}' for _ in range(n_loans)],
        'client_name': [f'Client {np.random.randint(1, 31)}' for _ in range(n_loans)],
        'principal': np.random.uniform(10000, 500000, n_loans),
        'apr': np.random.uniform(0.08, 0.25, n_loans),
        'term_days': np.random.choice([30, 60, 90, 120, 180], n_loans),
        'disbursement_date': [datetime.now() - timedelta(days=np.random.randint(1, 180)) for _ in range(n_loans)],
        'status': np.random.choice(['active', 'paid', 'overdue'], n_loans, p=[0.6, 0.3, 0.1]),
        'dpd': np.random.randint(0, 60, n_loans),
        'sector': np.random.choice(['Retail', 'Manufacturing', 'Services', 'Technology', 'Agriculture'], n_loans),
    })
    
    # Create sample disbursement requests
    n_requests = 50
    disbursement_requests = pd.DataFrame({
        'request_id': [f'R{i:05d}' for i in range(1, n_requests + 1)],
        'client_id': [f'C{np.random.randint(1, 31):03d}' for _ in range(n_requests)],
        'client_name': [f'Client {np.random.randint(1, 31)}' for _ in range(n_requests)],
        'requested_amount': np.random.uniform(10000, 500000, n_requests),
        'proposed_apr': np.random.uniform(0.08, 0.25, n_requests),
        'proposed_term': np.random.choice([30, 60, 90, 120, 180], n_requests),
        'request_date': [datetime.now() - timedelta(days=np.random.randint(0, 7)) for _ in range(n_requests)],
        'sector': np.random.choice(['Retail', 'Manufacturing', 'Services', 'Technology', 'Agriculture'], n_requests),
        'credit_score': np.random.uniform(500, 850, n_requests),
    })
    
    # Create sample client data
    n_clients = 30
    clients = pd.DataFrame({
        'client_id': [f'C{i:03d}' for i in range(1, n_clients + 1)],
        'client_name': [f'Client {i}' for i in range(1, n_clients + 1)],
        'sector': np.random.choice(['Retail', 'Manufacturing', 'Services', 'Technology', 'Agriculture'], n_clients),
        'credit_line': np.random.uniform(50000, 2000000, n_clients),
        'kam': np.random.choice(['KAM1', 'KAM2', 'KAM3', 'KAM4'], n_clients),
        'risk_rating': np.random.choice(['A', 'B', 'C'], n_clients, p=[0.3, 0.5, 0.2]),
    })
    
    return {
        'loan_tape': loan_tape,
        'disbursement_requests': disbursement_requests,
        'clients': clients,
    }
