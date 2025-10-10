import random
import time
import logging
from typing import Any, Callable, TypeVar, Optional, List, Union, Dict
from functools import wraps
from datetime import datetime, timedelta
from enum import Enum

T = TypeVar("T")

logger = logging.getLogger(__name__)


class RetryStrategy(Enum):
    """Retry strategy types for different commercial lending scenarios"""

    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    FIXED = "fixed"
    FIBONACCI = "fibonacci"
    CUSTOM = "custom"


class CommercialLendingRetryError(Exception):
    """Custom exception for Commercial-View retry failures"""

    def __init__(
        self,
        message: str,
        attempts: int,
        total_duration: float,
        last_exception: Exception,
    ):
        super().__init__(message)
        self.attempts = attempts
        self.total_duration = total_duration
        self.last_exception = last_exception


class RetryConfig:
    """Advanced retry configuration for commercial lending operations"""

    def __init__(
        self,
        max_attempts: int = 6,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
        backoff_multiplier: float = 2.0,
        jitter: bool = True,
        retriable_exceptions: Optional[List[Exception]] = None,
        retriable_status_codes: Optional[List[int]] = None,
        timeout: Optional[float] = None,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout: float = 300.0,
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.strategy = strategy
        self.backoff_multiplier = backoff_multiplier
        self.jitter = jitter
        self.retriable_exceptions = retriable_exceptions or [
            ConnectionError,
            TimeoutError,
        ]
        self.retriable_status_codes = retriable_status_codes or [
            429,
            500,
            502,
            503,
            504,
        ]
        self.timeout = timeout
        self.circuit_breaker_threshold = circuit_breaker_threshold
        self.circuit_breaker_timeout = circuit_breaker_timeout


class CircuitBreaker:
    """Circuit breaker for commercial lending API reliability"""

    def __init__(self, failure_threshold: int = 5, timeout: float = 300.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "closed"  # closed, open, half-open

    def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute function with circuit breaker protection"""
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half-open"
            else:
                raise CommercialLendingRetryError(
                    "Circuit breaker is open", 0, 0, Exception("Circuit breaker open")
                )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset"""
        if self.last_failure_time is None:
            return True
        return datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout)

    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        self.state = "closed"

    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = "open"


class CommercialLendingRetry:
    """Enhanced retry handler for Commercial-View operations"""

    def __init__(self, config: RetryConfig = None):
        self.config = config or RetryConfig()
        self.circuit_breaker = CircuitBreaker(
            self.config.circuit_breaker_threshold, self.config.circuit_breaker_timeout
        )

        # Commercial lending specific retry configurations
        self.operation_configs = {
            "loan_pricing": RetryConfig(
                max_attempts=3, base_delay=0.5, strategy=RetryStrategy.LINEAR
            ),
            "risk_assessment": RetryConfig(
                max_attempts=5, base_delay=1.0, strategy=RetryStrategy.EXPONENTIAL
            ),
            "dpd_calculation": RetryConfig(
                max_attempts=3, base_delay=0.2, strategy=RetryStrategy.FIXED
            ),
            "kpi_generation": RetryConfig(
                max_attempts=4, base_delay=2.0, strategy=RetryStrategy.FIBONACCI
            ),
            "data_export": RetryConfig(max_attempts=8, base_delay=5.0, max_delay=120.0),
            "regulatory_report": RetryConfig(
                max_attempts=10, base_delay=3.0, timeout=1800.0
            ),
            "portfolio_analysis": RetryConfig(
                max_attempts=6, base_delay=2.0, strategy=RetryStrategy.EXPONENTIAL
            ),
        }

    def calculate_delay(self, attempt: int, config: RetryConfig) -> float:
        """Calculate delay based on retry strategy"""
        if config.strategy == RetryStrategy.FIXED:
            delay = config.base_delay
        elif config.strategy == RetryStrategy.LINEAR:
            delay = config.base_delay * attempt
        elif config.strategy == RetryStrategy.EXPONENTIAL:
            delay = config.base_delay * (config.backoff_multiplier ** (attempt - 1))
        elif config.strategy == RetryStrategy.FIBONACCI:
            delay = config.base_delay * self._fibonacci(attempt)
        else:
            delay = config.base_delay

        # Apply jitter if enabled
        if config.jitter:
            delay += random.uniform(0, delay * 0.1)

        # Cap at max_delay
        return min(delay, config.max_delay)

    def _fibonacci(self, n: int) -> int:
        """Calculate fibonacci number for retry delays"""
        if n <= 1:
            return 1
        a, b = 1, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b

    def is_retriable_exception(self, exception: Exception, config: RetryConfig) -> bool:
        """Check if exception is retriable for commercial lending operations"""
        # Check exception type
        for exc_type in config.retriable_exceptions:
            if isinstance(exception, exc_type):
                return True

        # Check HTTP status codes in exception message
        exc_str = str(exception).lower()
        for status_code in config.retriable_status_codes:
            if str(status_code) in exc_str:
                return True

        # Commercial lending specific retriable conditions
        retriable_patterns = [
            "rate limit",
            "timeout",
            "connection",
            "unavailable",
            "overloaded",
            "busy",
            "throttle",
            "temporary",
        ]

        return any(pattern in exc_str for pattern in retriable_patterns)

    def retry_with_config(self, operation_type: str = None):
        """Decorator for retrying commercial lending operations"""

        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @wraps(func)
            def wrapper(*args, **kwargs) -> T:
                config = self.operation_configs.get(operation_type, self.config)
                return self.execute_with_retry(func, config, *args, **kwargs)

            return wrapper

        return decorator

    def execute_with_retry(
        self, func: Callable[..., T], config: RetryConfig, *args, **kwargs
    ) -> T:
        """Execute function with comprehensive retry logic"""
        start_time = time.time()
        last_exception = None

        for attempt in range(1, config.max_attempts + 1):
            try:
                logger.debug(
                    f"Attempt {attempt}/{config.max_attempts} for {func.__name__}"
                )

                # Check timeout
                if config.timeout and (time.time() - start_time) > config.timeout:
                    raise CommercialLendingRetryError(
                        f"Operation timeout after {config.timeout}s",
                        attempt - 1,
                        time.time() - start_time,
                        last_exception,
                    )

                # Use circuit breaker for reliability
                result = self.circuit_breaker.call(func, *args, **kwargs)

                if attempt > 1:
                    logger.info(f"Operation succeeded on attempt {attempt}")

                return result

            except Exception as exc:
                last_exception = exc

                # Check if we should retry
                if attempt == config.max_attempts or not self.is_retriable_exception(
                    exc, config
                ):
                    logger.error(f"Operation failed after {attempt} attempts: {exc}")
                    raise CommercialLendingRetryError(
                        f"Operation failed after {attempt} attempts: {exc}",
                        attempt,
                        time.time() - start_time,
                        exc,
                    )

                # Calculate and apply delay
                delay = self.calculate_delay(attempt, config)
                logger.warning(
                    f"Attempt {attempt} failed: {exc}. Retrying in {delay:.2f}s..."
                )
                time.sleep(delay)

        # This should never be reached, but just in case
        raise CommercialLendingRetryError(
            "Unexpected retry loop exit",
            config.max_attempts,
            time.time() - start_time,
            last_exception,
        )


# Initialize global retry handler
default_retry = CommercialLendingRetry()


def with_retry(
    config: Optional[RetryConfig] = None,
    call: Callable[..., T] = None,
    *args: Any,
    **kwargs: Any,
) -> T:
    """Decorator to add retry logic to a function."""
    if config is None:
        config = RetryConfig()  # Create default config instead of passing None

    # Extract operation type from function name or kwargs
    operation_type = kwargs.pop("operation_type", None)

    if hasattr(call, "__name__"):
        func_name = call.__name__.lower()

        # Map function names to operation types
        if "pricing" in func_name or "price" in func_name:
            operation_type = "loan_pricing"
        elif "risk" in func_name:
            operation_type = "risk_assessment"
        elif "dpd" in func_name:
            operation_type = "dpd_calculation"
        elif "kpi" in func_name:
            operation_type = "kpi_generation"
        elif "export" in func_name:
            operation_type = "data_export"
        elif "report" in func_name:
            operation_type = "regulatory_report"
        elif "portfolio" in func_name:
            operation_type = "portfolio_analysis"

    config = default_retry.operation_configs.get(operation_type, default_retry.config)
    return default_retry.execute_with_retry(call, config, *args, **kwargs)


# Decorators for specific commercial lending operations
def retry_loan_pricing(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator for loan pricing operations with optimized retry strategy"""
    return default_retry.retry_with_config("loan_pricing")(func)


def retry_risk_assessment(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator for risk assessment operations with robust retry strategy"""
    return default_retry.retry_with_config("risk_assessment")(func)


def retry_dpd_calculation(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator for DPD calculation operations with fast retry strategy"""
    return default_retry.retry_with_config("dpd_calculation")(func)


def retry_kpi_generation(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator for KPI generation operations with balanced retry strategy"""
    return default_retry.retry_with_config("kpi_generation")(func)


def retry_data_export(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator for data export operations with patient retry strategy"""
    return default_retry.retry_with_config("data_export")(func)


def retry_regulatory_report(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator for regulatory reporting with maximum reliability"""
    return default_retry.retry_with_config("regulatory_report")(func)


def retry_portfolio_analysis(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator for portfolio analysis operations"""
    return default_retry.retry_with_config("portfolio_analysis")(func)


def create_custom_retry(
    max_attempts: int = 6,
    base_delay: float = 1.0,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
    **kwargs,
) -> Callable:
    """Create custom retry decorator with specific parameters"""
    config = RetryConfig(
        max_attempts=max_attempts, base_delay=base_delay, strategy=strategy, **kwargs
    )

    retry_handler = CommercialLendingRetry(config)

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            return retry_handler.execute_with_retry(func, config, *args, **kwargs)

        return wrapper

    return decorator


# Utility functions for commercial lending operations
def get_retry_stats() -> Dict[str, Any]:
    """Get retry statistics for monitoring"""
    return {
        "circuit_breaker_state": default_retry.circuit_breaker.state,
        "failure_count": default_retry.circuit_breaker.failure_count,
        "last_failure": (
            default_retry.circuit_breaker.last_failure_time.isoformat()
            if default_retry.circuit_breaker.last_failure_time
            else None
        ),
        "available_operations": list(default_retry.operation_configs.keys()),
    }


def reset_circuit_breaker():
    """Reset circuit breaker for testing or manual recovery"""
    default_retry.circuit_breaker.failure_count = 0
    default_retry.circuit_breaker.state = "closed"
    default_retry.circuit_breaker.last_failure_time = None
    logger.info("Circuit breaker reset")


# Example usage functions for commercial lending
if __name__ == "__main__":
    # Example: Loan pricing with retry
    @retry_loan_pricing
    def calculate_loan_rate(principal: float, term: int, risk_score: int) -> float:
        """Example loan pricing function with retry protection"""
        # Simulate potential failure
        if random.random() < 0.3:
            raise ConnectionError("Pricing service unavailable")
        return 5.5 + (risk_score / 100)

    # Example: Risk assessment with retry
    @retry_risk_assessment
    def assess_credit_risk(customer_id: str) -> Dict[str, Any]:
        """Example risk assessment function with retry protection"""
        # Simulate rate limiting
        if random.random() < 0.2:
            raise ConnectionError("HTTP 429 Rate Limited")
        return {"risk_score": 720, "grade": "A", "pd": 0.02}

    # Demo the retry functionality
    try:
        rate = calculate_loan_rate(100000, 60, 75)
        print(f"Calculated rate: {rate:.2f}%")

        risk = assess_credit_risk("CUST123")
        print(f"Risk assessment: {risk}")

        stats = get_retry_stats()
        print(f"Retry stats: {stats}")

    except CommercialLendingRetryError as e:
        print(f"Retry failed: {e}")
        print(f"Attempts: {e.attempts}, Duration: {e.total_duration:.2f}s")
