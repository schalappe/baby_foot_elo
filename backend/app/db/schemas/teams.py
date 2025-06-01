# -*- coding: utf-8 -*-
"""
Schema definitions for the teams table.
"""

CREATE_TEAMS_TABLE = """
CREATE TABLE IF NOT EXISTS Teams (
    team_id SERIAL PRIMARY KEY,
    player1_id INTEGER NOT NULL,
    player2_id INTEGER NOT NULL,
    global_elo INTEGER NOT NULL DEFAULT 1000,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_match_at TIMESTAMPTZ,
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

CREATE_INDEX_TEAMS_TEAM_ID = """
CREATE INDEX IF NOT EXISTS idx_teams_team_id ON Teams(team_id);
"""

CREATE_INDEX_TEAMS_LAST_MATCH_AT = """
CREATE INDEX IF NOT EXISTS idx_teams_last_match_at ON Teams(last_match_at);
"""
