"""
Abaco Core - Core modules for Payments + DPD, Feature Engineering, 
Pricing Enrichment, and KPI computation.
"""

import logging
import sys

__version__ = "0.1.0"

# Expose main modules
from . import payment_logic
from . import feature_engineering
from . import pricing
from . import kpi
from . import metrics_registry


def configure_logging(level=logging.INFO, format_string=None):
    """
    Configure logging for abaco_core package.
    
    Args:
        level: Logging level (default: logging.INFO)
        format_string: Custom format string (optional)
    
    Returns:
        logging.Logger: Configured root logger
    """
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        format=format_string,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger('abaco_core')
    logger.setLevel(level)
    
    return logger


__all__ = [
    'configure_logging',
    'payment_logic',
    'feature_engineering',
    'pricing',
    'kpi',
    'metrics_registry',
]
