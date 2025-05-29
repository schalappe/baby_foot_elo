# -*- coding: utf-8 -*-
"""
Database Manager for DuckDB connections.
"""

import threading
from logging import getLogger
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import psycopg2
from psycopg2.extras import DictCursor

from backend.app.core.config import config

logger = getLogger(__name__)


class DatabaseManager:
    """
    Manages PostgreSQL connections, query execution, and transactions.
    Uses connection details from the global application configuration.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, **conn_params):
        """
        Singleton pattern for the database manager.
        """
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(DatabaseManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, **conn_params):
        """
        Initialize the database manager.

        Parameters
        ----------
        conn_params : dict
            Additional connection parameters for psycopg2.connect().
        """
        if getattr(self, "_initialized", False):
            return
        self.db_url = config.get_db_url()
        self.conn_params = conn_params
        self.connection = None
        self._initialized = True
        self.connect()

    def connect(self):
        """
        Establish a connection to the PostgreSQL database.
        """
        try:
            self.connection = psycopg2.connect(dsn=self.db_url, **self.conn_params)
            logger.info("Connected to PostgreSQL database.")
        except psycopg2.Error as exc:
            logger.error("Failed to connect to PostgreSQL: %s", exc)
            raise

    # pylint: disable=no-self-argument
    def _ensure_connection(method: Callable):
        """
        Decorator to ensure a connection exists before executing a method.
        """

        def wrapper(self, *args, **kwargs):
            if self.connection is None or self.connection.closed:
                self.connect()
            return method(self, *args, **kwargs)

        return wrapper

    @_ensure_connection
    def execute(self, query: str, params: Optional[Union[List, Tuple, Dict]] = None) -> None:
        """
        Execute a SQL query (typically DDL or DML like INSERT, UPDATE, DELETE).
        Commits the transaction.

        Parameters
        ----------
        query : str
            SQL query to execute.
        params : Optional[Union[List, Tuple, Dict]], optional
            Parameters for the query, defaults to None.
        """
        try:
            with self.connection.cursor() as cur:
                cur.execute(query, params)
            self.connection.commit()
            logger.debug("Executed query and committed: %s | Params: %s", query, params)
        except psycopg2.Error as exc:
            logger.error("Query execution failed: %s\nQuery: %s\nParams: %s", exc, query, params)
            self.connection.rollback()
            raise

    @_ensure_connection
    def fetchall(self, query: str, params: Optional[Union[List, Tuple, Dict]] = None) -> List[Tuple]:
        """
        Fetch all rows from a SELECT query result.

        Parameters
        ----------
        query : str
            SQL query to execute.
        params : Optional[Union[List, Tuple, Dict]], optional
            Parameters for the query, defaults to None.

        Returns
        -------
        List[Tuple]
            List of tuples containing the query results.
        """
        try:
            with self.connection.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(query, params)
                result = cur.fetchall()
            logger.debug("Fetched all from query: %s | Params: %s", query, params)
            return result
        except psycopg2.Error as exc:
            logger.error("Fetch all failed: %s\nQuery: %s\nParams: %s", exc, query, params)
            raise

    @_ensure_connection
    def fetchone(self, query: str, params: Optional[Union[List, Tuple, Dict]] = None) -> Optional[Tuple]:
        """
        Fetch a single row from a SELECT query result.

        Parameters
        ----------
        query : str
            SQL query to execute.
        params : Optional[Union[List, Tuple, Dict]], optional
            Parameters for the query, defaults to None.

        Returns
        -------
        Optional[Tuple]
            Single tuple containing the query result, or None if no result.
        """
        try:
            with self.connection.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(query, params)
                result = cur.fetchone()
            logger.debug("Fetched one from query: %s | Params: %s", query, params)
            return result
        except psycopg2.Error as exc:
            logger.error("Fetch one failed: %s\nQuery: %s\nParams: %s", exc, query, params)
            raise

    def close(self):
        """
        Close the database connection.
        """
        if self.connection and not self.connection.closed:
            self.connection.close()
            logger.info("PostgreSQL connection closed.")
            self.connection = None

    def __del__(self):
        """
        Close the database connection when the object is destroyed.
        """
        self.close()
