
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

"""
Create sample Abaco data for testing when real files aren't available
"""

import pandas as pd
import numpy as np
rng = np.random.default_rng(seed=42)  # Modern NumPy random generator
from pathlib import Path
from datetime import datetime, timedelta
import random

def create_sample_loan_data(n_loans=100):
    """Create sample loan data matching Abaco schema."""
    
    companies = [ABACO_TECHNOLOGIES, ABACO_FINANCIAL]
    product_types = ["factoring"]
    currencies = ["USD"]
    loan_statuses = ["Current", "Complete", "Default"]
    
    np.random.seed(42)  # For reproducible results
    
    data = []
    
    for i in range(n_loans):
        customer_id = f"CLIAB{str(i+1000).zfill(6)}"
        loan_id = f"DSB{random.randint(1000,9999)}-{str(random.randint(1,999)).zfill(3)}"
        
        # Random financial amounts
        tpv = rng.uniform(1000, 100000)
        disbursement_amount = tpv * rng.uniform(0.8, 0.95)  # 80-95% advance rate
        
        loan = {
            "Company": rng.choice(companies),
            CUSTOMER_ID: customer_id,
            "Cliente": f"EMPRESA EJEMPLO {i+1}, S.A. DE C.V.",
            "Pagador": f"PAGADOR EJEMPLO {i+1}, S.A. DE C.V.",
            "Application ID": loan_id,
            LOAN_ID: loan_id,
            PRODUCT_TYPE: "factoring",
            DISBURSEMENT_DATE: (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d"),
            "TPV": round(tpv, 2),
            DISBURSEMENT_AMOUNT: round(disbursement_amount, 2),
            "Origination Fee": round(disbursement_amount * 0.03, 2),
            "Origination Fee Taxes": round(disbursement_amount * 0.03 * 0.13, 2),
            LOAN_CURRENCY: "USD",
            INTEREST_RATE_APR: round(rng.uniform(0.15, 0.40), 4),
            "Term": rng.choice([30, 60, 90, 120, 180]),
            "Term Unit": "days",
            PAYMENT_FREQUENCY: "bullet",
            DAYS_IN_DEFAULT: rng.choice([0, 0, 0, 1, 3, 5, 10, 15, 30, 60, 90, 120], p=[0.6, 0.15, 0.1, 0.05, 0.03, 0.02, 0.02, 0.01, 0.01, 0.005, 0.003, 0.002]),
            LOAN_STATUS: rng.choice(loan_statuses, p=[0.7, 0.25, 0.05]),
            OUTSTANDING_LOAN_VALUE: round(tpv * rng.uniform(0, 1), 2),
            # Null columns from schema
            "Pledge To": None,
            "Pledge Date": None,
            "Other": None,
            "New Loan ID": None,
            "New Loan Date": None,
            "Old Loan ID": None,
            "Recovery Date": None,
            "Recovery Value": None
        }
        
        data.append(loan)
    
    return pd.DataFrame(data)

def create_sample_payment_history(loan_df, avg_payments_per_loan=2):
    """Create sample payment history based on loan data."""
    
    payment_data = []
    payment_statuses = ["On Time", "Late", "Prepayment"]
    
    for _, loan in loan_df.iterrows():
        n_payments = np.random.poisson(avg_payments_per_loan)
        n_payments = max(1, n_payments)  # At least 1 payment
        
        for p in range(n_payments):
            payment_date = datetime.strptime(loan[DISBURSEMENT_DATE], "%Y-%m-%d") + timedelta(days=random.randint(1, 180))
            
            total_payment = loan["TPV"] / n_payments * rng.uniform(0.8, 1.2)
            principal_payment = total_payment * rng.uniform(0.85, 0.95)
            interest_payment = total_payment * rng.uniform(0.05, 0.10)
            fee_payment = total_payment * rng.uniform(0.02, 0.05)
            
            payment = {
                "Company": loan["Company"],
                CUSTOMER_ID: loan[CUSTOMER_ID], 
                "Cliente": loan["Cliente"],
                "Pagador": loan["Pagador"],
                LOAN_ID: loan[LOAN_ID],
                TRUE_PAYMENT_DATE: payment_date.strftime("%Y-%m-%d"),
                "True Devolution": round(rng.uniform(0, 100), 2),
                "True Total Payment": round(total_payment, 2),
                "True Payment Currency": "USD",
                "True Principal Payment": round(principal_payment, 2),
                "True Interest Payment": round(interest_payment, 2),
                "True Fee Payment": round(fee_payment, 2),
                "True Other Payment": None,
                "True Tax Payment": round(total_payment * 0.01, 2),
                "True Fee Tax Payment": round(fee_payment * 0.13, 2),
                "True Rabates": 0,
                "True Outstanding Loan Value": round(loan[OUTSTANDING_LOAN_VALUE] * rng.uniform(0, 0.5), 2),
                TRUE_PAYMENT_STATUS: rng.choice(payment_statuses, p=[0.8, 0.15, 0.05])
            }
            
            payment_data.append(payment)
    
    return pd.DataFrame(payment_data)

def create_sample_payment_schedule(loan_df):
    """Create sample payment schedule based on loan data."""
    
    schedule_data = []
    
    for _, loan in loan_df.iterrows():
        payment_date = datetime.strptime(loan[DISBURSEMENT_DATE], "%Y-%m-%d") + timedelta(days=loan["Term"])
        
        total_payment = loan["TPV"] * 1.1  # Add some interest
        principal_payment = loan["TPV"]
        interest_payment = total_payment - principal_payment
        
        schedule = {
            "Company": loan["Company"],
            CUSTOMER_ID: loan[CUSTOMER_ID],
            "Cliente": loan["Cliente"], 
            "Pagador": loan["Pagador"],
            LOAN_ID: loan[LOAN_ID],
            "Payment Date": payment_date.strftime("%Y-%m-%d"),
            "TPV": loan["TPV"],
            "Total Payment": round(total_payment, 2),
            "Currency": "USD",
            "Principal Payment": round(principal_payment, 2),
            "Interest Payment": round(interest_payment, 2),
            "Fee Payment": round(total_payment * 0.03, 2),
            "Other Payment": None,
            "Tax Payment": round(total_payment * 0.01, 2),
            "All Rebates": None,
            OUTSTANDING_LOAN_VALUE: 0  # Paid off
        }
        
        schedule_data.append(schedule)
    
    return pd.DataFrame(schedule_data)

def create_sample_abaco_files():
    """Create all sample Abaco files."""
    
    print("🏭 Creating Sample Abaco Data Files")
    print("=" * 50)
    
    # Ensure data directory exists
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    print("📊 Generating loan data...")
    loan_df = create_sample_loan_data(500)  # 500 sample loans
    
    print("💰 Generating payment history...")
    payment_df = create_sample_payment_history(loan_df)
    
    print("📅 Generating payment schedule...")
    schedule_df = create_sample_payment_schedule(loan_df)
    
    # Save files
    files = {
        "Abaco - Loan Tape_Loan Data_Table.csv": loan_df,
        "Abaco - Loan Tape_Historic Real Payment_Table.csv": payment_df,
        "Abaco - Loan Tape_Payment Schedule_Table.csv": schedule_df
    }
    
    for filename, df in files.items():
        filepath = data_dir / filename
        df.to_csv(filepath, index=False)
        
        file_size = filepath.stat().st_size / 1024  # KB
        print(f"✅ Created {filename}: {len(df):,} rows, {file_size:.1f} KB")
    
    print("\n📈 Summary:")
    print(f"   • Loan records: {len(loan_df):,}")
    print(f"   • Payment records: {len(payment_df):,}")
    print(f"   • Schedule records: {len(schedule_df):,}")
    print(f"   • Total records: {len(loan_df) + len(payment_df) + len(schedule_df):,}")
    
    print("\n🎯 Sample data created successfully!")
    print(f"📁 Files location: {data_dir.absolute()}")
    
    return True

if __name__ == '__main__':
    create_sample_abaco_files()
