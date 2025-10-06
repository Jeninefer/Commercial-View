"""
Production configuration for Commercial-View
Real commercial lending parameters - no demo data
"""

import os
from pathlib import Path

class ProductionConfig:
    """Production configuration with real parameters"""
    
    # Google Drive production data source
    GOOGLE_DRIVE_FOLDER = "https://drive.google.com/drive/folders/1qIg_BnIf_IWYcWqCuvLaYU_Gu4C2-Dj8"
    
    # Production data files (real CSV names)
    DATA_FILES = {
        "loan_data": "loan_data.csv",
        "payment_schedule": "payment_schedule.csv", 
        "historic_payments": "historic_real_payment.csv",
        "customer_data": "customer_data.csv",
        "collateral_data": "collateral_data.csv"
    }
    
    # Real commercial lending thresholds (not demo values)
    RISK_THRESHOLDS = {
        "high_risk_dpd": 90,  # Real 90+ DPD threshold
        "npl_threshold": 180,  # Real NPL threshold
        "concentration_limit": 0.15,  # Real 15% concentration limit
        "ltv_max": 0.90,  # Real 90% LTV limit
        "dscr_min": 1.20   # Real 120% DSCR minimum
    }
    
    # Production KPI targets (real business targets)
    KPI_TARGETS = {
        "portfolio_yield": 0.185,  # Real 18.5% target yield
        "npl_rate": 0.025,         # Real 2.5% NPL target
        "collection_rate": 0.95,   # Real 95% collection target
        "growth_rate": 0.20        # Real 20% growth target
    }
    
    # Environment-based settings (no hardcoded values)
    @classmethod
    def get_database_url(cls):
        return os.getenv("DATABASE_URL", "")
    
    @classmethod 
    def get_api_keys(cls):
        return {
            "google_credentials": os.getenv("GOOGLE_CREDENTIALS_PATH"),
            "openai_key": os.getenv("OPENAI_API_KEY"),
            "hubspot_key": os.getenv("HUBSPOT_API_KEY"),
            "slack_webhook": os.getenv("SLACK_WEBHOOK_URL")
        }
    
    # Production logging (no debug info in prod)
    LOGGING_CONFIG = {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "handlers": ["file", "console"]
    }
