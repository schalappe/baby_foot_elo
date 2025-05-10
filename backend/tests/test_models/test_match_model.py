# -*- coding: utf-8 -*-
"""
Unit tests for match Pydantic models.
"""

from datetime import datetime, timezone
from typing import Optional
from unittest import TestCase, main

from pydantic import BaseModel, Field, ValidationError

from app.models.match import MatchCreate, MatchResponse, MatchUpdate


class MockTeamForMatch(BaseModel):
    team_id: int
    player1_id: int
    player2_id: int
    global_elo: float = 1000.0
    current_month_elo: float = 1000.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_match_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TestMatchModels(TestCase):
    """
    Test suite for match Pydantic models.
    """

    def test_match_create_valid(self):
        """
        Test MatchCreate with valid data and date part derivation.
        """
        played_timestamp = datetime(2023, 10, 26, 14, 30, 0, tzinfo=timezone.utc)
        data = {
            "winner_team_id": 1,
            "loser_team_id": 2,
            "is_fanny": True,
            "played_at": played_timestamp,
        }
        match = MatchCreate(**data)
        self.assertEqual(match.winner_team_id, 1)
        self.assertEqual(match.loser_team_id, 2)
        self.assertTrue(match.is_fanny)
        self.assertEqual(match.played_at, played_timestamp)
        self.assertEqual(match.year, 2023)
        self.assertEqual(match.month, 10)
        self.assertEqual(match.day, 26)

    def test_match_create_default_fanny(self):
        """
        Test MatchCreate with default is_fanny value.
        """
        played_timestamp = datetime.now(timezone.utc)
        match = MatchCreate(winner_team_id=3, loser_team_id=4, played_at=played_timestamp)
        self.assertFalse(match.is_fanny)

    def test_match_create_invalid_same_teams(self):
        """
        Test MatchCreate with winner_team_id and loser_team_id being the same.
        """
        played_timestamp = datetime.now(timezone.utc)
        with self.assertRaises(ValidationError) as context:
            MatchCreate(winner_team_id=1, loser_team_id=1, played_at=played_timestamp)

        errors = context.exception.errors()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["type"], "value_error")
        self.assertIn("Winner and loser team IDs cannot be the same", str(errors[0]["msg"]))

    def test_match_create_invalid_team_id_zero(self):
        """
        Test MatchCreate with team ID being zero.
        """
        played_timestamp = datetime.now(timezone.utc)
        with self.assertRaises(ValidationError):
            MatchCreate(winner_team_id=0, loser_team_id=1, played_at=played_timestamp)
        with self.assertRaises(ValidationError):
            MatchCreate(winner_team_id=1, loser_team_id=0, played_at=played_timestamp)

    def test_match_update_valid(self):
        """
        Test MatchUpdate (currently a placeholder, should instantiate).
        """
        match_update = MatchUpdate()
        self.assertIsInstance(match_update, MatchUpdate)

    def test_match_response_valid_no_teams(self):
        """
        Test MatchResponse with valid data, without nested team objects.
        """
        played_timestamp = datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        data = {
            "match_id": 100,
            "winner_team_id": 10,
            "loser_team_id": 20,
            "is_fanny": False,
            "played_at": played_timestamp,
            "year": 2023,
            "month": 1,
            "day": 1,
        }
        match_response = MatchResponse(**data)
        self.assertEqual(match_response.match_id, 100)
        self.assertEqual(match_response.winner_team_id, 10)
        self.assertEqual(match_response.loser_team_id, 20)
        self.assertEqual(match_response.year, 2023)
        self.assertIsNone(match_response.winner_team)
        self.assertIsNone(match_response.loser_team)

    def test_match_response_valid_with_teams(self):
        """
        Test MatchResponse with valid data, including nested team objects.
        """
        played_timestamp = datetime(2023, 5, 5, 12, 0, 0, tzinfo=timezone.utc)
        winner_team_data = MockTeamForMatch(team_id=30, player1_id=1, player2_id=2, created_at=played_timestamp)
        loser_team_data = MockTeamForMatch(team_id=40, player1_id=3, player2_id=4, created_at=played_timestamp)

        data = {
            "match_id": 200,
            "winner_team_id": 30,
            "loser_team_id": 40,
            "is_fanny": True,
            "played_at": played_timestamp,
            "year": 2023,
            "month": 5,
            "day": 5,
            "winner_team": winner_team_data,
            "loser_team": loser_team_data,
        }
        match_response = MatchResponse(**data)
        self.assertEqual(match_response.match_id, 200)
        self.assertIsNotNone(match_response.winner_team)
        self.assertEqual(match_response.winner_team.team_id, 30)
        self.assertIsNotNone(match_response.loser_team)
        self.assertEqual(match_response.loser_team.team_id, 40)

    def test_match_response_from_attributes(self):
        """
        Test MatchResponse creation using from_attributes (model_config).
        Simulates creating a response model from a DB ORM-like object.
        """

        class MockMatchDB:
            def __init__(self, match_id, winner_team_id, loser_team_id, is_fanny, played_at, year, month, day):
                self.match_id = match_id
                self.winner_team_id = winner_team_id
                self.loser_team_id = loser_team_id
                self.is_fanny = is_fanny
                self.played_at = played_at
                self.year = year
                self.month = month
                self.day = day

        played_timestamp = datetime.now(timezone.utc)
        mock_db_match = MockMatchDB(
            match_id=300,
            winner_team_id=50,
            loser_team_id=60,
            is_fanny=False,
            played_at=played_timestamp,
            year=played_timestamp.year,
            month=played_timestamp.month,
            day=played_timestamp.day,
        )

        match_response = MatchResponse.model_validate(mock_db_match)

        self.assertEqual(match_response.match_id, 300)
        self.assertEqual(match_response.winner_team_id, 50)
        self.assertEqual(match_response.loser_team_id, 60)
        self.assertEqual(match_response.played_at, played_timestamp)
        self.assertEqual(match_response.year, played_timestamp.year)
        self.assertIsNone(match_response.winner_team)
        self.assertIsNone(match_response.loser_team)


if __name__ == "__main__":
    main()
