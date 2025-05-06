# -*- coding: utf-8 -*-
"""
Operations related to ELO history.
"""

from logging import getLogger
from typing import Any, Dict, List, Optional

from app.db import transaction, with_retry

logger = getLogger(__name__)


@with_retry(max_retries=3, retry_delay=0.5)
def record_elo_update(player_id: int, match_id: int, elo_score: float) -> Optional[int]:
    """
    Record an ELO score update after a match.

    Parameters
    ----------
    player_id : int
        ID of the player
    match_id : int
        ID of the match
    elo_score : float
        New ELO score after the match

    Returns
    -------
    Optional[int]
        ID of the newly created ELO history record, or None on failure
    """
    with transaction() as db:
        result = db.fetchone(
            "INSERT INTO ELO_History (player_id, match_id, elo_score) VALUES (?, ?, ?) RETURNING history_id",
            [player_id, match_id, elo_score],
        )
        if result and result[0]:
            return result[0]
        return None


@with_retry(max_retries=3, retry_delay=0.5)
def get_current_elo(player_id: int) -> Optional[float]:
    """
    Get the current ELO score for a player.

    Parameters
    ----------
    player_id : int
        ID of the player

    Returns
    -------
    Optional[float]
        Current ELO score, or None if no history exists
    """
    try:
        with transaction() as db_manager:
            result = db_manager.fetchone(
                """
                SELECT elo_score
                FROM ELO_History
                WHERE player_id = ?
                ORDER BY history_id DESC
                LIMIT 1
                """,
                [player_id],
            )
            return result[0] if result else None
    except Exception as e:
        logger.error("Failed to get current ELO for player ID %d: %s", player_id, e)
        return None


@with_retry(max_retries=3, retry_delay=0.5)
def batch_record_elo_updates(elo_updates: List[Dict[str, Any]]) -> List[Optional[int]]:
    """
    Record multiple ELO updates in a single transaction.

    Parameters
    ----------
    elo_updates : List[Dict[str, Any]]
        List of ELO update dictionaries, each with 'player_id', 'match_id', and 'elo_score' keys

    Returns
    -------
    List[Optional[int]]
        List of IDs for the newly created ELO history records, or None for failures
    """
    history_ids = []
    with transaction() as db:
        for update in elo_updates:
            result = db.fetchone(
                "INSERT INTO ELO_History (player_id, match_id, elo_score) VALUES (?, ?, ?) RETURNING history_id",
                [update["player_id"], update["match_id"], update["elo_score"]],
            )
            history_ids.append(result[0] if result else None)

    return history_ids
