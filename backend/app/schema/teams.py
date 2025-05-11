# -*- coding: utf-8 -*-
"""
Schema definitions for the teams table.
"""

CREATE_SEQ_TEAMS = """
CREATE SEQUENCE IF NOT EXISTS seq_teams_id;
"""

CREATE_TEAMS_TABLE = """
CREATE TABLE IF NOT EXISTS Teams (
    team_id INTEGER PRIMARY KEY DEFAULT nextval('seq_teams_id'),
    player1_id INTEGER NOT NULL,
    player2_id INTEGER NOT NULL,
    global_elo FLOAT NOT NULL DEFAULT 1000.0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_match_at TIMESTAMP,
    FOREIGN KEY (player1_id) REFERENCES Players(player_id),
    FOREIGN KEY (player2_id) REFERENCES Players(player_id),
    CHECK (player1_id <> player2_id)
);
"""

CREATE_INDEX_TEAMS_PLAYER_PAIR_ORDER_INSENSITIVE = """
CREATE UNIQUE INDEX IF NOT EXISTS idx_teams_player_pair_order_insensitive 
ON Teams (LEAST(player1_id, player2_id), GREATEST(player1_id, player2_id));
"""

CREATE_INDEX_TEAMS_PLAYER1_ID = """
CREATE INDEX IF NOT EXISTS idx_teams_player1_id ON Teams(player1_id);
"""

CREATE_INDEX_TEAMS_PLAYER2_ID = """
CREATE INDEX IF NOT EXISTS idx_teams_player2_id ON Teams(player2_id);
"""
