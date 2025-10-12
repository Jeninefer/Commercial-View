"""
Create complete Abaco sample data matching your exact 48,853 record schema
This generates all three required files based on your JSON schema structure
"""

import pandas as pd
import numpy as np
rng = np.random.default_rng(seed=42)  # Modern NumPy random generator
from pathlib import Path
from datetime import datetime, timedelta
import json

def create_complete_abaco_sample():
    """Create all three Abaco data files matching the exact schema."""
    
    print("🏦 Creating Complete Abaco Sample Data")
    print("=" * 50)
    print("📊 Based on your exact 48,853 record schema structure")
    
    # Load schema
    schema_path = Path.home() / 'Downloads' / 'abaco_schema_autodetected.json'
    with open(schema_path, 'r') as f:
        schema = json.load(f)
    
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    
    # Create Loan Data (16,205 records, 28 columns)
    create_loan_data_sample(schema['datasets']['Loan Data'], data_dir)
    
    # Create Historic Real Payment (16,443 records, 18 columns)  
    create_payment_history_sample(schema['datasets']['Historic Real Payment'], data_dir)
    
    # Create Payment Schedule (16,205 records, 16 columns)
    create_payment_schedule_sample(schema['datasets']['Payment Schedule'], data_dir)
    
    print("\n✅ Complete Abaco sample data created!")
    print(f"📁 Files saved in: {data_dir}")

def create_loan_data_sample(loan_schema, data_dir):
    """Create loan data sample matching exact schema."""
    print("\n📊 Creating Loan Data Sample...")
    
    sample_size = 100
    columns = {col['name']: col for col in loan_schema['columns']}
    
    # Create data matching your exact schema structure
    loan_data = {}
    
    for col_name, col_info in columns.items():
        if col_info.get('non_null', 0) > 0:
            # Non-null columns with real data
            if col_name == 'Company':
                loan_data[col_name] = rng.choice(['Abaco Technologies', 'Abaco Financial'], sample_size)
            elif col_name == 'Customer ID':
                loan_data[col_name] = [f'CLIAB{str(i).zfill(6)}' for i in range(198, 198 + sample_size)]
            elif col_name == 'Cliente':
                loan_data[col_name] = create_spanish_clients(sample_size)
            elif col_name == 'Pagador':
                loan_data[col_name] = create_spanish_payers(sample_size)
            elif col_name in ['Application ID', 'Loan ID']:
                loan_data[col_name] = [f'DSB{1700+i}-{str(j+1).zfill(3)}' for i, j in enumerate(range(sample_size))]
            elif col_name == 'Product Type':
                loan_data[col_name] = ['factoring'] * sample_size
            elif col_name == 'Disbursement Date':
                loan_data[col_name] = [(datetime(2025, 9, 30) - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(sample_size)]
            elif col_name in ['TPV', 'Outstanding Loan Value']:
                loan_data[col_name] = rng.uniform(88.48, 77175.0, sample_size).round(2)
            elif col_name == 'Disbursement Amount':
                loan_data[col_name] = rng.uniform(87.47, 74340.75, sample_size).round(2)
            elif col_name == 'Origination Fee':
                loan_data[col_name] = rng.uniform(0.89, 2508.19, sample_size).round(2)
            elif col_name == 'Origination Fee Taxes':
                loan_data[col_name] = rng.uniform(0.12, 326.06, sample_size).round(2)
            elif col_name == 'Loan Currency':
                loan_data[col_name] = ['USD'] * sample_size
            elif col_name == 'Interest Rate APR':
                loan_data[col_name] = rng.uniform(0.2947, 0.3699, sample_size).round(4)
            elif col_name == 'Term':
                loan_data[col_name] = rng.choice([30, 90, 120], sample_size)
            elif col_name == 'Term Unit':
                loan_data[col_name] = ['days'] * sample_size
            elif col_name == 'Payment Frequency':
                loan_data[col_name] = ['bullet'] * sample_size
            elif col_name == 'Days in Default':
                loan_data[col_name] = rng.choice([0, 1, 3], sample_size)
            elif col_name == 'Loan Status':
                loan_data[col_name] = rng.choice(['Current', 'Complete', 'Default'], sample_size, p=[0.7, 0.25, 0.05])
            else:
                # Default numeric values for other columns
                loan_data[col_name] = rng.uniform(100, 1000, sample_size).round(2)
        else:
            # Null columns (Pledge To, Other, etc.)
            loan_data[col_name] = [None] * sample_size
    
    # Save loan data
    df = pd.DataFrame(loan_data)
    output_file = data_dir / 'Abaco - Loan Tape_Loan Data_Table.csv'
    df.to_csv(output_file, index=False)
    
    print(f"✅ Loan Data: {len(df)} records, {len(df.columns)} columns")
    print(f"   📁 Saved: {output_file}")

def create_payment_history_sample(payment_schema, data_dir):
    """Create payment history sample matching exact schema."""
    print("\n💰 Creating Payment History Sample...")
    
    sample_size = 110  # Slightly more than loan data (16,443 vs 16,205 in real data)
    columns = {col['name']: col for col in payment_schema['columns']}
    
    payment_data = {}
    
    for col_name, col_info in columns.items():
        if col_info.get('non_null', 0) > 0:
            if col_name == 'Company':
                payment_data[col_name] = rng.choice(['Abaco Financial', 'Abaco Technologies'], sample_size)
            elif col_name == 'Customer ID':
                # Mix of CLIAB and CLI formats as in real data
                cli_ids = [f'CLI{2000+i}' for i in range(sample_size//4)]
                cliab_ids = [f'CLIAB{str(i).zfill(6)}' for i in range(223, 223 + sample_size - sample_size//4)]
                payment_data[col_name] = cli_ids + cliab_ids
            elif col_name == 'Cliente':
                payment_data[col_name] = create_payment_clients(sample_size)
            elif col_name == 'Pagador':
                payment_data[col_name] = create_payment_payers(sample_size)
            elif col_name == 'Loan ID':
                payment_data[col_name] = [f'DSB{np.random.randint(1000, 4000)}-{str(j+1).zfill(3)}' for j in range(sample_size)]
            elif col_name == 'True Payment Date':
                payment_data[col_name] = [(datetime(2025, 9, 30) - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(sample_size)]
            elif col_name == 'True Devolution':
                payment_data[col_name] = rng.choice([0.0, 658.45, 0.01], sample_size)
            elif col_name == 'True Total Payment':
                payment_data[col_name] = rng.uniform(461.33, 62115.89, sample_size).round(2)
            elif col_name == 'True Payment Currency':
                payment_data[col_name] = ['USD'] * sample_size
            elif col_name == 'True Principal Payment':
                payment_data[col_name] = rng.uniform(448.04, 60270.32, sample_size).round(2)
            elif col_name == 'True Interest Payment':
                payment_data[col_name] = rng.uniform(7.69, 94.48, sample_size).round(2)
            elif col_name == 'True Fee Payment':
                payment_data[col_name] = rng.uniform(4.07, 1550.56, sample_size).round(2)
            elif col_name == 'True Tax Payment':
                payment_data[col_name] = rng.uniform(1.0, 12.28, sample_size).round(2)
            elif col_name == 'True Fee Tax Payment':
                payment_data[col_name] = rng.uniform(0.53, 201.57, sample_size).round(2)
            elif col_name == 'True Rabates':
                payment_data[col_name] = [0] * sample_size
            elif col_name == 'True Outstanding Loan Value':
                payment_data[col_name] = rng.uniform(0.0, 8054.78, sample_size).round(2)
            elif col_name == 'True Payment Status':
                payment_data[col_name] = rng.choice(['Late', 'On Time', 'Prepayment'], sample_size, p=[0.3, 0.6, 0.1])
        else:
            # Null columns (True Other Payment)
            payment_data[col_name] = [None] * sample_size
    
    # Save payment history
    df = pd.DataFrame(payment_data)
    output_file = data_dir / 'Abaco - Loan Tape_Historic Real Payment_Table.csv'
    df.to_csv(output_file, index=False)
    
    print(f"✅ Payment History: {len(df)} records, {len(df.columns)} columns")
    print(f"   📁 Saved: {output_file}")

def create_payment_schedule_sample(schedule_schema, data_dir):
    """Create payment schedule sample matching exact schema."""
    print("\n📅 Creating Payment Schedule Sample...")
    
    sample_size = 100  # Same as loan data (16,205 in real data)
    columns = {col['name']: col for col in schedule_schema['columns']}
    
    schedule_data = {}
    
    for col_name, col_info in columns.items():
        if col_info.get('non_null', 0) > 0:
            if col_name == 'Company':
                schedule_data[col_name] = rng.choice(['Abaco Technologies', 'Abaco Financial'], sample_size)
            elif col_name == 'Customer ID':
                schedule_data[col_name] = [f'CLIAB{str(i).zfill(6)}' for i in range(78, 78 + sample_size)]
            elif col_name == 'Cliente':
                schedule_data[col_name] = create_schedule_clients(sample_size)
            elif col_name == 'Pagador':
                schedule_data[col_name] = create_schedule_payers(sample_size)
            elif col_name == 'Loan ID':
                schedule_data[col_name] = [f'DSB{np.random.randint(600, 2000)}-{str(j+1).zfill(3)}' for j in range(sample_size)]
            elif col_name == 'Payment Date':
                # Future dates for schedules
                schedule_data[col_name] = [(datetime(2025, 10, 2) + timedelta(days=i*30)).strftime('%Y-%m-%d') for i in range(sample_size)]
            elif col_name == 'TPV':
                schedule_data[col_name] = rng.uniform(1731.5, 21784.0, sample_size).round(2)
            elif col_name == 'Total Payment':
                schedule_data[col_name] = rng.uniform(1558.35, 21889.957376, sample_size).round(6)
            elif col_name == 'Currency':
                schedule_data[col_name] = ['USD'] * sample_size
            elif col_name == 'Principal Payment':
                schedule_data[col_name] = rng.uniform(1524.28, 18857.61, sample_size).round(2)
            elif col_name == 'Interest Payment':
                schedule_data[col_name] = rng.uniform(0.0, 2021.5552, sample_size).round(4)
            elif col_name == 'Fee Payment':
                schedule_data[col_name] = rng.uniform(17.55, 661.94, sample_size).round(2)
            elif col_name == 'Tax Payment':
                schedule_data[col_name] = rng.uniform(3.9195, 348.854376, sample_size).round(6)
            elif col_name == 'Outstanding Loan Value':
                schedule_data[col_name] = [0] * sample_size  # All paid off as per schema
        else:
            # Null columns (Other Payment, All Rebates)
            schedule_data[col_name] = [None] * sample_size
    
    # Save payment schedule
    df = pd.DataFrame(schedule_data)
    output_file = data_dir / 'Abaco - Loan Tape_Payment Schedule_Table.csv'
    df.to_csv(output_file, index=False)
    
    print(f"✅ Payment Schedule: {len(df)} records, {len(df.columns)} columns")
    print(f"   📁 Saved: {output_file}")

def create_spanish_clients(count):
    """Create Spanish client names matching loan data schema."""
    companies = [
        'SERVICIOS TECNICOS MEDICOS, S.A. DE C.V.',
        'PRODUCTOS DE CONCRETO, S.A. DE C.V.',
        'TRANSPORTES MODERNOS, S.A. DE C.V.'
    ]
    individuals = ['KEVIN ENRIQUE CABEZAS MORALES']
    
    result = []
    for i in range(count):
        if rng.random() > 0.2:  # 80% companies
            company = rng.choice(companies)
            result.append(company.replace('MEDICOS', f'MEDICOS {i+1}'))
        else:
            result.append(f'KEVIN ENRIQUE CLIENTE {i+1:03d} MORALES')
    return result

def create_spanish_payers(count):
    """Create Spanish payer names matching loan data schema."""
    payers = [
        'HOSPITAL NACIONAL "SAN JUAN DE DIOS" SAN MIGUEL',
        'ASSA COMPAÑIA DE SEGUROS, S.A.',
        'EMPRESA TRANSMISORA DE EL SALVADOR, S.A. DE C.V. ETESAL, S.A. DE C.V.'
    ]
    
    result = []
    for i in range(count):
        payer = rng.choice(payers)
        result.append(payer.replace('NACIONAL', f'NACIONAL {i+1:03d}'))
    return result

def create_payment_clients(count):
    """Create client names for payment history."""
    clients = [
        'RAFAEL ALEXANDER AGUILAR AGUILAR',
        'SUPER MARINO, S.A. DE C.V.',
        'PRODUCTOS DE CONCRETO, S.A. DE C.V.'
    ]
    
    result = []
    for i in range(count):
        client = rng.choice(clients)
        result.append(client.replace('RAFAEL', f'CLIENTE {i+1:03d}'))
    return result

def create_payment_payers(count):
    """Create payer names for payment history."""
    payers = [
        'ALUMA SYSTEMS EL SALVADOR SA DE CV',
        'OPERADORA Y PROCESADORA DE PRODUCTOS MARINOS S.A.',
        'CTE TELECOM SA DE CV'
    ]
    
    result = []
    for i in range(count):
        payer = rng.choice(payers)
        result.append(payer.replace('ALUMA', f'PAGADOR {i+1:03d}'))
    return result

def create_schedule_clients(count):
    """Create client names for payment schedule."""
    clients = [
        'MYRNA DEL CARMEN GARCIA DE ARAUJO',
        'TRES DE TRES TRANSPORTES, S.A. DE C.V.',
        'ARTISTA LIVE, S.A. DE C.V.'
    ]
    
    result = []
    for i in range(count):
        client = rng.choice(clients)
        result.append(client.replace('MYRNA', f'SCHEDULE {i+1:03d}'))
    return result

def create_schedule_payers(count):
    """Create payer names for payment schedule."""
    payers = [
        'OSCAR ANTONIO ISLEÑO LOVO',
        'ADQUISICIONES EXTERNAS, S.A. DE C.V.',
        'CASA BETYKAS, S.A. DE C.V.'
    ]
    
    result = []
    for i in range(count):
        payer = rng.choice(payers)
        result.append(payer.replace('OSCAR', f'PAYER {i+1:03d}'))
    return result

if __name__ == '__main__':
    create_complete_abaco_sample()
    
    print("\n🎉 SUCCESS!")
    print("✅ All three Abaco data files created")
    print("🎯 Ready to test complete integration")
    print("\nNext steps:")
    print("1. Run: python scripts/complete_integration_test.py")
    print("2. Test: python portfolio.py --config config")
