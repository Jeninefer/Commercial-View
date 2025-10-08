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

data_loader: Optional[DataLoader] = None
pipeline: Optional[CommercialViewPipeline] = None


def _ensure_data_loader() -> Optional[DataLoader]:
    """Initialise the shared data loader on demand."""
    global data_loader
    if data_loader is None:
        try:
            data_loader = DataLoader()
            logger.info("✅ DataLoader initialised successfully")
        except Exception as exc:  # pragma: no cover - logged for observability
            logger.error(f"❌ Failed to initialise DataLoader: {exc}")
            data_loader = None
    return data_loader


def _ensure_pipeline() -> Optional[CommercialViewPipeline]:
    """Initialise the analytics pipeline on demand."""
    global pipeline
    if pipeline is None:
        try:
            pipeline = CommercialViewPipeline()
            logger.info("✅ CommercialViewPipeline initialised successfully")
        except Exception as exc:  # pragma: no cover - logged for observability
            logger.error(f"❌ Failed to initialise CommercialViewPipeline: {exc}")
            pipeline = None
    return pipeline

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

        loader = _ensure_data_loader()
        if loader:
            # Check core datasets
            core_datasets = ["loan_data", "payment_schedule", "historic_payments"]

            for dataset in core_datasets:
                try:
                    df = getattr(loader, f"load_{dataset}")()
                    datasets_status[dataset] = {
                        "available": df is not None and not df.empty,
                        "records": len(df) if df is not None else 0
                    }
                except Exception as e:
                    datasets_status[dataset] = {
                        "available": False,
                        "error": str(e)
                    }

        pipeline_instance = _ensure_pipeline()

        return {
            "status": "healthy",
            "version": "1.0.0",
            "application": "Commercial-View",
            "environment": os.getenv("ENVIRONMENT", "production"),
            "datasets_available": datasets_status,
            "data_source": "Production Google Drive",
            "timestamp": (
                pipeline_instance.get_current_timestamp() if pipeline_instance else None
            )
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
        pipeline_instance = _ensure_pipeline()

        if not pipeline_instance:
            raise HTTPException(status_code=503, detail="Analytics pipeline not available")

        # Load and process data
        pipeline_instance.load_all_datasets()

        # Calculate portfolio metrics
        metrics = {
            "portfolio_outstanding": pipeline_instance.compute_portfolio_outstanding(),
            "active_clients": pipeline_instance.compute_active_clients(),
            "weighted_apr": pipeline_instance.compute_weighted_apr(),
            "npl_rate": pipeline_instance.compute_npl_rate(),
            "concentration_risk": pipeline_instance.compute_concentration_risk(),
            "collection_rate": pipeline_instance.compute_collection_rate(),
            "status": "success",
            "calculation_timestamp": pipeline_instance.get_current_timestamp()
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
        loader = _ensure_data_loader()

        if not loader:
            raise HTTPException(status_code=503, detail="Data loader not available")

        # Load real loan data
        pipeline_instance = _ensure_pipeline()
        if pipeline_instance:
            try:
                pipeline_instance.load_all_datasets()
            except Exception as exc:
                logger.debug(f"Pipeline load_all_datasets failed: {exc}")

        try:
            loan_df = loader.load_loan_data()
        except FileNotFoundError:
            logger.warning("Loan data file not found")
            return []
        
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
        loader = _ensure_data_loader()

        if not loader:
            raise HTTPException(status_code=503, detail="Data loader not available")

        # Load payment schedule data
        pipeline_instance = _ensure_pipeline()
        if pipeline_instance:
            try:
                pipeline_instance.load_all_datasets()
            except Exception as exc:
                logger.debug(f"Pipeline load_all_datasets failed: {exc}")

            # DESIGN LIMITATION: The pipeline does not expose loaded datasets via a public interface.
            # Consider adding a method like `get_payment_schedule()` to CommercialViewPipeline to access cached datasets.
            # For now, fallback to loading payment schedule directly from loader.

        try:
            payment_df = loader.load_payment_schedule()
        except FileNotFoundError:
            logger.warning("Payment schedule file not found")
                records = dataset.to_dict("records")
        
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
        loader = _ensure_data_loader()

        if not loader:
            raise HTTPException(status_code=503, detail="Data loader not available")

        # Load historic payment data
        pipeline_instance = _ensure_pipeline()
        if pipeline_instance:
            try:
                pipeline_instance.load_all_datasets()
            except Exception as exc:
                logger.debug(f"Pipeline load_all_datasets failed: {exc}")

            # No get_dataset method; proceed to fallback loader
        try:
            historic_df = loader.load_historic_real_payment()
        except FileNotFoundError:
            logger.warning("Historic payment file not found")
            return []

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


@app.get("/customer-data")
async def get_customer_data() -> List[Dict[str, Any]]:
    """Return customer dataset when available, otherwise an empty list."""
    try:
        loader = _ensure_data_loader()

        if not loader:
            return []

        try:
            customer_df = loader.load_customer_data()
        except FileNotFoundError:
            logger.warning("Customer data file not found")
            return []

        if customer_df is None or customer_df.empty:
            return []

        return customer_df.to_dict("records")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to load customer data: {e}")
        raise HTTPException(status_code=500, detail="Failed to load customer data")


@app.get("/collateral")
async def get_collateral_data() -> List[Dict[str, Any]]:
    """Return collateral dataset when available, otherwise an empty list."""
    try:
        loader = _ensure_data_loader()

        if not loader:
            return []

        try:
            collateral_df = loader.load_collateral()
        except FileNotFoundError:
            logger.warning("Collateral data file not found")
            return []

        if collateral_df is None or collateral_df.empty:
            return []

        return collateral_df.to_dict("records")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to load collateral data: {e}")
        raise HTTPException(status_code=500, detail="Failed to load collateral data")


@app.get("/executive-summary")
async def get_executive_summary() -> Dict[str, Any]:
    """Return an executive summary of portfolio performance."""
    pipeline_instance = _ensure_pipeline()

    if not pipeline_instance:
        raise HTTPException(status_code=503, detail="Analytics pipeline not available")

    try:
        summary = pipeline_instance.generate_executive_summary()
    except Exception as e:
        logger.error(f"Failed to generate executive summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate executive summary")

    if not isinstance(summary, dict):
        return {"portfolio_overview": {}, "risk_indicators": {}}

    summary.setdefault("portfolio_overview", {})
    summary.setdefault("risk_indicators", {})
    return summary

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
    return {"message": "Welcome to the Commercial View API"}

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
