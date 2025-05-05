# -*- coding: utf-8 -*-
"""
Operations related to ELO history.
"""

from typing import Any, Dict, List, Optional

from app.db import DatabaseManager, transaction, with_retry


@with_retry()
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
        db.execute(
            "INSERT INTO ELO_History (player_id, match_id, elo_score) VALUES (?, ?, ?)",
            [player_id, match_id, elo_score],
        )
        result = db.fetchone("SELECT last_insert_rowid()")
        return result[0] if result else None


@with_retry()
def get_player_elo_history(player_id: int) -> List[Dict[str, Any]]:
    """
    Get the ELO history for a specific player.

    Parameters
    ----------
    player_id : int
        ID of the player

    Returns
    -------
    List[Dict[str, Any]]
        List of ELO history records
    """
    db = DatabaseManager()
    results = db.fetchall(
        """
        SELECT h.history_id, h.player_id, h.match_id, h.elo_score, h.updated_at, m.match_date
        FROM ELO_History h
        JOIN Matches m ON h.match_id = m.match_id
        WHERE h.player_id = ?
        ORDER BY m.match_date DESC
        """,
        [player_id],
    )
    return [
        {
            "history_id": row[0],
            "player_id": row[1],
            "match_id": row[2],
            "elo_score": row[3],
            "updated_at": row[4],
            "match_date": row[5],
        }
        for row in results
    ]


@with_retry()
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
    db = DatabaseManager()
    result = db.fetchone(
        """
        SELECT elo_score
        FROM ELO_History
        WHERE player_id = ?
        ORDER BY updated_at DESC
        LIMIT 1
        """,
        [player_id],
    )
    return result[0] if result else None
