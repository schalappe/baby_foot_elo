# -*- coding: utf-8 -*-
"""
Unit tests for the teams router.
"""

from unittest import TestCase, main
from unittest.mock import patch

from fastapi import status
from fastapi.testclient import TestClient
from loguru import logger

from app.main import app


class TestTeamsRouter(TestCase):
    """
    Test cases for the teams router endpoints.
    """

    def setUp(self):
        """
        Set up test client and mocks.
        """
        self.client = TestClient(app)
        self.test_team_data = {
            "player1_id": 1,
            "player2_id": 2,
            "global_elo": 1200.0,
            "current_month_elo": 1200.0,
        }
        self.test_team_response = {
            "team_id": 1,
            "player1_id": 1,
            "player2_id": 2,
            "global_elo": 1200.0,
            "current_month_elo": 1200.0,
            "created_at": "2025-01-01T00:00:00",
            "last_match_at": None,
            "player1": {
                "player_id": 1,
                "name": "Test Player 1",
                "global_elo": 1200,
                "current_month_elo": 1200,
                "matches_played": 0,
                "wins": 0,
                "losses": 0,
                "creation_date": "2025-01-01T00:00:00",
            },
            "player2": {
                "player_id": 2,
                "name": "Test Player 2",
                "global_elo": 1200,
                "current_month_elo": 1200,
                "matches_played": 0,
                "wins": 0,
                "losses": 0,
                "creation_date": "2025-01-01T00:00:00",
            },
        }

    @patch("app.routers.teams.create_team")
    @patch("app.routers.teams.get_player")
    @patch("app.routers.teams.get_team")
    def test_create_team_success(self, mock_get_team, mock_get_player, mock_create_team):
        """
        Test successful team creation.
        """
        # ##: Mock player retrieval.
        mock_get_player.side_effect = [
            {
                "player_id": 1,
                "name": "Test Player 1",
                "global_elo": 1200,
                "current_month_elo": 1200,
                "matches_played": 0,
                "wins": 0,
                "losses": 0,
                "creation_date": "2025-01-01T00:00:00",
            },
            {
                "player_id": 2,
                "name": "Test Player 2",
                "global_elo": 1200,
                "current_month_elo": 1200,
                "matches_played": 0,
                "wins": 0,
                "losses": 0,
                "creation_date": "2025-01-01T00:00:00",
            },
        ]

        # ##: Mock team creation and retrieval.
        mock_create_team.return_value = 1
        mock_get_team.return_value = {
            "team_id": 1,
            "player1_id": 1,
            "player2_id": 2,
            "global_elo": 1200.0,
            "current_month_elo": 1200.0,
            "created_at": "2025-01-01T00:00:00",
            "last_match_at": None,
        }

        # ##: Make request.
        response = self.client.post("/api/v1/teams", json=self.test_team_data)

        # ##: Verify response.
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["team_id"], 1)
        self.assertEqual(response.json()["player1_id"], 1)
        self.assertEqual(response.json()["player2_id"], 2)

        # ##: Verify mocks were called correctly.
        mock_get_player.assert_any_call(1)
        mock_get_player.assert_any_call(2)
        mock_create_team.assert_called_once_with(
            player1_id=1,
            player2_id=2,
            global_elo=1200.0,
            current_month_elo=1200.0,
        )
        mock_get_team.assert_called_once_with(1)

    @patch("app.routers.teams.get_player")
    def test_create_team_player_not_found(self, mock_get_player):
        """
        Test team creation with non-existent player.
        """
        # ##: Mock player retrieval to return None for player1.
        mock_get_player.return_value = None

        # ##: Make request.
        response = self.client.post("/api/v1/teams", json=self.test_team_data)

        # ##: Verify response.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("not found", response.json()["detail"])

        # ##: Verify mock was called correctly.
        mock_get_player.assert_called_once_with(1)

    @patch("app.routers.teams.create_team")
    @patch("app.routers.teams.get_player")
    def test_create_team_duplicate(self, mock_get_player, mock_create_team):
        """
        Test team creation with duplicate players.
        """
        # ##: Mock player retrieval.
        mock_get_player.side_effect = [
            {
                "player_id": 1,
                "name": "Test Player 1",
                "global_elo": 1200,
                "current_month_elo": 1200,
                "matches_played": 0,
                "wins": 0,
                "losses": 0,
                "creation_date": "2025-01-01T00:00:00",
            },
            {
                "player_id": 2,
                "name": "Test Player 2",
                "global_elo": 1200,
                "current_month_elo": 1200,
                "matches_played": 0,
                "wins": 0,
                "losses": 0,
                "creation_date": "2025-01-01T00:00:00",
            },
        ]

        # ##: Mock team creation to return None (duplicate).
        mock_create_team.return_value = None

        # ##: Make request.
        response = self.client.post("/api/v1/teams", json=self.test_team_data)

        # ##: Verify response.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Failed to create team", response.json()["detail"])

        # ##: Verify mocks were called correctly.
        mock_get_player.assert_any_call(1)
        mock_get_player.assert_any_call(2)
        mock_create_team.assert_called_once()

    @patch("app.routers.teams.get_all_teams")
    @patch("app.routers.teams.get_player")
    def test_get_teams(self, mock_get_player, mock_get_all_teams):
        """
        Test getting all teams.
        """
        # ##: Mock team retrieval.
        mock_get_all_teams.return_value = [
            {
                "team_id": 1,
                "player1_id": 1,
                "player2_id": 2,
                "global_elo": 1200.0,
                "current_month_elo": 1200.0,
                "created_at": "2025-01-01T00:00:00",
                "last_match_at": None,
            }
        ]

        # ##: Mock player retrieval.
        mock_get_player.side_effect = [
            {
                "player_id": 1,
                "name": "Test Player 1",
                "global_elo": 1200,
                "current_month_elo": 1200,
                "matches_played": 0,
                "wins": 0,
                "losses": 0,
                "creation_date": "2025-01-01T00:00:00",
            },
            {
                "player_id": 2,
                "name": "Test Player 2",
                "global_elo": 1200,
                "current_month_elo": 1200,
                "matches_played": 0,
                "wins": 0,
                "losses": 0,
                "creation_date": "2025-01-01T00:00:00",
            },
        ]

        # ##: Make request.
        response = self.client.get("/api/v1/teams")

        # ##: Verify response.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["team_id"], 1)

        # ##: Verify mocks were called correctly.
        mock_get_all_teams.assert_called_once()
        mock_get_player.assert_any_call(1)
        mock_get_player.assert_any_call(2)

    @patch("app.routers.teams.get_team")
    @patch("app.routers.teams.get_player")
    def test_get_team_by_id(self, mock_get_player, mock_get_team):
        """
        Test getting a team by ID.
        """
        # ##: Mock team retrieval.
        mock_get_team.return_value = {
            "team_id": 1,
            "player1_id": 1,
            "player2_id": 2,
            "global_elo": 1200.0,
            "current_month_elo": 1200.0,
            "created_at": "2025-01-01T00:00:00",
            "last_match_at": None,
        }

        # ##: Mock player retrieval.
        mock_get_player.side_effect = [
            {
                "player_id": 1,
                "name": "Test Player 1",
                "global_elo": 1200,
                "current_month_elo": 1200,
                "matches_played": 0,
                "wins": 0,
                "losses": 0,
                "creation_date": "2025-01-01T00:00:00",
            },
            {
                "player_id": 2,
                "name": "Test Player 2",
                "global_elo": 1200,
                "current_month_elo": 1200,
                "matches_played": 0,
                "wins": 0,
                "losses": 0,
                "creation_date": "2025-01-01T00:00:00",
            },
        ]

        # ##: Make request.
        response = self.client.get("/api/v1/teams/1")

        # ##: Verify response.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["team_id"], 1)
        self.assertEqual(response.json()["player1"]["name"], "Test Player 1")
        self.assertEqual(response.json()["player2"]["name"], "Test Player 2")

        # ##: Verify mocks were called correctly.
        mock_get_team.assert_called_once_with(1)
        mock_get_player.assert_any_call(1)
        mock_get_player.assert_any_call(2)

    @patch("app.routers.teams.get_team")
    def test_get_team_not_found(self, mock_get_team):
        """
        Test getting a non-existent team.
        """
        # ##: Mock team retrieval to return None.
        mock_get_team.return_value = None

        # ##: Make request.
        response = self.client.get("/api/v1/teams/999")

        # ##: Verify response.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("not found", response.json()["detail"])

        # ##: Verify mock was called correctly.
        mock_get_team.assert_called_once_with(999)

    @patch("app.routers.teams.get_team")
    @patch("app.routers.teams.get_player")
    async def test_update_team(self, mock_get_player, mock_get_team):
        """
        Test updating a team.
        """
        logger.info("Updating team")
        # ##: Mock team retrieval.
        mock_get_team.return_value = {
            "team_id": 1,
            "player1_id": 1,
            "player2_id": 2,
            "global_elo": 1200.0,
            "current_month_elo": 1200.0,
            "created_at": "2025-01-01T00:00:00",
            "last_match_at": None,
        }

        # ##: Mock player retrieval.
        mock_get_player.side_effect = [
            {
                "player_id": 1,
                "name": "Test Player 1",
                "global_elo": 1200,
                "current_month_elo": 1200,
                "matches_played": 0,
                "wins": 0,
                "losses": 0,
                "creation_date": "2025-01-01T00:00:00",
            },
            {
                "player_id": 2,
                "name": "Test Player 2",
                "global_elo": 1200,
                "current_month_elo": 1200,
                "matches_played": 0,
                "wins": 0,
                "losses": 0,
                "creation_date": "2025-01-01T00:00:00",
            },
        ]

        # ##: Make request with empty update (since TeamUpdate is currently empty).
        response = await self.client.put("/api/v1/teams/1", json={})

        # ##: Verify response.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["team_id"], 1)

        # ##: Verify mocks were called correctly.
        mock_get_team.assert_called_once_with(1)
        mock_get_player.assert_any_call(1)
        mock_get_player.assert_any_call(2)

    @patch("app.routers.teams.get_team")
    async def test_update_team_not_found(self, mock_get_team):
        """
        Test updating a non-existent team.
        """
        # ##: Mock team retrieval to return None.
        mock_get_team.return_value = None

        # ##: Make request.
        response = await self.client.put("/api/v1/teams/999", json={})

        # ##: Verify response.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("not found", response.json()["detail"])

        # ##: Verify mock was called correctly.
        mock_get_team.assert_called_once_with(999)

    @patch("app.routers.teams.get_team")
    @patch("app.routers.teams.delete_team")
    def test_delete_team(self, mock_delete_team, mock_get_team):
        """
        Test deleting a team.
        """
        # ##: Mock team retrieval and deletion.
        mock_get_team.return_value = {
            "team_id": 1,
            "player1_id": 1,
            "player2_id": 2,
            "global_elo": 1200.0,
            "current_month_elo": 1200.0,
            "created_at": "2025-01-01T00:00:00",
            "last_match_at": None,
        }
        mock_delete_team.return_value = True

        # ##: Make request.
        response = self.client.delete("/api/v1/teams/1")

        # ##: Verify response.
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")

        # ##: Verify mocks were called correctly.
        mock_get_team.assert_called_once_with(1)
        mock_delete_team.assert_called_once_with(1)

    @patch("app.routers.teams.get_team")
    def test_delete_team_not_found(self, mock_get_team):
        """
        Test deleting a non-existent team.
        """
        # ##: Mock team retrieval to return None.
        mock_get_team.return_value = None

        # ##: Make request.
        response = self.client.delete("/api/v1/teams/999")

        # ##: Verify response.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("not found", response.json()["detail"])

        # ##: Verify mock was called correctly.
        mock_get_team.assert_called_once_with(999)

    @patch("app.routers.teams.get_team")
    @patch("app.routers.teams.delete_team")
    def test_delete_team_failure(self, mock_delete_team, mock_get_team):
        """
        Test failure when deleting a team.
        """
        # ##: Mock team retrieval and deletion failure.
        mock_get_team.return_value = {
            "team_id": 1,
            "player1_id": 1,
            "player2_id": 2,
            "global_elo": 1200.0,
            "current_month_elo": 1200.0,
            "created_at": "2025-01-01T00:00:00",
            "last_match_at": None,
        }
        mock_delete_team.return_value = False

        # ##: Make request.
        response = self.client.delete("/api/v1/teams/1")

        # ##: Verify response.
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("Failed to delete", response.json()["detail"])

        # ##: Verify mocks were called correctly.
        mock_get_team.assert_called_once_with(1)
        mock_delete_team.assert_called_once_with(1)


    @patch("app.routers.teams.get_team_rankings")
    @patch("app.routers.teams.get_player")
    async def test_get_team_rankings(self, mock_get_player, mock_get_team_rankings):
        """
        Test getting team rankings.
        """
        # Mock team rankings retrieval
        mock_get_team_rankings.return_value = [
            {
                "team_id": 1,
                "player1_id": 1,
                "player2_id": 2,
                "global_elo": 1500.0,
                "current_month_elo": 1450.0,
                "created_at": "2025-01-01T00:00:00",
                "last_match_at": "2025-01-10T00:00:00",
                "rank": 1
            },
            {
                "team_id": 2,
                "player1_id": 3,
                "player2_id": 4,
                "global_elo": 1400.0,
                "current_month_elo": 1350.0,
                "created_at": "2025-01-02T00:00:00",
                "last_match_at": "2025-01-09T00:00:00",
                "rank": 2
            }
        ]
        
        # Mock player retrieval
        mock_get_player.side_effect = [
            {
                "player_id": 1,
                "name": "Player 1",
                "global_elo": 1500,
                "current_month_elo": 1450,
                "matches_played": 10,
                "wins": 7,
                "losses": 3,
                "creation_date": "2025-01-01T00:00:00"
            },
            {
                "player_id": 2,
                "name": "Player 2",
                "global_elo": 1500,
                "current_month_elo": 1450,
                "matches_played": 10,
                "wins": 7,
                "losses": 3,
                "creation_date": "2025-01-01T00:00:00"
            },
            {
                "player_id": 3,
                "name": "Player 3",
                "global_elo": 1400,
                "current_month_elo": 1350,
                "matches_played": 8,
                "wins": 4,
                "losses": 4,
                "creation_date": "2025-01-01T00:00:00"
            },
            {
                "player_id": 4,
                "name": "Player 4",
                "global_elo": 1400,
                "current_month_elo": 1350,
                "matches_played": 8,
                "wins": 4,
                "losses": 4,
                "creation_date": "2025-01-01T00:00:00"
            }
        ]
        
        # Make request
        response = await self.client.get("/api/v1/teams/rankings")
        
        # Verify response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)
        self.assertEqual(response.json()[0]["team_id"], 1)
        self.assertEqual(response.json()[1]["team_id"], 2)
        
        # Verify mocks were called correctly
        mock_get_team_rankings.assert_called_once_with(limit=100, use_monthly_elo=False)
        self.assertEqual(mock_get_player.call_count, 4)
    
    @patch("app.routers.teams.get_team_rankings")
    async def test_get_team_rankings_with_params(self, mock_get_team_rankings):
        """
        Test getting team rankings with custom parameters.
        """
        # Mock team rankings retrieval
        mock_get_team_rankings.return_value = []
        
        # Make request with custom parameters
        response = await self.client.get("/api/v1/teams/rankings?limit=50&use_monthly_elo=true")
        
        # Verify response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify mock was called with correct parameters
        mock_get_team_rankings.assert_called_once_with(limit=50, use_monthly_elo=True)


if __name__ == "__main__":
    main()
