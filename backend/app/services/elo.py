# -*- coding: utf-8 -*-
"""
ELO Calculation Module

This module provides functions to calculate team ELO, win probabilities, K factors, and ELO changes.

It implements a "pool" system with a correction factor to ensure that the total ELO points in the system remain
constant after each match, even when using variable K-factors. This prevents ELO inflation or deflation over time.

Example of pool system correction:
If Player A (ELO 1100, K=100) beats Player B (ELO 1900, K=24):
- Initial calculated change for A: +80 ELO
- Initial calculated change for B: -19 ELO
- Sum of changes: +61 ELO (inflation)

To correct this, the system will distribute a total of -61 ELO points back to the players, proportional to their K-factors:
- Total K-factor: 100 + 24 = 124
- Correction factor per K: -61 / 124 ≈ -0.49
- Corrected change for A: 80 + (100 * -0.49) = 80 - 49 = +31 ELO
- Corrected change for B: -19 + (24 * -0.49) = -19 - 12 = -31 ELO
- New sum of changes: +31 + (-31) = 0 ELO (zero-sum maintained)
"""

from ast import Tuple
from math import pow
from statistics import mean
from typing import Any, Dict, List

from loguru import logger

from app.models.player import PlayerResponse
from app.models.team import TeamResponse

# ##: K-factors for established players.
K_TIER1 = 200  # ELO < 1200
K_TIER2 = 100  # 1200 <= ELO < 1800
K_TIER3 = 50  # ELO >= 1800


def calculate_team_elo(member_1_elo: int, member_2_elo: int) -> int:
    """
    Calculate team ELO as the average of two player ELO ratings.

    Parameters
    ----------
    member_1_elo : int
        ELO rating of member 1.
    member_2_elo : int
        ELO rating of member 2.

    Returns
    -------
    int
        Team ELO rating.

    Raises
    ------
    ValueError
        If ELO ratings are negative.
    """
    if member_1_elo < 0 or member_2_elo < 0:
        raise ValueError("ELO ratings must be non-negative")
    team_elo = int(mean([member_1_elo, member_2_elo]))

    logger.debug(f"Calculated team ELO: {team_elo} from member ELOs {member_1_elo}, {member_2_elo}")
    return team_elo


def calculate_win_probability(competitor_a_elo: int, competitor_b_elo: int) -> float:
    """
    Calculate win probability using the ELO formula.

    Formula: 1 / (1 + 10 ** ((ELO_B - ELO_A) / 400))

    Parameters
    ----------
    competitor_a_elo : int
        ELO rating of competitor A.
    competitor_b_elo : int
        ELO rating of competitor B.

    Returns
    -------
    float
        Win probability of competitor A.

    Raises
    ------
    ValueError
        If ELO ratings are negative.
    """
    if competitor_a_elo < 0 or competitor_b_elo < 0:
        raise ValueError("ELO ratings must be non-negative")

    exponent = (competitor_b_elo - competitor_a_elo) / 400
    probability = 1 / (1 + pow(10, exponent))

    logger.debug(
        f"Calculated win probability: {probability:.4f} for competitor A ELO {competitor_a_elo} vs competitor B ELO {competitor_b_elo}"
    )
    return probability


def determine_k_factor(competitor_elo: int) -> int:
    """
    Determine the K factor based on competitor's ELO rating.

    K factor tiers:
    - 100 for ELO < 1200
    - 50 for 1200 <= ELO < 1800
    - 24 for ELO >= 1800

    Parameters
    ----------
    competitor_elo : int
        ELO rating of the competitor.

    Returns
    -------
    int
        K factor.

    Raises
    ------
    ValueError
        If ELO rating is negative.
    """
    if competitor_elo < 0:
        raise ValueError("ELO rating must be non-negative")

    if competitor_elo < 1200:
        return K_TIER1

    if competitor_elo < 1800:
        return K_TIER2

    return K_TIER3


def calculate_elo_change(competitor_elo: int, win_probability: float, match_result: int) -> int:
    """
    Calculate individual ELO change using the formula:

    ELO Change = K * (Result - Expected)

    Where Result is 1 for win, 0 for loss.

    Parameters
    ----------
    competitor_elo : int
        ELO rating of the competitor.
    win_probability : float
        Win probability of the competitor.
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
    if competitor_elo < 0:
        raise ValueError("ELO rating must be non-negative")
    if not (0 <= win_probability <= 1):
        raise ValueError("Win probability must be between 0 and 1")
    if match_result not in (0, 1):
        raise ValueError("Match result must be 0 (loss) or 1 (win)")

    factor = determine_k_factor(competitor_elo)
    change = int(factor * (match_result - win_probability))
    logger.debug(
        f"Calculated ELO change: {change} for competitor ELO {competitor_elo}, win_prob {win_probability:.4f}, result {match_result}"
    )
    return change


def calculate_players_elo_change(winning_team: TeamResponse, losing_team: TeamResponse) -> Dict[str, Any]:
    """
    Calculate ELO changes for each player in a match.

    This function applies a "pool" system correction to ensure that the sum of ELO changes
    for all players in a match is zero, preventing ELO inflation/deflation.

    Parameters
    ----------
    winning_team : TeamResponse
        The winning team.
    losing_team : TeamResponse
        The losing team.

    Returns
    -------
    Dict[str, Any]
        Mapping player IDs to a dict with 'old_elo', 'new_elo', and 'change'.
    """
    elo_winner = calculate_team_elo(winning_team.player1.global_elo, winning_team.player2.global_elo)
    elo_loser = calculate_team_elo(losing_team.player1.global_elo, losing_team.player2.global_elo)
    win_prob = calculate_win_probability(competitor_a_elo=elo_winner, competitor_b_elo=elo_loser)

    results = {}
    all_players_changes = []

    # ##: Calculate ELO changes for winning team.
    for player in [winning_team.player1, winning_team.player2]:
        change = calculate_elo_change(competitor_elo=player.global_elo, win_probability=win_prob, match_result=1)
        all_players_changes.append((player, change, determine_k_factor(player.global_elo)))

    # ##: Calculate ELO changes for losing team.
    for player in [losing_team.player1, losing_team.player2]:
        change = calculate_elo_change(competitor_elo=player.global_elo, win_probability=1 - win_prob, match_result=0)
        all_players_changes.append((player, change, determine_k_factor(player.global_elo)))

    # ##: Apply pool system correction.
    sum_delta_elo = sum(change for _, change, _ in all_players_changes)
    if sum_delta_elo != 0:
        total_k_factor = sum(k for _, _, k in all_players_changes)
        correction_factor_per_k = -sum_delta_elo / total_k_factor
        logger.debug(
            f"Applying ELO pool correction: sum_delta_elo={sum_delta_elo}, total_k_factor={total_k_factor}, correction_factor_per_k={correction_factor_per_k:.4f}"
        )

        for i, (player, change, k_factor) in enumerate(all_players_changes):
            corrected_change = change + (k_factor * correction_factor_per_k)
            all_players_changes[i] = (player, int(corrected_change), k_factor)

    for player, change, _ in all_players_changes:
        new_elo = player.global_elo + change
        logger.debug(f"Player {player.player_id}: ELO {player.global_elo} -> {new_elo} (Change: {change})")
        results[player.player_id] = {"old_elo": player.global_elo, "new_elo": new_elo, "change": change}

    return results


def calculate_team_elo_change(winning_team: TeamResponse, losing_team: TeamResponse) -> Dict[str, Any]:
    """
    Calculate ELO changes for a team match.

    This function applies a "pool" system correction to ensure that the sum of ELO changes
    for all teams in a match is zero, preventing ELO inflation/deflation.

    Parameters
    ----------
    winning_team : TeamResponse
        The winning team.
    losing_team : TeamResponse
        The losing team.

    Returns
    -------
    Dict[str, Any]
        Mapping team IDs to a dict with 'old_elo', 'new_elo', and 'change'.
    """

    results = {}
    all_teams_changes = []

    # ##: Calculate initial ELO changes for winning and losing teams.
    win_change = calculate_elo_change(
        competitor_elo=winning_team.global_elo,
        win_probability=calculate_win_probability(winning_team.global_elo, losing_team.global_elo),
        match_result=1,
    )
    all_teams_changes.append((winning_team, win_change, determine_k_factor(winning_team.global_elo)))

    lose_change = calculate_elo_change(
        competitor_elo=losing_team.global_elo,
        win_probability=calculate_win_probability(losing_team.global_elo, winning_team.global_elo),
        match_result=0,
    )
    all_teams_changes.append((losing_team, lose_change, determine_k_factor(losing_team.global_elo)))

    # ##: Apply pool system correction.
    sum_delta_elo = sum(change for _, change, _ in all_teams_changes)
    if sum_delta_elo != 0:
        total_k_factor = sum(k for _, _, k in all_teams_changes)
        correction_factor_per_k = -sum_delta_elo / total_k_factor
        logger.debug(
            f"Applying ELO pool correction for teams: sum_delta_elo={sum_delta_elo}, total_k_factor={total_k_factor}, correction_factor_per_k={correction_factor_per_k:.4f}"
        )

        for i, (team, change, k_factor) in enumerate(all_teams_changes):
            corrected_change = change + (k_factor * correction_factor_per_k)
            all_teams_changes[i] = (team, int(corrected_change), k_factor)

    for team, change, _ in all_teams_changes:
        new_elo = team.global_elo + change
        logger.debug(f"Team {team.team_id}: ELO {team.global_elo} -> {new_elo} (Change: {change})")
        results[team.team_id] = {"old_elo": team.global_elo, "new_elo": new_elo, "change": change}

    return results


def process_match_result(
    winning_team: TeamResponse, losing_team: TeamResponse
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Process match results and calculate updated ELO values for each player.

    Parameters
    ----------
    winning_team : TeamResponse
        The winning team.
    losing_team : TeamResponse
        The losing team.

    Returns
    -------
    Tuple[Dict[str, Any], Dict[str, Any]]
        Tuple of two dictionaries:
        - First dictionary: Mapping player IDs to a dict with 'old_elo', 'new_elo', and 'change'.
        - Second dictionary: Mapping team IDs to a dict with 'old_elo', 'new_elo', and 'change'.
    """
    if (
        winning_team.player1 is None
        or winning_team.player2 is None
        or losing_team.player1 is None
        or losing_team.player2 is None
    ):
        raise ValueError("Player must be provided")

    players_elo_change = calculate_players_elo_change(winning_team, losing_team)
    team_elo_change = calculate_team_elo_change(winning_team, losing_team)

    return players_elo_change, team_elo_change
