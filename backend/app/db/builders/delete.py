# -*- coding: utf-8 -*-
"""
Query builder for constructing DELETE SQL queries.
"""

from typing import Any, List, Tuple

from app.db.builders.base import BaseQueryBuilder


class DeleteQueryBuilder(BaseQueryBuilder):
    """
    Query builder for constructing DELETE SQL queries.
    """

    def build(self) -> Tuple[str, List[Any]]:
        """
        Build the DELETE SQL query and parameters for PostgreSQL.

        Returns
        -------
        Tuple[str, List[Any]]
            SQL query string and list of parameters.
        """
        query = f"DELETE FROM {self.base_table}"
        params: List[Any] = []

        if self.where_clauses:
            raw_where_query_part = " AND ".join(self.where_clauses)
            formatted_where_clause_str, where_params_for_query, _ = self._format_query_with_indexed_placeholders(
                raw_where_query_part, self.where_params
            )

            if formatted_where_clause_str:
                query += f" WHERE {formatted_where_clause_str}"
                params.extend(where_params_for_query)

        return query, params
