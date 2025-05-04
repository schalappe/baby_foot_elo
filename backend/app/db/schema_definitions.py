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

# ##: Indexes for performance optimization
# Index on player names for fast search and autocomplete
CREATE_INDEX_PLAYERS_NAME = """
CREATE INDEX IF NOT EXISTS idx_players_name ON Players(name);
"""  # Improves search/query speed on player names

# Indexes on foreign keys for faster joins and lookups
CREATE_INDEX_MATCHES_TEAM1 = """
CREATE INDEX IF NOT EXISTS idx_matches_team1_id ON Matches(team1_id);
"""  # Speeds up queries filtering by team1_id
CREATE_INDEX_MATCHES_TEAM2 = """
CREATE INDEX IF NOT EXISTS idx_matches_team2_id ON Matches(team2_id);
"""  # Speeds up queries filtering by team2_id
CREATE_INDEX_MATCHES_WINNER = """
CREATE INDEX IF NOT EXISTS idx_matches_winner_team_id ON Matches(winner_team_id);
"""  # Speeds up queries filtering by winner_team_id
CREATE_INDEX_ELOHIST_PLAYER = """
CREATE INDEX IF NOT EXISTS idx_elohist_player_id ON ELO_History(player_id);
"""  # Speeds up queries and joins on player_id in ELO_History
CREATE_INDEX_ELOHIST_MATCH = """
CREATE INDEX IF NOT EXISTS idx_elohist_match_id ON ELO_History(match_id);
"""  # Speeds up queries and joins on match_id in ELO_History
CREATE_INDEX_PERIODIC_PLAYER = """
CREATE INDEX IF NOT EXISTS idx_periodic_player_id ON Periodic_Rankings(player_id);
"""  # Speeds up queries and joins on player_id in rankings

# Compound index for efficient queries on periodic data (period + player)
CREATE_INDEX_PERIODIC_PERIOD_PLAYER = """
CREATE INDEX IF NOT EXISTS idx_periodic_period_player ON Periodic_Rankings(period, player_id);
"""  # Optimizes queries filtering by period and player

# Indexes on date fields for efficient time-based queries
CREATE_INDEX_MATCHES_DATE = """
CREATE INDEX IF NOT EXISTS idx_matches_match_date ON Matches(match_date);
"""  # Optimizes time-range queries on matches
CREATE_INDEX_ELOHIST_UPDATED = """
CREATE INDEX IF NOT EXISTS idx_elohist_updated_at ON ELO_History(updated_at);
"""  # Optimizes time-based queries on ELO_History

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
