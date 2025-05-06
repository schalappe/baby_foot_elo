# -*- coding: utf-8 -*-
"""
Database Manager for DuckDB connections.
"""

import threading
from logging import getLogger
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import duckdb

logger = getLogger(__name__)


class DatabaseManager:
    """
    Manages DuckDB connections, query execution, and transactions.
    Supports configuration for file path and connection parameters.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_path: str = ":memory:", **conn_params):
        """
        Singleton pattern for connection pooling if desired
        """
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(DatabaseManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_path: str = ":memory:", **conn_params):
        """
        Initialize a new database connection.

        Parameters
        ----------
        db_path : str
            Path to the DuckDB database file.
        conn_params : dict
            Connection parameters for DuckDB.
        """
        if getattr(self, "_initialized", False):
            return
        self.db_path = db_path
        self.conn_params = conn_params
        self.connection = None
        self._initialized = True
        self.connect()

    def connect(self):
        """
        Establish a connection to the DuckDB database.
        """
        try:
            self.connection = duckdb.connect(self.db_path, **self.conn_params)
            logger.info("Connected to DuckDB at %s", self.db_path)
        except Exception as exc:
            logger.error("Failed to connect to DuckDB: %s", exc)
            raise

    # pylint: disable=no-self-argument
    def _ensure_connection(method: Callable):
        """
        Decorator to ensure a connection exists before executing a method.
        """

        def wrapper(self, *args, **kwargs):
            if self.connection is None:
                self.connect()
            return method(self, *args, **kwargs)

        return wrapper

    @_ensure_connection
    def execute(self, query: str, params: Optional[Union[List, Tuple, Dict]] = None) -> Any:
        """
        Execute a SQL query.

        Parameters
        ----------
        query : str
            SQL query to execute.
        params : Optional[Union[List, Tuple, Dict]], optional
            Parameters for the query, defaults to None.

        Returns
        -------
        Any
            Result of the query execution.
        """
        try:
            if params:
                result = self.connection.execute(query, params)
            else:
                result = self.connection.execute(query)
            logger.debug("Executed query: %s | Params: %s", query, params)
            return result
        except Exception as exc:
            logger.error("Query execution failed: %s\nQuery: %s\nParams: %s", exc, query, params)
            raise

    @_ensure_connection
    def fetchall(
        self, query: str, params: Optional[Union[List, Tuple, Dict]] = None
    ) -> List[Tuple]:
        """
        Fetch all rows from a query result.

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
        cur = self.execute(query, params)
        return cur.fetchall()

    @_ensure_connection
    def fetchone(
        self, query: str, params: Optional[Union[List, Tuple, Dict]] = None
    ) -> Optional[Tuple]:
        """
        Fetch a single row from a query result.

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
        cur = self.execute(query, params)
        return cur.fetchone()

    def close(self):
        """
        Close the database connection.
        """
        if self.connection:
            self.connection.close()
            logger.info("DuckDB connection closed.")
            self.connection = None

    def __del__(self):
        """
        Close the database connection when the object is destroyed.
        """
        self.close()
