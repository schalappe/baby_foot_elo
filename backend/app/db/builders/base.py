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

    def _format_query_with_indexed_placeholders(
        self, query_template: str, params: List[Any]
    ) -> Tuple[str, List[Any], int]:
        """
        Replaces '?' placeholders in a query template with '%s' style placeholders
        suitable for psycopg2.

        Parameters
        ----------
        query_template : str
            The SQL query template with '?' placeholders.
        params : List[Any]
            A list of parameters corresponding to the '?' placeholders.

        Returns
        -------
        Tuple[str, List[Any], int]
            A tuple containing:
            - The formatted query string with '%s' placeholders.
            - The original list of parameters (psycopg2 handles them in order).
            - The count of parameters used (number of '%s' placeholders).
        """
        parts = query_template.split("?")
        if len(parts) - 1 != len(params):
            raise ValueError("Mismatch between '?' placeholders and number of parameters provided.")

        formatted_query = ""

        for i, part in enumerate(parts):
            formatted_query += part
            if i < len(params):
                formatted_query += "%s"

        return formatted_query, params, len(params)

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

    def execute(self, fetch_all: bool = True) -> Union[List[Tuple], Optional[Tuple], Any, int]:
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
                is_insert_with_returning = False
                if self.__class__.__name__ == "InsertQueryBuilder":
                    if getattr(self, "returning_column", None):
                        is_insert_with_returning = True

                if is_insert_with_returning:
                    result = db_manager.fetchone(query, params)
                    return result[0] if result else None
                elif hasattr(self, "select_fields"):
                    if fetch_all:
                        return db_manager.fetchall(query, params)
                    return db_manager.fetchone(query, params)
                else:
                    return db_manager.execute(query, params)
        except Exception as exc:
            logger.error(f"Failed to execute query: {exc}")
            return []
