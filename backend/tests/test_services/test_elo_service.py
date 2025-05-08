# -*- coding: utf-8 -*-
"""
Unit tests for the ELO calculator module.
"""

from unittest import TestCase, main
from app.services.elo import (
    calculate_team_elo,
    calculate_win_probability,
    determine_k_factor,
    calculate_elo_change,
    process_match_result,
    validate_teams,
    validate_scores,
    validate_match_result,
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

    def test_process_match_result_simple(self):
        """Test process_match_result with equal ELO players."""
        class MockPlayer:
            def __init__(self, id, elo):
                self.id = id
                self.elo = elo

        team_a = [MockPlayer(1, 1500), MockPlayer(2, 1500)]
        team_b = [MockPlayer(3, 1500), MockPlayer(4, 1500)]
        results = process_match_result(team_a, team_b, winner_score=2, loser_score=1)

        # Expected: K factor 50 => change 25 for winners, -25 for losers
        for pid in (1, 2):
            self.assertEqual(results[pid]['change'], 25)
            self.assertEqual(results[pid]['new_elo'], 1525)
        for pid in (3, 4):
            self.assertEqual(results[pid]['change'], -25)
            self.assertEqual(results[pid]['new_elo'], 1475)

    def test_validate_teams_empty(self):
        class MockPlayer: pass
        with self.assertRaises(ValueError):
            validate_teams([], [])

    def test_validate_teams_invalid_elo(self):
        class MockPlayer:
            def __init__(self):
                self.id = 1
                self.elo = -5
        with self.assertRaises(ValueError):
            validate_teams([MockPlayer()], [MockPlayer()])

    def test_validate_scores_negative(self):
        with self.assertRaises(ValueError):
            validate_scores(-1, 0)

    def test_validate_scores_invalid_order(self):
        with self.assertRaises(ValueError):
            validate_scores(1, 2)

    def test_validate_match_result_valid(self):
        class MockPlayer:
            def __init__(self, id, elo):
                self.id = id
                self.elo = elo
        team_a = [MockPlayer(1, 1000)]
        team_b = [MockPlayer(2, 1001)]
        # should not raise
        validate_match_result(team_a, team_b, 2, 1)


if __name__ == '__main__':
    main()
