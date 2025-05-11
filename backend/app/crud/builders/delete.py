# -*- coding: utf-8 -*-
"""
Query builder for constructing DELETE SQL queries.
"""

from typing import Any, List, Tuple

from .base import BaseQueryBuilder


class DeleteQueryBuilder(BaseQueryBuilder):
    """
    Query builder for constructing DELETE SQL queries.
    """

    def build(self) -> Tuple[str, List[Any]]:
        """
        Build the DELETE SQL query and parameters.

        Returns
        -------
        Tuple[str, List[Any]]
            SQL query string and list of parameters.
        """
        query = f"DELETE FROM {self.base_table}"
        if self.where_clauses:
            query += " WHERE " + " AND ".join(self.where_clauses)
        return query, self.where_params
