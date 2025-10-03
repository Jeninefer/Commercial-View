"""
Configuration module for Commercial View Platform.
Loads environment variables and provides centralized configuration management.
"""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================
# GOOGLE CONFIGURATION
# ============================================
GOOGLE_DRIVE_FOLDER_URL = os.getenv("GOOGLE_DRIVE_FOLDER_URL", "")
GOOGLE_SHEETS_ID = os.getenv("GOOGLE_SHEETS_ID", "")
GOOGLE_CLOUD_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID", "")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")

# OAuth 2.0 credentials file
CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"

# ============================================
# AI MODEL CONFIGURATION
# ============================================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# ============================================
# HUBSPOT & ATOMCHAT CONFIGURATION
# ============================================
HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY", "")
HUBSPOT_PORTAL_ID = os.getenv("HUBSPOT_PORTAL_ID", "")
ATOMCHAT_API_KEY = os.getenv("ATOMCHAT_API_KEY", "")
ATOMCHAT_APP_ID = os.getenv("ATOMCHAT_APP_ID", "")

# ============================================
# EMAIL CONFIGURATION
# ============================================
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
NOTIFICATION_EMAIL_FROM = os.getenv("NOTIFICATION_EMAIL_FROM", "")
NOTIFICATION_EMAIL_TO = os.getenv("NOTIFICATION_EMAIL_TO", "")

# ============================================
# APPLICATION CONFIGURATION
# ============================================
DAILY_JOB_TIME = os.getenv("DAILY_JOB_TIME", "08:00")
TIMEZONE = os.getenv("TIMEZONE", "America/Mexico_City")
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "8501"))
ENABLE_VIEW_ONLY_ROLE = os.getenv("ENABLE_VIEW_ONLY_ROLE", "true").lower() == "true"

# ============================================
# OUTPUT CONFIGURATION
# ============================================
OUTPUT_FORMAT = os.getenv("OUTPUT_FORMAT", "csv")
OUTPUT_DESTINATION = os.getenv("OUTPUT_DESTINATION", "google_drive")
FIRMA_CODE_SHEET_ID = os.getenv("FIRMA_CODE_SHEET_ID", "")

# Output directory
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# ============================================
# OPTIMIZATION PARAMETERS
# ============================================
# KPI weights (must sum to 1.0)
WEIGHT_APR = float(os.getenv("WEIGHT_APR", "0.25"))
WEIGHT_ROTATION_SPEED = float(os.getenv("WEIGHT_ROTATION_SPEED", "0.20"))
WEIGHT_CONCENTRATION_RISK = float(os.getenv("WEIGHT_CONCENTRATION_RISK", "0.20"))
WEIGHT_MOM_GROWTH = float(os.getenv("WEIGHT_MOM_GROWTH", "0.20"))
WEIGHT_DPD_MINIMIZATION = float(os.getenv("WEIGHT_DPD_MINIMIZATION", "0.15"))

# Risk thresholds
MAX_CLIENT_CONCENTRATION = float(os.getenv("MAX_CLIENT_CONCENTRATION", "0.15"))
MAX_SECTOR_CONCENTRATION = float(os.getenv("MAX_SECTOR_CONCENTRATION", "0.30"))
MAX_DPD_TOLERANCE = int(os.getenv("MAX_DPD_TOLERANCE", "30"))

# ============================================
# BRAND CONFIGURATION (ABACO)
# ============================================
BRAND_COLORS: Dict[str, str] = {
    "primary_dark": os.getenv("PRIMARY_COLOR_DARK", "#030E19"),
    "primary_purple": os.getenv("PRIMARY_COLOR_PURPLE", "#221248"),
    "neutral_grey_dark": os.getenv("NEUTRAL_GREY_DARK", "#6D7D8E"),
    "neutral_grey_mid": os.getenv("NEUTRAL_GREY_MID", "#9EA9B3"),
    "neutral_grey_light": os.getenv("NEUTRAL_GREY_LIGHT", "#CED4D9"),
    "contrast_white": os.getenv("CONTRAST_WHITE", "#FFFFFF"),
}

# ============================================
# AI PERSONAS CONFIGURATION
# ============================================
AI_PERSONAS: Dict[str, Dict[str, str]] = {
    "ceo": {
        "name": "CEO",
        "perspective": "Strategic leadership and overall business direction",
        "focus": "Long-term growth, market position, stakeholder value",
    },
    "cfo": {
        "name": "CFO",
        "perspective": "Financial oversight and fiscal responsibility",
        "focus": "Profitability, cash flow, financial risk management",
    },
    "cto": {
        "name": "CTO",
        "perspective": "Technology strategy and infrastructure",
        "focus": "System scalability, technical debt, innovation",
    },
    "head_of_growth": {
        "name": "Head of Growth",
        "perspective": "Customer acquisition and market expansion",
        "focus": "Growth metrics, customer lifetime value, market penetration",
    },
    "head_of_sales": {
        "name": "Head of Sales",
        "perspective": "Revenue generation and sales pipeline",
        "focus": "Deal closure, sales efficiency, revenue targets",
    },
    "head_of_marketing": {
        "name": "Head of Marketing",
        "perspective": "Brand positioning and lead generation",
        "focus": "Campaign effectiveness, brand awareness, lead quality",
    },
    "treasury_manager": {
        "name": "Treasury Manager",
        "perspective": "Cash flow and liquidity management",
        "focus": "Working capital, liquidity ratios, cash optimization",
    },
    "data_engineer": {
        "name": "Data Engineer",
        "perspective": "Data infrastructure and pipeline quality",
        "focus": "Data integrity, processing efficiency, system reliability",
    },
    "bi_analyst": {
        "name": "BI Analyst",
        "perspective": "Business intelligence and analytical insights",
        "focus": "Data patterns, predictive trends, actionable insights",
    },
}

# ============================================
# LOGGING CONFIGURATION
# ============================================
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


def validate_config() -> tuple[bool, list[str]]:
    """
    Validate that all required configuration variables are set.
    Returns tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Check critical API keys
    if not OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY is not set")
    
    if not GOOGLE_DRIVE_FOLDER_URL:
        errors.append("GOOGLE_DRIVE_FOLDER_URL is not set")
    
    # Validate optimization weights sum to 1.0
    total_weight = (
        WEIGHT_APR + WEIGHT_ROTATION_SPEED + WEIGHT_CONCENTRATION_RISK +
        WEIGHT_MOM_GROWTH + WEIGHT_DPD_MINIMIZATION
    )
    if abs(total_weight - 1.0) > 0.01:
        errors.append(f"Optimization weights must sum to 1.0 (current: {total_weight})")
    
    return len(errors) == 0, errors


def get_config_summary() -> Dict[str, Any]:
    """
    Returns a summary of current configuration (safe for logging).
    """
    return {
        "google_drive_configured": bool(GOOGLE_DRIVE_FOLDER_URL),
        "openai_configured": bool(OPENAI_API_KEY),
        "anthropic_configured": bool(ANTHROPIC_API_KEY),
        "google_cloud_configured": bool(GOOGLE_CLOUD_PROJECT_ID),
        "hubspot_configured": bool(HUBSPOT_API_KEY),
        "daily_job_time": DAILY_JOB_TIME,
        "timezone": TIMEZONE,
        "output_format": OUTPUT_FORMAT,
        "output_destination": OUTPUT_DESTINATION,
    }
