# -*- coding: utf-8 -*-
"""
CRUD operations for the Stats table.
"""

from typing import Any, Dict, Optional

from loguru import logger

from app.db.builders import SelectQueryBuilder
from app.db.repositories.players import get_player_by_id_or_name
from app.db.repositories.teams import get_team
from app.db.session import with_retry


@with_retry(max_retries=3, retry_delay=0.5)
def get_player_match_stats(player_id: int) -> Dict[str, Any]:
    """
    Get the match statistics for a player.

    Parameters
    ----------
    player_id : int
        ID of the player

    Returns
    -------
    Dict[str, Any]
        Match statistics for the player
    """
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

    # ##: Get the player's last match date using SelectQueryBuilder.
    last_match_query_result = (
        SelectQueryBuilder("Matches m")
        .select("MAX(m.played_at)")
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

    return {
        "matches_played": match_count,
        "wins": win_count,
        "losses": loss_count,
        "last_match_at": last_match_query_result[0] if last_match_query_result else None,
    }


def get_team_match_stats(team_id: int) -> Dict[str, Any]:
    """
    Get the match statistics for a team.

    Parameters
    ----------
    team_id : int
        ID of the team

    Returns
    -------
    Dict[str, Any]
        Match statistics for the team
    """
    # ##: Get match count via QueryBuilder
    mc_result = (
        SelectQueryBuilder("Matches m")
        .select("COUNT(DISTINCT m.match_id)")
        .join("Teams tw", "m.winner_team_id = tw.team_id")
        .join("Teams tl", "m.loser_team_id = tl.team_id")
        .where("tw.team_id = ? OR tl.team_id = ?", team_id, team_id)
        .execute(fetch_all=False)
    )
    match_count = mc_result[0] if mc_result else 0

    # ##: Get win count via QueryBuilder
    wc_result = (
        SelectQueryBuilder("Matches m")
        .select("COUNT(*)")
        .join("Teams t", "m.winner_team_id = t.team_id")
        .where("t.team_id = ?", team_id)
        .execute(fetch_all=False)
    )
    win_count = wc_result[0] if wc_result else 0

    # ##: Get loss count via QueryBuilder
    lc_result = (
        SelectQueryBuilder("Matches m")
        .select("COUNT(*)")
        .join("Teams t", "m.loser_team_id = t.team_id")
        .where("t.team_id = ?", team_id)
        .execute(fetch_all=False)
    )
    loss_count = lc_result[0] if lc_result else 0

    # ##: Get the team's last match date using SelectQueryBuilder.
    last_match_query_result = (
        SelectQueryBuilder("Matches m")
        .select("MAX(m.played_at)")
        .join("Teams tw", "m.winner_team_id = tw.team_id")
        .join("Teams tl", "m.loser_team_id = tl.team_id")
        .where("tw.team_id = ? OR tl.team_id = ?", team_id, team_id)
        .execute(fetch_all=False)
    )

    return {
        "matches_played": match_count,
        "wins": win_count,
        "losses": loss_count,
        "last_match_at": last_match_query_result[0] if last_match_query_result else None,
    }


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
        player = get_player_by_id_or_name(player_id=player_id)
        if not player:
            return None
        match_stats = get_player_match_stats(player_id)

        # ##: Calculate win rate.
        win_rate = (
            (match_stats["wins"] / match_stats["matches_played"] * 100) if match_stats["matches_played"] > 0 else 0
        )

        return {
            **player,
            **match_stats,
            "win_rate": win_rate,
        }
    except Exception as e:
        logger.error("Failed to get player stats for ID %d: %s", player_id, e)
        return None


def get_team_stats(team_id: int) -> Optional[Dict[str, Any]]:
    """
    Get comprehensive stats for a team.

    Parameters
    ----------
    team_id : int
        ID of the team

    Returns
    -------
    Optional[Dict[str, Any]]
        Team statistics, or None if team not found
    """
    try:
        # ##: Get team details.
        team = get_team(team_id)
        if not team:
            return None
        match_stats = get_team_match_stats(team_id)

        # ##: Calculate win rate.
        win_rate = (
            (match_stats["wins"] / match_stats["matches_played"] * 100) if match_stats["matches_played"] > 0 else 0
        )

        return {
            **team,
            **match_stats,
            "win_rate": win_rate,
        }
    except Exception as e:
        logger.error("Failed to get team stats for ID %d: %s", team_id, e)
        return None
