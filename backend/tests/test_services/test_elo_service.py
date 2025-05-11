# -*- coding: utf-8 -*-
"""
Unit tests for the ELO calculator module.
"""

from unittest import TestCase, main

from app.services.elo.calculator import (
    calculate_elo_change,
    calculate_team_elo,
    calculate_win_probability,
    determine_k_factor,
    process_match_result,
)


class TestEloCalculator(TestCase):
    """Unit tests for the ELO calculator module."""

    def test_calculate_team_elo_valid(self):
        """Test team ELO calculation with valid inputs."""
        self.assertEqual(calculate_team_elo(1400, 1500), 1450)

    def test_calculate_team_elo_negative(self):
        """Test team ELO calculation with negative inputs."""
        with self.assertRaises(ValueError):
            calculate_team_elo(-100, 1500)

    def test_calculate_win_probability_equal(self):
        """Test win probability calculation with equal inputs."""
        prob = calculate_win_probability(1500, 1500)
        self.assertAlmostEqual(prob, 0.5, places=3)

    def test_calculate_win_probability_extreme_difference(self):
        """Test win probability with extreme ELO differences."""
        # Stronger player A (2000) vs weaker player B (1000)
        prob_A_stronger = calculate_win_probability(2000, 1000)
        self.assertAlmostEqual(prob_A_stronger, 0.996, delta=0.001)

        # Weaker player A (1000) vs stronger player B (2000)
        prob_A_weaker = calculate_win_probability(1000, 2000)
        self.assertAlmostEqual(prob_A_weaker, 0.003, delta=0.001)

    def test_calculate_win_probability_range(self):
        """Test win probability calculation with out of range inputs."""
        with self.assertRaises(ValueError):
            calculate_win_probability(-1500, 1500)

    def test_determine_k_factor_tiers(self):
        """Test K factor determination with valid inputs."""
        self.assertEqual(determine_k_factor(1100), 100)
        self.assertEqual(determine_k_factor(1500), 50)
        self.assertEqual(determine_k_factor(1900), 24)

    def test_determine_k_factor_negative(self):
        """Test K factor determination with negative inputs."""
        with self.assertRaises(ValueError):
            determine_k_factor(-10)

    def test_calculate_elo_change_win(self):
        """Test ELO change calculation with win."""
        prob = calculate_win_probability(1500, 1500)
        change = calculate_elo_change(1500, prob, 1)
        self.assertGreater(change, 0)

    def test_calculate_elo_change_loss(self):
        """Test ELO change calculation with loss."""
        prob = calculate_win_probability(1500, 1500)
        change = calculate_elo_change(1500, prob, 0)
        self.assertLess(change, 0)

    def test_calculate_elo_change_invalid_prob(self):
        """Test ELO change calculation with invalid probability."""
        with self.assertRaises(ValueError):
            calculate_elo_change(1500, 1.5, 1)

    def test_calculate_elo_change_invalid_result(self):
        """Test ELO change calculation with invalid result."""
        prob = calculate_win_probability(1500, 1500)
        with self.assertRaises(ValueError):
            calculate_elo_change(1500, prob, 2)

    def test_calculate_elo_change_negative_match_count(self):
        """Test ELO change with negative match count."""
        with self.assertRaises(ValueError):
            calculate_elo_change(1500, 0.5, -1)

    def test_process_match_result_simple(self):
        """Test process_match_result with equal ELO players."""

        team_a = [{"id": 1, "elo": 1500}, {"id": 2, "elo": 1500}]
        team_b = [{"id": 3, "elo": 1500}, {"id": 4, "elo": 1500}]
        results = process_match_result(team_a, team_b)

        for pid in (1, 2):
            self.assertEqual(results[pid]["change"], 25)
            self.assertEqual(results[pid]["new_elo"], 1525)
        for pid in (3, 4):
            self.assertEqual(results[pid]["change"], -25)
            self.assertEqual(results[pid]["new_elo"], 1475)

    def test_process_match_result_new_players(self):
        """Test process_match_result with new players (low ELO, provisional K-factor)."""

        results = process_match_result(
            winning_team=[{"id": 1, "elo": 1000}, {"id": 2, "elo": 1000}],
            losing_team=[{"id": 3, "elo": 1100}, {"id": 4, "elo": 1100}],
        )

        self.assertEqual(results[1]["change"], 64)
        self.assertEqual(results[1]["new_elo"], 1064)
        self.assertEqual(results[2]["change"], 64)
        self.assertEqual(results[2]["new_elo"], 1064)

        self.assertEqual(results[3]["change"], -64)
        self.assertEqual(results[3]["new_elo"], 1100 - 64)
        self.assertEqual(results[4]["change"], -64)
        self.assertEqual(results[4]["new_elo"], 1100 - 64)

    def test_process_match_result_extreme_elo_difference_upset(self):
        """Test process_match_result with extreme ELO difference - upset win, mixed provisional/established."""
        team_a_player1 = {"id": 1, "elo": 1000}
        team_a_player2 = {"id": 2, "elo": 1000}
        team_a = [team_a_player1, team_a_player2]

        team_b_player3 = {"id": 3, "elo": 2000}
        team_b_player4 = {"id": 4, "elo": 2000}
        team_b = [team_b_player3, team_b_player4]

        results = process_match_result(team_a, team_b)

        self.assertEqual(results[1]["change"], 99)
        self.assertEqual(results[1]["new_elo"], 1099)
        self.assertEqual(results[2]["change"], 99)
        self.assertEqual(results[2]["new_elo"], 1099)

        self.assertEqual(results[3]["change"], -23)
        self.assertEqual(results[3]["new_elo"], 1977)
        self.assertEqual(results[4]["change"], -23)
        self.assertEqual(results[4]["new_elo"], 1977)

    def test_process_match_result_extreme_elo_difference_expected(self):
        """Test process_match_result with extreme ELO difference - expected win, mixed K-factors."""
        team_a_player1 = {"id": 1, "elo": 2000}
        team_a_player2 = {"id": 2, "elo": 2000}
        team_a = [team_a_player1, team_a_player2]

        team_b_player3 = {"id": 3, "elo": 1000}
        team_b_player4 = {"id": 4, "elo": 1000}
        team_b = [team_b_player3, team_b_player4]

        results = process_match_result(team_a, team_b)

        self.assertEqual(results[1]["change"], 0)
        self.assertEqual(results[1]["new_elo"], 2000)
        self.assertEqual(results[2]["change"], 0)
        self.assertEqual(results[2]["new_elo"], 2000)

        self.assertEqual(results[3]["change"], 0)
        self.assertEqual(results[3]["new_elo"], 1000)
        self.assertEqual(results[4]["change"], 0)
        self.assertEqual(results[4]["new_elo"], 1000)

    def test_process_match_result_with_tournament_modifier(self):
        """Test process_match_result with a tournament importance modifier."""
        team_a = [{"id": 1, "elo": 1500}, {"id": 2, "elo": 1500}]
        team_b = [{"id": 3, "elo": 1500}, {"id": 4, "elo": 1500}]
        results = process_match_result(team_a, team_b)

        for pid in (1, 2):
            self.assertEqual(results[pid]["change"], 25)
            self.assertEqual(results[pid]["new_elo"], 1525)
        for pid in (3, 4):
            self.assertEqual(results[pid]["change"], -25)
            self.assertEqual(results[pid]["new_elo"], 1475)


if __name__ == "__main__":
    main()
