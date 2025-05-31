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
    database_url_env : str | None
        Full database connection URL from the DATABASE_URL environment variable (can be derived).
    db_user : str | None
        Database user.
    db_password : str | None
        Database password.
    db_host : str | None
        Database host.
    db_port : str | None
        Database port.
    db_name : str | None
        Database name.
    frontend_url : str
        URL of the frontend application.
    """

    def __init__(self):
        """
        Initialize a new configuration object.

        The database connection URL is loaded from the DATABASE_URL environment variable.
        """
        self.db_user = environ.get("DB_USER")
        self.db_password = environ.get("DB_PASSWORD")
        self.db_host = environ.get("DB_HOST")
        self.db_port = environ.get("DB_PORT")
        self.db_name = environ.get("DB_NAME")

    @property
    def frontend_url(self):
        """
        URL of the frontend application.
        """
        return environ.get("FRONTEND_URL", "http://localhost:3000")
