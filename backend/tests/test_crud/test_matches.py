# -*- coding: utf-8 -*-
"""
Unit tests for match CRUD operations using unittest.
"""

import datetime
from unittest import TestCase, main

from app.crud.matches import (
    create_match,
    delete_match,
    get_match,
    get_matches_by_team,
)
from app.crud.players import create_player
from app.crud.teams import create_team
from app.db import DatabaseManager, initialize_database


class TestMatchCRUD(TestCase):
    """Test suite for match CRUD operations."""

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

    def test_create_and_get_match(self):
        """Test creating a match and retrieving it."""
        # ##: Create players and teams.
        p1 = create_player("Alice")
        p2 = create_player("Bob")
        p3 = create_player("Charlie")
        p4 = create_player("David")
        t1 = create_team(p1, p2)
        t2 = create_team(p3, p4)

        # ##: Create match.
        date = datetime.datetime(2023, 1, 1, 10, 0, 0)
        m_id = create_match(t1, t2, t2, date)
        self.assertIsNotNone(m_id)
        self.assertIsInstance(m_id, int)

        # ##: Retrieve match.
        match = get_match(m_id)
        self.assertIsNotNone(match)
        self.assertEqual(match["match_id"], m_id)
        self.assertEqual(match["team1_id"], t1)
        self.assertEqual(match["team2_id"], t2)
        self.assertEqual(match["winner_team_id"], t2)
        self.assertEqual(match["match_date"], date)

    def test_get_match_not_exists(self):
        """Test retrieving a non-existent match."""
        self.assertIsNone(get_match(9999))

    def test_get_matches_by_team_empty(self):
        """Test get_matches_by_team returns empty list if none."""
        p1 = create_player("Eve")
        p2 = create_player("Frank")
        t = create_team(p1, p2)
        self.assertEqual(get_matches_by_team(t), [])

    def test_get_matches_by_team_multiple(self):
        """Test retrieving multiple matches for a team in date-desc order."""
        # ##: Create players and teams.
        p1 = create_player("Gina")
        p2 = create_player("Hank")
        p3 = create_player("Ivy")
        p4 = create_player("Jack")
        t1 = create_team(p1, p2)
        t2 = create_team(p3, p4)

        # ##: Create two matches with different dates.
        date1 = datetime.datetime(2023, 1, 1, 9, 0, 0)
        date2 = datetime.datetime(2023, 1, 2, 11, 0, 0)
        m1 = create_match(t1, t2, t1, date1)
        m2 = create_match(t2, t1, t2, date2)

        # ##: Retrieve matches for t1.
        matches = get_matches_by_team(t1)
        self.assertEqual(len(matches), 2)

        # ##: Verify order by descending date.
        self.assertEqual(matches[0]["match_date"], date2)
        self.assertEqual(matches[1]["match_date"], date1)

        # ##: Verify match IDs order.
        self.assertEqual([m["match_id"] for m in matches], [m2, m1])

    def test_delete_match(self):
        """Test deleting existing and non-existent match."""
        # ##: Create players and teams.
        p1 = create_player("Karen")
        p2 = create_player("Leo")
        p3 = create_player("Mona")
        p4 = create_player("Nina")
        t1 = create_team(p1, p2)
        t2 = create_team(p3, p4)

        # ##: Create and delete match.
        date = datetime.datetime(2023, 2, 2, 14, 0, 0)
        m_id = create_match(t1, t2, t1, date)
        self.assertTrue(delete_match(m_id))
        self.assertIsNone(get_match(m_id))

        # ##: Deleting a non-existent match should return False.
        self.assertFalse(delete_match(9999))


if __name__ == "__main__":
    main()
