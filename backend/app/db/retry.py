# -*- coding: utf-8 -*-
"""
Retry logic for database operations.
"""

from logging import getLogger
from time import sleep
from typing import Callable, TypeVar

# ##: Type variable for generic return types.
T = TypeVar("T")

logger = getLogger(__name__)


def with_retry(max_retries: int, retry_delay: float):
    """
    Decorator for retrying database operations on failure.

    Parameters
    ----------
    max_retries : int
        Maximum number of retry attempts
    retry_delay : float
        Delay between retries in seconds

    Example:
    --------
    ```python
    @with_retry(max_retries=5, retry_delay=1.0)
    def get_player(player_id):
        # Function implementation
    ```
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    last_exception = exc
                    logger.warning(
                        "Attempt %d/%d failed: %s. Retrying in %fs...", attempt + 1, max_retries, exc, retry_delay
                    )
                    if attempt < max_retries - 1:
                        sleep(retry_delay)

            logger.error("All %d attempts failed. Last error: %s", max_retries, last_exception)
            raise last_exception

        return wrapper

    return decorator
