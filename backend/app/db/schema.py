# -*- coding: utf-8 -*-
"""
SQL schema definitions for all tables required by the Baby Foot ELO project.
Each schema is defined as a constant string and includes comments for clarity.
"""

# Sequence for Players table
CREATE_SEQ_PLAYERS = """
CREATE SEQUENCE IF NOT EXISTS seq_players_id;
"""

# ##: Players table: Stores player information.
CREATE_PLAYERS_TABLE = """
CREATE TABLE IF NOT EXISTS Players (
    player_id INTEGER PRIMARY KEY DEFAULT nextval('seq_players_id'),  -- Unique player identifier, auto-incrementing
    name TEXT NOT NULL,                          -- Player's full name
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Creation timestamp
);
"""

# Sequence for Teams table
CREATE_SEQ_TEAMS = """
CREATE SEQUENCE IF NOT EXISTS seq_teams_id;
"""

# ##: Teams table: Stores team information.
CREATE_TEAMS_TABLE = """
CREATE TABLE IF NOT EXISTS Teams (
    team_id INTEGER PRIMARY KEY DEFAULT nextval('seq_teams_id'),    -- Unique team identifier, auto-incrementing
    name TEXT NOT NULL,                          -- Team name (can be auto-generated or custom)
    player1_id INTEGER NOT NULL,                 -- Foreign key to Players
    player2_id INTEGER NOT NULL,                 -- Foreign key to Players
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Creation timestamp
    FOREIGN KEY (player1_id) REFERENCES Players(player_id),
    FOREIGN KEY (player2_id) REFERENCES Players(player_id),
    UNIQUE (player1_id, player2_id) -- Ensure a pair of players forms only one team
);
"""

# Sequence for Matches table
CREATE_SEQ_MATCHES = """
CREATE SEQUENCE IF NOT EXISTS seq_matches_id;
"""

# ##: Matches table: Stores match results and references teams.
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

# Sequence for ELO_History table
CREATE_SEQ_ELO_HISTORY = """
CREATE SEQUENCE IF NOT EXISTS seq_elo_history_id;
"""

# ##: ELO_History table: Stores ELO scores after each match.
CREATE_ELO_HISTORY_TABLE = """
CREATE TABLE IF NOT EXISTS ELO_History (
    history_id INTEGER PRIMARY KEY DEFAULT nextval('seq_elo_history_id'), -- Unique record identifier, auto-incrementing
    player_id INTEGER NOT NULL,                   -- Foreign key to Players
    match_id INTEGER NOT NULL,                    -- Foreign key to Matches
    elo_score REAL NOT NULL,                      -- ELO score after match
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Update timestamp
    FOREIGN KEY (player_id) REFERENCES Players(player_id),
    FOREIGN KEY (match_id) REFERENCES Matches(match_id)
);
"""

# Sequence for Periodic_Rankings table
CREATE_SEQ_PERIODIC_RANKINGS = """
CREATE SEQUENCE IF NOT EXISTS seq_periodic_rankings_id;
"""

# ##: Periodic_Rankings table: Stores player rankings for each period.
CREATE_PERIODIC_RANKINGS_TABLE = """
CREATE TABLE IF NOT EXISTS Periodic_Rankings (
    ranking_id INTEGER PRIMARY KEY DEFAULT nextval('seq_periodic_rankings_id'), -- Unique ranking record, auto-incrementing
    player_id INTEGER NOT NULL,                   -- Foreign key to Players
    period TEXT NOT NULL,                         -- Period (e.g., '2025-W18')
    ranking INTEGER NOT NULL,                     -- Player's rank in this period
    elo_score REAL NOT NULL,                      -- ELO score at period end
    FOREIGN KEY (player_id) REFERENCES Players(player_id)
);
"""

# Sequence for Team_Periodic_Rankings table
CREATE_SEQ_TEAM_PERIODIC_RANKINGS = """
CREATE SEQUENCE IF NOT EXISTS seq_team_periodic_rankings_id;
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
    team_ranking_id INTEGER PRIMARY KEY DEFAULT nextval('seq_team_periodic_rankings_id'), -- Unique team ranking record, auto-incrementing
    team_id INTEGER NOT NULL,                          -- Foreign key to Teams
    period TEXT NOT NULL,                              -- Period (e.g., '2025-W18')
    ranking INTEGER NOT NULL,                          -- Team's rank in this period
    elo_score REAL NOT NULL,                           -- ELO score at period end
    FOREIGN KEY (team_id) REFERENCES Teams(team_id)
);
"""
