# -*- coding: utf-8 -*-
"""
Schema definitions for the matches table.
"""

CREATE_SEQ_MATCHES = """
CREATE SEQUENCE IF NOT EXISTS seq_matches_id;
"""

CREATE_MATCHES_TABLE = """
CREATE TABLE IF NOT EXISTS Matches (
    match_id INTEGER PRIMARY KEY DEFAULT nextval('seq_matches_id'),   -- Unique match identifier, auto-incrementing
    team1_id INTEGER NOT NULL,                   -- Foreign key to Teams
    team2_id INTEGER NOT NULL,                   -- Foreign key to Teams
    winner_team_id INTEGER NOT NULL,             -- Foreign key to Teams
    match_date TIMESTAMP NOT NULL,               -- Date/time of the match
    FOREIGN KEY (team1_id) REFERENCES Teams(team_id),
    FOREIGN KEY (team2_id) REFERENCES Teams(team_id),
    FOREIGN KEY (winner_team_id) REFERENCES Teams(team_id)
);
"""

# ##: Index definitions for the matches table.
CREATE_INDEX_MATCHES_TEAM1 = """
CREATE INDEX IF NOT EXISTS idx_matches_team1_id ON Matches(team1_id);
"""

CREATE_INDEX_MATCHES_TEAM2 = """
CREATE INDEX IF NOT EXISTS idx_matches_team2_id ON Matches(team2_id);
"""

CREATE_INDEX_MATCHES_WINNER = """
CREATE INDEX IF NOT EXISTS idx_matches_winner_team_id ON Matches(winner_team_id);
"""

CREATE_INDEX_MATCHES_DATE = """
CREATE INDEX IF NOT EXISTS idx_matches_match_date ON Matches(match_date);
"""
