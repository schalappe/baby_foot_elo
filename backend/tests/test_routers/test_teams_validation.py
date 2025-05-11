# -*- coding: utf-8 -*-
"""
Unit tests for team router validation and error handling.
"""

from unittest import TestCase, main
from unittest.mock import patch

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.utils.validation import ValidationErrorResponse


class TestTeamsRouterValidation(TestCase):
    """
    Test cases for the teams router validation and error handling.
    """

    def setUp(self):
        """
        Set up test client and mocks.
        """
        self.client = TestClient(app)
        self.invalid_team_data = {
            "player1_id": 1,
            "player2_id": 1,  # Same player ID, should fail validation
            "global_elo": 1200.0,
            "current_month_elo": 1200.0,
        }
        self.negative_id_team_data = {
            "player1_id": -1,  # Negative ID, should fail validation
            "player2_id": 2,
            "global_elo": 1200.0,
            "current_month_elo": 1200.0,
        }

    def test_create_team_validation_error(self):
        """
        Test team creation with validation error.
        """
        # Make request with invalid data (same player IDs)
        response = self.client.post("/api/v1/teams", json=self.invalid_team_data)

        # Verify response
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(response.json()["status"], "error")
        self.assertEqual(response.json()["message"], "Input validation error")
        self.assertTrue(len(response.json()["errors"]) > 0)

    def test_get_team_invalid_id(self):
        """
        Test getting a team with invalid ID format.
        """
        # Test with negative ID
        response = self.client.get("/api/v1/teams/-1")
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn("error", response.json()["status"].lower())

        # Test with non-integer ID
        response = self.client.get("/api/v1/teams/abc")
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn("error", response.json()["status"].lower())

    def test_get_team_matches_invalid_params(self):
        """
        Test getting team matches with invalid parameters.
        """
        # Test with invalid limit (too high)
        response = self.client.get("/api/v1/teams/1/matches?limit=101")
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn("error", response.json()["status"].lower())

        # Test with invalid skip (negative)
        response = self.client.get("/api/v1/teams/1/matches?skip=-1")
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn("error", response.json()["status"].lower())

    def test_get_teams_invalid_params(self):
        """
        Test getting teams list with invalid parameters.
        """
        # Test with invalid min_elo (negative)
        response = self.client.get("/api/v1/teams?min_elo=-100")
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn("error", response.json()["status"].lower())

        # Test with invalid player_id (zero)
        response = self.client.get("/api/v1/teams?player_id=0")
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn("error", response.json()["status"].lower())


if __name__ == "__main__":
    main()
