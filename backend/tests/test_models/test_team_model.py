# -*- coding: utf-8 -*-
"""
Unit tests for team Pydantic models.
"""

from datetime import datetime, timezone
from typing import Optional
from unittest import TestCase, main

from pydantic import BaseModel, ValidationError

from app.models.team import TeamCreate, TeamResponse, TeamUpdate


class MockPlayerForTeam(BaseModel):
    id: int
    name: str
    global_elo: int
    current_month_elo: int
    creation_date: datetime
    matches_played: int = 0
    wins: int = 0
    losses: int = 0

    model_config = {"from_attributes": True}


class TestTeamModels(TestCase):
    """
    Test suite for team Pydantic models.
    """

    def test_team_create_valid(self):
        """
        Test TeamCreate with valid data.
        """
        data = {"player1_id": 1, "player2_id": 2, "global_elo": 1200.0, "current_month_elo": 1100.0}
        team = TeamCreate(**data)
        self.assertEqual(team.player1_id, 1)
        self.assertEqual(team.player2_id, 2)
        self.assertEqual(team.global_elo, 1200.0)
        self.assertEqual(team.current_month_elo, 1100.0)

    def test_team_create_default_elo(self):
        """
        Test TeamCreate with default ELO values.
        """
        team = TeamCreate(player1_id=3, player2_id=4)
        self.assertEqual(team.player1_id, 3)
        self.assertEqual(team.player2_id, 4)
        self.assertEqual(team.global_elo, 1000.0)
        self.assertEqual(team.current_month_elo, 1000.0)

    def test_team_create_player_ids_swapped(self):
        """
        Test TeamCreate validator swaps player IDs to enforce player1_id < player2_id.
        """
        team = TeamCreate(player1_id=5, player2_id=1)
        self.assertEqual(team.player1_id, 1, "Player1_id should be swapped to the lower ID")
        self.assertEqual(team.player2_id, 5, "Player2_id should be swapped to the higher ID")

    def test_team_create_invalid_same_players(self):
        """
        Test TeamCreate with player1_id and player2_id being the same.
        """
        with self.assertRaises(ValidationError) as context:
            TeamCreate(player1_id=1, player2_id=1)
        errors = context.exception.errors()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["type"], "value_error")
        self.assertIn("player1_id and player2_id cannot be the same", str(errors[0]["msg"]))

    def test_team_create_invalid_player_id_zero(self):
        """
        Test TeamCreate with player ID being zero.
        """
        with self.assertRaises(ValidationError):
            TeamCreate(player1_id=0, player2_id=1)
        with self.assertRaises(ValidationError):
            TeamCreate(player1_id=1, player2_id=0)

    def test_team_update_valid(self):
        """
        Test TeamUpdate (currently a placeholder, should instantiate).
        """
        team_update = TeamUpdate()
        self.assertIsInstance(team_update, TeamUpdate)

    def test_team_response_valid_no_players(self):
        """
        Test TeamResponse with valid data, without nested player objects.
        """
        now = datetime.now(timezone.utc)
        data = {
            "team_id": 1,
            "player1_id": 1,
            "player2_id": 2,
            "global_elo": 1500.0,
            "current_month_elo": 1400.0,
            "created_at": now,
            "last_match_at": now,
        }
        team_response = TeamResponse(**data)
        self.assertEqual(team_response.team_id, 1)
        self.assertEqual(team_response.player1_id, 1)
        self.assertEqual(team_response.player2_id, 2)
        self.assertEqual(team_response.global_elo, 1500.0)
        self.assertEqual(team_response.current_month_elo, 1400.0)
        self.assertEqual(team_response.created_at, now)
        self.assertEqual(team_response.last_match_at, now)
        self.assertIsNone(team_response.player1)
        self.assertIsNone(team_response.player2)

    def test_team_response_valid_with_players(self):
        """
        Test TeamResponse with valid data, including nested player objects.
        """
        now = datetime.now(timezone.utc)
        player1_data = MockPlayerForTeam(
            id=1, name="Player One", global_elo=1200, current_month_elo=1150, creation_date=now
        )
        player2_data = MockPlayerForTeam(
            id=2, name="Player Two", global_elo=1300, current_month_elo=1250, creation_date=now
        )

        data = {
            "team_id": 2,
            "player1_id": 1,
            "player2_id": 2,
            "global_elo": 1250.0,
            "current_month_elo": 1200.0,
            "created_at": now,
            "last_match_at": None,
            "player1": player1_data,
            "player2": player2_data,
        }
        team_response = TeamResponse(**data)
        self.assertEqual(team_response.team_id, 2)
        self.assertEqual(team_response.player1_id, 1)
        self.assertEqual(team_response.player2_id, 2)
        self.assertIsNotNone(team_response.player1)
        self.assertEqual(team_response.player1.name, "Player One")
        self.assertIsNotNone(team_response.player2)
        self.assertEqual(team_response.player2.name, "Player Two")

    def test_team_response_from_attributes(self):
        """
        Test TeamResponse creation using from_attributes (model_config).
        Simulates creating a response model from a DB ORM-like object.
        """

        class MockTeamDB:
            def __init__(
                self,
                team_id,
                player1_id,
                player2_id,
                global_elo,
                current_month_elo,
                created_at,
                last_match_at: Optional[datetime] = None,
            ):
                self.team_id = team_id
                self.player1_id = player1_id
                self.player2_id = player2_id
                self.global_elo = global_elo
                self.current_month_elo = current_month_elo
                self.created_at = created_at
                self.last_match_at = last_match_at
                # For testing nested from_attributes, if services populate these
                # self.player1 = None # or MockPlayerForTeam instance
                # self.player2 = None # or MockPlayerForTeam instance

        now = datetime.now(timezone.utc)
        mock_db_team = MockTeamDB(
            team_id=3,
            player1_id=10,
            player2_id=20,
            global_elo=1600.0,
            current_month_elo=1550.0,
            created_at=now,
            last_match_at=now,
        )

        team_response = TeamResponse.model_validate(mock_db_team)

        self.assertEqual(team_response.team_id, 3)
        self.assertEqual(team_response.player1_id, 10)
        self.assertEqual(team_response.player2_id, 20)
        self.assertEqual(team_response.global_elo, 1600.0)
        self.assertEqual(team_response.current_month_elo, 1550.0)
        self.assertEqual(team_response.created_at, now)
        self.assertEqual(team_response.last_match_at, now)
        self.assertIsNone(team_response.player1)
        self.assertIsNone(team_response.player2)


if __name__ == "__main__":
    main()
