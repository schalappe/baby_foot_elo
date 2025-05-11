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
            .join("Teams tw", "m.winner_team_id = tw.team_id")
            .join("Teams tl", "m.loser_team_id = tl.team_id")
            .where(
                "tw.player1_id = ? OR tw.player2_id = ? OR tl.player1_id = ? OR tl.player2_id = ?",
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

        # ##: Get loss count via QueryBuilder
        lc_result = (
            SelectQueryBuilder("Matches m")
            .select("COUNT(*)")
            .join("Teams t", "m.loser_team_id = t.team_id")
            .where("t.player1_id = ? OR t.player2_id = ?", player_id, player_id)
            .execute(fetch_all=False)
        )
        loss_count = lc_result[0] if lc_result else 0

        # ##: Calculate win rate.
        win_rate = (win_count / match_count * 100) if match_count > 0 else 0

        return {
            **player,
            "matches_played": match_count,
            "wins": win_count,
            "losses": loss_count,
            "win_rate": win_rate,
        }
    except Exception as e:
        logger.error("Failed to get player stats for ID %d: %s", player_id, e)
        return None


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
                "h.old_elo",
                "h.new_elo",
                "h.difference",
                "h.date",
                "h.year",
                "h.month",
                "h.day",
                "m.played_at",
            )
            .join("Matches m", "h.match_id = m.match_id")
            .where("h.player_id = ?", player_id)
            .order_by_clause("h.date DESC")
            .execute()
        )
        return (
            [
                {
                    "history_id": r[0],
                    "player_id": r[1],
                    "match_id": r[2],
                    "old_elo": r[4],
                    "new_elo": r[5],
                    "difference": r[6],
                    "date": r[7],
                    "year": r[8],
                    "month": r[9],
                    "day": r[10],
                    "match_date": r[11],
                }
                for r in rows
            ]
            if rows
            else []
        )
    except Exception as e:
        logger.error("Failed to get player ELO history for ID %d: %s", player_id, e)
        return []
