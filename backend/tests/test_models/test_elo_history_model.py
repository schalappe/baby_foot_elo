# -*- coding: utf-8 -*-
"""
Unit tests for ELO history Pydantic models.
"""

from datetime import datetime, timezone
from unittest import TestCase, main

from pydantic import ValidationError

from app.models.elo_history import EloHistoryCreate, EloHistoryResponse, EloHistoryUpdate


class TestEloHistoryModels(TestCase):
    """
    Test suite for ELO history Pydantic models.
    """

    def test_elo_history_create_valid_global(self):
        """
        Test EloHistoryCreate with valid data for 'global' type.
        """
        event_date = datetime(2023, 11, 15, 10, 0, 0, tzinfo=timezone.utc)
        data = {
            "player_id": 1,
            "match_id": 10,
            "type": "global",
            "old_elo": 1000,
            "new_elo": 1025,
            "difference": 25,
            "date": event_date,
        }
        history = EloHistoryCreate(**data)
        self.assertEqual(history.player_id, 1)
        self.assertEqual(history.match_id, 10)
        self.assertEqual(history.type, "global")
        self.assertEqual(history.old_elo, 1000)
        self.assertEqual(history.new_elo, 1025)
        self.assertEqual(history.difference, 25)
        self.assertEqual(history.date, event_date)
        self.assertEqual(history.year, 2023)
        self.assertEqual(history.month, 11)
        self.assertEqual(history.day, 15)

    def test_elo_history_create_valid_monthly(self):
        """
        Test EloHistoryCreate with valid data for 'monthly' type.
        """
        event_date = datetime(2023, 12, 1, 18, 30, 0, tzinfo=timezone.utc)
        data = {
            "player_id": 2,
            "match_id": 12,
            "type": "monthly",
            "old_elo": 950,
            "new_elo": 930,
            "difference": -20,
            "date": event_date,
        }
        history = EloHistoryCreate(**data)
        self.assertEqual(history.type, "monthly")
        self.assertEqual(history.difference, -20)
        self.assertEqual(history.year, 2023)
        self.assertEqual(history.month, 12)
        self.assertEqual(history.day, 1)

    def test_elo_history_create_invalid_type(self):
        """
        Test EloHistoryCreate with an invalid ELO type.
        """
        event_date = datetime.now(timezone.utc)
        with self.assertRaises(ValidationError):
            EloHistoryCreate(
                player_id=1,
                match_id=1,
                type="annual",
                old_elo=1000,
                new_elo=1010,
                difference=10,
                date=event_date,
            )

    def test_elo_history_create_invalid_difference(self):
        """
        Test EloHistoryCreate with inconsistent ELO difference.
        """
        event_date = datetime.now(timezone.utc)
        with self.assertRaises(ValidationError) as context:
            EloHistoryCreate(
                player_id=1,
                match_id=1,
                type="global",
                old_elo=1000,
                new_elo=1010,
                difference=5,
                date=event_date,  # Expected 10
            )
        errors = context.exception.errors()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["type"], "value_error")
        self.assertIn("ELO difference does not match new_elo - old_elo", str(errors[0]["msg"]))

    def test_elo_history_create_invalid_player_id_zero(self):
        """
        Test EloHistoryCreate with player ID being zero.
        """
        event_date = datetime.now(timezone.utc)
        with self.assertRaises(ValidationError):
            EloHistoryCreate(
                player_id=0,
                match_id=1,
                type="global",
                old_elo=1000,
                new_elo=1000,
                difference=0,
                date=event_date,
            )

    def test_elo_history_create_invalid_match_id_zero(self):
        """
        Test EloHistoryCreate with match ID being zero.
        """
        event_date = datetime.now(timezone.utc)
        with self.assertRaises(ValidationError):
            EloHistoryCreate(
                player_id=1,
                match_id=0,
                type="global",
                old_elo=1000,
                new_elo=1000,
                difference=0,
                date=event_date,
            )

    def test_elo_history_update_valid(self):
        """
        Test EloHistoryUpdate (currently a placeholder, should instantiate).
        """
        history_update = EloHistoryUpdate()
        self.assertIsInstance(history_update, EloHistoryUpdate)

    def test_elo_history_response_valid(self):
        """
        Test EloHistoryResponse with valid data.
        """
        event_date = datetime(2023, 10, 1, 0, 0, 0, tzinfo=timezone.utc)
        data = {
            "history_id": 100,
            "player_id": 5,
            "match_id": 50,
            "type": "monthly",
            "old_elo": 1200,
            "new_elo": 1215,
            "difference": 15,
            "date": event_date,
            "year": 2023,
            "month": 10,
            "day": 1,
        }
        response = EloHistoryResponse(**data)
        self.assertEqual(response.history_id, 100)
        self.assertEqual(response.type, "monthly")
        self.assertEqual(response.year, 2023)

    def test_elo_history_response_from_attributes(self):
        """
        Test EloHistoryResponse creation using from_attributes.
        """

        class MockEloHistoryDB:
            def __init__(
                self,
                history_id,
                player_id,
                match_id,
                type,
                old_elo,
                new_elo,
                difference,
                date,
                year,
                month,
                day,
            ):
                self.history_id = history_id
                self.player_id = player_id
                self.match_id = match_id
                self.type = type
                self.old_elo = old_elo
                self.new_elo = new_elo
                self.difference = difference
                self.date = date
                self.year = year
                self.month = month
                self.day = day

        event_date = datetime.now(timezone.utc)
        mock_db_entry = MockEloHistoryDB(
            history_id=200,
            player_id=8,
            match_id=80,
            type="global",
            old_elo=1500,
            new_elo=1480,
            difference=-20,
            date=event_date,
            year=event_date.year,
            month=event_date.month,
            day=event_date.day,
        )
        response = EloHistoryResponse.model_validate(mock_db_entry)
        self.assertEqual(response.history_id, 200)
        self.assertEqual(response.player_id, 8)
        self.assertEqual(response.difference, -20)
        self.assertEqual(response.date, event_date)


if __name__ == "__main__":
    main()
