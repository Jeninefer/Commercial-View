import csv
from typing import List
from src.models import LoanData, HistoricRealPayment, PaymentSchedule, CustomerData, Collateral

DATA_PATH = '/Users/jenineferderas/Documents/GitHub/Commercial-View/data/pricing/'

def load_loan_data() -> List[LoanData]:
    file_path = f'{DATA_PATH}Abaco - Loan Tape_Loan Data_Table.csv'
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        return [LoanData(**row) for row in reader]

def load_historic_real_payment() -> List[HistoricRealPayment]:
    file_path = f'{DATA_PATH}Abaco - Loan Tape_Historic Real Payment_Table.csv'
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        return [HistoricRealPayment(**row) for row in reader]

def load_payment_schedule() -> List[PaymentSchedule]:
    file_path = f'{DATA_PATH}Abaco - Loan Tape_Payment Schedule_Table.csv'
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        return [PaymentSchedule(**row) for row in reader]

def load_customer_data() -> List[CustomerData]:
    file_path = f'{DATA_PATH}Abaco - Loan Tape_Customer Data_Table.csv'
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        return [CustomerData(**row) for row in reader]

def load_collateral() -> List[Collateral]:
    file_path = f'{DATA_PATH}Abaco - Loan Tape_Collateral_Table.csv'
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        return [Collateral(**row) for row in reader]