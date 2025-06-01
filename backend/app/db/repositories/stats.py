# -*- coding: utf-8 -*-
"""
CRUD operations for the Stats table.
"""

from typing import Any, Dict, Optional

from loguru import logger

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
        rpc_params = {"p_player_id": player_id}
        response = db_client.rpc("get_player_comprehensive_stats", rpc_params).execute()

    if response.data:
        return response.data
    return {
        "matches_played": 0,
        "wins": 0,
        "losses": 0,
        "last_match_at": None,
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
        response = db_client.rpc("get_team_comprehensive_stats", rpc_params).execute()

    if response.data:
        return response.data
    return {
        "matches_played": 0,
        "wins": 0,
        "losses": 0,
        "last_match_at": None,
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
        with transaction() as db_client:
            rpc_params = {"p_player_id": player_id}
            response = db_client.rpc("get_player_full_stats", rpc_params).execute()

        if response.data:
            return response.data
        return None
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
        with transaction() as db_client:
            rpc_params = {"p_team_id": team_id}
            response = db_client.rpc("get_team_full_stats", rpc_params).execute()

        if response.data:
            return response.data
        return None
    except Exception as e:
        logger.error("Failed to get team stats for ID %d: %s", team_id, e)
        return None
