# -*- coding: utf-8 -*-
"""
ELO Calculation Module

This module provides functions to calculate team ELO, win probabilities, K factors, and ELO changes.
"""

from typing import List, Dict, Any

from math import pow
from statistics import mean

from loguru import logger


# ##: K-factors for established players.
K_TIER1 = 100  # ELO < 1200
K_TIER2 = 50  # 1200 <= ELO < 1800
K_TIER3 = 24  # ELO >= 1800


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
    team_elo = int(mean([player1_elo, player2_elo]))

    logger.debug(f"Calculated team ELO: {team_elo} from player ELOs {player1_elo}, {player2_elo}")
    return team_elo


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
    probability = 1 / (1 + pow(10, exponent))

    logger.debug(
        f"Calculated win probability: {probability:.4f} for team A ELO {team_a_elo} vs team B ELO {team_b_elo}"
    )
    return probability


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
        return K_TIER1

    if player_elo < 1800:
        return K_TIER2

    return K_TIER3


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
    change = int(k * (match_result - win_probability))
    logger.debug(
        f"Calculated ELO change: {change} for player ELO {player_elo}, win_prob {win_probability:.4f}, result {match_result}"
    )
    return change


def process_match_result(winning_team: List[Dict[str, Any]], losing_team: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Process match results and calculate updated ELO values for each player.

    Parameters
    ----------
    winning_team : List[Dict[str, Any]]
        List of player objects for the winning team.
    losing_team : List[Dict[str, Any]]
        List of player objects for the losing team.

    Returns
    -------
    Dict[str, Any]
        Mapping player IDs to a dict with 'old_elo', 'new_elo', and 'change'.
    """
    logger.info(
        f"Processing match: Winners ({[p['id'] for p in winning_team]}) vs Losers ({[p['id'] for p in losing_team]})"
    )

    # ##: Calculate team ELOs by averaging individual ratings.
    elo_winner = calculate_team_elo(winning_team[0]["elo"], winning_team[1]["elo"])
    elo_loser = calculate_team_elo(losing_team[0]["elo"], losing_team[1]["elo"])
    logger.debug(f"Team ELOs calculated: Winners {elo_winner}, Losers {elo_loser}")

    results = {}

    # ##: Calculate ELO changes for winning team.
    for player in winning_team:
        win_prob = calculate_win_probability(elo_winner, elo_loser)
        change = calculate_elo_change(player["elo"], win_prob, 1)
        new_elo = player["elo"] + change
        logger.info(f"Player {player['id']} (Winner): ELO {player['elo']} -> {new_elo} (Change: {change})")
        results[player["id"]] = {"old_elo": player["elo"], "new_elo": new_elo, "change": change}

    # ##: Calculate ELO changes for losing team.
    for player in losing_team:
        win_prob = calculate_win_probability(elo_loser, elo_winner)
        change = calculate_elo_change(player["elo"], win_prob, 0)
        new_elo = player["elo"] + change
        logger.info(f"Player {player['id']} (Loser): ELO {player['elo']} -> {new_elo} (Change: {change})")
        results[player["id"]] = {"old_elo": player["elo"], "new_elo": new_elo, "change": change}

    return results
