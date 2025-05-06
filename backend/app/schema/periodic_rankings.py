# -*- coding: utf-8 -*-
"""
Schema definitions for periodic player rankings table.
"""

CREATE_SEQ_PERIODIC_RANKINGS = """
CREATE SEQUENCE IF NOT EXISTS seq_periodic_rankings_id;
"""

CREATE_PERIODIC_RANKINGS_TABLE = """
CREATE TABLE IF NOT EXISTS Periodic_Rankings (
    ranking_id INTEGER PRIMARY KEY DEFAULT nextval('seq_periodic_rankings_id'), -- Unique ranking record, auto-incrementing
    player_id INTEGER NOT NULL,                   -- Foreign key to Players
    period TEXT NOT NULL,                         -- Period (e.g., '2025-W18')
    ranking INTEGER NOT NULL,                     -- Player's rank in this period
    elo_score REAL NOT NULL,                      -- ELO score at period end
    FOREIGN KEY (player_id) REFERENCES Players(player_id)
);
"""

CREATE_INDEX_PERIODIC_PLAYER = """
CREATE INDEX IF NOT EXISTS idx_periodic_player_id ON Periodic_Rankings(player_id);
"""

CREATE_INDEX_PERIODIC_PERIOD_PLAYER = """
CREATE INDEX IF NOT EXISTS idx_periodic_period_player ON Periodic_Rankings(period, player_id);
"""
