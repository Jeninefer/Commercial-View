import pandas as pd
from pandas import DataFrame

DATA_PATH = '/Users/jenineferderas/Documents/GitHub/Commercial-View/data/pricing/'

def load_loan_data() -> DataFrame:
    file_path = f'{DATA_PATH}Abaco - Loan Tape_Loan Data_Table.csv'
    return pd.read_csv(file_path)

def load_historic_real_payment() -> DataFrame:
    file_path = f'{DATA_PATH}Abaco - Loan Tape_Historic Real Payment_Table.csv'
    return pd.read_csv(file_path)

def load_payment_schedule() -> DataFrame:
    file_path = f'{DATA_PATH}Abaco - Loan Tape_Payment Schedule_Table.csv'
    return pd.read_csv(file_path)

def load_customer_data() -> DataFrame:
    file_path = f'{DATA_PATH}Abaco - Loan Tape_Customer Data_Table.csv'
    return pd.read_csv(file_path)

def load_collateral() -> DataFrame:
    file_path = f'{DATA_PATH}Abaco - Loan Tape_Collateral_Table.csv'
    return pd.read_csv(file_path)