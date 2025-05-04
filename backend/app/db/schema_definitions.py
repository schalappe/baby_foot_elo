# -*- coding: utf-8 -*-
"""
SQL schema definitions for all tables required by the Baby Foot ELO project.
Each schema is defined as a constant string and includes comments for clarity.
"""

# ##: Players table: Stores player information.
CREATE_PLAYERS_TABLE = """
CREATE TABLE IF NOT EXISTS Players (
    player_id INTEGER PRIMARY KEY,  -- Unique player identifier
    name TEXT NOT NULL,                          -- Player's full name
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Creation timestamp
);
"""

# ##: Teams table: Stores team information.
CREATE_TEAMS_TABLE = """
CREATE TABLE IF NOT EXISTS Teams (
    team_id INTEGER PRIMARY KEY,    -- Unique team identifier
    name TEXT NOT NULL,                          -- Team name
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Creation timestamp
);
"""

# ##: Matches table: Stores match results and references teams.
CREATE_MATCHES_TABLE = """
CREATE TABLE IF NOT EXISTS Matches (
    match_id INTEGER PRIMARY KEY,   -- Unique match identifier
    team1_id INTEGER NOT NULL,                   -- Foreign key to Teams
    team2_id INTEGER NOT NULL,                   -- Foreign key to Teams
    winner_team_id INTEGER NOT NULL,             -- Foreign key to Teams
    match_date TIMESTAMP NOT NULL,               -- Date/time of the match
    FOREIGN KEY (team1_id) REFERENCES Teams(team_id),
    FOREIGN KEY (team2_id) REFERENCES Teams(team_id),
    FOREIGN KEY (winner_team_id) REFERENCES Teams(team_id)
);
"""

# ##: ELO_History table: Stores ELO scores after each match.
CREATE_ELO_HISTORY_TABLE = """
CREATE TABLE IF NOT EXISTS ELO_History (
    history_id INTEGER PRIMARY KEY, -- Unique record identifier
    player_id INTEGER NOT NULL,                   -- Foreign key to Players
    match_id INTEGER NOT NULL,                    -- Foreign key to Matches
    elo_score REAL NOT NULL,                      -- ELO score after match
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Update timestamp
    FOREIGN KEY (player_id) REFERENCES Players(player_id),
    FOREIGN KEY (match_id) REFERENCES Matches(match_id)
);
"""

# ##: Periodic_Rankings table: Stores player rankings for each period.
CREATE_PERIODIC_RANKINGS_TABLE = """
CREATE TABLE IF NOT EXISTS Periodic_Rankings (
    ranking_id INTEGER PRIMARY KEY, -- Unique ranking record
    player_id INTEGER NOT NULL,                   -- Foreign key to Players
    period TEXT NOT NULL,                         -- Period (e.g., '2025-W18')
    ranking INTEGER NOT NULL,                     -- Player's rank in this period
    elo_score REAL NOT NULL,                      -- ELO score at period end
    FOREIGN KEY (player_id) REFERENCES Players(player_id)
);
"""

# ##: Team_Periodic_Rankings table: Stores team rankings for each period.
CREATE_TEAM_PERIODIC_RANKINGS_TABLE = """
CREATE TABLE IF NOT EXISTS Team_Periodic_Rankings (
    team_ranking_id INTEGER PRIMARY KEY, -- Unique team ranking record
    team_id INTEGER NOT NULL,                          -- Foreign key to Teams
    period TEXT NOT NULL,                              -- Period (e.g., '2025-W18')
    ranking INTEGER NOT NULL,                          -- Team's rank in this period
    elo_score REAL NOT NULL,                           -- ELO score at period end
    FOREIGN KEY (team_id) REFERENCES Teams(team_id)
);
"""
