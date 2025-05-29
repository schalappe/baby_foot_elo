# -*- coding: utf-8 -*-
"""
Core database utilities like transaction management and retry logic.
"""

from contextlib import contextmanager

from loguru import logger

from app.db.database import DatabaseManager

@contextmanager
def transaction():
    """
    Context manager to provide a DatabaseManager instance for a block of operations.
    Logs the conceptual start and end of a transaction block.
    Relies on DatabaseManager for commit/rollback of individual operations.

    Example
    -------
    ```python
    with transaction() as db:
        db.execute("INSERT INTO Players (name, global_elo) VALUES (%s, %s)", ["John Doe", 1000])
    ```
    """
    logger.debug("Entering transaction context.")
    try:
        with DatabaseManager() as db:
            yield db
    except Exception as exc:
        logger.error(f"Error within transaction context: {exc}", exc_info=True)
        raise
