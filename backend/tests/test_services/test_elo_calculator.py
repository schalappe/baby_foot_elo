# -*- coding: utf-8 -*-
"""
Unit tests for the ELO calculator module.
"""

from unittest import TestCase, main
from app.services.elo_calculator import (
    calculate_team_elo,
    calculate_win_probability,
    determine_k_factor,
    calculate_elo_change,
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


if __name__ == '__main__':
    main()
