# -*- coding: utf-8 -*-
"""
Database tests.
"""

from datetime import datetime
from unittest import TestCase, main

from app.db.database import DatabaseManager
from app.db.initializer import initialize_database


class TestDatabase(TestCase):
    """Test the DatabaseManager class."""

    def setUp(self):
        """Set up the test environment."""
        self.db = DatabaseManager(db_path=":memory:")
        initialize_database(self.db)

    def test_initialize_database_creates_all_tables(self):
        """Test that initialize_database creates all required tables and is idempotent."""
        expected_tables = {
            "Players",
            "Teams",
            "Matches",
            "ELO_History",
        }

        initialize_database(self.db)
        tables = set(
            row[0]
            for row in self.db.fetchall("SELECT table_name FROM information_schema.tables WHERE table_schema='main'")
        )
        for table in expected_tables:
            self.assertIn(table, tables)

        initialize_database(self.db)
        tables2 = set(
            row[0]
            for row in self.db.fetchall("SELECT table_name FROM information_schema.tables WHERE table_schema='main'")
        )
        for table in expected_tables:
            self.assertIn(table, tables2)

    def tearDown(self):
        """Clean up the test environment."""
        self.db.close()

    def test_connection(self):
        """Test database connection."""
        result = self.db.fetchone("SELECT 1")
        self.assertEqual(result[0], 1)

    def test_schema_creation(self):
        """Test schema creation."""
        table = self.db.fetchone("SELECT table_name FROM information_schema.tables WHERE table_name='Players'")
        self.assertIsNotNone(table)
        self.assertEqual(table[0], "Players")

    def test_crud_operations(self):
        """Test CRUD operations."""
        now = datetime.now()

        self.db.execute("INSERT INTO Players (player_id, name, created_at) VALUES (?, ?, ?)", (1, "Alice", now))
        joueur = self.db.fetchone("SELECT * FROM Players WHERE player_id=1")
        self.assertIsNotNone(joueur)
        self.assertEqual(joueur[1], "Alice")

        self.db.execute("UPDATE Players SET name=? WHERE player_id=?", ("Bob", 1))
        updated_name = self.db.fetchone("SELECT name FROM Players WHERE player_id=1")[0]
        self.assertEqual(updated_name, "Bob")

        self.db.execute("DELETE FROM Players WHERE player_id=1")
        deleted = self.db.fetchone("SELECT * FROM Players WHERE player_id=1")
        self.assertIsNone(deleted)


if __name__ == "__main__":
    main()
