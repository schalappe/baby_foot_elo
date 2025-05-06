# -*- coding: utf-8 -*-
"""
Unit tests for team CRUD operations using unittest.
"""

from unittest import TestCase, main
from app.db import DatabaseManager, initialize_database
from app.crud.players import create_player
from app.crud.teams import (
    create_team,
    get_team,
    get_all_teams,
    delete_team,
    batch_insert_teams,
)


class TestTeamCRUD(TestCase):
    """Test suite for team CRUD operations."""

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

    def test_create_team(self):
        """Test creating and retrieving a team and duplicate prevention."""
        p1 = create_player("Alice")
        p2 = create_player("Bob")
        team_id = create_team(p1, p2)
        self.assertIsNotNone(team_id)
        self.assertIsInstance(team_id, int)

        team = get_team(team_id)
        self.assertIsNotNone(team)
        self.assertEqual(team["team_id"], team_id)
        self.assertEqual({team["player1_id"], team["player2_id"]}, {p1, p2})

        self.assertIsNone(create_team(p1, p2))
        self.assertIsNone(create_team(p2, p1))

    def test_get_team_not_exists(self):
        """Test retrieving a non-existent team."""
        self.assertIsNone(get_team(9999))

    def test_get_all_teams_empty(self):
        """Test get_all_teams on empty DB."""
        self.assertEqual(get_all_teams(), [])

    def test_get_all_teams_multiple(self):
        """Test retrieving multiple teams."""
        p1 = create_player("Charlie")
        p2 = create_player("David")
        p3 = create_player("Eve")

        id1 = create_team(p1, p2)
        id2 = create_team(p2, p3)

        teams = get_all_teams()
        self.assertEqual(len(teams), 2)
        ids = [t["team_id"] for t in teams]
        self.assertEqual(ids, [id1, id2])

    def test_delete_team(self):
        """Test deleting existing and non-existing team."""
        p1 = create_player("Frank")
        p2 = create_player("Grace")
        t_id = create_team(p1, p2)

        self.assertTrue(delete_team(t_id))
        self.assertIsNone(get_team(t_id))
        self.assertFalse(delete_team(9999))

    def test_batch_insert_teams(self):
        """Test batch inserting teams with ordering."""
        p1 = create_player("Heidi")
        p2 = create_player("Ivan")
        p3 = create_player("Judy")

        team_list = [{"player1_id": p1, "player2_id": p2}, {"player1_id": p3, "player2_id": p1}]
        ids = batch_insert_teams(team_list)
        self.assertEqual(len(ids), 2)
        self.assertTrue(all(isinstance(i, int) for i in ids))

        teams = get_all_teams()
        pairs = {(t["player1_id"], t["player2_id"]) for t in teams}
        expected = {(p1, p2), (min(p1, p3), max(p1, p3))}
        self.assertEqual(pairs, expected)


if __name__ == '__main__':
    main()
