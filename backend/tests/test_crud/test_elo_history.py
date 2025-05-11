# -*- coding: utf-8 -*-
"""
Unit tests for ELO history CRUD operations using unittest.
"""

from datetime import datetime
from unittest import TestCase, main

from app.crud.elo_history import (
    batch_record_elo_updates,
    get_elo_by_date,
    get_monthly_elo_history,
    get_player_elo_history,
    record_elo_update,
)
from app.crud.matches import create_match
from app.crud.players import create_player
from app.crud.teams import create_team
from app.db import DatabaseManager, initialize_database


class TestELOHistoryCRUD(TestCase):
    """Test suite for ELO history CRUD operations."""

    def setUp(self):
        """Prepare a fresh in-memory DB with schema."""
        DatabaseManager._instance = None
        self.db = DatabaseManager(db_path=":memory:")
        initialize_database(self.db)

    def tearDown(self):
        """Clean up DB connection."""
        if hasattr(self, "db") and self.db.connection:
            self.db.close()
        DatabaseManager._instance = None

    def test_batch_record_elo_updates(self):
        """Test batch recording multiple ELO updates."""
        # ##: Create players, teams, and matches.
        p1 = create_player("Eve")
        p2 = create_player("Frank")
        p3 = create_player("Grace")
        p4 = create_player("David")
        t1 = create_team(p1, p2)
        t2 = create_team(p3, p4)
        m1 = create_match(t1, t2, datetime(2023, 2, 1, 10, 0, 0))
        m2 = create_match(t2, t1, datetime(2023, 2, 2, 11, 0, 0))

        updates = [
            {
                "player_id": p1,
                "match_id": m1,
                "old_elo": 1000,
                "new_elo": 1100,
                "date": datetime(2023, 2, 1, 10, 0, 0),
            },
            {
                "player_id": p2,
                "match_id": m1,
                "old_elo": 1000,
                "new_elo": 1150,
                "date": datetime(2023, 2, 1, 10, 0, 0),
            },
            {
                "player_id": p1,
                "match_id": m2,
                "old_elo": 1100,
                "new_elo": 1125,
                "date": datetime(2023, 2, 2, 11, 0, 0),
            },
        ]
        hist_ids = batch_record_elo_updates(updates)
        self.assertEqual(len(hist_ids), 3)
        self.assertTrue(all(i is not None for i in hist_ids), "Some history IDs are None")

        self.assertEqual(get_player_elo_history(p1)[0]["new_elo"], 1125)
        self.assertEqual(get_player_elo_history(p2)[0]["new_elo"], 1150)

    def test_empty_batch(self):
        """Test that empty batch returns empty list."""
        self.assertEqual(batch_record_elo_updates([]), [])

    def test_get_player_elo_history(self):
        """Test retrieving a player's ELO history with filtering."""
        # ##: Create player, team, and matches.
        p1 = create_player("Grace")
        p2 = create_player("Pierre")
        p3 = create_player("Pascal")
        p4 = create_player("Paul")
        t1 = create_team(p1, p2)
        t2 = create_team(p3, p4)

        # ##: Create matches on different dates.
        date1 = datetime(2023, 3, 1, 10, 0, 0)
        date2 = datetime(2023, 3, 15, 11, 0, 0)
        date3 = datetime(2023, 4, 1, 12, 0, 0)

        m1 = create_match(t1, t2, date1)
        m2 = create_match(t2, t1, date2)
        m3 = create_match(t1, t2, date3)

        # ##: Record ELO updates.
        record_elo_update(p1, m1, 1000, 1050, "global", date1)
        record_elo_update(p1, m2, 1050, 1075, "global", date2)
        record_elo_update(p1, m3, 1075, 1100, "global", date3)

        # ##: Test getting all history.
        history = get_player_elo_history(p1)
        self.assertEqual(len(history), 3)

        # ##: Test date filtering.
        march_history = get_player_elo_history(p1, start_date=datetime(2023, 3, 1), end_date=datetime(2023, 3, 31))
        self.assertEqual(len(march_history), 2)

        # ##: Test limit and offset.
        limited_history = get_player_elo_history(p1, limit=1)
        self.assertEqual(len(limited_history), 1)
        self.assertEqual(limited_history[0]["new_elo"], 1100)  # Most recent first

        offset_history = get_player_elo_history(p1, limit=1, offset=1)
        self.assertEqual(len(offset_history), 1)
        self.assertEqual(offset_history[0]["new_elo"], 1075)  # Second most recent

    def test_get_elo_by_date(self):
        """Test retrieving a player's ELO at a specific date."""
        # ##: Create player, team, and matches.
        p1 = create_player("Hannah")
        p2 = create_player("Grace")
        p3 = create_player("John")
        p4 = create_player("Jane")
        t1 = create_team(p1, p2)
        t2 = create_team(p3, p4)

        # ##: Create matches on different dates.
        date1 = datetime(2023, 5, 1, 10, 0, 0)
        date2 = datetime(2023, 5, 15, 11, 0, 0)
        date3 = datetime(2023, 5, 30, 12, 0, 0)

        m1 = create_match(t1, t2, date1)
        m2 = create_match(t2, t1, date2)
        m3 = create_match(t1, t2, date3)

        # ##: Record ELO updates.
        record_elo_update(p1, m1, 1000, 1050, "global", date1)
        record_elo_update(p1, m2, 1050, 1075, "global", date2)
        record_elo_update(p1, m3, 1075, 1100, "global", date3)

        # ##: Test getting ELO at different dates.
        self.assertEqual(get_elo_by_date(p1, datetime(2023, 5, 2)), 1050)  # Exactly on date1
        self.assertEqual(get_elo_by_date(p1, datetime(2023, 5, 10)), 1050)  # Between date1 and date2
        self.assertEqual(get_elo_by_date(p1, datetime(2023, 5, 20)), 1075)  # Between date2 and date3
        self.assertEqual(get_elo_by_date(p1, datetime(2023, 6, 1)), 1100)  # After date3

        # ##: Test with date before any records.
        self.assertIsNone(get_elo_by_date(p1, datetime(2023, 4, 1)))

    def test_get_monthly_elo_history(self):
        """Test retrieving a player's monthly ELO history."""
        # ##: Create player, team, and matches.
        p1 = create_player("Ian")
        p2 = create_player("Sarah")
        p3 = create_player("John")
        p4 = create_player("Jane")
        t1 = create_team(p1, p2)
        t2 = create_team(p3, p4)

        # ##: Create matches in different months.
        date1 = datetime(2023, 6, 1, 10, 0, 0)
        date2 = datetime(2023, 6, 15, 11, 0, 0)
        date3 = datetime(2023, 7, 1, 12, 0, 0)

        m1 = create_match(t1, t2, date1)
        m2 = create_match(t2, t1, date2)
        m3 = create_match(t1, t2, date3)

        # ##: Record ELO updates.
        record_elo_update(p1, m1, 1000, 1050, "global", date1)
        record_elo_update(p1, m2, 1050, 1075, "global", date2)
        record_elo_update(p1, m3, 1075, 1100, "global", date3)

        # ##: Test getting monthly history.
        june_history = get_monthly_elo_history(p1, 2023, 6)
        self.assertEqual(len(june_history), 2)

        july_history = get_monthly_elo_history(p1, 2023, 7)
        self.assertEqual(len(july_history), 1)

        # ##: Test empty month.
        may_history = get_monthly_elo_history(p1, 2023, 5)
        self.assertEqual(len(may_history), 0)


if __name__ == "__main__":
    main()
