# -*- coding: utf-8 -*-
"""
Unit tests for team periodic ranking Pydantic models.
"""

from datetime import datetime, timezone
from typing import Optional
from unittest import TestCase, main

from pydantic import BaseModel, Field, ValidationError

from app.models.team_periodic_ranking import (
    TeamPeriodicRankingCreate,
    TeamPeriodicRankingResponse,
    TeamPeriodicRankingUpdate,
)


class MockTeamForRanking(BaseModel):
    team_id: int
    player1_id: int
    player2_id: int
    global_elo: float = 1000.0
    current_month_elo: float = 1000.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_match_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TestTeamPeriodicRankingModels(TestCase):
    """
    Test suite for team periodic ranking Pydantic models.
    """

    def test_team_periodic_ranking_create_valid(self):
        """
        Test TeamPeriodicRankingCreate with valid data.
        """
        data = {
            "team_id": 1,
            "year": 2023,
            "month": 10,
            "day": 31,
            "initial_elo": 1000.5,
            "final_elo": 1050.75,
            "ranking": 5,
            "matches_played": 10,
            "wins": 6,
            "losses": 4,
        }
        ranking_create = TeamPeriodicRankingCreate(**data)
        self.assertEqual(ranking_create.team_id, 1)
        self.assertEqual(ranking_create.year, 2023)
        self.assertAlmostEqual(ranking_create.final_elo, 1050.75)
        self.assertEqual(ranking_create.ranking, 5)
        self.assertEqual(ranking_create.losses, 4)

    def test_team_periodic_ranking_create_invalid_ranking_zero(self):
        """
        Test TeamPeriodicRankingCreate with ranking as zero.
        """
        data = {
            "team_id": 1,
            "year": 2023,
            "month": 10,
            "day": 31,
            "initial_elo": 1000.0,
            "final_elo": 1050.0,
            "ranking": 0,
            "matches_played": 10,
            "wins": 6,
            "losses": 4,
        }
        with self.assertRaises(ValidationError):
            TeamPeriodicRankingCreate(**data)

    def test_team_periodic_ranking_create_invalid_negative_stats(self):
        """
        Test TeamPeriodicRankingCreate with negative ELOs or match stats.
        """
        base_data = {
            "team_id": 1,
            "year": 2023,
            "month": 10,
            "day": 31,
            "ranking": 1,
            "matches_played": 10,
            "wins": 6,
            "losses": 4,
        }
        with self.assertRaises(ValidationError):
            TeamPeriodicRankingCreate(**{**base_data, "initial_elo": -100.0, "final_elo": 1000.0})
        with self.assertRaises(ValidationError):
            TeamPeriodicRankingCreate(**{**base_data, "initial_elo": 1000.0, "final_elo": -100.0})
        with self.assertRaises(ValidationError):
            TeamPeriodicRankingCreate(
                **{**base_data, "initial_elo": 1000.0, "final_elo": 1000.0, "matches_played": -1}
            )
        with self.assertRaises(ValidationError):
            TeamPeriodicRankingCreate(**{**base_data, "initial_elo": 1000.0, "final_elo": 1000.0, "wins": -1})
        with self.assertRaises(ValidationError):
            TeamPeriodicRankingCreate(**{**base_data, "initial_elo": 1000.0, "final_elo": 1000.0, "losses": -1})

    def test_team_periodic_ranking_update_valid(self):
        """
        Test TeamPeriodicRankingUpdate (currently a placeholder).
        """
        ranking_update = TeamPeriodicRankingUpdate()
        self.assertIsInstance(ranking_update, TeamPeriodicRankingUpdate)

    def test_team_periodic_ranking_response_valid_no_team(self):
        """
        Test TeamPeriodicRankingResponse without nested team object.
        """
        data = {
            "team_ranking_id": 100,
            "team_id": 2,
            "year": 2023,
            "month": 11,
            "day": 30,
            "initial_elo": 1100.25,
            "final_elo": 1120.5,
            "ranking": 3,
            "matches_played": 5,
            "wins": 3,
            "losses": 2,
        }
        response = TeamPeriodicRankingResponse(**data)
        self.assertEqual(response.team_ranking_id, 100)
        self.assertEqual(response.team_id, 2)
        self.assertAlmostEqual(response.initial_elo, 1100.25)
        self.assertIsNone(response.team)

    def test_team_periodic_ranking_response_valid_with_team(self):
        """
        Test TeamPeriodicRankingResponse with a nested team object.
        """
        team_data = MockTeamForRanking(team_id=3, player1_id=5, player2_id=6, global_elo=1200.0)

        data = {
            "team_ranking_id": 101,
            "team_id": 3,
            "year": 2023,
            "month": 12,
            "day": 31,
            "initial_elo": 1150.0,
            "final_elo": 1200.0,
            "ranking": 1,
            "matches_played": 8,
            "wins": 7,
            "losses": 1,
            "team": team_data,
        }
        response = TeamPeriodicRankingResponse(**data)
        self.assertEqual(response.team_ranking_id, 101)
        self.assertIsNotNone(response.team)
        self.assertEqual(response.team.team_id, 3)
        self.assertAlmostEqual(response.team.global_elo, 1200.0)

    def test_team_periodic_ranking_response_from_attributes(self):
        """
        Test TeamPeriodicRankingResponse creation using from_attributes.
        """

        class MockTeamPeriodicRankingDB:
            def __init__(
                self,
                team_ranking_id,
                team_id,
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
                self.team_ranking_id = team_ranking_id
                self.team_id = team_id
                self.year = year
                self.month = month
                self.day = day
                self.initial_elo = initial_elo
                self.final_elo = final_elo
                self.ranking = ranking
                self.matches_played = matches_played
                self.wins = wins
                self.losses = losses

        mock_db_entry = MockTeamPeriodicRankingDB(
            team_ranking_id=200,
            team_id=4,
            year=2024,
            month=1,
            day=31,
            initial_elo=1300.5,
            final_elo=1350.25,
            ranking=2,
            matches_played=12,
            wins=8,
            losses=4,
        )
        response = TeamPeriodicRankingResponse.model_validate(mock_db_entry)
        self.assertEqual(response.team_ranking_id, 200)
        self.assertEqual(response.team_id, 4)
        self.assertAlmostEqual(response.final_elo, 1350.25)
        self.assertEqual(response.losses, 4)
        self.assertIsNone(response.team)


if __name__ == "__main__":
    main()
