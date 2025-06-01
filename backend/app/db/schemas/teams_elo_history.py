# -*- coding: utf-8 -*-
"""
Schema definitions for the Teams ELO history table.
"""

CREATE_TEAMS_ELO_HISTORY_TABLE = """
CREATE TABLE IF NOT EXISTS Teams_ELO_History (
    history_id SERIAL PRIMARY KEY,
    team_id INTEGER NOT NULL,
    match_id INTEGER NOT NULL,
    old_elo INTEGER NOT NULL,
    new_elo INTEGER NOT NULL,
    difference INTEGER NOT NULL,
    date TIMESTAMPTZ NOT NULL,
    FOREIGN KEY (team_id) REFERENCES Teams(team_id),
    FOREIGN KEY (match_id) REFERENCES Matches(match_id)
);
"""

CREATE_INDEX_TEAMS_ELOHIST_HISTORY_ID = """
CREATE INDEX IF NOT EXISTS idx_teams_elohist_history_id ON Teams_ELO_History(history_id);
"""

CREATE_INDEX_TEAMS_ELOHIST_TEAM_ID = """
CREATE INDEX IF NOT EXISTS idx_teams_elohist_team_id ON Teams_ELO_History(team_id);
"""

CREATE_INDEX_TEAMS_ELOHIST_MATCH_ID = """
CREATE INDEX IF NOT EXISTS idx_teams_elohist_match_id ON Teams_ELO_History(match_id);
"""

CREATE_INDEX_TEAMS_ELOHIST_DATE = """
CREATE INDEX IF NOT EXISTS idx_teams_elohist_date ON Teams_ELO_History(date);
"""
