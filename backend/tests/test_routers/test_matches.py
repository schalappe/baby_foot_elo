# -*- coding: utf-8 -*-
"""
Unit tests for the matches router.
"""

import unittest
from datetime import datetime
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.models.match import MatchCreate, MatchResponse, MatchWithEloResponse


class TestMatchesRouter(unittest.TestCase):
    """
    Test cases for the matches router.
    """

    def setUp(self):
        """
        Set up test client and mocks before each test.
        """
        self.client = TestClient(app)

    @patch("app.routers.matches.get_team")
    @patch("app.routers.matches.get_player")
    @patch("app.routers.matches.create_match")
    @patch("app.routers.matches.batch_record_elo_updates")
    @patch("app.routers.matches.process_match_result")
    @patch("app.routers.matches.calculate_team_elo")
    @patch("app.routers.matches.update_player")
    @patch("app.routers.matches.update_team")
    @patch("app.routers.matches.get_match")
    async def test_record_match_success(
        self,
        mock_get_match,
        mock_update_team,
        mock_update_player,
        mock_calculate_team_elo,
        mock_process_match_result,
        mock_batch_record_elo_updates,
        mock_create_match,
        mock_get_player,
        mock_get_team,
    ):
        """
        Test successful match recording with ELO updates.
        """
        # Mock team data
        mock_get_team.side_effect = [
            {  # Winner team
                "team_id": 1,
                "player1_id": 1,
                "player2_id": 2,
                "global_elo": 1200,
                "created_at": "2025-01-01T12:00:00",
                "last_match_at": "2025-01-01T12:00:00",
            },
            {  # Loser team
                "team_id": 2,
                "player1_id": 3,
                "player2_id": 4,
                "global_elo": 1100,
                "created_at": "2025-01-01T12:00:00",
                "last_match_at": "2025-01-01T12:00:00",
            },
        ]

        # Mock player data
        mock_get_player.side_effect = [
            {  # Winner player 1
                "player_id": 1,
                "name": "Player 1",
                "global_elo": 1250,
                "created_at": "2025-01-01T12:00:00",
            },
            {  # Winner player 2
                "player_id": 2,
                "name": "Player 2",
                "global_elo": 1150,
                "created_at": "2025-01-01T12:00:00",
            },
            {  # Loser player 1
                "player_id": 3,
                "name": "Player 3",
                "global_elo": 1050,
                "created_at": "2025-01-01T12:00:00",
            },
            {  # Loser player 2
                "player_id": 4,
                "name": "Player 4",
                "global_elo": 1150,
                "created_at": "2025-01-01T12:00:00",
            },
        ]

        # Mock match creation
        mock_create_match.return_value = 1

        # Mock match data
        mock_get_match.return_value = {
            "match_id": 1,
            "winner_team_id": 1,
            "loser_team_id": 2,
            "is_fanny": False,
            "played_at": datetime.now(),
            "year": 2025,
            "month": 5,
            "day": 11,
        }

        # Mock ELO calculation
        mock_process_match_result.return_value = {
            1: {"old_elo": 1250, "new_elo": 1265, "change": 15},
            2: {"old_elo": 1150, "new_elo": 1165, "change": 15},
            3: {"old_elo": 1050, "new_elo": 1035, "change": -15},
            4: {"old_elo": 1150, "new_elo": 1135, "change": -15},
        }

        # Mock team ELO calculation
        mock_calculate_team_elo.side_effect = [1215, 1085]

        # Test API endpoint
        response = await self.client.post(
            "/api/v1/matches",
            json={
                "winner_team_id": 1,
                "loser_team_id": 2,
                "is_fanny": False,
            },
        )

        # Verify response
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["match_id"], 1)
        self.assertEqual(data["winner_team_id"], 1)
        self.assertEqual(data["loser_team_id"], 2)
        self.assertEqual(data["is_fanny"], False)
        self.assertIn("elo_changes", data)
        self.assertEqual(len(data["elo_changes"]), 4)

        # Verify that all required functions were called
        mock_get_team.assert_any_call(1)
        mock_get_team.assert_any_call(2)
        mock_get_player.assert_any_call(1)
        mock_get_player.assert_any_call(2)
        mock_get_player.assert_any_call(3)
        mock_get_player.assert_any_call(4)
        mock_create_match.assert_called_once()
        mock_process_match_result.assert_called_once()
        mock_batch_record_elo_updates.assert_called_once()
        mock_update_team.assert_any_call(
            1, global_elo=1215, last_match_at=mock_get_match.return_value["played_at"].isoformat()
        )
        mock_update_team.assert_any_call(
            2, global_elo=1085, last_match_at=mock_get_match.return_value["played_at"].isoformat()
        )

    @patch("app.routers.matches.get_team")
    def test_record_match_team_not_found(self, mock_get_team):
        """
        Test match recording with non-existent team.
        """
        # Mock team not found
        mock_get_team.return_value = None

        # Test API endpoint
        response = self.client.post(
            "/api/v1/matches/",
            json={
                "winner_team_id": 999,
                "loser_team_id": 2,
                "is_fanny": False,
                "played_at": datetime.now().isoformat(),
            },
        )

        # Verify response
        self.assertEqual(response.status_code, 404)
        self.assertIn("not found", response.json()["detail"])

    @patch("app.routers.matches.get_team")
    async def test_record_match_same_teams(self, mock_get_team):
        """
        Test match recording with same winner and loser team.
        """
        # Mock team data
        mock_get_team.return_value = {
            "team_id": 1,
            "player1_id": 1,
            "player2_id": 2,
            "global_elo": 1200,
            "created_at": "2025-01-01T12:00:00",
            "last_match_at": "2025-01-01T12:00:00",
        }

        # Test API endpoint
        response = await self.client.post(
            "/api/v1/matches/",
            json={
                "winner_team_id": 1,
                "loser_team_id": 1,
                "is_fanny": False,
                "played_at": datetime.now().isoformat(),
            },
        )

        # Verify response
        self.assertEqual(response.status_code, 400)
        self.assertIn("cannot be the same", response.json()["detail"])

    @patch("app.routers.matches.get_match")
    @patch("app.routers.matches.get_team")
    @patch("app.routers.matches.get_elo_history_by_match")
    def test_get_match_details(self, mock_get_elo_history, mock_get_team, mock_get_match):
        """
        Test retrieving match details.
        """
        # Mock match data
        mock_get_match.return_value = {
            "match_id": 1,
            "winner_team_id": 1,
            "loser_team_id": 2,
            "is_fanny": False,
            "played_at": datetime.now(),
            "year": 2025,
            "month": 5,
            "day": 11,
        }

        # Mock empty ELO history
        mock_get_elo_history.return_value = []

        # Mock team data
        mock_get_team.return_value = None

        # Mock match not found
        mock_get_match.side_effect = [
            {
                "match_id": 1,
                "winner_team_id": 1,
                "loser_team_id": 2,
                "is_fanny": False,
                "played_at": datetime.now(),
                "year": 2025,
                "month": 5,
                "day": 11,
            },
            None,
        ]

        # Test API endpoint - success case
        response = self.client.get("/api/v1/matches/1")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["match_id"], 1)

        # Test API endpoint - not found case
        response = self.client.get("/api/v1/matches/999")
        self.assertEqual(response.status_code, 404)

    @patch("app.routers.matches.get_all_matches")
    @patch("app.routers.matches.get_matches_by_team")
    @patch("app.routers.matches.get_matches_by_date_range")
    @patch("app.routers.matches.get_fanny_matches")
    def test_list_matches(
        self, mock_get_fanny_matches, mock_get_matches_by_date_range, mock_get_matches_by_team, mock_get_all_matches
    ):
        """
        Test listing matches with pagination and filtering.
        """
        # Mock matches data
        mock_get_all_matches.return_value = [
            {
                "match_id": 1,
                "winner_team_id": 1,
                "loser_team_id": 2,
                "is_fanny": False,
                "played_at": datetime.now(),
                "year": 2025,
                "month": 5,
                "day": 11,
            },
            {
                "match_id": 2,
                "winner_team_id": 3,
                "loser_team_id": 4,
                "is_fanny": True,
                "played_at": datetime.now(),
                "year": 2025,
                "month": 5,
                "day": 10,
            },
        ]

        # Test API endpoint
        response = self.client.get("/api/v1/matches?skip=0&limit=10")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["match_id"], 1)
        self.assertEqual(data[1]["match_id"], 2)

        # Test with team filter
        mock_get_matches_by_team.return_value = [
            {
                "match_id": 1,
                "winner_team_id": 1,
                "loser_team_id": 2,
                "is_fanny": False,
                "played_at": datetime.now(),
                "year": 2025,
                "month": 5,
                "day": 11,
                "won": True,
            }
        ]
        response = self.client.get("/api/v1/matches?team_id=1")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["match_id"], 1)

    @patch("app.routers.matches.get_all_matches")
    async def test_export_matches(self, mock_get_all_matches):
        """
        Test exporting all matches.
        """
        # Mock matches data
        mock_get_all_matches.return_value = [
            {
                "match_id": 1,
                "winner_team_id": 1,
                "loser_team_id": 2,
                "is_fanny": False,
                "played_at": datetime.now(),
                "year": 2025,
                "month": 5,
                "day": 11,
            },
            {
                "match_id": 2,
                "winner_team_id": 3,
                "loser_team_id": 4,
                "is_fanny": True,
                "played_at": datetime.now(),
                "year": 2025,
                "month": 5,
                "day": 10,
            },
        ]

        # Test API endpoint
        response = await self.client.get("/api/v1/matches/export")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["match_id"], 1)
        self.assertEqual(data[1]["match_id"], 2)


if __name__ == "__main__":
    unittest.main()
