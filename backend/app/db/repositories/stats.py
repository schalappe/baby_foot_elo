# -*- coding: utf-8 -*-
"""
CRUD operations for the Stats table.
"""

from typing import Any, Dict, Optional

from loguru import logger

from app.db.repositories.players import get_player_by_id_or_name
from app.db.repositories.teams import get_team_by_id
from app.db.session import transaction, with_retry


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
    with transaction() as db_client:
        # ##: Match Count (using RPC).
        rpc_params = {"p_player_id": player_id}
        mc_rpc_response = db_client.rpc("get_player_total_matches", rpc_params).execute()
        match_count = mc_rpc_response.data if mc_rpc_response.data is not None else 0

        # ##: Win Count (using RPC).
        wc_rpc_response = db_client.rpc("get_player_win_count", rpc_params).execute()
        win_count = wc_rpc_response.data if wc_rpc_response.data is not None else 0

        # ##: Loss Count (using RPC).
        lc_rpc_response = db_client.rpc("get_player_loss_count", rpc_params).execute()
        loss_count = lc_rpc_response.data if lc_rpc_response.data is not None else 0

        # ##: Last Match Date (using RPC).
        last_match_rpc_response = db_client.rpc("get_player_last_match_date", rpc_params).execute()
        last_match_at = last_match_rpc_response.data if last_match_rpc_response.data is not None else None

    return {
        "matches_played": match_count,
        "wins": win_count,
        "losses": loss_count,
        "last_match_at": last_match_at,
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
    with transaction() as db_client:
        rpc_params = {"p_team_id": team_id}

        # ##: Match Count (using RPC).
        mc_rpc_response = db_client.rpc("get_team_total_matches", rpc_params).execute()
        match_count = mc_rpc_response.data if mc_rpc_response.data is not None else 0

        # ##: Win Count (using RPC).
        wc_rpc_response = db_client.rpc("get_team_win_count", rpc_params).execute()
        win_count = wc_rpc_response.data if wc_rpc_response.data is not None else 0

        # ##: Loss Count (using RPC).
        lc_rpc_response = db_client.rpc("get_team_loss_count", rpc_params).execute()
        loss_count = lc_rpc_response.data if lc_rpc_response.data is not None else 0

        # ##: Last Match Date (using RPC).
        last_match_rpc_response = db_client.rpc("get_team_last_match_date", rpc_params).execute()
        last_match_at = last_match_rpc_response.data if last_match_rpc_response.data is not None else None

    return {
        "matches_played": match_count,
        "wins": win_count,
        "losses": loss_count,
        "last_match_at": last_match_at,
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
        team = get_team_by_id(team_id)
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
