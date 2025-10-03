"""
Commercial-View Portfolio Monitoring System

A production-quality portfolio monitoring and optimization framework for
commercial lending portfolios. Includes alert detection, risk metrics,
and automated reporting.
"""

__version__ = "1.0.0"

from .config import Config
from .alerts import AlertEngine
from .optimizer import PortfolioOptimizer

__all__ = ["Config", "AlertEngine", "PortfolioOptimizer"]

# Optional: Google Drive integration (requires google-api-python-client)
try:
    from .gdrive_ingest import GoogleDriveIngestor
    __all__.append("GoogleDriveIngestor")
except ImportError:
    pass  # Google Drive dependencies not installed
