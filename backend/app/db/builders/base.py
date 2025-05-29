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
        self, query_template: str, params: List[Any], start_index: int = 1
    ) -> Tuple[str, List[Any], int]:
        """
        Replaces '?' placeholders in a query template with '$n' style placeholders
        and reorders parameters accordingly.

        Parameters
        ----------
        query_template : str
            The SQL query template with '?' placeholders.
        params : List[Any]
            A list of parameters corresponding to the '?' placeholders.
        start_index : int, optional
            The starting index for the '$n' placeholders (default is 1).

        Returns
        -------
        Tuple[str, List[Any], int]
            A tuple containing:
            - The formatted query string with '$n' placeholders.
            - The list of parameters (can be the same if order doesn't change, but returned for consistency).
            - The next available parameter index.
        """
        parts = query_template.split("?")
        if len(parts) - 1 != len(params):
            raise ValueError("Mismatch between '?' placeholders and number of parameters provided.")

        formatted_query = ""
        current_param_idx = start_index
        param_list_for_clause = []

        for i, part in enumerate(parts):
            formatted_query += part
            if i < len(params):
                formatted_query += f"${current_param_idx}"
                param_list_for_clause.append(params[i])
                current_param_idx += 1

        return formatted_query, param_list_for_clause, current_param_idx

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

    def execute(
        self, fetch_all: bool = True
    ) -> Union[List[Tuple], Optional[Tuple], Any, int]:  # Added Any for returning_column case
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
