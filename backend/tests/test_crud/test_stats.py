# -*- coding: utf-8 -*-
"""
Unit tests for stats CRUD operations using unittest.
"""

from datetime import datetime
from unittest import TestCase, main

from loguru import logger

from app.crud.elo_history import record_elo_update
from app.crud.matches import create_match
from app.crud.players import create_player, update_player
from app.crud.stats import get_player_elo_history, get_player_stats
from app.crud.teams import create_team
from app.db import DatabaseManager, initialize_database


class TestStatsCRUD(TestCase):
    """Test suite for stats and leaderboard operations."""

    def setUp(self):
        DatabaseManager._instance = None
        self.db = DatabaseManager(db_path=":memory:")
        initialize_database(self.db)

    def tearDown(self):
        if hasattr(self, "db") and self.db.connection:
            self.db.close()
        DatabaseManager._instance = None

    def test_get_player_stats_not_exists(self):
        """
        Test retrieving a player's stats that does not exist.
        """
        self.assertIsNone(get_player_stats(9999))

    def test_get_player_stats_defaults(self):
        """
        Test retrieving a player's stats with default values.
        """
        p1 = create_player("Alice")
        stats = get_player_stats(p1)
        self.assertIsNotNone(stats)
        self.assertEqual(stats["player_id"], p1)
        self.assertEqual(stats["name"], "Alice")
        self.assertEqual(stats["global_elo"], 1000)
        self.assertEqual(stats["current_month_elo"], 1000)
        self.assertEqual(stats["matches_played"], 0)
        self.assertEqual(stats["wins"], 0)
        self.assertEqual(stats["losses"], 0)
        self.assertEqual(stats["win_rate"], 0)

    def test_get_player_stats_with_match_and_history(self):
        """
        Test retrieving a player's stats with match history.
        """
        # ##: Create players and teams.
        logger.info("Creating players and teams")
        p1 = create_player("Bob")
        p2 = create_player("Carol")
        p3 = create_player("Dave")
        p4 = create_player("Eve")
        t1 = create_team(p1, p2)
        t2 = create_team(p3, p4)

        # ##: Record a match where p1's team wins.
        date = datetime(2025, 1, 1, 12, 0, 0)
        m1 = create_match(winner_team_id=t1, loser_team_id=t2, played_at=date, is_fanny=False)

        # ##: Update player ELO.
        update_player(p1, global_elo=1500)

        # ##: Record ELO update for p1.
        record_elo_update(player_id=p1, match_id=m1, old_elo=1000, new_elo=1500, elo_type="global")

        # ##: Get player stats.
        stats = get_player_stats(p1)
        self.assertEqual(stats["matches_played"], 1)
        self.assertEqual(stats["wins"], 1)
        self.assertEqual(stats["losses"], 0)
        self.assertEqual(stats["win_rate"], 100)
        self.assertEqual(stats["global_elo"], 1500)
        self.assertEqual(stats["current_month_elo"], 1000)

    def test_get_player_elo_history(self):
        """
        Test retrieving a player's ELO history with filtering.
        """
        # ##: Create players, teams, matches, and history.
        p1 = create_player("Ivy")
        p2 = create_player("Judy")
        t1 = create_team(p1, p2)
        t2 = create_team(create_player("K"), create_player("L"))
        date1 = datetime(2025, 2, 1, 10, 0, 0)
        date2 = datetime(2025, 2, 2, 11, 0, 0)
        m1 = create_match(winner_team_id=t1, loser_team_id=t2, is_fanny=False, played_at=date1)
        m2 = create_match(winner_team_id=t1, loser_team_id=t2, is_fanny=False, played_at=date2)
        record_elo_update(player_id=p1, match_id=m1, old_elo=1000, new_elo=1200, elo_type="global")
        record_elo_update(player_id=p1, match_id=m2, old_elo=1200, new_elo=1300, elo_type="global")

        history = get_player_elo_history(p1)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["match_date"], date2)
        self.assertEqual(history[1]["match_date"], date1)
        self.assertEqual(history[0]["new_elo"], 1300)
        self.assertEqual(history[1]["new_elo"], 1200)
        self.assertEqual(history[0]["old_elo"], 1200)
        self.assertEqual(history[1]["old_elo"], 1000)


if __name__ == "__main__":
    main()
