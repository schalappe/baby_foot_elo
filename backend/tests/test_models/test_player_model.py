# -*- coding: utf-8 -*-
"""
Unit tests for player Pydantic models.
"""

from datetime import datetime, timezone
from unittest import TestCase, main

from pydantic import ValidationError

from app.models.player import PlayerCreate, PlayerResponse, PlayerUpdate


class TestPlayerModels(TestCase):
    """
    Test suite for player Pydantic models.
    """

    def test_player_create_valid(self):
        """
        Test PlayerCreate with valid data.
        """
        data = {"name": "Valid Player", "global_elo": 1200}
        player = PlayerCreate(**data)
        self.assertEqual(player.name, "Valid Player")
        self.assertEqual(player.global_elo, 1200)

    def test_player_create_default_elo(self):
        """
        Test PlayerCreate with default ELO values.
        """
        player = PlayerCreate(name="Default Elo Player")
        self.assertEqual(player.name, "Default Elo Player")
        self.assertEqual(player.global_elo, 1000)

    def test_player_create_invalid_name_short(self):
        """
        Test PlayerCreate with a name that is too short.
        """
        with self.assertRaises(ValidationError) as context:
            PlayerCreate(name="", global_elo=1000)

        errors = context.exception.errors()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["type"], "string_too_short")
        self.assertEqual(errors[0]["loc"], ("name",))
        self.assertIn("String should have at least 1 character", errors[0]["msg"])

    def test_player_create_invalid_name_long(self):
        """
        Test PlayerCreate with a name that is too long.
        """
        long_name = "a" * 101
        with self.assertRaises(ValidationError):
            PlayerCreate(name=long_name)

    def test_player_create_invalid_elo_negative(self):
        """
        Test PlayerCreate with a negative ELO value.
        """
        with self.assertRaises(ValidationError):
            PlayerCreate(name="Negative Elo", global_elo=-100)

    def test_player_update_valid(self):
        """
        Test PlayerUpdate with valid data.
        """
        data = {"name": "Updated Name"}
        player_update = PlayerUpdate(**data)
        self.assertEqual(player_update.name, "Updated Name")

    def test_player_update_empty(self):
        """
        Test PlayerUpdate with no data (all fields optional).
        """
        player_update = PlayerUpdate()
        self.assertIsNone(player_update.name)

    def test_player_update_invalid_name_long(self):
        """
        Test PlayerUpdate with a name that is too long.
        """
        long_name = "b" * 101
        with self.assertRaises(ValidationError):
            PlayerUpdate(name=long_name)

    def test_player_response_valid(self):
        """
        Test PlayerResponse with valid data.
        """
        now = datetime.now(timezone.utc)
        data = {
            "player_id": 1,
            "name": "Response Player",
            "global_elo": 1500,
            "creation_date": now,
            "matches_played": 10,
            "wins": 5,
            "losses": 5,
        }
        player_response = PlayerResponse(**data)
        self.assertEqual(player_response.player_id, 1)
        self.assertEqual(player_response.name, "Response Player")
        self.assertEqual(player_response.global_elo, 1500)
        self.assertEqual(player_response.creation_date, now)
        self.assertEqual(player_response.matches_played, 10)
        self.assertEqual(player_response.wins, 5)
        self.assertEqual(player_response.losses, 5)

    def test_player_response_from_attributes(self):
        """
        Test PlayerResponse creation using from_attributes (model_config).

        Simulates creating a response model from a DB ORM-like object.
        """

        class MockPlayerDB:
            def __init__(
                self,
                player_id,
                name,
                global_elo,
                creation_date,
                matches_played=0,
                wins=0,
                losses=0,
            ):
                self.player_id = player_id
                self.name = name
                self.global_elo = global_elo
                self.creation_date = creation_date
                self.matches_played = matches_played
                self.wins = wins
                self.losses = losses

        now = datetime.now(timezone.utc)
        mock_db_player = MockPlayerDB(
            player_id=2,
            name="Orm Player",
            global_elo=1600,
            creation_date=now,
            matches_played=20,
            wins=15,
            losses=5,
        )

        player_response = PlayerResponse.model_validate(mock_db_player)

        self.assertEqual(player_response.player_id, 2)
        self.assertEqual(player_response.name, "Orm Player")
        self.assertEqual(player_response.global_elo, 1600)
        self.assertEqual(player_response.creation_date, now)
        self.assertEqual(player_response.matches_played, 20)
        self.assertEqual(player_response.wins, 15)
        self.assertEqual(player_response.losses, 5)

    def test_player_response_invalid_id(self):
        """
        Test PlayerResponse with an invalid ID (e.g., 0 or negative).
        """
        now = datetime.now(timezone.utc)
        with self.assertRaises(ValidationError):
            PlayerResponse(
                player_id=0,
                name="Invalid ID Player",
                global_elo=1000,
                creation_date=now,
            )

    def test_player_response_invalid_elo(self):
        """
        Test PlayerResponse with a negative ELO.
        """
        now = datetime.now(timezone.utc)
        with self.assertRaises(ValidationError):
            PlayerResponse(
                player_id=1,
                name="Invalid Elo Player",
                global_elo=-100,
                creation_date=now,
            )


if __name__ == "__main__":
    main()
