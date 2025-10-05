from dotenv import load_dotenv
load_dotenv()

import os
from pathlib import Path
from typing import List, Dict, Any

from fastapi import FastAPI, HTTPException
from src.data_loader import (
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


data_root = os.getenv("COMMERCIAL_VIEW_DATA_PATH")
if data_root:
    DATA_BASE_PATH = Path(data_root).expanduser().resolve()
else:
    DATA_BASE_PATH = Path(__file__).resolve().parent / "data" / "pricing"

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
        df = load_loan_data(DATA_BASE_PATH)
        return df.to_dict(orient="records")
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Loan data file not found. Please upload the CSV file to the directory: {DATA_BASE_PATH}"
        )

@app.get("/historic-real-payment", response_model=List[HistoricRealPayment])
def get_historic_real_payment():
    try:
        df = load_historic_real_payment(DATA_BASE_PATH)
        return df.to_dict(orient="records")
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/payment-schedule", response_model=List[PaymentSchedule])
def get_payment_schedule():
    try:
        df = load_payment_schedule(DATA_BASE_PATH)
        return df.to_dict(orient="records")
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Payment schedule data file not found. Please upload the CSV file to the directory: {DATA_BASE_PATH}"
        )

@app.get("/customer-data", response_model=List[CustomerData])
def get_customer_data():
    try:
        df = load_customer_data(DATA_BASE_PATH)
        return df.to_dict(orient="records")
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Customer data file not found. Please upload the CSV file to the directory: {DATA_BASE_PATH}"
        )

@app.get("/collateral", response_model=List[Collateral])
def get_collateral():
    try:
        df = load_collateral(DATA_BASE_PATH)
        return df.to_dict(orient="records")
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Collateral data file not found. Please upload the CSV file to the directory configured by the COMMERCIAL_VIEW_DATA_PATH environment variable or the default data/pricing directory."
        )

# Figma endpoint
@app.get("/figma-file/{file_key}", response_model=Dict[str, Any])
def get_figma_file_endpoint(file_key: str):
    try:
        return get_figma_file(file_key)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))