# -*- coding: utf-8 -*-
"""
Schema definitions for the team periodic rankings table.
"""

CREATE_SEQ_TEAM_PERIODIC_RANKINGS = """
CREATE SEQUENCE IF NOT EXISTS seq_team_periodic_rankings_id;
"""

CREATE_TEAM_PERIODIC_RANKINGS_TABLE = """
CREATE TABLE IF NOT EXISTS Team_Periodic_Rankings (
    team_ranking_id INTEGER PRIMARY KEY DEFAULT nextval('seq_team_periodic_rankings_id'),
    team_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day INTEGER NOT NULL,
    initial_elo FLOAT NOT NULL,
    final_elo FLOAT NOT NULL,
    ranking INTEGER NOT NULL,
    matches_played INTEGER NOT NULL,
    wins INTEGER NOT NULL,
    loses INTEGER NOT NULL,
    FOREIGN KEY (team_id) REFERENCES Teams(team_id),
    UNIQUE (team_id, year, month, day)
);
"""

CREATE_INDEX_TEAM_PERIODIC_RANKINGS_TEAM_ID = """
CREATE INDEX IF NOT EXISTS idx_team_periodic_rankings_team_id ON Team_Periodic_Rankings(team_id);
"""

CREATE_INDEX_TEAM_PERIODIC_RANKINGS_PERIOD = """
CREATE INDEX IF NOT EXISTS idx_team_periodic_rankings_period ON Team_Periodic_Rankings(team_id, year, month);
"""
