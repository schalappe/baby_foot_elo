# -*- coding: utf-8 -*-
"""
Module containing configuration class.
"""

from os import environ

from dotenv import load_dotenv

load_dotenv()


class Config:
    """
    Configuration class for the application.

    The configuration object is responsible for storing information about the environment in which
    the application is running. It uses the environment variable ENV to select between the development
    and production environments. If ENV is not set, the development environment is assumed.

    Attributes
    ----------
    env : str
        The current environment (either "dev" or "prod").

    Methods
    -------
    get_db_url() -> str
        Return the URL of the DuckDB database to use.
    """

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

    def get_frontend_url(self):
        """
        Return the URL of the frontend application.

        Returns
        -------
        str
            The URL of the frontend application.
        """
        return environ.get("FRONTEND_URL", "http://localhost:3000")


config = Config()
