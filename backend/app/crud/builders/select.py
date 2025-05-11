# -*- coding: utf-8 -*-
"""
Query builder for constructing SELECT SQL queries.
"""

from __future__ import annotations

from typing import Any, List, Tuple

from .base import BaseQueryBuilder


class SelectQueryBuilder(BaseQueryBuilder):
    """
    Query builder for constructing SELECT SQL queries.
    """

    def __init__(self, base_table: str):
        """
        Initialize a SelectQueryBuilder instance.

        Parameters
        ----------
        base_table : str
            The table to select from.
        """
        super().__init__(base_table)
        self.select_fields = ["*"]
        self.joins = []
        self.order_by = None
        self.limit_val = None
        self.offset_val = None
        self.group_by = None

    def select(self, *fields) -> SelectQueryBuilder:
        """
        Set the fields to select.

        Parameters
        ----------
        *fields : str
            Fields to select. If not provided, selects all fields.

        Returns
        -------
        SelectQueryBuilder
            Self for method chaining.
        """
        self.select_fields = fields if fields else ["*"]
        return self

    def join(self, table: str, on: str) -> SelectQueryBuilder:
        """
        Add a JOIN clause.

        Parameters
        ----------
        table : str
            Table to join.
        on : str
            Join condition.

        Returns
        -------
        SelectQueryBuilder
            Self for method chaining.
        """
        self.joins.append(f"JOIN {table} ON {on}")
        return self

    def left_join(self, table: str, on: str) -> SelectQueryBuilder:
        """
        Add a LEFT JOIN clause.

        Parameters
        ----------
        table : str
            Table to join.
        on : str
            Join condition.

        Returns
        -------
        SelectQueryBuilder
            Self for method chaining.
        """
        self.joins.append(f"LEFT JOIN {table} ON {on}")
        return self

    def order_by_clause(self, clause: str) -> SelectQueryBuilder:
        """
        Add an ORDER BY clause.

        Parameters
        ----------
        clause : str
            ORDER BY expression.

        Returns
        -------
        SelectQueryBuilder
            Self for method chaining.
        """
        self.order_by = clause
        return self

    def limit(self, limit: int) -> SelectQueryBuilder:
        """
        Add a LIMIT clause.

        Parameters
        ----------
        limit : int
            Maximum number of rows to return.

        Returns
        -------
        SelectQueryBuilder
            Self for method chaining.
        """
        self.limit_val = limit
        return self

    def offset(self, offset: int) -> SelectQueryBuilder:
        """
        Add an OFFSET clause.

        Parameters
        ----------
        offset : int
            Number of rows to skip.

        Returns
        -------
        SelectQueryBuilder
            Self for method chaining.
        """
        self.offset_val = offset
        return self

    def group_by_clause(self, clause: str) -> SelectQueryBuilder:
        """
        Add a GROUP BY clause.

        Parameters
        ----------
        clause : str
            GROUP BY expression.

        Returns
        -------
        SelectQueryBuilder
            Self for method chaining.
        """
        self.group_by = clause
        return self

    def build(self) -> Tuple[str, List[Any]]:
        """
        Build the SELECT SQL query and parameters.

        Returns
        -------
        Tuple[str, List[Any]]
            SQL query string and list of parameters.
        """
        query = f"SELECT {', '.join(map(str, self.select_fields))} FROM {self.base_table}"
        if self.joins:
            query += " " + " ".join(self.joins)
        if self.where_clauses:
            query += " WHERE " + " AND ".join(self.where_clauses)
        if self.group_by:
            query += f" GROUP BY {self.group_by}"
        if self.order_by:
            query += f" ORDER BY {self.order_by}"
        if self.limit_val is not None:
            query += f" LIMIT {self.limit_val}"
        if self.offset_val is not None:
            query += f" OFFSET {self.offset_val}"
        return query, self.where_params
