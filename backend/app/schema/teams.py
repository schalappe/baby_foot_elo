# -*- coding: utf-8 -*-
"""
Schema definitions for the teams table.
"""

CREATE_SEQ_TEAMS = """
CREATE SEQUENCE IF NOT EXISTS seq_teams_id;
"""

CREATE_TEAMS_TABLE = """
CREATE TABLE IF NOT EXISTS Teams (
    team_id INTEGER PRIMARY KEY DEFAULT nextval('seq_teams_id'),    -- Unique team identifier, auto-incrementing
    player1_id INTEGER NOT NULL,                 -- Foreign key to Players
    player2_id INTEGER NOT NULL,                 -- Foreign key to Players
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Creation timestamp
    FOREIGN KEY (player1_id) REFERENCES Players(player_id),
    FOREIGN KEY (player2_id) REFERENCES Players(player_id),
    UNIQUE (player1_id, player2_id)
);
"""
