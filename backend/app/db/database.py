# -*- coding: utf-8 -*-
"""
Database Manager for PostgreSQL connections.
"""

import threading
from typing import Any, Dict, List, Optional, Tuple, Union

import psycopg2
from loguru import logger
from psycopg2.extras import RealDictCursor


class DatabaseManager:
    """
    Manages a singleton PostgreSQL connection using psycopg2.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """
        Singleton pattern for connection pooling if desired
        """
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(DatabaseManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_path: str):
        """
        Initialize a new database connection.

        Parameters
        ----------
        db_path : str
            Path to the database file.
        """
        if getattr(self, "_initialized", False):
            return
        self.connect(db_path)
        self._initialized = True
        logger.info("Connected to PostgreSQL at %s", db_path)

    def connect(self, db_path: str):
        """
        Connect to the database.

        Parameters
        ----------
        db_path : str
            Path to the database file.
        """
        try:
            self.connection = psycopg2.connect(db_path, cursor_factory=RealDictCursor)
        except Exception as exc:
            logger.error("Failed to connect to PostgreSQL: %s", exc)
            raise

    @property
    def cursor(self):
        """
        Get the cursor for the database connection.

        Returns
        -------
        cursor
            The cursor for the database connection.
        """
        if self.connection is None or self.connection.closed:
            self.connect()
        return self.connection.cursor()

    def close(self):
        """
        Close the database connection.
        """
        if self.connection and not self.connection.closed:
            self.connection.close()

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
                result = self.cursor.execute(query, params)
            else:
                result = self.cursor.execute(query)
            logger.debug("Executed query: %s | Params: %s", query, params)
            return result
        except Exception as exc:
            logger.error("Query execution failed: %s\nQuery: %s\nParams: %s", exc, query, params)
            raise

    @_ensure_connection
    def fetchall(self, query: str, params: Optional[Union[List, Tuple, Dict]] = None) -> List[Tuple]:
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
        return self.execute(query, params).fetchall()

    @_ensure_connection
    def fetchone(self, query: str, params: Optional[Union[List, Tuple, Dict]] = None) -> Optional[Tuple]:
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
        return self.execute(query, params).fetchone()

    def close(self):
        """
        Close the database connection.
        """
        if self.connection:
            self.connection.close()
            logger.info("PostgreSQL connection closed.")
            self.connection = None

    def __del__(self):
        """
        Close the database connection when the object is destroyed.
        """
        self.close()
