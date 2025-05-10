# -*- coding: utf-8 -*-
"""
Schema definitions for the players table.
"""

CREATE_SEQ_PLAYERS = """
CREATE SEQUENCE IF NOT EXISTS seq_players_id;
"""

CREATE_PLAYERS_TABLE = """
CREATE TABLE IF NOT EXISTS Players (
    player_id INTEGER PRIMARY KEY DEFAULT nextval('seq_players_id'),
    name VARCHAR NOT NULL,
    global_elo INTEGER NOT NULL DEFAULT 1000,
    current_month_elo INTEGER NOT NULL DEFAULT 1000,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_INDEX_PLAYERS_NAME = """
CREATE INDEX IF NOT EXISTS idx_players_name ON Players(name);
"""
