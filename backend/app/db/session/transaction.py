# -*- coding: utf-8 -*-
"""
Core database utilities like transaction management and retry logic.
"""

import uuid
from contextlib import contextmanager

from loguru import logger

from app.db.database import DatabaseManager


class TransactionHandler:
    """
    Handles logging for transaction blocks.
    Actual commit/rollback is handled by DatabaseManager per operation or by direct connection control.
    """

    def begin(self, db: DatabaseManager, transaction_id: uuid.UUID):
        """
        Log the beginning of a conceptual transaction block.
        Actual DB transaction BEGIN might not be issued if DBManager handles atomicity per call.
        """
        # For psycopg2, transactions are implicitly started with the first SQL command.
        # No explicit BEGIN is strictly necessary unless managing multiple statements
        # outside of DatabaseManager's individual execute/fetch methods.
        logger.info(f"Entering transactional block {transaction_id}.")

    def commit(self, db: DatabaseManager, transaction_id: uuid.UUID):
        """
        Log the successful completion of a conceptual transaction block.
        Actual DB COMMIT is handled by DatabaseManager.execute for DML/DDL.
        """
        # DatabaseManager.execute() already commits.
        # If multiple DML operations were grouped and needed a single commit,
        # DatabaseManager would need an explicit commit method and suppression of auto-commit in execute.
        logger.info(f"Transactional block {transaction_id} completed successfully.")

    def rollback(self, db: DatabaseManager, transaction_id: uuid.UUID):
        """
        Log the rollback of a conceptual transaction block.
        Actual DB ROLLBACK is handled by DatabaseManager.execute on error.
        """
        # DatabaseManager.execute() already rolls back on error.
        logger.warning(f"Transactional block {transaction_id} rolled back due to an error.")


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
    db = DatabaseManager()
    handler = TransactionHandler()
    transaction_id = uuid.uuid4()
    
    logger.debug(f"Entering transaction context {transaction_id}.")
    handler.begin(db, transaction_id)
    try:
        yield db
        handler.commit(db, transaction_id)
    except Exception as exc:
        handler.rollback(db, transaction_id)
        logger.error(f"Error within transaction context {transaction_id}: {exc}", exc_info=True)
        raise
