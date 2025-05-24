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

from statistics import mean
from typing import Any, Dict, Tuple

from loguru import logger

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
    - 200 for ELO < 1200
    - 100 for 1200 <= ELO < 1800
    - 50 for ELO >= 1800

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


def calculate_elo_changes_with_pool_correction(
    competitors_data: Dict[Any, Dict[str, Any]],
) -> Dict[Any, Dict[str, Any]]:
    """
    Calculate ELO changes for a group of competitors, applying a "pool" system correction
    to ensure the sum of ELO changes is zero.

    Parameters
    ----------
    competitors_data : Dict[Any, Dict[str, Any]]
        A dictionary where keys are competitor IDs and values are dictionaries
        containing 'old_elo', 'win_prob', 'match_result', and 'k_factor' for each competitor.

    Returns
    -------
    Dict[Any, Dict[str, Any]]
        Mapping competitor IDs to a dict with 'old_elo', 'new_elo', and 'change'.
    """
    initial_elo_changes = {}
    total_k_factor = 0
    sum_of_initial_changes = 0

    for comp_id, data in competitors_data.items():
        initial_change = calculate_elo_change(data["old_elo"], data["win_prob"], data["match_result"])
        initial_elo_changes[comp_id] = initial_change
        total_k_factor += data["k_factor"]
        sum_of_initial_changes += initial_change

    # ##: Apply pool system correction.
    corrected_elo_changes = {}
    if total_k_factor != 0:
        correction_factor_per_k = -sum_of_initial_changes / total_k_factor
    else:
        correction_factor_per_k = 0

    for comp_id, data in competitors_data.items():
        initial_change = initial_elo_changes[comp_id]
        corrected_change = initial_change + int(data["k_factor"] * correction_factor_per_k)
        corrected_elo_changes[comp_id] = {
            "old_elo": data["old_elo"],
            "new_elo": data["old_elo"] + corrected_change,
            "change": corrected_change,
        }
    return corrected_elo_changes


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
    all_players_data = {}
    elo_winner = calculate_team_elo(winning_team.player1.global_elo, winning_team.player2.global_elo)
    elo_loser = calculate_team_elo(losing_team.player1.global_elo, losing_team.player2.global_elo)
    win_prob = calculate_win_probability(competitor_a_elo=elo_winner, competitor_b_elo=elo_loser)

    # ##: Winning team players.
    all_players_data[winning_team.player1.player_id] = {
        "old_elo": winning_team.player1.global_elo,
        "win_prob": win_prob,
        "match_result": 1,
        "k_factor": determine_k_factor(winning_team.player1.global_elo),
    }
    all_players_data[winning_team.player2.player_id] = {
        "old_elo": winning_team.player2.global_elo,
        "win_prob": win_prob,
        "match_result": 1,
        "k_factor": determine_k_factor(winning_team.player2.global_elo),
    }

    # ##: Losing team players.
    all_players_data[losing_team.player1.player_id] = {
        "old_elo": losing_team.player1.global_elo,
        "win_prob": 1 - win_prob,
        "match_result": 0,
        "k_factor": determine_k_factor(losing_team.player1.global_elo),
    }
    all_players_data[losing_team.player2.player_id] = {
        "old_elo": losing_team.player2.global_elo,
        "win_prob": 1 - win_prob,
        "match_result": 0,
        "k_factor": determine_k_factor(losing_team.player2.global_elo),
    }

    return calculate_elo_changes_with_pool_correction(all_players_data)


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
    # ##: Calculate initial ELO changes for winning and losing teams.
    win_probability = calculate_win_probability(winning_team.global_elo, losing_team.global_elo)

    teams_data = {
        winning_team.team_id: {
            "old_elo": winning_team.global_elo,
            "win_prob": win_probability,
            "match_result": 1,
            "k_factor": determine_k_factor(winning_team.global_elo),
        },
        losing_team.team_id: {
            "old_elo": losing_team.global_elo,
            "win_prob": 1 - win_probability,
            "match_result": 0,
            "k_factor": determine_k_factor(losing_team.global_elo),
        },
    }
    return calculate_elo_changes_with_pool_correction(teams_data)


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
