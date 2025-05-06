# -*- coding: utf-8 -*-
"""
Schema definitions for the players table.
"""

CREATE_SEQ_PLAYERS = """
CREATE SEQUENCE IF NOT EXISTS seq_players_id;
"""

CREATE_PLAYERS_TABLE = """
CREATE TABLE IF NOT EXISTS Players (
    player_id INTEGER PRIMARY KEY DEFAULT nextval('seq_players_id'),  -- Unique player identifier, auto-incrementing
    name TEXT NOT NULL,                          -- Player's full name
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Creation timestamp
);
"""

CREATE_INDEX_PLAYERS_NAME = """
CREATE INDEX IF NOT EXISTS idx_players_name ON Players(name);
"""
