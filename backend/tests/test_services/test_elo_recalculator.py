# -*- coding: utf-8 -*-
"""
Unit tests for the ELO recalculation service.
"""

from unittest import TestCase, main
from unittest.mock import patch

from app.services.elo.recalculator import recalculate_all_elos


class TestEloRecalculator(TestCase):
    """
    Test suite for the ELO recalculation functionalities.
    """

    def setUp(self):
        """
        Set up common test data.
        """
        # ##: Default mock players.
        self.mock_players_data = [
            {"player_id": 1, "name": "Player A", "global_elo": 1000, "created_at": "2023-01-01T10:00:00"},
            {"player_id": 2, "name": "Player B", "global_elo": 1000, "created_at": "2023-01-01T10:00:00"},
            {"player_id": 3, "name": "Player C", "global_elo": 1000, "created_at": "2023-01-01T10:00:00"},
            {"player_id": 4, "name": "Player D", "global_elo": 1000, "created_at": "2023-01-01T10:00:00"},
        ]

        # ##: Default mock matches (chronological).
        self.mock_matches_data = [
            {
                "match_id": 1,
                "match_date": "2023-01-10T10:00:00",
                "winner_p1_id": 1,
                "winner_p2_id": 2,
                "loser_p1_id": 3,
                "loser_p2_id": 4,
            },
            {
                "match_id": 2,
                "match_date": "2023-01-11T10:00:00",
                "winner_p1_id": 3,
                "winner_p2_id": 1,
                "loser_p1_id": 2,
                "loser_p2_id": 4,
            },
        ]

    @patch("app.services.elo.recalculator.crud_players.get_all_players")
    @patch("app.services.elo.recalculator.crud_matches.get_all_matches_for_recalculation")
    def test_basic_recalculation(self, mock_get_matches, mock_get_players):
        """
        Test basic ELO recalculation with a small dataset.
        """
        mock_get_players.return_value = self.mock_players_data
        mock_get_matches.return_value = self.mock_matches_data

        results = recalculate_all_elos(initial_elo=1000)

        self.assertIsNotNone(results)
        self.assertIn("final_recalculated_elos", results)
        self.assertIn("original_elos_for_comparison", results)
        self.assertIn("elo_evolution_log", results)

        final_elos = results["final_recalculated_elos"]
        self.assertEqual(len(final_elos), 4)
        self.assertEqual(final_elos[1], 1100)
        self.assertEqual(final_elos[2], 1000)
        self.assertEqual(final_elos[3], 1000)
        self.assertEqual(final_elos[4], 900)

        original_elos_comp = results["original_elos_for_comparison"]
        self.assertEqual(original_elos_comp[1], 1000)

        self.assertTrue(len(results["elo_evolution_log"]) > 0)

    @patch("app.services.elo.recalculator.crud_players.get_all_players")
    @patch("app.services.elo.recalculator.crud_matches.get_all_matches_for_recalculation")
    def test_no_players(self, mock_get_matches, mock_get_players):
        """
        Test recalculation when no players are found in the database.
        """
        mock_get_players.return_value = []
        mock_get_matches.return_value = self.mock_matches_data

        results = recalculate_all_elos(initial_elo=1200)

        self.assertEqual(results["final_recalculated_elos"], {})
        self.assertEqual(results["original_elos_for_comparison"], {})
        self.assertEqual(results["elo_evolution_log"], [])
        mock_get_matches.assert_not_called()

    @patch("app.services.elo.recalculator.crud_players.get_all_players")
    @patch("app.services.elo.recalculator.crud_matches.get_all_matches_for_recalculation")
    def test_no_matches(self, mock_get_matches, mock_get_players):
        """
        Test recalculation when no matches are found.
        """
        mock_get_players.return_value = self.mock_players_data
        mock_get_matches.return_value = []

        results = recalculate_all_elos(initial_elo=1200)

        expected_final_elos = {p["player_id"]: 1200 for p in self.mock_players_data}
        self.assertEqual(results["final_recalculated_elos"], expected_final_elos)

        expected_original_elos = {p["player_id"]: p["global_elo"] for p in self.mock_players_data}
        self.assertEqual(results["original_elos_for_comparison"], expected_original_elos)
        self.assertEqual(results["elo_evolution_log"], [])

    @patch("app.services.elo.recalculator.crud_players.get_all_players")
    @patch("app.services.elo.recalculator.crud_matches.get_all_matches_for_recalculation")
    def test_original_elos_comparison(self, mock_get_matches, mock_get_players):
        """
        Test that original ELOs are correctly reported for comparison.
        """
        varied_elo_players = [
            {"player_id": 1, "name": "Player A", "global_elo": 1100},
            {"player_id": 2, "name": "Player B", "global_elo": 950},
        ]
        mock_get_players.return_value = varied_elo_players
        mock_get_matches.return_value = []

        results = recalculate_all_elos(initial_elo=1000)

        expected_original = {p["player_id"]: p["global_elo"] for p in varied_elo_players}
        self.assertEqual(results["original_elos_for_comparison"], expected_original)

        # ##: Final recalculated ELOs should be the initial_elo since no matches played.
        expected_recalculated = {p["player_id"]: 1000 for p in varied_elo_players}
        self.assertEqual(results["final_recalculated_elos"], expected_recalculated)


if __name__ == "__main__":
    main()
