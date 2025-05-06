# -*- coding: utf-8 -*-
"""
Schema definitions for the team periodic rankings table.
"""

CREATE_SEQ_TEAM_PERIODIC_RANKINGS = """
CREATE SEQUENCE IF NOT EXISTS seq_team_periodic_rankings_id;
"""

CREATE_TEAM_PERIODIC_RANKINGS_TABLE = """
CREATE TABLE IF NOT EXISTS Team_Periodic_Rankings (
    team_ranking_id INTEGER PRIMARY KEY DEFAULT nextval('seq_team_periodic_rankings_id'), -- Unique team ranking record, auto-incrementing
    team_id INTEGER NOT NULL,                          -- Foreign key to Teams
    period TEXT NOT NULL,                              -- Period (e.g., '2025-W18')
    ranking INTEGER NOT NULL,                          -- Team's rank in this period
    elo_score REAL NOT NULL,                           -- ELO score at period end
    FOREIGN KEY (team_id) REFERENCES Teams(team_id)
);
"""
