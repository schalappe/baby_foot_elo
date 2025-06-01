# -*- coding: utf-8 -*-
"""
Database module.

Expose the core database functionalities:
- Supabase client
- Database initialization
"""

from app.db.database import supabase
from app.db.initializer import initialize_database

__all__ = ["supabase", "initialize_database"]
