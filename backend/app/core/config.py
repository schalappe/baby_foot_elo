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
    db_url : str
        The URL of the PostgreSQL database to use.
    frontend_url : str
        The URL of the frontend application.
    """

    @property
    def db_url(self):
        """
        The URL of the PostgreSQL database to use.

        Returns
        -------
        str
            The URL of the PostgreSQL database to use.

        Raises
        ------
        ValueError
            If the database URL is not set.
        """
        db_url = environ.get("DATABASE_URL")
        if not db_url:
            raise ValueError("DATABASE_URL environment variable must be set.")
        return db_url

    @property
    def frontend_url(self):
        """
        The URL of the frontend application.

        Returns
        -------
        str
            The URL of the frontend application.
        """
        return environ.get("FRONTEND_URL", "http://localhost:3000")
