"""Commercial View API - Enterprise Grade Implementation."""

import logging
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import os
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from pydantic import BaseModel

from src.data_loader import (
    load_loan_data,
    load_historic_real_payment,
    load_payment_schedule,
    load_customer_data,
    load_collateral,
)
from src.pipeline import CommercialViewPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI instance
app = FastAPI(
    title="Commercial View API",
    description="Enterprise grade portfolio analytics for Abaco Capital",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS with environment variables for production security
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

# Optional: Add API key security for production
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Initialize pipeline
pipeline = CommercialViewPipeline()

@app.on_event("startup")
async def startup_event():
    """Load all datasets on startup."""
    try:
        pipeline.load_all_datasets()
        logger.info("Successfully loaded all available datasets")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")

@app.get("/", response_model=Dict[str, str])
async def root():
    """Welcome endpoint."""
    return {"message": "Welcome to the Commercial View API"}

@app.get("/loan-data", response_model=List[Dict[str, Any]])
async def get_loan_data(limit: Optional[int] = None):
    """Get loan data with optional limit."""
    try:
        df = pipeline._datasets.get('loan_data', pd.DataFrame())
        if df.empty:
            return []
        if limit:
            df = df.head(limit)
        return df.to_dict('records')
    except Exception as e:
        logger.error(f"Error fetching loan data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/payment-schedule", response_model=List[dict])
async def get_payment_schedule(limit: Optional[int] = None):
    """Get payment schedule data with optional limit."""
    try:
        df = pipeline._datasets.get('payment_schedule', pd.DataFrame())
        if df.empty:
            return []
        if limit:
            df = df.head(limit)
        return df.to_dict('records')
    except Exception as e:
        logger.error(f"Error fetching payment schedule: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/historic-real-payment", response_model=List[dict])
async def get_historic_real_payment(limit: Optional[int] = None):
    """Get historic real payment data with optional limit."""
    try:
        df = pipeline._datasets.get('historic_real_payment', pd.DataFrame())
        if df.empty:
            return []
        if limit:
            df = df.head(limit)
        return df.to_dict('records')
    except Exception as e:
        logger.error(f"Error fetching historic payments: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/customer-data", response_model=List[dict])
async def get_customer_data(limit: Optional[int] = None):
    """Get customer data with optional limit."""
    try:
        df = pipeline._datasets.get('customer_data', pd.DataFrame())
        if df.empty:
            return []
        if limit:
            df = df.head(limit)
        return df.to_dict('records')
    except Exception as e:
        logger.error(f"Error fetching customer data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/collateral", response_model=List[dict])
async def get_collateral(limit: Optional[int] = None):
    """Get collateral data with optional limit."""
    try:
        df = pipeline._datasets.get('collateral', pd.DataFrame())
        if df.empty:
            return []
        if limit:
            df = df.head(limit)
        return df.to_dict('records')
    except Exception as e:
        logger.error(f"Error fetching collateral data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/executive-summary", response_model=dict)
async def get_executive_summary():
    """Get comprehensive executive summary with all KPIs."""
    try:
        summary = pipeline.generate_executive_summary()
        return summary
    except Exception as e:
        logger.error(f"Error generating executive summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/portfolio-metrics", response_model=dict)
async def get_portfolio_metrics():
    """Get detailed portfolio metrics."""
    try:
        metrics = pipeline.compute_portfolio_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Error computing portfolio metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dpd-analysis", response_model=dict)
async def get_dpd_analysis():
    """Get Days Past Due (DPD) analysis."""
    try:
        dpd_data = pipeline.compute_dpd_metrics()
        if dpd_data.empty:
            return {"message": "No DPD data available"}
        
        # Convert to JSON-serializable format
        dpd_summary = dpd_data.groupby('dpd_bucket').agg({
            'Outstanding Loan Value': 'sum',
            'Loan ID': 'count'
        }).rename(columns={'Loan ID': 'loan_count'})
        
        return {
            "dpd_buckets": dpd_summary.to_dict('index'),
            "total_past_due": float(dpd_data['past_due_amount'].sum()),
            "default_count": int(dpd_data['is_default'].sum())
        }
    except Exception as e:
        logger.error(f"Error in DPD analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recovery-analysis", response_model=dict)
async def get_recovery_analysis():
    """Get recovery curve analysis by cohort."""
    try:
        recovery_data = pipeline.compute_recovery_metrics()
        if recovery_data.empty:
            return {"message": "No recovery data available"}
        
        # Format for API response
        recovery_by_cohort = {}
        for cohort in recovery_data['cohort'].unique():
            cohort_data = recovery_data[recovery_data['cohort'] == cohort]
            recovery_by_cohort[str(cohort)] = cohort_data[[
                'months_since_disbursement', 'recovery_pct'
            ]].to_dict('records')
        
        return {
            "recovery_curves": recovery_by_cohort,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in recovery analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/schema/{dataset_name}", response_model=dict)
async def get_schema(dataset_name: str):
    """Get schema information for a specific dataset."""
    try:
        df = pipeline._datasets.get(dataset_name)
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail=f"Dataset '{dataset_name}' not found")
        
        schema = {
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "shape": df.shape,
            "null_counts": df.isnull().sum().to_dict()
        }
        return schema
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching schema: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health", response_model=dict)
async def health_check():
    """Health check endpoint with detailed status."""
    datasets_status = {}
    for name, df in pipeline._datasets.items():
        datasets_status[name] = {
            "loaded": not df.empty,
            "row_count": len(df) if not df.empty else 0
        }
    
    return {
        "status": "healthy",
        "datasets": datasets_status,
        "timestamp": datetime.now().isoformat()
    }

# Define your data models
class LoanData(BaseModel):
    loan_id: str
    amount: float
    term_months: int
    interest_rate: float
    # other fields...

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)