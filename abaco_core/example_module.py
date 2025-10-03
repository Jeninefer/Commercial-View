"""
Example module demonstrating logging usage.

This module shows how to use the logging configuration in abaco_core.
"""

import logging

# Create a logger for this module
logger = logging.getLogger("abaco_core.example_module")


def example_function():
    """Example function that demonstrates logging at different levels."""
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")


if __name__ == "__main__":
    # Import and configure logging
    from abaco_core.logging_config import configure_logging
    
    # Configure with INFO level (default)
    print("=== Logging with INFO level ===")
    configure_logging(level=logging.INFO)
    example_function()
    
    print("\n=== Logging with DEBUG level ===")
    configure_logging(level=logging.DEBUG)
    example_function()
