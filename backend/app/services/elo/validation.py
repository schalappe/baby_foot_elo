# -*- coding: utf-8 -*-
"""
ELO Match Result Validation Utilities
"""

from logging import getLogger

logger = getLogger(__name__)


def validate_teams(team_a: list, team_b: list) -> None:
    """
    Verify teams structure and player ELO ratings.
    Raises ValueError on invalid team lists or player ELOs.
    """
    if len(team_a) == 0 or len(team_b) == 0:
        raise ValueError("Teams must contain at least one player")
    for team in (team_a, team_b):
        logger.debug(f"Validating team: {[getattr(p, 'id', 'Unknown') for p in team]}")
        for player in team:
            if not hasattr(player, "elo") or not isinstance(player.elo, int) or player.elo < 0:
                logger.error(
                    f"Invalid ELO for player {getattr(player, 'id', 'Unknown')}: {getattr(player, 'elo', 'Missing ELO attribute')}"
                )
                raise ValueError(f"Player {getattr(player, 'id', None)} has invalid ELO rating")


def validate_scores(winner_score: int, loser_score: int) -> None:
    """
    Confirm scores are non-negative, and winner > loser.
    """
    if winner_score < 0 or loser_score < 0:
        raise ValueError("Scores must be non-negative")
    if winner_score <= loser_score:
        logger.error(
            f"Invalid scores: Winner {winner_score}, Loser {loser_score}. Winner score must be greater."
        )
        raise ValueError("Winner score must be greater than loser score")


def validate_match_result(
    winning_team: list, losing_team: list, winner_score: int, loser_score: int
) -> None:
    """
    Comprehensive validation before processing a match result.
    Calls validate_teams and validate_scores.
    """
    validate_teams(winning_team, losing_team)
    validate_scores(winner_score, loser_score)
    logger.debug("Match result validation successful.")
