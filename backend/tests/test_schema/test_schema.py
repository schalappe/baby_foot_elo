# -*- coding: utf-8 -*-
"""
Unit tests for the schema definitions module.
"""

from unittest import TestCase, main

import duckdb

from app import schema


def get_table_info(con, table_name):
    """Get comprehensive table information from DuckDB (name, type, notnull, dflt_value, pk)."""
    return {
        row[1]: {"type": row[2], "notnull": bool(row[3]), "dflt_value": row[4], "pk": bool(row[5])}
        for row in con.execute(f"PRAGMA table_info('{table_name}')").fetchall()
    }


def get_indexes_info(con, table_name):
    """Get index information for a table from sqlite_master."""
    query = f"SELECT name FROM sqlite_master WHERE type = 'index' AND tbl_name = '{table_name}';"
    return [row[0] for row in con.execute(query).fetchall()]


def get_foreign_key_constraints(con, table_name):
    """Retrieves foreign key constraint details by parsing the CREATE TABLE statement."""
    create_table_sql = con.execute(
        f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}';"
    ).fetchone()[0]
    fks = []
    parts = create_table_sql.split(",")
    for part in parts:
        part_upper = part.strip().upper()
        if "FOREIGN KEY" in part_upper and "REFERENCES" in part_upper:
            fks.append(part.strip())
    return fks


class TestSchemaDefinitions(TestCase):
    """Unit tests for the schema definitions module."""

    @classmethod
    def setUpClass(cls):
        cls.con = duckdb.connect(database=":memory:")
        sequences = [
            schema.CREATE_SEQ_PLAYERS,
            schema.CREATE_SEQ_TEAMS,
            schema.CREATE_SEQ_MATCHES,
            schema.CREATE_SEQ_ELO_HISTORY,
        ]
        for sql in sequences:
            cls.con.execute(sql)

        tables = [
            schema.CREATE_PLAYERS_TABLE,
            schema.CREATE_TEAMS_TABLE,
            schema.CREATE_MATCHES_TABLE,
            schema.CREATE_ELO_HISTORY_TABLE,
        ]
        for sql in tables:
            try:
                cls.con.execute(sql)
            except duckdb.ParserException as e:
                print(f"Failed to execute SQL for table: {sql}")
                raise e

        indexes = [
            schema.CREATE_INDEX_PLAYERS_NAME,
            schema.CREATE_INDEX_TEAMS_PLAYER_PAIR_ORDER_INSENSITIVE,
            schema.CREATE_INDEX_MATCHES_WINNER_TEAM_ID,
            schema.CREATE_INDEX_MATCHES_LOSER_TEAM_ID,
            schema.CREATE_INDEX_MATCHES_PLAYED_AT,
            schema.CREATE_INDEX_ELOHIST_PLAYER_ID,
            schema.CREATE_INDEX_ELOHIST_MATCH_ID,
            schema.CREATE_INDEX_ELOHIST_DATE,
        ]
        for sql in indexes:
            try:
                cls.con.execute(sql)
            except duckdb.ParserException as e:
                print(f"Failed to execute SQL for index: {sql}")
                raise e

    @classmethod
    def tearDownClass(cls):
        cls.con.close()

    def assertColumn(self, table_info, col_name, expected_type, is_notnull, dflt_val_contains=None, is_pk=False):
        self.assertIn(col_name, table_info, f"Column {col_name} not found.")
        col = table_info[col_name]
        self.assertEqual(col["type"].upper(), expected_type.upper(), f"Type mismatch for {col_name}")
        self.assertEqual(col["notnull"], is_notnull, f"NOT NULL constraint mismatch for {col_name}")
        if dflt_val_contains:
            self.assertIsNotNone(col["dflt_value"], f"{col_name} default value is None")
            self.assertIn(
                dflt_val_contains,
                str(col["dflt_value"]),
                f"{col_name} default value content mismatch",
            )
        else:
            self.assertIsNone(col["dflt_value"], f"{col_name} default value expected to be None")
        self.assertEqual(col["pk"], is_pk, f"Primary Key constraint mismatch for {col_name}")

    def test_players_table(self):
        table_info = get_table_info(self.con, "Players")
        self.assertColumn(table_info, "player_id", "INTEGER", True, "nextval('seq_players_id')", True)
        self.assertColumn(table_info, "name", "VARCHAR", True)
        self.assertColumn(table_info, "global_elo", "INTEGER", True, "1000")
        self.assertColumn(table_info, "created_at", "TIMESTAMP", True, "CURRENT_TIMESTAMP")
        indexes = get_indexes_info(self.con, "Players")
        self.assertIn("idx_players_name", indexes)

    def test_teams_table(self):
        table_info = get_table_info(self.con, "Teams")
        self.assertColumn(table_info, "team_id", "INTEGER", True, "nextval('seq_teams_id')", True)
        self.assertColumn(table_info, "player1_id", "INTEGER", True)
        self.assertColumn(table_info, "player2_id", "INTEGER", True)
        self.assertColumn(table_info, "global_elo", "FLOAT", True, "1000.0")
        self.assertColumn(table_info, "created_at", "TIMESTAMP", True, "CURRENT_TIMESTAMP")
        self.assertColumn(table_info, "last_match_at", "TIMESTAMP", False)

        # ##: Test Foreign Keys (simplified check by string presence).
        fks = get_foreign_key_constraints(self.con, "Teams")
        self.assertTrue(any("FOREIGN KEY (player1_id) REFERENCES Players(player_id)" in fk for fk in fks))
        self.assertTrue(any("FOREIGN KEY (player2_id) REFERENCES Players(player_id)" in fk for fk in fks))

        # ##: Test UNIQUE constraint (player1_id, player2_id).
        self.con.execute("INSERT INTO Players (name) VALUES ('P1'), ('P2')")
        p1_id = self.con.execute("SELECT player_id FROM Players WHERE name='P1'").fetchone()[0]
        p2_id = self.con.execute("SELECT player_id FROM Players WHERE name='P2'").fetchone()[0]
        self.con.execute("INSERT INTO Teams (player1_id, player2_id) VALUES (?, ?)", (p1_id, p2_id))
        with self.assertRaises(duckdb.ConstraintException, msg="UNIQUE constraint on (player1_id, player2_id) failed"):
            self.con.execute("INSERT INTO Teams (player1_id, player2_id) VALUES (?, ?)", (p1_id, p2_id))
        with self.assertRaises(
            duckdb.ConstraintException,
            msg="UNIQUE constraint on (player1_id, player2_id) failed for swapped players",
        ):
            self.con.execute("INSERT INTO Teams (player1_id, player2_id) VALUES (?, ?)", (p2_id, p1_id))

        # ##: Test CHECK constraint (player1_id <> player2_id).
        with self.assertRaises(duckdb.ConstraintException, msg="CHECK constraint player1_id <> player2_id failed"):
            self.con.execute("INSERT INTO Teams (player1_id, player2_id) VALUES (?, ?)", (p1_id, p1_id))

    def test_matches_table(self):
        table_info = get_table_info(self.con, "Matches")
        self.assertColumn(table_info, "match_id", "INTEGER", True, "nextval('seq_matches_id')", True)
        self.assertColumn(table_info, "winner_team_id", "INTEGER", True)
        self.assertColumn(table_info, "loser_team_id", "INTEGER", True)
        self.assertColumn(table_info, "is_fanny", "BOOLEAN", True, "CAST('f' AS BOOLEAN)")
        self.assertColumn(table_info, "played_at", "TIMESTAMP", True)
        self.assertColumn(table_info, "year", "INTEGER", True)
        self.assertColumn(table_info, "month", "INTEGER", True)
        self.assertColumn(table_info, "day", "INTEGER", True)

        fks = get_foreign_key_constraints(self.con, "Matches")
        self.assertTrue(any("FOREIGN KEY (winner_team_id) REFERENCES Teams(team_id)" in fk for fk in fks))
        self.assertTrue(any("FOREIGN KEY (loser_team_id) REFERENCES Teams(team_id)" in fk for fk in fks))

        indexes = get_indexes_info(self.con, "Matches")
        self.assertIn("idx_matches_winner_team_id", indexes)
        self.assertIn("idx_matches_loser_team_id", indexes)
        self.assertIn("idx_matches_played_at", indexes)

        # ##: Test CHECK constraint (winner_team_id <> loser_team_id).
        self.con.execute("INSERT INTO Players (name) VALUES ('P3'), ('P4'), ('P5'), ('P6')")
        p3_id = self.con.execute("SELECT player_id FROM Players WHERE name='P3'").fetchone()[0]
        p4_id = self.con.execute("SELECT player_id FROM Players WHERE name='P4'").fetchone()[0]
        self.con.execute("INSERT INTO Teams (player1_id, player2_id) VALUES (?, ?)", (p3_id, p4_id))
        t1_id = self.con.execute("SELECT team_id FROM Teams WHERE player1_id=?", (p3_id,)).fetchone()[0]
        with self.assertRaises(
            duckdb.ConstraintException,
            msg="CHECK constraint winner_team_id <> loser_team_id failed",
        ):
            self.con.execute(
                "INSERT INTO Matches (winner_team_id, loser_team_id, played_at, year, month, day) VALUES (?, ?, CURRENT_TIMESTAMP, 2024, 1, 1)",
                (t1_id, t1_id),
            )

    def test_elo_history_table(self):
        table_info = get_table_info(self.con, "ELO_History")
        self.assertColumn(table_info, "history_id", "INTEGER", True, "nextval('seq_elo_history_id')", True)
        self.assertColumn(table_info, "player_id", "INTEGER", True)
        self.assertColumn(table_info, "match_id", "INTEGER", True)
        self.assertColumn(table_info, "old_elo", "INTEGER", True)
        self.assertColumn(table_info, "new_elo", "INTEGER", True)
        self.assertColumn(table_info, "difference", "INTEGER", True)
        self.assertColumn(table_info, "date", "TIMESTAMP", True)
        self.assertColumn(table_info, "year", "INTEGER", True)
        self.assertColumn(table_info, "month", "INTEGER", True)
        self.assertColumn(table_info, "day", "INTEGER", True)

        fks = get_foreign_key_constraints(self.con, "ELO_History")
        self.assertTrue(any("FOREIGN KEY (player_id) REFERENCES Players(player_id)" in fk for fk in fks))
        self.assertTrue(any("FOREIGN KEY (match_id) REFERENCES Matches(match_id)" in fk for fk in fks))

        indexes = get_indexes_info(self.con, "ELO_History")
        self.assertIn("idx_elohist_player_id", indexes)
        self.assertIn("idx_elohist_match_id", indexes)
        self.assertIn("idx_elohist_date", indexes)


if __name__ == "__main__":
    main()
