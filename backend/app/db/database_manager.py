# -*- coding: utf-8 -*-
"""
Database Manager for DuckDB connections.
"""

import threading
from logging import getLogger
from typing import Any, Dict, List, Optional, Tuple, Union

import duckdb

from . import schema_definitions


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
        self.logger = getLogger("DatabaseManager")
        self._initialized = True
        self.connect()

    def connect(self):
        """
        Establish a connection to the DuckDB database.
        """
        try:
            self.connection = duckdb.connect(self.db_path, **self.conn_params)
            self.logger.info(f"Connected to DuckDB at {self.db_path}")
        except Exception as exc:
            self.logger.error(f"Failed to connect to DuckDB: {exc}")
            raise

    def _ensure_connection(method):
        """
        Decorator to ensure a connection exists before executing a method.
        """

        def wrapper(self, *args, **kwargs):
            if self.connection is None:
                self.connect()
            return method(self, *args, **kwargs)

        return wrapper

    def initialize_database(self):
        """
        Initialize the database: create all tables if they do not exist, and handle future migrations.
        This method is idempotent and can be safely called multiple times.
        """

        schemas = [
            schema_definitions.CREATE_PLAYERS_TABLE,
            schema_definitions.CREATE_TEAMS_TABLE,
            schema_definitions.CREATE_MATCHES_TABLE,
            schema_definitions.CREATE_ELO_HISTORY_TABLE,
            schema_definitions.CREATE_PERIODIC_RANKINGS_TABLE,
            schema_definitions.CREATE_TEAM_PERIODIC_RANKINGS_TABLE,
        ]
        for sql in schemas:
            try:
                self.execute(sql)
                self.logger.info(f"Executed schema statement: {sql.splitlines()[0]}")
            except Exception as exc:
                self.logger.error(f"Error executing schema statement: {exc}\nSQL: {sql}")
                raise

        self.logger.info("Database initialization complete. (No migrations applied)")

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
            self.logger.debug(f"Executed query: {query} | Params: {params}")
            return result
        except Exception as exc:
            self.logger.error(f"Query execution failed: {exc}\nQuery: {query}\nParams: {params}")
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
        cur = self.execute(query, params)
        return cur.fetchall()

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
        cur = self.execute(query, params)
        return cur.fetchone()

    def begin(self):
        """
        Begin a transaction.
        """
        self.execute("BEGIN;")
        self.logger.debug("Transaction started.")

    def commit(self):
        """
        Commit a transaction.
        """
        self.execute("COMMIT;")
        self.logger.debug("Transaction committed.")

    def rollback(self):
        """
        Rollback a transaction.
        """
        self.execute("ROLLBACK;")
        self.logger.debug("Transaction rolled back.")

    def close(self):
        """
        Close the database connection.
        """
        if self.connection:
            self.connection.close()
            self.logger.info("DuckDB connection closed.")
            self.connection = None

    def __del__(self):
        """
        Close the database connection when the object is destroyed.
        """
        self.close()
