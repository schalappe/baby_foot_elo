# -*- coding: utf-8 -*-
"""
Core database utilities like transaction management and retry logic.
"""

import uuid
from contextlib import contextmanager

from loguru import logger

from .database import DatabaseManager


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
    transaction_id = uuid.uuid4()
    logger.debug(f"Starting transaction {transaction_id}.")
    try:
        handler.begin(db, transaction_id)
        yield db
        handler.commit(db, transaction_id)
        logger.info(f"Transaction {transaction_id} committed successfully.")
    except Exception as exc:
        handler.rollback(db, transaction_id)
        logger.error(f"Transaction {transaction_id} failed and rolled back. Error: {exc}", exc_info=True)
        raise
