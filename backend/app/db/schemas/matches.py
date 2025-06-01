# -*- coding: utf-8 -*-
"""
Schema definitions for the matches table.
"""

CREATE_MATCHES_TABLE = """
CREATE TABLE IF NOT EXISTS Matches (
    match_id SERIAL PRIMARY KEY,
    winner_team_id INTEGER NOT NULL,
    loser_team_id INTEGER NOT NULL,
    is_fanny BOOLEAN NOT NULL DEFAULT FALSE,
    played_at TIMESTAMP NOT NULL,
    notes TEXT,
    FOREIGN KEY (winner_team_id) REFERENCES Teams(team_id),
    FOREIGN KEY (loser_team_id) REFERENCES Teams(team_id),
    CHECK (winner_team_id <> loser_team_id)
);
"""

CREATE_INDEX_MATCHES_MATCH_ID = """
CREATE INDEX IF NOT EXISTS idx_matches_match_id ON Matches(match_id);
"""

CREATE_INDEX_MATCHES_WINNER_TEAM_ID = """
CREATE INDEX IF NOT EXISTS idx_matches_winner_team_id ON Matches(winner_team_id);
"""

CREATE_INDEX_MATCHES_LOSER_TEAM_ID = """
CREATE INDEX IF NOT EXISTS idx_matches_loser_team_id ON Matches(loser_team_id);
"""

CREATE_INDEX_MATCHES_PLAYED_AT = """
CREATE INDEX IF NOT EXISTS idx_matches_played_at ON Matches(played_at);
"""
