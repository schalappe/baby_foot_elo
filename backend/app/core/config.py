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
    the application is running.

    Attributes
    ----------
    supabase_url : str | None
        URL of the Supabase project.
    supabase_key : str | None
        Supabase API key (typically the anon key or service role key).
    frontend_url : str
        URL of the frontend application.
    """

    def __init__(self):
        """
        Initialize a new configuration object.

        Supabase connection details are loaded from environment variables.
        """
        self.supabase_url = environ.get("SUPABASE_URL")
        self.supabase_key = environ.get("SUPABASE_KEY")

    @property
    def frontend_url(self):
        """
        URL of the frontend application.
        """
        return environ.get("FRONTEND_URL", "http://localhost:3000")
