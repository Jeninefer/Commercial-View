import os
from datetime import datetime
import logging
from typing import Optional, Dict, Any, List

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.data_loader import DataLoader
from src.figma_client import get_figma_file
from src.models import (
    LoanData, 
    HistoricRealPayment, 
    PaymentSchedule,
    CustomerData,
    Collateral
)

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PRICING_BASE_PATH = os.getenv("COMMERCIAL_VIEW_PRICING_PATH")

# Initialize FastAPI app
app = FastAPI(
    title="Commercial View API",
    description="Production-grade API for commercial loan portfolio analytics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for production use
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global data loader instance
data_loader = None
datasets = {}

@app.on_event("startup")
async def startup_event():
    """Load all datasets on application startup."""
    global data_loader, datasets
    try:
        logger.info("Starting Commercial View API...")
        data_loader = DataLoader()
        datasets = data_loader.load_all_datasets()
        logger.info(f"Successfully loaded {len(datasets)} datasets")
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")

@app.get("/")
async def root():
    """API health check and basic information."""
    return {
        "message": "Welcome to the Commercial View API",
        "version": "1.0.0",
        "status": "operational",
        "datasets_loaded": len(datasets),
        "endpoints": {
            "documentation": "/docs",
            "health": "/health",
            "loan_data": "/loan-data",
            "payments": "/payment-schedule",
            "historic_payments": "/historic-real-payment",
            "portfolio_summary": "/portfolio-summary",
            "dpd_analysis": "/dpd-analysis",
            "data_quality": "/data-quality"
        }
    }

@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "datasets": {}
    }
    
    for name, df in datasets.items():
        health_status["datasets"][name] = {
            "loaded": True,
            "row_count": len(df),
            "last_updated": datetime.now().isoformat()
        }
    
    # Check for missing critical datasets
    missing_datasets = ["customer_data", "collateral"]
    for dataset in missing_datasets:
        if dataset not in datasets:
            health_status["datasets"][dataset] = {
                "loaded": False,
                "status": "missing"
            }
            health_status["status"] = "degraded"
    
    return health_status

@app.get("/loan-data")
async def get_loan_data(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    customer_id: Optional[str] = Query(None, description="Filter by customer ID"),
    status: Optional[str] = Query(None, description="Filter by loan status")
):
    """Get loan data with pagination and filtering."""
    if "loan_data" not in datasets:
        raise HTTPException(status_code=404, detail="Loan data not available")
    
    df = datasets["loan_data"].copy()
    
    # Apply filters
    if customer_id:
        df = df[df["customer_id"] == customer_id]
    if status:
        df = df[df["loan_status"] == status]
    
    # Apply pagination
    total_records = len(df)
    df_paginated = df.iloc[skip:skip + limit]
    
    return {
        "data": df_paginated.fillna("").to_dict(orient="records"),
        "pagination": {
            "skip": skip,
            "limit": limit,
            "total": total_records,
            "has_more": skip + limit < total_records
        }
    }

@app.get("/portfolio-summary")
async def get_portfolio_summary():
    """Get comprehensive portfolio analytics."""
    if "loan_data" not in datasets:
        raise HTTPException(status_code=404, detail="Loan data not available")
    
    df = datasets["loan_data"]
    
    # Calculate key metrics
    summary = {
        "overview": {
            "total_loans": len(df),
            "active_loans": len(df[df["loan_status"] == "Current"]),
            "completed_loans": len(df[df["loan_status"] == "Complete"]),
            "defaulted_loans": len(df[df["loan_status"] == "Default"]),
            "total_portfolio_value": float(df["outstanding_balance"].sum()),
            "weighted_average_apr": float(
                (df["interest_rate"] * df["outstanding_balance"]).sum() / 
                df["outstanding_balance"].sum()
            ) if df["outstanding_balance"].sum() > 0 else 0
        },
        "by_status": df.groupby("loan_status").agg({
            "loan_id": "count",
            "outstanding_balance": "sum"
        }).to_dict(),
        "top_customers": df.groupby("customer_id").agg({
            "outstanding_balance": "sum"
        }).nlargest(10, "outstanding_balance").to_dict(),
        "concentration_metrics": {
            "single_obligor_limit": 0.04,  # 4% as per manifest
            "top_10_concentration": float(
                df.groupby("customer_id")["outstanding_balance"].sum()
                .nlargest(10).sum() / df["outstanding_balance"].sum()
            ) if df["outstanding_balance"].sum() > 0 else 0
        }
    }
    
    return summary

@app.get("/dpd-analysis")
async def get_dpd_analysis():
    """Get Days Past Due (DPD) analysis."""
    if "loan_data" not in datasets:
        raise HTTPException(status_code=404, detail="Loan data not available")
    
    df = datasets["loan_data"]
    
    # Define DPD buckets as per manifest
    dpd_buckets = [0, 7, 15, 21, 30, 60, 75, 90, 120, 150, 180]
    
    # Create DPD bucket labels
    def get_dpd_bucket(days):
        for i, bucket in enumerate(dpd_buckets):
            if days <= bucket:
                return f"0-{bucket}" if i == 0 else f"{dpd_buckets[i-1]+1}-{bucket}"
        return "180+"
    
    df["dpd_bucket"] = df["days_past_due"].apply(get_dpd_bucket)
    
    dpd_analysis = {
        "buckets": df.groupby("dpd_bucket").agg({
            "loan_id": "count",
            "outstanding_balance": "sum"
        }).to_dict(),
        "metrics": {
            "dpd_0": len(df[df["days_past_due"] == 0]),
            "dpd_1_30": len(df[(df["days_past_due"] >= 1) & (df["days_past_due"] <= 30)]),
            "dpd_31_60": len(df[(df["days_past_due"] >= 31) & (df["days_past_due"] <= 60)]),
            "dpd_61_90": len(df[(df["days_past_due"] >= 61) & (df["days_past_due"] <= 90)]),
            "dpd_over_90": len(df[df["days_past_due"] > 90]),
            "npl_180": float(df[df["days_past_due"] >= 180]["outstanding_balance"].sum())
        }
    }
    
    return dpd_analysis

@app.get("/data-quality")
async def get_data_quality_report():
    """Get comprehensive data quality report."""
    if data_loader is None:
        raise HTTPException(status_code=500, detail="Data loader not initialized")
    
    return data_loader.get_data_quality_report()

@app.get("/payment-schedule")
async def get_payment_schedule(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    loan_id: Optional[str] = Query(None)
):
    """Get payment schedule data."""
    if "payment_schedule" not in datasets:
        raise HTTPException(status_code=404, detail="Payment schedule data not available")
    
    df = datasets["payment_schedule"].copy()
    
    if loan_id:
        df = df[df["loan_id"] == loan_id]
    
    total_records = len(df)
    df_paginated = df.iloc[skip:skip + limit]
    
    return {
        "data": df_paginated.fillna("").to_dict(orient="records"),
        "pagination": {
            "skip": skip,
            "limit": limit,
            "total": total_records
        }
    }

@app.get("/historic-real-payment")
async def get_historic_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    payment_status: Optional[str] = Query(None)
):
    """Get historic payment data."""
    if "historic_real_payment" not in datasets:
        raise HTTPException(status_code=404, detail="Historic payment data not available")
    
    df = datasets["historic_real_payment"].copy()
    
    if payment_status:
        df = df[df["True Payment Status"] == payment_status]
    
    total_records = len(df)
    df_paginated = df.iloc[skip:skip + limit]
    
    return {
        "data": df_paginated.fillna("").to_dict(orient="records"),
        "pagination": {
            "skip": skip,
            "limit": limit,
            "total": total_records
        }
    }

@app.get("/figma-file/{file_key}", response_model=Dict[str, Any])
def get_figma_file_endpoint(file_key: str):
    try:
        return get_figma_file(file_key)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for production error handling."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "timestamp": datetime.now().isoformat()
        }
    )

# For running with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)