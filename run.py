from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from typing import List, Dict, Any
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
from src.serializers import dataframe_to_models

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
        loan_df = load_loan_data()
        return dataframe_to_models(loan_df, LoanData)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Loan data file not found. Please upload the CSV file to the data/pricing directory.")
    except ValidationError as exc:
        raise HTTPException(status_code=500, detail=f"Failed to serialize loan data: {exc}")

@app.get("/historic-real-payment", response_model=List[HistoricRealPayment])
def get_historic_real_payment():
    try:
        historic_df = load_historic_real_payment()
        return dataframe_to_models(historic_df, HistoricRealPayment)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"Historic real payment data file not found at '{exc.filename}'. Please upload the CSV file to the configured data directory.")
    except ValidationError as exc:
        raise HTTPException(status_code=500, detail=f"Failed to serialize historic real payment data: {exc}")

@app.get("/payment-schedule", response_model=List[PaymentSchedule])
def get_payment_schedule():
    try:
        schedule_df = load_payment_schedule()
        return dataframe_to_models(schedule_df, PaymentSchedule)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=f"Payment schedule data file not found at '{getattr(exc, 'filename', str(exc))}'. Please upload the CSV file to the data/pricing directory."
        )
    except ValidationError as exc:
        raise HTTPException(status_code=500, detail=f"Failed to serialize payment schedule data: {exc}")

@app.get("/customer-data", response_model=List[CustomerData])
def get_customer_data():
    try:
        customer_df = load_customer_data()
        return dataframe_to_models(customer_df, CustomerData)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Customer data file not found. Please upload the CSV file to the data/pricing directory.")
    except ValidationError as exc:
        raise HTTPException(status_code=500, detail=f"Failed to serialize customer data: {exc}")

@app.get("/collateral", response_model=List[Collateral])
def get_collateral():
    try:
        collateral_df = load_collateral()
        return dataframe_to_models(collateral_df, Collateral)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Collateral data file not found. Please upload the CSV file to the data/pricing directory.")
    except ValidationError as exc:
        raise HTTPException(status_code=500, detail=f"Failed to serialize collateral data: {exc}")

# Figma endpoint
@app.get("/figma-file/{file_key}", response_model=Dict[str, Any])
def get_figma_file_endpoint(file_key: str):
    try:
        return get_figma_file(file_key)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))