# -*- coding: utf-8 -*-
"""
Schema definitions for the ELO history table.
"""

CREATE_SEQ_ELO_HISTORY = """
CREATE SEQUENCE IF NOT EXISTS seq_elo_history_id;
"""

CREATE_ELO_HISTORY_TABLE = """
CREATE TABLE IF NOT EXISTS ELO_History (
    history_id INTEGER PRIMARY KEY DEFAULT nextval('seq_elo_history_id'), -- Unique record identifier, auto-incrementing
    player_id INTEGER NOT NULL,                   -- Foreign key to Players
    match_id INTEGER NOT NULL,                    -- Foreign key to Matches
    elo_score REAL NOT NULL,                      -- ELO score after match
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Update timestamp
    FOREIGN KEY (player_id) REFERENCES Players(player_id),
    FOREIGN KEY (match_id) REFERENCES Matches(match_id)
);
"""

CREATE_INDEX_ELOHIST_PLAYER = """
CREATE INDEX IF NOT EXISTS idx_elohist_player_id ON ELO_History(player_id);
"""

CREATE_INDEX_ELOHIST_MATCH = """
CREATE INDEX IF NOT EXISTS idx_elohist_match_id ON ELO_History(match_id);
"""

CREATE_INDEX_ELOHIST_UPDATED = """
CREATE INDEX IF NOT EXISTS idx_elohist_updated_at ON ELO_History(updated_at);
"""
