#!/usr/bin/env python3
"""Add DataLoader class to data_loader.py"""

# Read the current file
with open('src/data_loader.py', 'r') as f:
    content = f.read()

# Check if DataLoader class already exists
if 'class DataLoader' in content:
    print("✅ DataLoader class already exists")
    exit(0)

# Add the DataLoader class
additional_code = '''

class DataLoader:
    """DataLoader class wrapper for Abaco data loading functions."""
    
    def __init__(self, schema_path=None):
        self.schema_path = schema_path
        self.records_loaded = 0
        
    def load_abaco_dataset(self, records=48853, base_path=None):
        """Load Abaco dataset."""
        from pathlib import Path
        df = load_loan_data(base_path)
        self.records_loaded = len(df)
        return df
    
    def load_abaco_data(self, base_path=None):
        """Load all Abaco data tables."""
        return {
            'loan_data': load_loan_data(base_path),
            'payment_history': load_historic_real_payment(base_path),
            'payment_schedule': load_payment_schedule(base_path)
        }
    
    def get_processing_stats(self):
        """Get processing statistics."""
        return {'records_loaded': self.records_loaded}

__all__ = ['DataLoader', 'load_loan_data', 'load_historic_real_payment', 
           'load_payment_schedule', 'load_customer_data', 'load_collateral',
           'load_abaco_schema', 'validate_portfolio_data']
'''

# Write the updated file
with open('src/data_loader.py', 'w') as f:
    f.write(content + additional_code)

print("✅ DataLoader class added successfully!")
