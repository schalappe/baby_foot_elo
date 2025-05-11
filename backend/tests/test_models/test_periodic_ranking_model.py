# -*- coding: utf-8 -*-
"""
Unit tests for periodic ranking Pydantic models.
"""

from datetime import datetime, timezone
from unittest import TestCase, main

from pydantic import BaseModel, Field, ValidationError

from app.models.periodic_ranking import (
    PeriodicRankingCreate,
    PeriodicRankingResponse,
    PeriodicRankingUpdate,
)


class MockPlayerForRanking(BaseModel):
    id: int
    name: str
    global_elo: int
    current_month_elo: int
    creation_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    matches_played: int = 0
    wins: int = 0
    losses: int = 0

    model_config = {"from_attributes": True}


class TestPeriodicRankingModels(TestCase):
    """
    Test suite for periodic ranking Pydantic models.
    """

    def test_periodic_ranking_create_valid(self):
        """
        Test PeriodicRankingCreate with valid data.
        """
        data = {
            "player_id": 1,
            "year": 2023,
            "month": 10,
            "day": 31,
            "initial_elo": 1000,
            "final_elo": 1050,
            "ranking": 5,
            "matches_played": 10,
            "wins": 6,
            "losses": 4,
        }
        ranking_create = PeriodicRankingCreate(**data)
        self.assertEqual(ranking_create.player_id, 1)
        self.assertEqual(ranking_create.year, 2023)
        self.assertEqual(ranking_create.final_elo, 1050)
        self.assertEqual(ranking_create.ranking, 5)
        self.assertEqual(ranking_create.losses, 4)

    def test_periodic_ranking_create_invalid_ranking_zero(self):
        """
        Test PeriodicRankingCreate with ranking as zero (should be > 0).
        """
        data = {
            "player_id": 1,
            "year": 2023,
            "month": 10,
            "day": 31,
            "initial_elo": 1000,
            "final_elo": 1050,
            "ranking": 0,
            "matches_played": 10,
            "wins": 6,
            "losses": 4,
        }
        with self.assertRaises(ValidationError):
            PeriodicRankingCreate(**data)

    def test_periodic_ranking_create_invalid_negative_stats(self):
        """
        Test PeriodicRankingCreate with negative ELOs or match stats.
        """
        base_data = {
            "player_id": 1,
            "year": 2023,
            "month": 10,
            "day": 31,
            "ranking": 1,
            "matches_played": 10,
            "wins": 6,
            "losses": 4,
        }
        with self.assertRaises(ValidationError):
            PeriodicRankingCreate(**{**base_data, "initial_elo": -100, "final_elo": 1000})
        with self.assertRaises(ValidationError):
            PeriodicRankingCreate(**{**base_data, "initial_elo": 1000, "final_elo": -100})
        with self.assertRaises(ValidationError):
            PeriodicRankingCreate(**{**base_data, "initial_elo": 1000, "final_elo": 1000, "matches_played": -1})
        with self.assertRaises(ValidationError):
            PeriodicRankingCreate(**{**base_data, "initial_elo": 1000, "final_elo": 1000, "wins": -1})
        with self.assertRaises(ValidationError):
            PeriodicRankingCreate(**{**base_data, "initial_elo": 1000, "final_elo": 1000, "losses": -1})

    def test_periodic_ranking_update_valid(self):
        """
        Test PeriodicRankingUpdate (currently a placeholder).
        """
        ranking_update = PeriodicRankingUpdate()
        self.assertIsInstance(ranking_update, PeriodicRankingUpdate)

    def test_periodic_ranking_response_valid_no_player(self):
        """
        Test PeriodicRankingResponse without nested player object.
        """
        data = {
            "ranking_id": 100,
            "player_id": 2,
            "year": 2023,
            "month": 11,
            "day": 30,
            "initial_elo": 1100,
            "final_elo": 1120,
            "ranking": 3,
            "matches_played": 5,
            "wins": 3,
            "losses": 2,
        }
        response = PeriodicRankingResponse(**data)
        self.assertEqual(response.ranking_id, 100)
        self.assertEqual(response.player_id, 2)
        self.assertEqual(response.ranking, 3)
        self.assertIsNone(response.player)

    def test_periodic_ranking_response_valid_with_player(self):
        """
        Test PeriodicRankingResponse with a nested player object.
        """
        player_data = MockPlayerForRanking(id=3, name="Ranked Player", global_elo=1200, current_month_elo=1200)
        data = {
            "ranking_id": 101,
            "player_id": 3,
            "year": 2023,
            "month": 12,
            "day": 31,
            "initial_elo": 1150,
            "final_elo": 1200,
            "ranking": 1,
            "matches_played": 8,
            "wins": 7,
            "losses": 1,
            "player": player_data,
        }
        response = PeriodicRankingResponse(**data)
        self.assertEqual(response.ranking_id, 101)
        self.assertIsNotNone(response.player)
        self.assertEqual(response.player.id, 3)
        self.assertEqual(response.player.name, "Ranked Player")

    def test_periodic_ranking_response_from_attributes(self):
        """
        Test PeriodicRankingResponse creation using from_attributes.
        """

        class MockPeriodicRankingDB:
            def __init__(
                self,
                ranking_id,
                player_id,
                year,
                month,
                day,
                initial_elo,
                final_elo,
                ranking,
                matches_played,
                wins,
                losses,
            ):
                self.ranking_id = ranking_id
                self.player_id = player_id
                self.year = year
                self.month = month
                self.day = day
                self.initial_elo = initial_elo
                self.final_elo = final_elo
                self.ranking = ranking
                self.matches_played = matches_played
                self.wins = wins
                self.losses = losses

        mock_db_entry = MockPeriodicRankingDB(
            ranking_id=200,
            player_id=4,
            year=2024,
            month=1,
            day=31,
            initial_elo=1300,
            final_elo=1350,
            ranking=2,
            matches_played=12,
            wins=8,
            losses=4,
        )
        response = PeriodicRankingResponse.model_validate(mock_db_entry)
        self.assertEqual(response.ranking_id, 200)
        self.assertEqual(response.player_id, 4)
        self.assertEqual(response.final_elo, 1350)
        self.assertEqual(response.losses, 4)
        self.assertIsNone(response.player)


if __name__ == "__main__":
    main()
