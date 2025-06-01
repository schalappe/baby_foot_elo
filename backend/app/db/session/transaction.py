# -*- coding: utf-8 -*-
"""
Core database utilities like transaction management.
"""

from contextlib import contextmanager

from loguru import logger

from app.core import config
from app.db.database import DatabaseManager


class TransactionHandler:
    """
    Handles the execution of transaction commands (BEGIN, COMMIT, ROLLBACK).

    This class is intended to be used with the context manager provided by the transaction()
    function. It provides methods to begin, commit and rollback transactions.
    """

    def begin(self, db: DatabaseManager, transaction_id: uuid.UUID):
        """
        Begin a transaction.

        This method is used within the `transaction()` context manager to start a transaction.
        It executes the "BEGIN" SQL command to start the transaction.

        Parameters
        ----------
        db : DatabaseManager
            The database manager instance to use for the transaction.
        transaction_id : uuid.UUID
            The unique ID for this transaction for logging.
        """
        db.execute("BEGIN;")
        logger.info("Transaction started.")
        logger.info(f"Transaction {transaction_id} started.")

    def commit(self, db: DatabaseManager, transaction_id: uuid.UUID):
        """
        Commit a transaction.

        This method is used within the `transaction()` context manager to commit a transaction.
        It executes the "COMMIT" SQL command to commit the transaction.

        Parameters
        ----------
        db : DatabaseManager
            The database manager instance to use for the transaction.
        transaction_id : uuid.UUID
            The unique ID for this transaction for logging.
        """
        db.execute("COMMIT;")
        logger.info("Transaction committed.")
        logger.info(f"Transaction {transaction_id} committed.")

    def rollback(self, db: DatabaseManager, transaction_id: uuid.UUID):
        """
        Rollback a transaction.

        This method is used within the `transaction()` context manager to rollback a transaction.
        It executes the "ROLLBACK" SQL command to rollback the transaction.

        Parameters
        ----------
        db : DatabaseManager
            The database manager instance to use for the transaction.
        transaction_id : uuid.UUID
            The unique ID for this transaction for logging.
        """
        db.execute("ROLLBACK;")
        logger.warning("Transaction rolled back.")
        logger.warning(f"Transaction {transaction_id} rolled back.")
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
