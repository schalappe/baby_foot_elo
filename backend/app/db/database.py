# -*- coding: utf-8 -*-
"""
Database Manager for PostgreSQL connections.
"""

import threading
from typing import Dict, List, Optional, Tuple, Union

import psycopg2
from loguru import logger
from psycopg2 import pool
from psycopg2.extras import DictCursor

from app.core.config import config


class DatabaseManager:
    """
    Manages PostgreSQL connections using a connection pool, query execution, and transactions.
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

    def __init__(self, min_conn=1, max_conn=10, **conn_params):
        """
        Initialize the database manager and its connection pool.

        Parameters
        ----------
        min_conn : int, optional
            Minimum number of connections in the pool, by default 1.
        max_conn : int, optional
            Maximum number of connections in the pool, by default 10.
        conn_params : dict
            Additional connection parameters for psycopg2.connect().
        """
        if getattr(self, "_initialized", False):
            return

        self.db_user = config.db_user
        self.db_password = config.db_password
        self.db_host = config.db_host
        self.db_port = config.db_port
        self.db_name = config.db_name

        self.conn_params = conn_params
        self.pool = None
        self._initialized = True
        self._initialize_pool(min_conn, max_conn)

    def _initialize_pool(self, min_conn: int, max_conn: int):
        """
        Initialize the PostgreSQL connection pool.

        Parameters
        ----------
        min_conn : int
            Minimum number of connections in the pool.
        max_conn : int
            Maximum number of connections in the pool.

        Raises
        -----
        ValueError
            If any of the required database connection parameters are not set.
        psycopg2.Error
            If an error occurs while initializing the connection pool.
        """
        try:
            if self.db_user and self.db_password and self.db_host and self.db_port and self.db_name:
                self.pool = pool.SimpleConnectionPool(
                    min_conn,
                    max_conn,
                    user=self.db_user,
                    password=self.db_password,
                    host=self.db_host,
                    port=self.db_port,
                    dbname=self.db_name,
                    **self.conn_params,
                )

                base = f"{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
                logger.info(f"PostgreSQL connection pool initialized (min: {min_conn}, max: {max_conn}) for {base}.")
            else:
                error_msg = (
                    "Database connection details are not sufficiently set for pooling. "
                    "Ensure DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME are set in config."
                )
                logger.error(error_msg)
                raise ValueError(error_msg)
        except (psycopg2.Error, pool.PoolError) as exc:
            logger.error("Failed to initialize PostgreSQL connection pool: %s", exc)
            raise

    def execute(self, query: str, params: Optional[Union[List, Tuple, Dict]] = None) -> None:
        """
        Execute a SQL query (typically DDL or DML like INSERT, UPDATE, DELETE).
        Commits the transaction on the acquired connection.

        Parameters
        ----------
        query : str
            SQL query to execute.
        params : Optional[Union[List, Tuple, Dict]], optional
            Parameters for the query, defaults to None.
        """
        conn = None
        try:
            conn = self.pool.getconn()
            with conn.cursor() as cur:
                cur.execute(query, params)
            conn.commit()
            logger.debug("Executed query and committed: %s | Params: %s", query, params)
        except (psycopg2.Error, pool.PoolError) as exc:
            logger.error("Query execution failed: %s\nQuery: %s\nParams: %s", exc, query, params)
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                self.pool.putconn(conn)

    def fetchall(self, query: str, params: Optional[Union[List, Tuple, Dict]] = None) -> List[Tuple]:
        """
        Fetch all rows from a SELECT query result using a connection from the pool.

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
        conn = None
        try:
            conn = self.pool.getconn()
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(query, params)
                result = cur.fetchall()
            logger.debug("Fetched all from query: %s | Params: %s", query, params)
            return result
        except (psycopg2.Error, pool.PoolError) as exc:
            logger.error("Fetch all failed: %s\nQuery: %s\nParams: %s", exc, query, params)
            if conn and not conn.closed and conn.status != psycopg2.extensions.STATUS_READY:
                conn.rollback()
            raise
        finally:
            if conn:
                self.pool.putconn(conn)

    def fetchone(self, query: str, params: Optional[Union[List, Tuple, Dict]] = None) -> Optional[Tuple]:
        """
        Fetch a single row from a SELECT query result using a connection from the pool.

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
        conn = None
        try:
            conn = self.pool.getconn()
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(query, params)
                result = cur.fetchone()
            logger.debug("Fetched one from query: %s | Params: %s", query, params)
            return result
        except (psycopg2.Error, pool.PoolError) as exc:
            logger.error("Fetch one failed: %s\nQuery: %s\nParams: %s", exc, query, params)
            if conn and not conn.closed and conn.status != psycopg2.extensions.STATUS_READY:
                conn.rollback()
            raise
        finally:
            if conn:
                self.pool.putconn(conn)

    def close(self):
        """
        Close all connections in the pool.
        """
        if self.pool:
            self.pool.closeall()
            logger.info("PostgreSQL connection pool closed.")
            self.pool = None

    def __del__(self):
        """
        Close the connection pool when the object is destroyed.
        """
        self.close()
