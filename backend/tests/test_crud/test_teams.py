# -*- coding: utf-8 -*-
"""
Unit tests for team CRUD operations using unittest.
"""

from datetime import datetime
from unittest import TestCase, main

from app.crud.players import create_player
from app.crud.teams import (
    batch_insert_teams,
    create_team,
    delete_team,
    get_all_teams,
    get_team,
    get_teams_by_player,
    update_team,
)
from app.db import DatabaseManager, initialize_database


class TestTeamCRUD(TestCase):
    """Test suite for team CRUD operations."""

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

    def test_create_team(self):
        """
        Test creating and retrieving a team, including duplicate prevention and default fields.
        """
        p1 = create_player("Alice")
        p2 = create_player("Bob")
        team_id = create_team(p1, p2)
        self.assertIsNotNone(team_id)
        self.assertIsInstance(team_id, int)

        team = get_team(team_id)
        self.assertIsNotNone(team)
        self.assertEqual(team["team_id"], team_id)
        self.assertEqual({team["player1_id"], team["player2_id"]}, {p1, p2})
        self.assertEqual(team["global_elo"], 1000.0)
        import datetime

        self.assertIsInstance(team["created_at"], datetime.datetime)
        self.assertIsNone(team["last_match_at"])

        # ##: Duplicate prevention (order-insensitive).
        self.assertIsNone(create_team(p1, p2))
        self.assertIsNone(create_team(p2, p1))

    def test_create_team_custom_elos_and_last_match(self):
        """
        Test creating a team with custom ELOs and last_match_at.
        """
        p1 = create_player("Cathy")
        p2 = create_player("Dan")
        team_id = create_team(p1, p2, global_elo=1200.0, last_match_at="2023-01-01 12:00:00")
        self.assertIsNotNone(team_id)
        team = get_team(team_id)
        self.assertEqual(team["global_elo"], 1200.0)
        import datetime

        self.assertIsInstance(team["last_match_at"], datetime.datetime)
        self.assertEqual(team["last_match_at"], datetime.datetime(2023, 1, 1, 12, 0, 0))

    def test_get_team_not_exists(self):
        """
        Test retrieving a non-existent team.
        """
        self.assertIsNone(get_team(9999))

    def test_get_all_teams_empty(self):
        """
        Test get_all_teams on empty DB.
        """
        self.assertEqual(get_all_teams(), [])

    def test_get_all_teams_multiple(self):
        """
        Test retrieving multiple teams.
        """
        p1 = create_player("Charlie")
        p2 = create_player("David")
        t1 = create_team(p1, p2)
        p3 = create_player("Eve")
        t2 = create_team(p1, p3)
        teams = get_all_teams()
        self.assertEqual(len(teams), 2)
        ids = {team["team_id"] for team in teams}
        self.assertIn(t1, ids)
        self.assertIn(t2, ids)

    def test_delete_team(self):
        """
        Test deleting a team.
        """
        p1 = create_player("Frank")
        p2 = create_player("Grace")
        team_id = create_team(p1, p2)
        self.assertTrue(delete_team(team_id))
        self.assertIsNone(get_team(team_id))
        self.assertFalse(delete_team(team_id))

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

    def test_update_team(self):
        """
        Test updating team ELOs and last_match_at, including edge and failure cases.
        """
        p1 = create_player("Heidi")
        p2 = create_player("Ivan")
        team_id = create_team(p1, p2)

        # ##: Update global_elo only.
        self.assertTrue(update_team(team_id, global_elo=1500.0))
        team = get_team(team_id)
        self.assertEqual(team["global_elo"], 1500.0)

        # ##: Update last_match_at only.
        self.assertTrue(update_team(team_id, last_match_at="2023-02-02 15:00:00"))
        team = get_team(team_id)
        self.assertIsInstance(team["last_match_at"], datetime)
        self.assertEqual(team["last_match_at"], datetime(2023, 2, 2, 15, 0, 0))

        # ##: No fields to update (failure).
        self.assertFalse(update_team(team_id))

        # ##: Non-existent team.
        self.assertFalse(update_team(9999, global_elo=1234.0))

    def test_create_team_same_player(self):
        """
        Test creating a team with the same player for both slots (should fail due to CHECK constraint).
        """
        p1 = create_player("Jack")
        team_id = create_team(p1, p1)
        self.assertIsNone(team_id)

    def test_get_teams_by_player(self):
        """
        Test retrieving all teams that a specific player is part of.
        """
        # Create players
        p1 = create_player("Alice")
        p2 = create_player("Bob")
        p3 = create_player("Charlie")
        p4 = create_player("David")

        # Create teams with different combinations
        t1 = create_team(p1, p2)  # Alice and Bob
        t2 = create_team(p1, p3)  # Alice and Charlie
        t3 = create_team(p3, p4)  # Charlie and David (no Alice)

        # Test getting teams for Alice (should be in 2 teams)
        alice_teams = get_teams_by_player(p1)
        self.assertEqual(len(alice_teams), 2)
        team_ids = {team["team_id"] for team in alice_teams}
        self.assertIn(t1, team_ids)
        self.assertIn(t2, team_ids)

        # Check that partner_id and is_player1 fields are correctly set
        for team in alice_teams:
            if team["team_id"] == t1:
                self.assertEqual(team["partner_id"], p2)  # Bob is partner
            elif team["team_id"] == t2:
                self.assertEqual(team["partner_id"], p3)  # Charlie is partner

            # Alice should be player1 in both teams since we created them with Alice as player1
            self.assertTrue(team["is_player1"])
            self.assertEqual(team["player1_id"], p1)

        # Test getting teams for Charlie (should be in 2 teams)
        charlie_teams = get_teams_by_player(p3)
        self.assertEqual(len(charlie_teams), 2)
        team_ids = {team["team_id"] for team in charlie_teams}
        self.assertIn(t2, team_ids)
        self.assertIn(t3, team_ids)

        # Test getting teams for David (should be in 1 team)
        david_teams = get_teams_by_player(p4)
        self.assertEqual(len(david_teams), 1)
        self.assertEqual(david_teams[0]["team_id"], t3)
        self.assertEqual(david_teams[0]["partner_id"], p3)  # Charlie is partner

        # Test getting teams for non-existent player
        nonexistent_teams = get_teams_by_player(9999)
        self.assertEqual(len(nonexistent_teams), 0)


if __name__ == "__main__":
    main()
