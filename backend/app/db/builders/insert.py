# -*- coding: utf-8 -*-
"""
Query builder for constructing INSERT SQL queries.
"""

from __future__ import annotations

from typing import Any, List, Tuple

from app.db.builders.base import BaseQueryBuilder


class InsertQueryBuilder(BaseQueryBuilder):
    """
    Query builder for constructing INSERT SQL queries.
    """

    def __init__(self, base_table: str, returning_column: Optional[str] = None):
        """
        Initialize an InsertQueryBuilder instance.

        Parameters
        ----------
        base_table : str
            The table to insert into.
        """
        super().__init__(base_table)
        self.fields: List[str] = []
        self.values: List[Any] = []
        self.returning_column: Optional[str] = returning_column

    def set(self, **field_values) -> InsertQueryBuilder:
        """
        Set the fields and values for the INSERT statement.

        Parameters
        ----------
        **field_values : dict
            Field-value pairs to insert.

        Returns
        -------
        InsertQueryBuilder
            Self for method chaining.
        """
        for k, v in field_values.items():
            self.fields.append(k)
            self.values.append(v)
        return self

    def build(self) -> Tuple[str, List[Any]]:
        """
        Build the INSERT SQL query and parameters.

        Returns
        -------
        Tuple[str, List[Any]]
            SQL query string and list of parameters.
        """
        if not self.fields:
            return "", []

        placeholders = ", ".join([f"${i+1}" for i in range(len(self.fields))])
        fields_str = ", ".join(self.fields)
        query = f"INSERT INTO {self.base_table} ({fields_str}) VALUES ({placeholders})"

        if self.returning_column:
            query += f" RETURNING {self.returning_column}"

        return query, self.values
