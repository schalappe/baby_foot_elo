# -*- coding: utf-8 -*-
"""
Operations related to player statistics and leaderboards.
"""

import logging
from typing import Any, Dict, List, Optional

from app.db.retry import with_retry
from app.db.transaction import transaction

from .elo_history import get_current_elo
from .players import get_player

logger = logging.getLogger(__name__)


@with_retry(max_retries=3, retry_delay=0.5)
def get_player_stats(player_id: int) -> Optional[Dict[str, Any]]:
    """
    Get comprehensive stats for a player.

    Parameters
    ----------
    player_id : int
        ID of the player

    Returns
    -------
    Optional[Dict[str, Any]]
        Player statistics, or None if player not found
    """
    try:
        with transaction() as db_manager:
            # ##: Get player details.
            player = get_player(player_id)
            if not player:
                return None

            # ##: Get current ELO.
            current_elo = get_current_elo(player_id)

            # ##: Get match count.
            match_count_query = """
            SELECT COUNT(DISTINCT m.match_id) FROM Matches m
            JOIN Teams t1 ON m.team1_id = t1.team_id
            JOIN Teams t2 ON m.team2_id = t2.team_id
            WHERE t1.player1_id = ? OR t1.player2_id = ? OR t2.player1_id = ? OR t2.player2_id = ?
            """
            match_count_result = db_manager.fetchone(
                match_count_query, [player_id, player_id, player_id, player_id]
            )
            match_count = match_count_result[0] if match_count_result else 0

            # ##: Get win count.
            win_count_query = """
            SELECT COUNT(*) FROM Matches m
            JOIN Teams t ON m.winner_team_id = t.team_id
            WHERE t.player1_id = ? OR t.player2_id = ?
            """
            win_count_result = db_manager.fetchone(win_count_query, [player_id, player_id])
            win_count = win_count_result[0] if win_count_result else 0

            # ##: Calculate win rate.
            win_rate = (win_count / match_count * 100) if match_count > 0 else 0

            return {
                **player,
                "current_elo": current_elo if current_elo is not None else 1000.0,
                "matches_played": match_count,
                "wins": win_count,
                "win_rate": win_rate,
            }
    except Exception as e:
        logger.error("Failed to get player stats for ID %d: %s", player_id, e)
        return None


@with_retry(max_retries=3, retry_delay=0.5)
def get_leaderboard(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get the current leaderboard based on ELO scores.
    Assumes a default ELO of 1000 for players without history.

    Parameters
    ----------
    limit : int
        Maximum number of players to include

    Returns
    -------
    List[Dict[str, Any]]
        Leaderboard entries
    """
    try:
        with transaction() as db_manager:
            query = """
            SELECT
                p.player_id,
                p.name,
                COALESCE(h.elo_score, 1000.0) as elo_score
            FROM Players p
            LEFT JOIN (
                SELECT player_id, MAX(updated_at) as latest_update
                FROM ELO_History
                GROUP BY player_id
            ) latest ON p.player_id = latest.player_id
            LEFT JOIN ELO_History h ON latest.player_id = h.player_id AND latest.latest_update = h.updated_at
            ORDER BY elo_score DESC
            LIMIT ?
            """

            leaderboard_players = db_manager.fetchall(query, [limit])
            results = []

            # ##: Now, for each player in the top list, fetch their stats.
            for player_data in leaderboard_players:
                player_id_from_lb = player_data[0]
                stats = get_player_stats(player_id_from_lb)
                if stats:
                    results.append(stats)

            # ##: Re-sort based on the potentially updated ELO from stats (though it should match).
            results.sort(key=lambda x: x.get("current_elo", 1000.0), reverse=True)

            return results
    except Exception as e:
        logger.error("Failed to get leaderboard: %s", e)
        return []


@with_retry(max_retries=3, retry_delay=0.5)
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
    try:
        with transaction() as db_manager:
            results = db_manager.fetchall(
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
    except Exception as e:
        logger.error("Failed to get player ELO history for ID %d: %s", player_id, e)
        return []
