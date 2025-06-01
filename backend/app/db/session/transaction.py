# -*- coding: utf-8 -*-
"""
Core database utilities like transaction management.
"""

from contextlib import contextmanager

from loguru import logger

from app.db.database import supabase


@contextmanager
def transaction():
    """
    Context manager to provide a Supabase instance for a block of operations.
    Logs the conceptual start and end of a transaction block.

    Example
    -------
    ```python
    with transaction() as db_manager:
        db.execute("INSERT INTO Players (name) VALUES (?)", ["John Doe"])
    with transaction() as supabase:
        supabase.table("Players").insert({"name": "John Doe", "global_elo": 1000}).execute()
    ```
    """
    logger.debug("Entering transaction context.")
    try:
        yield supabase
    except Exception as exc:
        logger.error(f"Error within transaction context: {exc}", exc_info=True)
        raise
    finally:
        logger.debug("Exiting transaction context.")
