# -*- coding: utf-8 -*-
"""
Unit tests for the schema definitions module.
"""

from unittest import TestCase, main

import duckdb

from app.db import schema_definitions


def get_table_columns(con, table_name):
    """Get the column names of a table from DuckDB."""
    return [row[1] for row in con.execute(f"PRAGMA table_info({table_name})").fetchall()]


class TestSchemaDefinitions(TestCase):
    """Unit tests for the schema definitions module."""

    @classmethod
    def setUpClass(cls):
        """Set up an in-memory DuckDB connection for all tests."""
        cls.con = duckdb.connect(database=':memory:')
        schemas = [
            schema_definitions.CREATE_PLAYERS_TABLE,
            schema_definitions.CREATE_TEAMS_TABLE,
            schema_definitions.CREATE_MATCHES_TABLE,
            schema_definitions.CREATE_ELO_HISTORY_TABLE,
            schema_definitions.CREATE_PERIODIC_RANKINGS_TABLE,
            schema_definitions.CREATE_TEAM_PERIODIC_RANKINGS_TABLE,
        ]
        for schema in schemas:
            cls.con.execute(schema)

    @classmethod
    def tearDownClass(cls):
        """Close the DuckDB connection."""
        cls.con.close()

    def test_players_table(self):
        """Test the Players table."""
        columns = get_table_columns(self.con, "Players")
        self.assertSetEqual(set(columns), {"player_id", "name", "created_at"})

    def test_teams_table(self):
        """Test the Teams table."""
        columns = get_table_columns(self.con, "Teams")
        self.assertSetEqual(set(columns), {"team_id", "name", "created_at"})

    def test_matches_table(self):
        """Test the Matches table."""
        columns = get_table_columns(self.con, "Matches")
        self.assertSetEqual(set(columns), {"match_id", "team1_id", "team2_id", "winner_team_id", "match_date"})

    def test_elo_history_table(self):
        """Test the ELO_History table."""
        columns = get_table_columns(self.con, "ELO_History")
        self.assertSetEqual(set(columns), {"history_id", "player_id", "match_id", "elo_score", "updated_at"})

    def test_periodic_rankings_table(self):
        """Test the Periodic_Rankings table."""
        columns = get_table_columns(self.con, "Periodic_Rankings")
        self.assertSetEqual(set(columns), {"ranking_id", "player_id", "period", "ranking", "elo_score"})

    def test_team_periodic_rankings_table(self):
        """Test the Team_Periodic_Rankings table."""
        columns = get_table_columns(self.con, "Team_Periodic_Rankings")
        self.assertSetEqual(set(columns), {"team_ranking_id", "team_id", "period", "ranking", "elo_score"})

if __name__ == "__main__":
    main()
