# -*- coding: utf-8 -*-
"""
ELO Calculation Module

This module provides functions to calculate team ELO, win probabilities, K factors, and ELO changes.
"""

from statistics import mean
from math import pow

def calculate_team_elo(player1_elo: int, player2_elo: int) -> int:
    """
    Calculate team ELO as the average of two player ELO ratings.

    Parameters
    ----------
    player1_elo : int
        ELO rating of player 1.
    player2_elo : int
        ELO rating of player 2.

    Returns
    -------
    int
        Team ELO rating.

    Raises
    ------
    ValueError
        If ELO ratings are negative.
    """
    if player1_elo < 0 or player2_elo < 0:
        raise ValueError("ELO ratings must be non-negative")
    return int(mean([player1_elo, player2_elo]))


def calculate_win_probability(team_a_elo: int, team_b_elo: int) -> float:
    """
    Calculate win probability using the ELO formula.

    Formula: 1 / (1 + 10 ** ((ELO_B - ELO_A) / 400))

    Parameters
    ----------
    team_a_elo : int
        ELO rating of team A.
    team_b_elo : int
        ELO rating of team B.

    Returns
    -------
    float
        Win probability of team A.

    Raises
    ------
    ValueError
        If ELO ratings are negative.
    """
    if team_a_elo < 0 or team_b_elo < 0:
        raise ValueError("ELO ratings must be non-negative")
    exponent = (team_b_elo - team_a_elo) / 400
    return 1 / (1 + pow(10, exponent))


def determine_k_factor(player_elo: int) -> int:
    """
    Determine the K factor based on player's ELO rating.

    K factor tiers:
    - 100 for ELO < 1200
    - 50 for 1200 <= ELO < 1800
    - 24 for ELO >= 1800

    Parameters
    ----------
    player_elo : int
        ELO rating of the player.

    Returns
    -------
    int
        K factor.

    Raises
    ------
    ValueError
        If ELO rating is negative.
    """
    if player_elo < 0:
        raise ValueError("ELO rating must be non-negative")
    if player_elo < 1200:
        return 100
    if player_elo < 1800:
        return 50
    return 24


def calculate_elo_change(player_elo: int, win_probability: float, match_result: int) -> int:
    """
    Calculate individual ELO change using the formula:

    ELO Change = K * (Result - Expected)

    Where Result is 1 for win, 0 for loss.

    Parameters
    ----------
    player_elo : int
        ELO rating of the player.
    win_probability : float
        Win probability of the player.
    match_result : int
        Match result (1 for win, 0 for loss).

    Returns
    -------
    int
        ELO change.

    Raises
    ------
    ValueError
        If inputs are invalid or out of range.
    """
    if player_elo < 0:
        raise ValueError("ELO rating must be non-negative")
    if not (0 <= win_probability <= 1):
        raise ValueError("Win probability must be between 0 and 1")
    if match_result not in (0, 1):
        raise ValueError("Match result must be 0 (loss) or 1 (win)")

    k = determine_k_factor(player_elo)
    return int(k * (match_result - win_probability))
