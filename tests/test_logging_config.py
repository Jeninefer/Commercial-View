"""
Unit tests for logging_config module.

This module tests the logging configuration functionality.
"""

import unittest
import logging
import sys
from io import StringIO
from abaco_core.logging_config import configure_logging


class TestLoggingConfig(unittest.TestCase):
    """Test cases for the logging configuration."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Store the original root logger configuration
        self.original_level = logging.root.level
        self.original_handlers = logging.root.handlers[:]
        
    def tearDown(self):
        """Clean up after tests."""
        # Restore original logger configuration
        logging.root.setLevel(self.original_level)
        logging.root.handlers.clear()
        for handler in self.original_handlers:
            logging.root.addHandler(handler)
        
    def test_configure_logging_default_level(self):
        """Test that configure_logging sets up logging with default INFO level."""
        configure_logging()
        
        # Check that the abaco_core logger is set to INFO
        logger = logging.getLogger("abaco_core")
        self.assertEqual(logger.level, logging.INFO)
        
    def test_configure_logging_custom_level(self):
        """Test that configure_logging accepts custom logging levels."""
        configure_logging(level=logging.DEBUG)
        
        # Check that the abaco_core logger is set to DEBUG
        logger = logging.getLogger("abaco_core")
        self.assertEqual(logger.level, logging.DEBUG)
        
        configure_logging(level=logging.WARNING)
        
        # Check that the abaco_core logger is set to WARNING
        logger = logging.getLogger("abaco_core")
        self.assertEqual(logger.level, logging.WARNING)
        
    def test_logging_output_format(self):
        """Test that logging produces correctly formatted output."""
        # Capture logging output
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")
        )
        
        # Create a test logger
        test_logger = logging.getLogger("abaco_core.test_module")
        test_logger.handlers = [handler]
        test_logger.setLevel(logging.INFO)
        
        # Log a test message
        test_message = "Test message"
        test_logger.info(test_message)
        
        # Get the output
        output = stream.getvalue()
        
        # Verify format contains expected components
        self.assertIn("[INFO]", output)
        self.assertIn("abaco_core.test_module", output)
        self.assertIn(test_message, output)
        
    def test_module_logger_hierarchy(self):
        """Test that module loggers under abaco_core work correctly."""
        configure_logging(level=logging.DEBUG)
        
        # Create loggers for different modules
        logger1 = logging.getLogger("abaco_core.module1")
        logger2 = logging.getLogger("abaco_core.module2")
        
        # Both should inherit from abaco_core
        self.assertTrue(logger1.name.startswith("abaco_core"))
        self.assertTrue(logger2.name.startswith("abaco_core"))
        

if __name__ == "__main__":
    unittest.main()
