# -*- coding: utf-8 -*-
"""
QueryBuilder class for constructing SQL queries.
"""

from typing import Any, List, Optional, Tuple, Union

from app.db import DatabaseManager


class QueryBuilder:
    """
    Query builder for constructing complex SQL queries.
    """

    def __init__(self, base_table: str):
        """
        Initialize a new query builder.

        Parameters
        ----------
        base_table : str
            Base table for the query
        """
        self.base_table = base_table
        self.select_fields = ["*"]
        self.joins = []
        self.where_clauses = []
        self.where_params = []
        self.order_by = None
        self.limit_val = None
        self.offset_val = None
        self.group_by = None

    def select(self, *fields) -> "QueryBuilder":
        """
        Set the fields to select.

        Parameters
        ----------
        *fields : str
            Fields to select

        Returns
        -------
        QueryBuilder
            Self for method chaining
        """
        self.select_fields = fields
        return self

    def join(self, table: str, on: str) -> "QueryBuilder":
        """
        Add a JOIN clause.

        Parameters
        ----------
        table : str
            Table to join
        on : str
            Join condition

        Returns
        -------
        QueryBuilder
            Self for method chaining
        """
        self.joins.append(f"JOIN {table} ON {on}")
        return self

    def left_join(self, table: str, on: str) -> "QueryBuilder":
        """
        Add a LEFT JOIN clause.

        Parameters
        ----------
        table : str
            Table to join
        on : str
            Join condition

        Returns
        -------
        QueryBuilder
            Self for method chaining
        """
        self.joins.append(f"LEFT JOIN {table} ON {on}")
        return self

    def where(self, clause: str, *params) -> "QueryBuilder":
        """
        Add a WHERE clause.

        Parameters
        ----------
        clause : str
            WHERE condition
        *params : Any
            Parameters for the condition

        Returns
        -------
        QueryBuilder
            Self for method chaining
        """
        self.where_clauses.append(clause)
        self.where_params.extend(params)
        return self

    def order_by_clause(self, clause: str) -> "QueryBuilder":
        """
        Add an ORDER BY clause.

        Parameters
        ----------
        clause : str
            ORDER BY expression

        Returns
        -------
        QueryBuilder
            Self for method chaining
        """
        self.order_by = clause
        return self

    def limit(self, limit: int) -> "QueryBuilder":
        """
        Add a LIMIT clause.

        Parameters
        ----------
        limit : int
            Maximum number of rows to return

        Returns
        -------
        QueryBuilder
            Self for method chaining
        """
        self.limit_val = limit
        return self

    def offset(self, offset: int) -> "QueryBuilder":
        """
        Add an OFFSET clause.

        Parameters
        ----------
        offset : int
            Number of rows to skip

        Returns
        -------
        QueryBuilder
            Self for method chaining
        """
        self.offset_val = offset
        return self

    def group_by_clause(self, clause: str) -> "QueryBuilder":
        """
        Add a GROUP BY clause.

        Parameters
        ----------
        clause : str
            GROUP BY expression

        Returns
        -------
        QueryBuilder
            Self for method chaining
        """
        self.group_by = clause
        return self

    def build(self) -> Tuple[str, List[Any]]:
        """
        Build the SQL query and parameters.

        Returns
        -------
        Tuple[str, List[Any]]
            SQL query string and list of parameters
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

    def execute(self, fetch_all: bool = True) -> Union[List[Tuple], Optional[Tuple]]:
        """
        Build and execute the query.

        Parameters
        ----------
        fetch_all : bool
            Whether to fetch all results or just one

        Returns
        -------
        Union[List[Tuple], Optional[Tuple]]
            Query results
        """
        db = DatabaseManager()
        query, params = self.build()

        if fetch_all:
            return db.fetchall(query, params)
        else:
            return db.fetchone(query, params)
