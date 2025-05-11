# -*- coding: utf-8 -*-
"""
Operations related to player statistics and leaderboards.
"""

from typing import Any, Dict, List, Optional

from loguru import logger

from app.db import DatabaseManager
from app.db.retry import with_retry

from .builders import SelectQueryBuilder
from .players import get_player


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
        # ##: Get player details.
        player = get_player(player_id)
        if not player:
            return None

        # ##: Get match count via QueryBuilder
        mc_result = (
            SelectQueryBuilder("Matches m")
            .select("COUNT(DISTINCT m.match_id)")
            .join("Teams t1", "m.team1_id = t1.team_id")
            .join("Teams t2", "m.team2_id = t2.team_id")
            .where(
                "t1.player1_id = ? OR t1.player2_id = ? OR t2.player1_id = ? OR t2.player2_id = ?",
                player_id,
                player_id,
                player_id,
                player_id,
            )
            .execute(fetch_all=False)
        )
        match_count = mc_result[0] if mc_result else 0

        # ##: Get win count via QueryBuilder
        wc_result = (
            SelectQueryBuilder("Matches m")
            .select("COUNT(*)")
            .join("Teams t", "m.winner_team_id = t.team_id")
            .where("t.player1_id = ? OR t.player2_id = ?", player_id, player_id)
            .execute(fetch_all=False)
        )
        win_count = wc_result[0] if wc_result else 0

        # ##: Calculate win rate.
        win_rate = (win_count / match_count * 100) if match_count > 0 else 0

        return {
            **player,
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
        db_manager = DatabaseManager()
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
        # ##: Fetch ELO history via QueryBuilder
        rows = (
            SelectQueryBuilder("ELO_History h")
            .select(
                "h.history_id",
                "h.player_id",
                "h.match_id",
                "h.elo_score",
                "h.updated_at",
                "m.match_date",
            )
            .join("Matches m", "h.match_id = m.match_id")
            .where("h.player_id = ?", player_id)
            .order_by_clause("m.match_date DESC")
            .execute()
        )
        return (
            [
                {
                    "history_id": r[0],
                    "player_id": r[1],
                    "match_id": r[2],
                    "elo_score": r[3],
                    "updated_at": r[4],
                    "match_date": r[5],
                }
                for r in rows
            ]
            if rows
            else []
        )
    except Exception as e:
        logger.error("Failed to get player ELO history for ID %d: %s", player_id, e)
        return []
