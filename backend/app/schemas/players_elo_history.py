# -*- coding: utf-8 -*-
"""
Schema definitions for the Players ELO history table.
"""

CREATE_PLAYERS_ELO_HISTORY_TABLE = """
CREATE TABLE IF NOT EXISTS Players_ELO_History (
    history_id SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL,
    match_id INTEGER NOT NULL,
    old_elo INTEGER NOT NULL,
    new_elo INTEGER NOT NULL,
    difference INTEGER NOT NULL,
    date TIMESTAMP NOT NULL,
    FOREIGN KEY (player_id) REFERENCES Players(player_id),
    FOREIGN KEY (match_id) REFERENCES Matches(match_id)
);
"""

CREATE_INDEX_PLAYERS_ELOHIST_HISTORY_ID = """
CREATE INDEX IF NOT EXISTS idx_players_elohist_history_id ON Players_ELO_History(history_id);
"""

CREATE_INDEX_PLAYERS_ELOHIST_PLAYER_ID = """
CREATE INDEX IF NOT EXISTS idx_players_elohist_player_id ON Players_ELO_History(player_id);
"""

CREATE_INDEX_PLAYERS_ELOHIST_MATCH_ID = """
CREATE INDEX IF NOT EXISTS idx_players_elohist_match_id ON Players_ELO_History(match_id);
"""

CREATE_INDEX_PLAYERS_ELOHIST_DATE = """
CREATE INDEX IF NOT EXISTS idx_players_elohist_date ON Players_ELO_History(date);
"""
