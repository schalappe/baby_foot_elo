# -*- coding: utf-8 -*-
"""
Query builder for constructing SQL queries.
"""

from __future__ import annotations

from typing import Any, List, Optional, Tuple, Union

from loguru import logger

from app.db.session import transaction


class BaseQueryBuilder:
    """
    Base class for constructing SQL queries (common logic for all CRUD operations).
    """

    def __init__(self, base_table: str):
        """
        Initialize the base query builder.

        Parameters
        ----------
        base_table : str
            The table to operate on.
        """
        self.base_table = base_table
        self.where_clauses = []
        self.where_params = []

    def where(self, clause: str, *params) -> "BaseQueryBuilder":
        """
        Add a WHERE clause.

        Parameters
        ----------
        clause : str
            WHERE condition.
        *params : Any
            Parameters for the condition.

        Returns
        -------
        BaseQueryBuilder
            Self for method chaining.
        """
        self.where_clauses.append(clause)
        self.where_params.extend(params)
        return self

    def build(self) -> Tuple[str, List[Any]]:
        """
        Build the SQL query and parameters. To be implemented in subclasses.

        Returns
        -------
        Tuple[str, List[Any]]
            SQL query string and list of parameters.

        Raises
        ------
        NotImplementedError
            If not implemented in subclasses.
        """
        raise NotImplementedError

    def execute(self, fetch_all: bool = True) -> Union[List[Tuple], Optional[Tuple], int]:
        """
        Build and execute the query.

        Parameters
        ----------
        fetch_all : bool, optional
            Whether to fetch all results or just one (only for SELECT), by default True.

        Returns
        -------
        Union[List[Tuple], Optional[Tuple], int]
            Query results or affected row count (for non-SELECT).
        """
        query, params = self.build()

        try:
            with transaction() as db_manager:
                if hasattr(self, "select_fields"):
                    if fetch_all:
                        return db_manager.fetchall(query, params)
                    return db_manager.fetchone(query, params)
                return db_manager.execute(query, params)
        except Exception as exc:
            logger.error(f"Failed to execute query: {exc}")
            return []
