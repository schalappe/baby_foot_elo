# -*- coding: utf-8 -*-
"""
Database tests.
"""

from datetime import datetime
from unittest import TestCase, main

from app.db.database_manager import DatabaseManager

# ##: Schema SQL for Joueurs table.
CREATE_JOUEURS_SQL = '''
CREATE TABLE IF NOT EXISTS Joueurs (
    id INTEGER PRIMARY KEY,
    nom VARCHAR,
    elo INTEGER,
    date_creation TIMESTAMP
);
'''

class TestDatabase(TestCase):
    def setUp(self):
        """
        Set up the test environment.
        """
        self.db = DatabaseManager(db_path=':memory:')
        self.db.execute(CREATE_JOUEURS_SQL)

    def tearDown(self):
        """
        Clean up the test environment.
        """
        self.db.close()

    def test_connection(self):
        """
        Test database connection.
        """
        result = self.db.fetchone('SELECT 1')
        self.assertEqual(result[0], 1)

    def test_schema_creation(self):
        """
        Test schema creation.
        """
        table = self.db.fetchone("SELECT table_name FROM information_schema.tables WHERE table_name='Joueurs'")
        self.assertIsNotNone(table)
        self.assertEqual(table[0], 'Joueurs')

    def test_crud_operations(self):
        """
        Test CRUD operations.
        """
        now = datetime.now()
        self.db.execute("INSERT INTO Joueurs (id, nom, elo, date_creation) VALUES (?, ?, ?, ?)", (1, 'Alice', 1000, now))
        joueur = self.db.fetchone("SELECT * FROM Joueurs WHERE id=1")
        self.assertIsNotNone(joueur)
        self.assertEqual(joueur[1], 'Alice')
        
        self.db.execute("UPDATE Joueurs SET elo=? WHERE id=?", (1100, 1))
        updated_elo = self.db.fetchone("SELECT elo FROM Joueurs WHERE id=1")[0]
        self.assertEqual(updated_elo, 1100)
        
        self.db.execute("DELETE FROM Joueurs WHERE id=1")
        deleted = self.db.fetchone("SELECT * FROM Joueurs WHERE id=1")
        self.assertIsNone(deleted)

if __name__ == '__main__':
    main()
