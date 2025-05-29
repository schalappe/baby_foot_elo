# -*- coding: utf-8 -*-
"""
Module containing configuration class.
"""

from os import environ
from urllib.parse import quote_plus  # For password quoting

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
    database_url_env : str | None
        Full database connection URL from the DATABASE_URL environment variable.

    Methods
    -------
    get_db_url() -> str
        Return the URL of the PostgreSQL database to use.
    get_frontend_url() -> str
        Return the URL of the frontend application.
    """

    def __init__(self):
        """
        Initialize a new configuration object.

        The environment variable ENV is used to select between the development and production environments.
        If ENV is not set, the development environment is assumed.
        The database connection URL is loaded from the DATABASE_URL environment variable.
        """
        self.env = environ.get("ENV", "dev")
        self.database_url_env = environ.get("DATABASE_URL")

    def get_db_url(self) -> str:
        """
        Return the URL of the PostgreSQL database to use from the DATABASE_URL environment variable.

        Returns
        -------
        str
            The URL of the PostgreSQL database.

        Raises
        ------
        ValueError
            If the DATABASE_URL environment variable is not set.
        """
        if self.database_url_env:
            return self.database_url_env

        raise ValueError(
            "DATABASE_URL environment variable is not set. "
            "Please ensure it is configured in your .env file or environment."
        )

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
