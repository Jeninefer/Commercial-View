"""
Commercial-View FastAPI Application
Production-ready commercial lending analytics platform
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    import uvicorn
    
    # Import application modules
    from pipeline import CommercialViewPipeline
    from data_loader import DataLoader
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title="Commercial-View API",
    description="Enterprise commercial lending analytics platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for production
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Initialize data components
try:
    data_loader = DataLoader()
    pipeline = CommercialViewPipeline()
    logger.info("✅ Commercial-View application initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize application components: {e}")
    data_loader = None
    pipeline = None

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception for {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error occurred", "path": str(request.url.path)}
    )

# Health endpoint
@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    System health check with data availability status
    Returns comprehensive health information for monitoring
    """
    try:
        # Check data availability
        datasets_status = {}
        
        if data_loader:
            # Check core datasets
            core_datasets = ["loan_data", "payment_schedule", "historic_payments"]
            
            for dataset in core_datasets:
                try:
                    df = getattr(data_loader, f"load_{dataset}")()
                    datasets_status[dataset] = {
                        "available": df is not None and not df.empty,
                        "records": len(df) if df is not None else 0
                    }
                except Exception as e:
                    datasets_status[dataset] = {
                        "available": False,
                        "error": str(e)
                    }
        
        return {
            "status": "healthy",
            "version": "1.0.0",
            "application": "Commercial-View",
            "environment": os.getenv("ENVIRONMENT", "production"),
            "datasets_available": datasets_status,
            "data_source": "Production Google Drive",
            "timestamp": pipeline.get_current_timestamp() if pipeline else None
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy", 
                "error": str(e),
                "application": "Commercial-View"
            }
        )

# Portfolio metrics endpoint
@app.get("/portfolio-metrics")
async def get_portfolio_metrics() -> Dict[str, Any]:
    """
    Get comprehensive portfolio metrics and KPIs
    Returns real-time commercial lending analytics
    """
    try:
        if not pipeline:
            raise HTTPException(status_code=503, detail="Analytics pipeline not available")
        
        # Load and process data
        pipeline.load_all_datasets()
        
        # Calculate portfolio metrics
        metrics = {
            "portfolio_outstanding": pipeline.compute_portfolio_outstanding(),
            "active_clients": pipeline.compute_active_clients(),
            "weighted_apr": pipeline.compute_weighted_apr(),
            "npl_rate": pipeline.compute_npl_rate(),
            "concentration_risk": pipeline.compute_concentration_risk(),
            "collection_rate": pipeline.compute_collection_rate(),
            "status": "success",
            "calculation_timestamp": pipeline.get_current_timestamp()
        }
        
        logger.info("✅ Portfolio metrics calculated successfully")
        return metrics
        
    except Exception as e:
        logger.error(f"Portfolio metrics calculation failed: {e}")
        # Return fallback metrics to maintain API stability
        return {
            "portfolio_outstanding": 0.0,
            "active_clients": 0,
            "weighted_apr": 0.0,
            "npl_rate": 0.0,
            "concentration_risk": 0.0,
            "collection_rate": 0.0,
            "status": "error",
            "error": str(e),
            "fallback": True
        }

# Loan data endpoint
@app.get("/loan-data")
async def get_loan_data() -> List[Dict[str, Any]]:
    """
    Get active commercial loan portfolio data
    Returns real loan records from production sources
    """
    try:
        if not data_loader:
            raise HTTPException(status_code=503, detail="Data loader not available")
        
        # Load real loan data
        loan_df = data_loader.load_loan_data()
        
        if loan_df is not None and not loan_df.empty:
            # Convert to records format for API response
            records = loan_df.to_dict('records')
            logger.info(f"✅ Loaded {len(records)} loan records")
            return records
        else:
            logger.warning("No loan data available")
            return []
            
    except Exception as e:
        logger.error(f"Failed to load loan data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load loan data: {str(e)}")

# Payment schedule endpoint  
@app.get("/payment-schedule")
async def get_payment_schedule() -> List[Dict[str, Any]]:
    """
    Get payment schedule data for cash flow analysis
    Returns scheduled payments from production sources
    """
    try:
        if not data_loader:
            raise HTTPException(status_code=503, detail="Data loader not available")
        
        # Load payment schedule data
        payment_df = data_loader.load_payment_schedule()
        
        if payment_df is not None and not payment_df.empty:
            records = payment_df.to_dict('records')
            logger.info(f"✅ Loaded {len(records)} payment schedule records")
            return records
        else:
            logger.warning("No payment schedule data available")
            return []
            
    except Exception as e:
        logger.error(f"Failed to load payment schedule: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load payment schedule: {str(e)}")

# Historic payments endpoint
@app.get("/historic-real-payment")
async def get_historic_payments() -> List[Dict[str, Any]]:
    """
    Get historic payment performance data
    Returns actual payment history for performance analysis
    """
    try:
        if not data_loader:
            raise HTTPException(status_code=503, detail="Data loader not available")
        
        # Load historic payment data
        historic_df = data_loader.load_historic_real_payment()
        
        if historic_df is not None and not historic_df.empty:
            records = historic_df.to_dict('records')
            logger.info(f"✅ Loaded {len(records)} historic payment records")
            return records
        else:
            logger.warning("No historic payment data available")
            return []
            
    except Exception as e:
        logger.error(f"Failed to load historic payments: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load historic payments: {str(e)}")

# Schema metadata endpoint
@app.get("/schema/{dataset_name}")
async def get_dataset_schema(dataset_name: str) -> Dict[str, Any]:
    """
    Get dataset schema information
    Returns column metadata for supported datasets
    """
    try:
        schemas = {
            "loan_data": {
                "name": "loan_data",
                "description": "Commercial loan portfolio data",
                "columns": ["Customer ID", "Loan Amount", "Interest Rate", "Term", "Status", "Origination Date"]
            },
            "payment_schedule": {
                "name": "payment_schedule", 
                "description": "Scheduled loan payments",
                "columns": ["Customer ID", "Due Date", "Principal Payment", "Interest Payment", "Total Payment"]
            },
            "historic_real_payment": {
                "name": "historic_real_payment",
                "description": "Historical payment performance",
                "columns": ["Customer ID", "Payment Date", "Amount Paid", "Days Past Due", "Payment Status"]
            }
        }
        
        if dataset_name not in schemas:
            raise HTTPException(status_code=404, detail="Dataset schema not found")
        
        return schemas[dataset_name]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Schema retrieval failed for {dataset_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Schema retrieval failed: {str(e)}")

# Root endpoint
@app.get("/")
async def root() -> Dict[str, str]:
    """Welcome message for Commercial-View API"""
    return {
        "message": "Welcome to Commercial-View API",
        "description": "Enterprise commercial lending analytics platform",
        "version": "1.0.0",
        "documentation": "/docs"
    }

# Application startup
@app.on_event("startup")
async def startup_event():
    """Application startup initialization"""
    logger.info("🚀 Starting Commercial-View application...")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'production')}")
    logger.info(f"CORS Origins: {ALLOWED_ORIGINS}")

# Application shutdown
@app.on_event("shutdown") 
async def shutdown_event():
    """Application shutdown cleanup"""
    logger.info("🛑 Shutting down Commercial-View application...")

# Development server runner
if __name__ == "__main__":
    # Development configuration
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    reload = os.getenv("ENVIRONMENT", "production") == "development"
    
    logger.info(f"Starting server on {host}:{port}")
    
    try:
        uvicorn.run(
            "run:app",
            host=host,
            port=port, 
            reload=reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        sys.exit(1)
