# abaco_core Package

This package provides core functionality for the Commercial-View application, including centralized logging configuration.

## Modules

### logging_config

The `logging_config` module provides centralized logging configuration for all modules within the `abaco_core` package.

#### Usage

```python
from abaco_core.logging_config import configure_logging
import logging

# Configure logging with default INFO level
configure_logging()

# Or configure with a specific level
configure_logging(level=logging.DEBUG)

# Create a logger for your module
logger = logging.getLogger("abaco_core.my_module")

# Use the logger
logger.debug("This is a debug message")
logger.info("This is an info message")
logger.warning("This is a warning message")
logger.error("This is an error message")
logger.critical("This is a critical message")
```

#### Configuration Details

The `configure_logging()` function:
- Sets up a consistent logging format: `%(asctime)s [%(levelname)s] %(name)s - %(message)s`
- Configures the logging level (default: `INFO`)
- Ensures all loggers under the `abaco_core` namespace use the same configuration

#### Logging Levels

The standard Python logging levels are:
- `DEBUG`: Detailed information, typically of interest only when diagnosing problems
- `INFO`: Confirmation that things are working as expected
- `WARNING`: An indication that something unexpected happened, but the software is still working
- `ERROR`: A more serious problem, the software has not been able to perform some function
- `CRITICAL`: A serious error, indicating that the program itself may be unable to continue running

## Example

See `example_module.py` for a working example of how to use the logging configuration.

## Testing

Run the tests with:

```bash
python -m unittest tests.test_logging_config
```

Or if you have pytest installed:

```bash
pytest tests/test_logging_config.py
```
