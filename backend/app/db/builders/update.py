# -*- coding: utf-8 -*-
"""
Query builder for constructing UPDATE SQL queries.
"""

from __future__ import annotations

from typing import Any, List, Tuple

from app.db.builders.base import BaseQueryBuilder


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
        self.update_fields_values: List[Tuple[str, Any]] = []  # Stores (field, value) tuples

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
            self.update_fields_values.append((k, v))
        return self

    def build(self) -> Tuple[str, List[Any]]:
        """
        Build the UPDATE SQL query and parameters for PostgreSQL.

        Returns
        -------
        Tuple[str, List[Any]]
            SQL query string and list of parameters.

        Raises
        ------
        ValueError
            If no fields are set for update.
        """
        if not self.update_fields_values:
            raise ValueError("No fields provided for UPDATE operation.")

        params: List[Any] = []
        set_clause_parts: List[str] = []
        current_param_idx = 1

        for field, value in self.update_fields_values:
            set_clause_parts.append(f"{field} = ${current_param_idx}")
            params.append(value)
            current_param_idx += 1

        set_clause_str = ", ".join(set_clause_parts)
        query = f"UPDATE {self.base_table} SET {set_clause_str}"

        if self.where_clauses:
            if self.where_clauses:
                raw_where_query_part = " AND ".join(self.where_clauses)
                formatted_where_clause_str, where_params_for_query, _ = self._format_query_with_indexed_placeholders(
                    raw_where_query_part, self.where_params, current_param_idx
                )

                if formatted_where_clause_str:
                    query += f" WHERE {formatted_where_clause_str}"
                    params.extend(where_params_for_query)

        return query, params
