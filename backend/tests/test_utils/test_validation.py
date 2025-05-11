# -*- coding: utf-8 -*-
"""
Unit tests for validation utilities.
"""

import unittest

from fastapi import status

from app.utils.validation import ValidationErrorResponse, validate_team_players


class TestValidation(unittest.TestCase):
    """
    Test cases for validation utilities.
    """

    def test_validate_team_players_valid(self):
        """
        Test validation of valid team players.
        """
        # Should not raise an exception
        validate_team_players(1, 2)

    def test_validate_team_players_same_player(self):
        """
        Test validation when both players are the same.
        """
        with self.assertRaises(ValidationErrorResponse) as context:
            validate_team_players(1, 1)

        exception = context.exception
        self.assertEqual(exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(exception.detail, "Invalid player IDs for team")
        self.assertEqual(len(exception.errors), 1)
        self.assertIn("Players in a team must be different", exception.errors[0]["message"])

    def test_validate_team_players_invalid_ids(self):
        """
        Test validation with invalid player IDs.
        """
        with self.assertRaises(ValidationErrorResponse) as context:
            validate_team_players(-1, 0)

        exception = context.exception
        self.assertEqual(exception.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(exception.detail, "Invalid player IDs for team")
        self.assertEqual(len(exception.errors), 2)  # Both IDs are invalid


if __name__ == "__main__":
    unittest.main()
