# -*- coding: utf-8 -*-
"""
Schema definitions for the players table.
"""

CREATE_PLAYERS_TABLE = """
CREATE TABLE IF NOT EXISTS Players (
    player_id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    global_elo INTEGER NOT NULL DEFAULT 1000,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_INDEX_PLAYERS_NAME = """
CREATE INDEX IF NOT EXISTS idx_players_name ON Players(name);
"""
