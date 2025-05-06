# -*- coding: utf-8 -*-
"""
Core database utilities like transaction management and retry logic.
"""

from contextlib import contextmanager
from logging import getLogger

from .database import DatabaseManager

logger = getLogger(__name__)


class TransactionHandler:
    """
    Handles the execution of transaction commands (BEGIN, COMMIT, ROLLBACK).

    This class is intended to be used with the context manager provided by the transaction()
    function. It provides methods to begin, commit and rollback transactions.
    """

    def begin(self, db: DatabaseManager):
        """
        Begin a transaction.

        This method is used within the `transaction()` context manager to start a transaction.
        It executes the "BEGIN" SQL command to start the transaction.

        Parameters
        ----------
        db : DatabaseManager
            The database manager instance to use for the transaction.
        """
        db.execute("BEGIN;")
        logger.debug("Transaction started.")

    def commit(self, db: DatabaseManager):
        """
        Commit a transaction.

        This method is used within the `transaction()` context manager to commit a transaction.
        It executes the "COMMIT" SQL command to commit the transaction.

        Parameters
        ----------
        db : DatabaseManager
            The database manager instance to use for the transaction.
        """
        db.execute("COMMIT;")
        logger.debug("Transaction committed.")

    def rollback(self, db: DatabaseManager):
        """
        Rollback a transaction.

        This method is used within the `transaction()` context manager to rollback a transaction.
        It executes the "ROLLBACK" SQL command to rollback the transaction.

        Parameters
        ----------
        db : DatabaseManager
            The database manager instance to use for the transaction.
        """
        db.execute("ROLLBACK;")
        logger.debug("Transaction rolled back.")


@contextmanager
def transaction():
    """
    Context manager for transaction management.
    Automatically handles begin, commit, and rollback operations.

    This context manager is used to manage database transactions. It ensures that a transaction
    is started before the block of code is executed, and that the transaction is committed if
    no exceptions are raised, or rolled back if an exception is raised.

    Example
    -------
    ```python
    with transaction() as db:
        db.execute("INSERT INTO Players (name) VALUES (?)", ["John Doe"])
    ```
    """
    # ##: Get the singleton instance of DatabaseManager.
    db = DatabaseManager()
    handler = TransactionHandler()
    try:
        handler.begin(db)
        yield db
        handler.commit(db)
    except Exception as exc:
        handler.rollback(db)
        logger.error("Transaction failed: %s", exc)
        raise
