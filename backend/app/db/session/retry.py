# -*- coding: utf-8 -*-
"""
Retry logic for database operations.
"""

from time import sleep
from typing import Callable, TypeVar

from loguru import logger

# ##: Type variable for generic return types.
T = TypeVar("T")


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
                    logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {exc}. Retrying in {retry_delay}s...")
                    if attempt < max_retries - 1:
                        sleep(retry_delay)

            logger.error(f"All {max_retries} attempts failed. Last error: {last_exception}")
            raise last_exception

        return wrapper

    return decorator
