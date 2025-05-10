# -*- coding: utf-8 -*-
"""
Schema definitions for the ELO history table.
"""

CREATE_SEQ_ELO_HISTORY = """
CREATE SEQUENCE IF NOT EXISTS seq_elo_history_id;
"""

CREATE_ELO_HISTORY_TABLE = """
CREATE TABLE IF NOT EXISTS ELO_History (
    history_id INTEGER PRIMARY KEY DEFAULT nextval('seq_elo_history_id'),
    player_id INTEGER NOT NULL,
    match_id INTEGER NOT NULL,
    type VARCHAR NOT NULL, -- 'global' or 'monthly'
    old_elo INTEGER NOT NULL,
    new_elo INTEGER NOT NULL,
    difference INTEGER NOT NULL,
    date TIMESTAMP NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day INTEGER NOT NULL,
    FOREIGN KEY (player_id) REFERENCES Players(player_id),
    FOREIGN KEY (match_id) REFERENCES Matches(match_id)
);
"""

CREATE_INDEX_ELOHIST_PLAYER_ID = """
CREATE INDEX IF NOT EXISTS idx_elohist_player_id ON ELO_History(player_id);
"""

CREATE_INDEX_ELOHIST_MATCH_ID = """
CREATE INDEX IF NOT EXISTS idx_elohist_match_id ON ELO_History(match_id);
"""

CREATE_INDEX_ELOHIST_DATE = """
CREATE INDEX IF NOT EXISTS idx_elohist_date ON ELO_History(date);
"""
