import random
import time
from typing import Any, Callable, TypeVar

T = TypeVar("T")


def with_retry(call: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """Retry a callable on HTTP 429 (rate limit) responses with exponential backoff."""
    delay = 1.0
    for _ in range(6):
        try:
            return call(*args, **kwargs)
        except Exception as exc:  # noqa: BLE001 - broad to inspect message
            if "429" not in str(exc):
                raise
            time.sleep(delay + random.random())
            delay *= 2
    raise RuntimeError("Rate limit persisted after retries")
