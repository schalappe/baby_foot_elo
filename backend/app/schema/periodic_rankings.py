# -*- coding: utf-8 -*-
"""
Schema definitions for periodic player rankings table.
"""

CREATE_SEQ_PERIODIC_RANKINGS = """
CREATE SEQUENCE IF NOT EXISTS seq_periodic_rankings_id;
"""

CREATE_PERIODIC_RANKINGS_TABLE = """
CREATE TABLE IF NOT EXISTS Periodic_Rankings (
    ranking_id INTEGER PRIMARY KEY DEFAULT nextval('seq_periodic_rankings_id'),
    player_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day INTEGER NOT NULL,
    initial_elo INTEGER NOT NULL,
    final_elo INTEGER NOT NULL,
    ranking INTEGER NOT NULL,
    matches_played INTEGER NOT NULL,
    wins INTEGER NOT NULL,
    losses INTEGER NOT NULL,
    FOREIGN KEY (player_id) REFERENCES Players(player_id) ON DELETE CASCADE,
    UNIQUE (player_id, year, month, day)
);
"""

CREATE_INDEX_PERIODIC_RANKINGS_PLAYER_ID = """
CREATE INDEX IF NOT EXISTS idx_periodic_rankings_player_id ON Periodic_Rankings(player_id);
"""

CREATE_INDEX_PERIODIC_RANKINGS_PERIOD = """
CREATE INDEX IF NOT EXISTS idx_periodic_rankings_period ON Periodic_Rankings(player_id, year, month);
"""
