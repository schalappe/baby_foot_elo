# -*- coding: utf-8 -*-
"""
CRUD operations for the Matches table.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from loguru import logger

from app.db.session import transaction, with_retry


@with_retry(max_retries=3, retry_delay=0.5)
def create_match_by_team_ids(
    winner_team_id: int,
    loser_team_id: int,
    played_at: Union[datetime, str],
    is_fanny: bool = False,
    notes: Optional[str] = None,
) -> Optional[int]:
    """
    Record a new match in the database.

    Parameters
    ----------
    winner_team_id : int
        ID of the winning team
    loser_team_id : int
        ID of the losing team
    played_at : Union[datetime, str]
        Date and time when the match was played
    is_fanny : bool, optional
        Whether the match was a fanny (10-0), by default False
    notes : Optional[str], optional
        Optional notes about the match, by default None

    Returns
    -------
    Optional[int]
        ID of the newly created match, or None on failure
    """
    try:
        # ##: Convert string to datetime if necessary.
        if isinstance(played_at, str):
            played_at = datetime.fromisoformat(played_at)

        # ##: Validate teams are different.
        if winner_team_id == loser_team_id:
            logger.error("Winner and loser team IDs cannot be the same")
            return None

        with transaction() as db_client:
            match_data = {
                "winner_team_id": winner_team_id,
                "loser_team_id": loser_team_id,
                "is_fanny": is_fanny,
                "played_at": played_at.isoformat() if isinstance(played_at, datetime) else played_at,
            }
            if notes is not None:
                match_data["notes"] = notes

            response = db_client.table("matches").insert(match_data).execute()

            if response.data and len(response.data) > 0:
                new_match_id = response.data[0].get("match_id")
                if new_match_id is not None:
                    logger.info(f"Match created successfully with ID: {new_match_id}")
                    return new_match_id

            logger.warning("Match creation did not return an ID or failed.")
            return None
    except Exception as exc:
        logger.error(f"Failed to create match: {exc}")
        return None


@with_retry(max_retries=3, retry_delay=0.5)
def get_match_by_id(match_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a match by ID.

    Parameters
    ----------
    match_id : int
        ID of the match to retrieve

    Returns
    -------
    Optional[Dict[str, Any]]
        Match data as a dictionary, or None if not found
    """
    with transaction() as db_client:
        response = (
            db_client.table("matches")
            .select("match_id, winner_team_id, loser_team_id, is_fanny, played_at, notes")
            .eq("match_id", match_id)
            .maybe_single()
            .execute()
        )
        if response and response.data:
            if response.data.get("played_at"):
                response.data["played_at"] = datetime.fromisoformat(response.data["played_at"])
            return response.data
    return None


@with_retry(max_retries=3, retry_delay=0.5)
def get_matches_by_team_id(
    team_id: int,
    limit: int = 100,
    offset: int = 0,
    is_fanny: bool = False,
    start_date: Optional[Union[datetime, str]] = None,
    end_date: Optional[Union[datetime, str]] = None,
) -> List[Dict[str, Any]]:
    """
    Get all matches involving a specific team.

    Parameters
    ----------
    team_id : int
        ID of the team
    limit : int, optional
        Maximum number of matches to return (default: 100).
    offset : int, optional
        Number of matches to skip for pagination (default: 0).
    is_fanny : bool, optional
        Whether to filter matches by fanny (10-0), by default False
    start_date : Optional[Union[datetime, str]], optional
        Start date to filter matches (inclusive), by default None
    end_date : Optional[Union[datetime, str]], optional
        End date to filter matches (inclusive), by default None

    Returns
    -------
    List[Dict[str, Any]]
        List of match dictionaries
    """
    try:
        # ##: Convert string dates to datetime objects.
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date)
        if end_date is not None:
            end_date = datetime.combine(end_date, datetime.max.time())

        with transaction() as db_client:
            query = (
                db_client.table("teams_elo_history")
                .select(
                    "old_elo, new_elo, difference, "
                    "match:matches!inner(match_id, winner_team_id, loser_team_id, is_fanny, played_at, notes)"
                )
                .eq("team_id", team_id)
            )

            if start_date is not None:
                query = query.gte("matches.played_at", start_date.isoformat())
            if end_date is not None:
                query = query.lte("matches.played_at", end_date.isoformat())
            if is_fanny:
                query = query.eq("matches.is_fanny", True)

            response = (
                query.order("played_at", desc=True, foreign_table="matches").limit(limit).offset(offset).execute()
            )

            matches_data = []
            if response.data:
                for row_item in response.data:
                    match_info = row_item.get("match")
                    if match_info:
                        played_at_val = match_info.get("played_at")
                        matches_data.append(
                            {
                                "match_id": match_info["match_id"],
                                "winner_team_id": match_info["winner_team_id"],
                                "loser_team_id": match_info["loser_team_id"],
                                "is_fanny": match_info["is_fanny"],
                                "played_at": datetime.fromisoformat(played_at_val) if played_at_val else None,
                                "notes": match_info["notes"],
                                "won": match_info["winner_team_id"] == team_id,
                                "elo_changes": {
                                    "old_elo": row_item["old_elo"],
                                    "new_elo": row_item["new_elo"],
                                    "elo_change": row_item["difference"],
                                },
                            }
                        )
            return matches_data
    except Exception as exc:
        logger.error(f"Failed to get matches for team ID {team_id}: {exc}")
        return []


@with_retry(max_retries=3, retry_delay=0.5)
def get_matches_by_player_id(
    player_id: int,
    limit: int = 100,
    offset: int = 0,
    is_fanny: bool = False,
    start_date: Optional[Union[datetime, str]] = None,
    end_date: Optional[Union[datetime, str]] = None,
) -> List[Dict[str, Any]]:
    """
    Get all matches involving a specific player with optional filtering and pagination.

    Parameters
    ----------
    player_id : int
        ID of the player
    limit : int, optional
        Maximum number of matches to return, by default 100
    offset : int, optional
        Number of matches to skip, by default 0
    is_fanny : bool, optional
        Whether to filter matches by fanny (10-0), by default False
    start_date : Optional[Union[datetime, str]], optional
        Start date to filter matches (inclusive), by default None
    end_date : Optional[Union[datetime, str]], optional
        End date to filter matches (inclusive), by default None

    Returns
    -------
    List[Dict[str, Any]]
        List of match dictionaries including match details and player's ELO change
    """
    try:
        # ##: Convert string dates to datetime objects.
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date)
        if end_date is not None:
            end_date = datetime.combine(end_date, datetime.max.time())

        with transaction() as db_client:
            query = (
                db_client.table("players_elo_history")
                .select(
                    "team_id, old_elo, new_elo, difference, "
                    "match:matches!inner("
                    "    match_id, winner_team_id, loser_team_id, is_fanny, played_at, notes,"
                    "    winner_team:teams!winner_team_id(name),"
                    "    loser_team:teams!loser_team_id(name)"
                    ")"
                )
                .eq("player_id", player_id)
            )

            if start_date is not None:
                query = query.gte("match.played_at", start_date.isoformat())
            if end_date is not None:
                query = query.lte("match.played_at", end_date.isoformat())
            if is_fanny:
                query = query.eq("match.is_fanny", True)

            response = query.order("played_at", desc=True, foreign_table="match").limit(limit).offset(offset).execute()

            matches_details = []
            if response.data:
                for row_item in response.data:
                    match_info = row_item.get("match")
                    if not match_info:
                        continue

                    team_id_for_player_in_match = row_item["team_id"]
                    winner_team_info = match_info.get("winner_team")
                    loser_team_info = match_info.get("loser_team")
                    played_at_val = match_info.get("played_at")

                    matches_details.append(
                        {
                            "match_id": match_info["match_id"],
                            "played_at": datetime.fromisoformat(played_at_val) if played_at_val else None,
                            "is_fanny": match_info["is_fanny"],
                            "notes": match_info["notes"],
                            "winner_team_id": match_info["winner_team_id"],
                            "winner_team_name": winner_team_info.get("name") if winner_team_info else "N/A",
                            "loser_team_id": match_info["loser_team_id"],
                            "loser_team_name": loser_team_info.get("name") if loser_team_info else "N/A",
                            "won": team_id_for_player_in_match == match_info["winner_team_id"],
                            "player_elo_change": {
                                "old_elo": row_item["old_elo"],
                                "new_elo": row_item["new_elo"],
                                "change": row_item["difference"],
                            },
                        }
                    )
            return matches_details
    except Exception as exc:
        logger.error(f"Failed to get matches for player {player_id}: {exc}")
        return []


@with_retry(max_retries=3, retry_delay=0.5)
def get_all_matches(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Get all matches with pagination support.

    Parameters
    ----------
    limit : int, optional
        Maximum number of matches to return, by default 100
    offset : int, optional
        Number of matches to skip, by default 0

    Returns
    -------
    List[Dict[str, Any]]
        List of match dictionaries
    """
    try:
        with transaction() as db_client:
            response = (
                db_client.table("matches")
                .select("match_id, winner_team_id, loser_team_id, is_fanny, played_at, notes")
                .order("played_at", desc=True)
                .limit(limit)
                .offset(offset)
                .execute()
            )
            matches_list = []
            if response.data:
                for row_data in response.data:
                    if row_data.get("played_at"):
                        row_data["played_at"] = datetime.fromisoformat(row_data["played_at"])
                    matches_list.append(row_data)
            return matches_list
    except Exception as exc:
        logger.error(f"Failed to get all matches: {exc}")
        return []


@with_retry(max_retries=3, retry_delay=0.5)
def delete_match_by_id(match_id: int) -> bool:
    """
    Delete a match from the database.

    Parameters
    ----------
    match_id : int
        ID of the match to delete

    Returns
    -------
    bool
        True if the deletion was successful, False otherwise
    """
    try:
        with transaction() as db_client:
            response = db_client.table("matches").delete(count="exact").eq("match_id", match_id).execute()
            if response.count is not None and response.count > 0:
                logger.info(f"Match with ID {match_id} deleted successfully.")
                return True
            logger.warning(f"Match with ID {match_id} not found or not deleted.")
            return False
    except Exception as exc:
        logger.error(f"Failed to delete match ID {match_id}: {exc}")
        return False
