# -*- coding: utf-8 -*-
"""
Unit tests for stats CRUD operations using unittest.
"""

import datetime
from unittest import TestCase, main

from app.crud.elo_history import record_elo_update
from app.crud.matches import create_match
from app.crud.players import create_player
from app.crud.stats import (
    get_leaderboard,
    get_player_elo_history,
    get_player_stats,
)
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
        self.assertIsNone(get_player_stats(9999))

    def test_get_player_stats_defaults(self):
        p1 = create_player("Alice")
        stats = get_player_stats(p1)
        self.assertIsNotNone(stats)
        self.assertEqual(stats["player_id"], p1)
        self.assertEqual(stats["name"], "Alice")
        self.assertEqual(stats["current_elo"], 1000.0)
        self.assertEqual(stats["matches_played"], 0)
        self.assertEqual(stats["wins"], 0)
        self.assertEqual(stats["win_rate"], 0)

    def test_get_player_stats_with_match_and_history(self):
        # Create players and teams
        p1 = create_player("Bob")
        p2 = create_player("Carol")
        p3 = create_player("Dave")
        p4 = create_player("Eve")
        t1 = create_team(p1, p2)
        t2 = create_team(p3, p4)
        # Record a match where p1's team wins
        date = datetime.datetime(2025, 1, 1, 12, 0, 0)
        m1 = create_match(t1, t2, t1, date)
        # Record ELO update for p1
        record_elo_update(p1, m1, 1500.0)
        stats = get_player_stats(p1)
        self.assertEqual(stats["matches_played"], 1)
        self.assertEqual(stats["wins"], 1)
        self.assertEqual(stats["win_rate"], 100)
        self.assertEqual(stats["current_elo"], 1500.0)

    def test_get_leaderboard(self):
        # Create players and record ELO
        p1 = create_player("Gina")
        p2 = create_player("Hank")
        # p1 higher
        record_elo_update(
            p1,
            create_match(
                create_team(p1, p2),
                create_team(create_player("X"), create_player("Y")),
                p1,
                datetime.datetime.now(),
            ),
            2000.0,
        )
        # p2 none
        lb = get_leaderboard(limit=2)
        self.assertEqual(len(lb), 2)
        # Top is p1
        self.assertEqual(lb[0]["player_id"], p1)
        self.assertEqual(lb[0]["current_elo"], 2000.0)
        # Second is p2 default
        self.assertEqual(lb[1]["player_id"], p2)
        self.assertEqual(lb[1]["current_elo"], 1000.0)

    def test_get_player_elo_history(self):
        # Create players, teams, matches, and history
        p1 = create_player("Ivy")
        p2 = create_player("Judy")
        t1 = create_team(p1, p2)
        t2 = create_team(create_player("K"), create_player("L"))
        date1 = datetime.datetime(2025, 2, 1, 10, 0, 0)
        date2 = datetime.datetime(2025, 2, 2, 11, 0, 0)
        m1 = create_match(t1, t2, t1, date1)
        m2 = create_match(t1, t2, t1, date2)
        record_elo_update(p1, m1, 1200.0)
        record_elo_update(p1, m2, 1300.0)
        history = get_player_elo_history(p1)
        self.assertEqual(len(history), 2)
        # Sorted by match_date desc
        self.assertEqual(history[0]["match_date"], date2)
        self.assertEqual(history[1]["match_date"], date1)
        self.assertEqual(history[0]["elo_score"], 1300.0)
        self.assertEqual(history[1]["elo_score"], 1200.0)


if __name__ == "__main__":
    main()
