# -*- coding: utf-8 -*-
"""
Unit tests for ELO history CRUD operations using unittest.
"""

from unittest import TestCase, main
import datetime
from app.db import DatabaseManager, initialize_database
from app.crud.players import create_player
from app.crud.teams import create_team
from app.crud.matches import create_match
from app.crud.elo_history import (
    record_elo_update,
    get_current_elo,
    batch_record_elo_updates,
)


class TestELOHistoryCRUD(TestCase):
    """Test suite for ELO history CRUD operations."""

    def setUp(self):
        """Prepare a fresh in-memory DB with schema."""
        DatabaseManager._instance = None
        self.db = DatabaseManager(db_path=":memory:")
        initialize_database(self.db)

    def tearDown(self):
        """Clean up DB connection."""
        if hasattr(self, 'db') and self.db.connection:
            self.db.close()
        DatabaseManager._instance = None

    def test_record_and_get_current_elo(self):
        """Test recording a single ELO update and retrieving current ELO."""
        # Create players and teams and a match
        p1 = create_player("Alice")
        p2 = create_player("Bob")
        p3 = create_player("Charlie")
        p4 = create_player("David")
        t1 = create_team(p1, p2)
        t2 = create_team(p3, p4)
        match_date = datetime.datetime(2023, 1, 1, 12, 0, 0)
        m_id = create_match(t1, t2, t1, match_date)

        # Record first ELO update
        hist_id = record_elo_update(p1, m_id, 1200.5)
        self.assertIsNotNone(hist_id)
        self.assertIsInstance(hist_id, int)
        self.assertEqual(get_current_elo(p1), 1200.5)

        # Record second ELO update
        hist_id2 = record_elo_update(p1, m_id, 1250.0)
        self.assertIsNotNone(hist_id2)
        self.assertEqual(get_current_elo(p1), 1250.0)

        # No history for player without records
        self.assertIsNone(get_current_elo(p2))

    def test_batch_record_elo_updates(self):
        """Test batch recording multiple ELO updates."""
        # Create players, teams, and matches
        p1 = create_player("Eve")
        p2 = create_player("Frank")
        t1 = create_team(p1, p2)
        date1 = datetime.datetime(2023, 2, 1, 10, 0, 0)
        date2 = datetime.datetime(2023, 2, 2, 11, 0, 0)
        m1 = create_match(t1, t1, t1, date1)
        m2 = create_match(t1, t1, t1, date2)

        updates = [
            {"player_id": p1, "match_id": m1, "elo_score": 1100.0},
            {"player_id": p2, "match_id": m1, "elo_score": 1150.0},
            {"player_id": p1, "match_id": m2, "elo_score": 1125.5},
        ]
        hist_ids = batch_record_elo_updates(updates)
        self.assertEqual(len(hist_ids), 3)
        self.assertTrue(all(isinstance(i, int) for i in hist_ids))

        # Check current ELO for each
        self.assertEqual(get_current_elo(p1), 1125.5)
        self.assertEqual(get_current_elo(p2), 1150.0)

    def test_empty_batch(self):
        """Test that empty batch returns empty list."""
        self.assertEqual(batch_record_elo_updates([]), [])


if __name__ == '__main__':
    main()
