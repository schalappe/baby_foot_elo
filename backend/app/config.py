# -*- coding: utf-8 -*-
"""
Module containing configuration class.
"""

from os import environ


class Config:
    def __init__(self):
        """
        Initialize a new configuration object.

        The environment variable ENV is used to select between the development and production environments.
        If ENV is not set, the development environment is assumed.
        """
        self.env = environ.get("ENV", "dev")

    def get_db_url(self):
        """
        Return the URL of the DuckDB database to use.

        Returns
        -------
        str
            The URL of the DuckDB database to use.

        Raises
        ------
        ValueError
            If the environment is invalid.
        """
        if self.env == "dev":
            return "duckdb://:memory:"
        if self.env == "prod":
            return environ.get("DB_URL")
        raise ValueError("Invalid environment")


config = Config()
