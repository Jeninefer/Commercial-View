"""
Logging configuration for the abaco_core package.

This module provides centralized logging configuration for all modules
within the abaco_core package.
"""

import logging


def configure_logging(level=logging.INFO):
    """
    Configure logging for the abaco_core package.
    
    This function sets up a consistent logging format and level for all
    loggers under the abaco_core namespace. Each module should create
    loggers using: logger = logging.getLogger("abaco_core.<module_name>")
    
    Args:
        level: The logging level (e.g., logging.DEBUG, logging.INFO, 
               logging.WARNING, logging.ERROR, logging.CRITICAL).
               Defaults to logging.INFO.
    
    Example:
        >>> from abaco_core.logging_config import configure_logging
        >>> import logging
        >>> configure_logging(level=logging.DEBUG)
        >>> logger = logging.getLogger("abaco_core.my_module")
        >>> logger.debug("This is a debug message")
    """
    # Configure logging for the abaco_core logger explicitly
    logger = logging.getLogger("abaco_core")
    logger.setLevel(level)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")
    # Remove all existing handlers
    while logger.handlers:
        logger.removeHandler(logger.handlers[0])
    # Add a new StreamHandler
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
