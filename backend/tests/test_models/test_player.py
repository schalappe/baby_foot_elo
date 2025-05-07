# -*- coding: utf-8 -*-
"""
Test models for the Baby Foot Elo backend.
"""

from datetime import datetime, timezone
from unittest import TestCase, main

from pydantic import ValidationError

from app.models.player import PlayerCreate, PlayerResponse, PlayerUpdate


class TestPlayerModels(TestCase):
    """Test models for the Baby Foot Elo backend."""

    def test_player_create_defaults(self):
        """Test player creation with default values."""
        player = PlayerCreate(name="Alice")
        self.assertEqual(player.name, "Alice")
        self.assertEqual(player.initial_elo, 1000)

    def test_player_create_custom_elo(self):
        """Test player creation with custom initial ELO."""
        player = PlayerCreate(name="Bob", initial_elo=1200)
        self.assertEqual(player.name, "Bob")
        self.assertEqual(player.initial_elo, 1200)

    def test_player_create_missing_name(self):
        """Test player creation with missing name."""
        with self.assertRaises(ValidationError):
            PlayerCreate()

    def test_player_update_partial(self):
        """Test partial player update."""
        update = PlayerUpdate(name="Charlie")
        self.assertEqual(update.name, "Charlie")
        self.assertIsNone(update.initial_elo)

        update = PlayerUpdate(initial_elo=1300)
        self.assertIsNone(update.name)
        self.assertEqual(update.initial_elo, 1300)

    def test_player_update_empty(self):
        """Test empty player update."""
        update = PlayerUpdate()
        self.assertIsNone(update.name)
        self.assertIsNone(update.initial_elo)

    def test_player_response_fields(self):
        """Test player response fields."""
        now = datetime.now(timezone.utc)
        response = PlayerResponse(
            id=1,
            name="Diana",
            elo=1500,
            creation_date=now,
            matches_played=10,
            wins=7,
            losses=3,
        )
        self.assertEqual(response.id, 1)
        self.assertEqual(response.name, "Diana")
        self.assertEqual(response.elo, 1500)
        self.assertEqual(response.creation_date, now)
        self.assertEqual(response.matches_played, 10)
        self.assertEqual(response.wins, 7)
        self.assertEqual(response.losses, 3)

    def test_player_response_defaults(self):
        """Test player response defaults."""
        now = datetime.now(timezone.utc)
        response = PlayerResponse(id=2, name="Eve", elo=1100, creation_date=now)
        self.assertEqual(response.matches_played, 0)
        self.assertEqual(response.wins, 0)
        self.assertEqual(response.losses, 0)


if __name__ == "__main__":
    main()
