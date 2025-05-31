# -*- coding: utf-8 -*-
"""
Database Manager for Supabase connections.
"""

from supabase import Client, create_client

from app.core import config

SUPABASE_URL = config.supabase_url
SUPABASE_KEY = config.supabase_key

if not all([SUPABASE_URL, SUPABASE_KEY]):
    raise EnvironmentError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
