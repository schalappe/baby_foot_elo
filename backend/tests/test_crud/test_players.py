# -*- coding: utf-8 -*-
"""
Unit tests for player CRUD operations using unittest.
"""

import unittest
from app.db import DatabaseManager, initialize_database 

from app.crud.players import (
    batch_insert_players,
    create_player,
    delete_player,
    get_all_players,
    get_player,
    search_players,
    update_player,
)


class TestPlayerCRUD(unittest.TestCase):
    """Test suite for player CRUD operations."""

    def setUp(self):
        """Prepare for each test: Create a fresh in-memory DB and schema."""
        DatabaseManager._instance = None
        self.db = DatabaseManager(db_path=":memory:")
        initialize_database(self.db)

    def tearDown(self):
        """Clean up after each test: Close connection and reset singleton."""
        if hasattr(self, 'db') and self.db.connection:
            self.db.close()
        DatabaseManager._instance = None

    def test_create_player(self):
        """Test creating a single player."""
        player_name = "Alice"
        player_id = create_player(player_name)
        self.assertIsNotNone(player_id)
        self.assertIsInstance(player_id, int)

        retrieved_player = get_player(player_id)
        self.assertIsNotNone(retrieved_player)
        self.assertEqual(retrieved_player["name"], player_name)
        self.assertEqual(retrieved_player["player_id"], player_id)

    def test_get_player_exists(self):
        """Test retrieving an existing player."""
        player_name = "Bob"
        player_id = create_player(player_name)
        self.assertIsNotNone(player_id)

        retrieved_player = get_player(player_id)
        self.assertIsNotNone(retrieved_player)
        self.assertEqual(retrieved_player["name"], player_name)
        self.assertEqual(retrieved_player["player_id"], player_id)

    def test_get_player_not_exists(self):
        """Test retrieving a non-existent player."""
        retrieved_player = get_player(99999)
        self.assertIsNone(retrieved_player)

    def test_get_all_players_empty(self):
        """Test getting all players when the table is empty."""
        players = get_all_players()
        self.assertEqual(players, [])

    def test_get_all_players_multiple(self):
        """Test getting all players when multiple exist."""
        id1 = create_player("Charlie")
        id2 = create_player("David")
        self.assertIsNotNone(id1)
        self.assertIsNotNone(id2)

        players = get_all_players()
        self.assertEqual(len(players), 2)
        player_names = {p["name"] for p in players}
        self.assertEqual(player_names, {"Charlie", "David"})
        self.assertEqual(players[0]["name"], "Charlie")
        self.assertEqual(players[1]["name"], "David")

    def test_update_player_exists(self):
        """Test updating an existing player."""
        player_name = "Eve"
        player_id = create_player(player_name)
        self.assertIsNotNone(player_id)

        new_name = "Evelyn"
        updated = update_player(player_id, new_name)
        self.assertTrue(updated)

        retrieved_player = get_player(player_id)
        self.assertIsNotNone(retrieved_player)
        self.assertEqual(retrieved_player["name"], new_name)

    def test_update_player_not_exists(self):
        """Test updating a non-existent player."""
        updated = update_player(99999, "No One")
        self.assertFalse(updated)

    def test_delete_player_exists(self):
        """Test deleting an existing player."""
        player_name = "Frank"
        player_id = create_player(player_name)
        self.assertIsNotNone(player_id)
        self.assertIsNotNone(get_player(player_id))

        deleted = delete_player(player_id)
        self.assertTrue(deleted)
        self.assertIsNone(get_player(player_id))

    def test_delete_player_not_exists(self):
        """Test deleting a non-existent player."""
        deleted = delete_player(99999)
        self.assertFalse(deleted)

    def test_batch_insert_players(self):
        """Test inserting multiple players in a batch."""
        players_to_insert = [{"name": "Grace"}, {"name": "Heidi"}]
        player_ids = batch_insert_players(players_to_insert)

        self.assertEqual(len(player_ids), 2)
        self.assertTrue(all(isinstance(pid, int) for pid in player_ids))

        all_players = get_all_players()
        self.assertEqual(len(all_players), 2)
        player_names = {p["name"] for p in all_players}
        self.assertEqual(player_names, {"Grace", "Heidi"})

    def test_search_players_found(self):
        """Test searching for players that exist."""
        create_player("Ivy")
        create_player("Judy")
        create_player("Ivan")

        results = search_players("Iv")
        self.assertEqual(len(results), 2)
        names = {p["name"] for p in results}
        self.assertEqual(names, {"Ivan", "Ivy"})
        self.assertEqual(results[0]["name"], "Ivan")
        self.assertEqual(results[1]["name"], "Ivy")

    def test_search_players_not_found(self):
        """Test searching for players that do not exist."""
        create_player("Mallory")
        results = search_players("Xyz")
        self.assertEqual(results, [])

    def test_search_players_limit(self):
        """Test the limit parameter in search."""
        create_player("Player A")
        create_player("Player B")
        create_player("Player C")

        results = search_players("Player", limit=2)
        self.assertEqual(len(results), 2)
        names = {p["name"] for p in results}
        self.assertEqual(names, {"Player A", "Player B"})


if __name__ == '__main__':
    unittest.main()
