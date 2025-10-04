import os

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any
from src.data_loader import (
    dataframe_to_models,
    load_loan_data,
    load_historic_real_payment,
    load_payment_schedule,
    load_customer_data,
    load_collateral
)
from src.models import (
    LoanData, 
    HistoricRealPayment, 
    PaymentSchedule,
    CustomerData,
    Collateral
)
from src.figma_client import get_figma_file

PRICING_BASE_PATH = os.getenv("COMMERCIAL_VIEW_PRICING_PATH")

app = FastAPI(
    title="Commercial View API",
    description="API for the Commercial View dashboard, providing access to loan and payment data and Figma designs.",
    version="0.3.1",
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Commercial View API"}

# Data endpoints
@app.get("/loan-data", response_model=List[LoanData])
def get_loan_data():
    try:
        dataframe = load_loan_data(PRICING_BASE_PATH)
        return dataframe_to_models(dataframe, LoanData)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Loan data file not found. Please upload the CSV file to the data/pricing directory.")

@app.get("/historic-real-payment", response_model=List[HistoricRealPayment])
def get_historic_real_payment():
    try:
        dataframe = load_historic_real_payment(PRICING_BASE_PATH)
        return dataframe_to_models(dataframe, HistoricRealPayment)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Historic real payment data file not found. Please upload the CSV file to the data/pricing directory.")

@app.get("/payment-schedule", response_model=List[PaymentSchedule])
def get_payment_schedule():
    try:
        dataframe = load_payment_schedule(PRICING_BASE_PATH)
        return dataframe_to_models(dataframe, PaymentSchedule)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Payment schedule data file not found. Please upload the CSV file to the data/pricing directory.")

@app.get("/customer-data", response_model=List[CustomerData])
def get_customer_data():
    try:
        dataframe = load_customer_data(PRICING_BASE_PATH)
        return dataframe_to_models(dataframe, CustomerData)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Customer data file not found. Please upload the CSV file to the data/pricing directory.")

@app.get("/collateral", response_model=List[Collateral])
def get_collateral():
    try:
        dataframe = load_collateral(PRICING_BASE_PATH)
        return dataframe_to_models(dataframe, Collateral)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Collateral data file not found. Please upload the CSV file to the data/pricing directory.")

# Figma endpoint
@app.get("/figma-file/{file_key}", response_model=Dict[str, Any])
def get_figma_file_endpoint(file_key: str):
    try:
        return get_figma_file(file_key)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))