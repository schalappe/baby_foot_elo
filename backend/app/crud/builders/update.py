# -*- coding: utf-8 -*-
"""
Query builder for constructing UPDATE SQL queries.
"""

from __future__ import annotations

from typing import Any, List, Tuple

from .base import BaseQueryBuilder


class UpdateQueryBuilder(BaseQueryBuilder):
    """
    Query builder for constructing UPDATE SQL queries.
    """

    def __init__(self, base_table: str):
        """
        Initialize an UpdateQueryBuilder instance.

        Parameters
        ----------
        base_table : str
            The table to update.
        """
        super().__init__(base_table)
        self.set_clauses = []
        self.set_params = []

    def set(self, **field_values) -> UpdateQueryBuilder:
        """
        Set the fields and values for the UPDATE statement.

        Parameters
        ----------
        **field_values : dict
            Field-value pairs to update.

        Returns
        -------
        UpdateQueryBuilder
            Self for method chaining.
        """
        for k, v in field_values.items():
            self.set_clauses.append(f"{k} = ?")
            self.set_params.append(v)
        return self

    def build(self) -> Tuple[str, List[Any]]:
        """
        Build the UPDATE SQL query and parameters.

        Returns
        -------
        Tuple[str, List[Any]]
            SQL query string and list of parameters.
        """
        set_clause = ", ".join(self.set_clauses)
        query = f"UPDATE {self.base_table} SET {set_clause}"
        params = self.set_params.copy()
        if self.where_clauses:
            query += " WHERE " + " AND ".join(self.where_clauses)
            params.extend(self.where_params)
        return query, params
