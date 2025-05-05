# -*- coding: utf-8 -*-
"""
Unit tests for transaction management.
"""

from unittest import TestCase, main
from unittest.mock import MagicMock, patch

from app.db.database import DatabaseManager
from app.db.transaction import TransactionHandler, transaction


class TestTransactionHandler(TestCase):
    """Tests for the TransactionHandler class."""

    def setUp(self):
        """Set up a mock DatabaseManager."""
        self.mock_db = MagicMock(spec=DatabaseManager)
        self.handler = TransactionHandler()

    def test_begin(self):
        """Test that begin executes the BEGIN command."""
        self.handler.begin(self.mock_db)
        self.mock_db.execute.assert_called_once_with("BEGIN;")

    def test_commit(self):
        """Test that commit executes the COMMIT command."""
        self.handler.commit(self.mock_db)
        self.mock_db.execute.assert_called_once_with("COMMIT;")

    def test_rollback(self):
        """Test that rollback executes the ROLLBACK command."""
        self.handler.rollback(self.mock_db)
        self.mock_db.execute.assert_called_once_with("ROLLBACK;")


class TestTransactionContextManager(TestCase):
    """Tests for the transaction context manager."""

    @patch("app.db.transaction.DatabaseManager")
    @patch("app.db.transaction.TransactionHandler")
    def test_transaction_success(self, MockTransactionHandler, MockDatabaseManager):
        """Test successful transaction execution."""
        mock_db_instance = MockDatabaseManager.return_value
        mock_handler_instance = MockTransactionHandler.return_value

        with transaction() as db:
            self.assertEqual(db, mock_db_instance)
            # ##: Simulate some database operation within the context.
            db.execute("SELECT 1;")

        mock_handler_instance.begin.assert_called_once_with(mock_db_instance)
        mock_db_instance.execute.assert_called_once_with("SELECT 1;")
        mock_handler_instance.commit.assert_called_once_with(mock_db_instance)
        mock_handler_instance.rollback.assert_not_called()

    @patch("app.db.transaction.DatabaseManager")
    @patch("app.db.transaction.TransactionHandler")
    def test_transaction_failure(self, MockTransactionHandler, MockDatabaseManager):
        """Test transaction rollback on exception."""
        mock_db_instance = MockDatabaseManager.return_value
        mock_handler_instance = MockTransactionHandler.return_value
        test_exception = ValueError("Something went wrong")

        with self.assertRaises(ValueError) as cm:
            with transaction() as db:
                self.assertEqual(db, mock_db_instance)
                # ##: Simulate a failing operation.
                raise test_exception

        self.assertEqual(cm.exception, test_exception)
        mock_handler_instance.begin.assert_called_once_with(mock_db_instance)
        mock_handler_instance.commit.assert_not_called()
        mock_handler_instance.rollback.assert_called_once_with(mock_db_instance)


if __name__ == "__main__":
    main()
