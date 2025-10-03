"""Configuration package for Commercial View Platform."""

from .settings import *

__all__ = [
    "GOOGLE_DRIVE_FOLDER_URL",
    "GOOGLE_SHEETS_ID",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "BRAND_COLORS",
    "AI_PERSONAS",
    "validate_config",
    "get_config_summary",
]
