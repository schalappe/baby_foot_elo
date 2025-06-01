# -*- coding: utf-8 -*-
"""
Operations related to the Teams table using Supabase client.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from loguru import logger

from app.db.session.retry import with_retry
from app.db.session.transaction import transaction


@with_retry(max_retries=3, retry_delay=0.5)
def create_team_by_player_ids(
    player1_id: int,
    player2_id: int,
    global_elo: int = 1000,
    last_match_at: Optional[Union[str, datetime]] = None,
) -> Optional[int]:
    """
    Create a new team in the database.

    Parameters
    ----------
    player1_id : int
        ID of the first player.
    player2_id : int
        ID of the second player.
    global_elo : int, optional
        Initial global ELO rating, by default 1000.
    last_match_at : Optional[Union[str, datetime]], optional
        Timestamp of the last match, by default None.

    Returns
    -------
    Optional[int]
        ID of the newly created team, or the existing team ID if a duplicate is found.
    """
    # ##: Ensure player IDs are ordered to handle (p1, p2) and (p2, p1) as the same team.
    p1, p2 = sorted((player1_id, player2_id))

    try:
        with transaction() as db_client:
            # ##: Check if team with same players exists (order-insensitive).
            existing_team_response = (
                db_client.table("teams")
                .select("team_id")
                .eq("player1_id", p1)
                .eq("player2_id", p2)
                .maybe_single()
                .execute()
            )

            if existing_team_response:
                existing_team_id = existing_team_response.data.get("team_id")
                logger.warning(
                    f"Attempted to create duplicate team for players {player1_id} ({p1}) and {player2_id} ({p2}). "
                    f"Returning existing team ID: {existing_team_id}"
                )
                return existing_team_id

            team_data: Dict[str, Any] = {
                "player1_id": p1,
                "player2_id": p2,
                "global_elo": global_elo,
            }
            if last_match_at is not None:
                team_data["last_match_at"] = (
                    datetime.fromisoformat(last_match_at).isoformat()
                    if isinstance(last_match_at, str)
                    else last_match_at.isoformat() if isinstance(last_match_at, datetime) else None
                )
                if team_data["last_match_at"] is None and last_match_at is not None:
                    logger.warning(f"Could not parse last_match_at: {last_match_at}")

            insert_response = db_client.table("teams").insert(team_data, returning="representation").execute()

            if insert_response.data and len(insert_response.data) > 0:
                new_team_id = insert_response.data[0].get("team_id")
                if new_team_id is not None:
                    logger.info(f"Created team with ID: {new_team_id} for players {p1}, {p2}")
                    return new_team_id

            logger.error(f"Failed to create team or retrieve its ID. Response: {insert_response}")
            return None
    except Exception as exc:
        logger.error(f"Failed to create team for players {p1}, {p2}: {exc}. Type: {type(exc)}")
        return None


@with_retry(max_retries=3, retry_delay=0.5)
def batch_insert_teams_by_player_ids(teams: List[Dict[str, Any]]) -> List[Optional[int]]:
    """
    Insert multiple teams in a single transaction.

    Parameters
    ----------
    teams : List[Dict[str, Any]]
        List of team dictionaries, each with 'player1_id', 'player2_id' keys.
        Optional: 'global_elo', 'last_match_at'.

    Returns
    -------
    List[Optional[int]]
        List of IDs for the newly created teams, or None for failures/duplicates not inserted.
    """
    team_ids: List[Optional[int]] = []
    teams_to_insert: List[Dict[str, Any]] = []

    if not teams:
        return []

    for team_data_orig in teams:
        p1_id = team_data_orig["player1_id"]
        p2_id = team_data_orig["player2_id"]
        p1, p2 = sorted((p1_id, p2_id))

        current_team_data: Dict[str, Any] = {
            "player1_id": p1,
            "player2_id": p2,
            "global_elo": team_data_orig.get("global_elo", 1000),
        }
        if "last_match_at" in team_data_orig and team_data_orig["last_match_at"] is not None:
            last_match_at = team_data_orig["last_match_at"]
            current_team_data["last_match_at"] = (
                datetime.fromisoformat(last_match_at).isoformat()
                if isinstance(last_match_at, str)
                else last_match_at.isoformat() if isinstance(last_match_at, datetime) else None
            )
        teams_to_insert.append(current_team_data)

    try:
        with transaction() as db_client:
            response = db_client.table("teams").insert(teams_to_insert, returning="representation").execute()

        if response.data:
            inserted_map = {(d["player1_id"], d["player2_id"]): d["team_id"] for d in response.data}
            for team_spec in teams_to_insert:
                team_ids.append(inserted_map.get((team_spec["player1_id"], team_spec["player2_id"])))
        else:
            team_ids = [None] * len(teams_to_insert)
            logger.warning(f"Batch insert of teams returned no data or failed. Response: {response}")

        while len(team_ids) < len(teams):
            team_ids.append(None)

        return team_ids
    except Exception as exc:
        logger.error(f"Error during batch insert of teams: {exc}")
        return [None] * len(teams)


@with_retry(max_retries=3, retry_delay=0.5)
def get_all_teams(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Get all teams from the database.

    Parameters
    ----------
    limit : int, optional
        Maximum number of teams to return, by default 100.
    offset : int, optional
        Number of teams to skip for pagination, by default 0.

    Returns
    -------
    List[Dict[str, Any]]
        List of team dictionaries.
    """
    try:
        with transaction() as db_client:
            response = db_client.rpc("get_all_teams_with_stats", {"p_skip": offset, "p_limit": limit}).execute()

        if response.data:
            return response.data
        return []
    except Exception as exc:
        logger.error(f"Failed to get all teams: {exc}")
        return []


@with_retry(max_retries=3, retry_delay=0.5)
def get_team_by_id(team_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a team by ID.

    Parameters
    ----------
    team_id : int
        ID of the team to retrieve.

    Returns
    -------
    Optional[Dict[str, Any]]
        Team data as a dictionary, or None if not found.
    """
    try:
        with transaction() as db_client:
            response = (
                db_client.table("teams")
                .select("team_id, player1_id, player2_id, global_elo, created_at, last_match_at")
                .eq("team_id", team_id)
                .maybe_single()
                .execute()
            )
        if response and response.data:
            return response.data
        return None
    except Exception as exc:
        logger.error(f"Failed to get team by ID {team_id}: {exc}")
        return None


@with_retry(max_retries=3, retry_delay=0.5)
def get_teams_by_player_id(player_id: int) -> List[Dict[str, Any]]:
    """
    Get all teams that a specific player is part of.

    Parameters
    ----------
    player_id : int
        ID of the player to find teams for.

    Returns
    -------
    List[Dict[str, Any]]
        List of team dictionaries, each containing team details.
    """
    try:
        with transaction() as db_client:
            response = (
                db_client.table("teams")
                .select("team_id, player1_id, player2_id, global_elo, created_at, last_match_at")
                .or_(f"player1_id.eq.{player_id},player2_id.eq.{player_id}")
                .order("last_match_at", desc=True, nulls_first=False)
                .execute()
            )
        return response.data if response.data else []
    except Exception as exc:
        logger.error(f"Failed to get teams for player ID {player_id}: {exc}")
        return []


@with_retry(max_retries=3, retry_delay=0.5)
def update_team_elo(
    team_id: int,
    global_elo: Optional[int] = None,
    last_match_at: Optional[Union[str, datetime]] = None,
) -> bool:
    """
    Update a team's ELO ratings or last match timestamp.

    Parameters
    ----------
    team_id : int
        ID of the team to update.
    global_elo : Optional[int], optional
        New global ELO value.
    last_match_at : Optional[Union[str, datetime]], optional
        New last match timestamp.

    Returns
    -------
    bool
        True if update was successful, False otherwise.
    """
    update_fields: Dict[str, Any] = {}
    if global_elo is not None:
        update_fields["global_elo"] = global_elo
    if last_match_at is not None:
        update_fields["last_match_at"] = (
            datetime.fromisoformat(last_match_at).isoformat()
            if isinstance(last_match_at, str)
            else last_match_at.isoformat() if isinstance(last_match_at, datetime) else None
        )
        if update_fields["last_match_at"] is None:
            del update_fields["last_match_at"]

    if not update_fields:
        logger.warning(f"No fields to update for team ID {team_id}.")
        return False

    try:
        with transaction() as db_client:
            response = db_client.table("teams").update(update_fields).eq("team_id", team_id).execute()

        updated_successfully = bool(response.data and len(response.data) > 0) or getattr(response, "count", 0) > 0

        if updated_successfully:
            logger.info(f"Team ID {team_id} updated successfully.")
            return True

        logger.warning(f"Team ID {team_id} not found or no changes made. Response: {response}")
        return False
    except Exception as exc:
        logger.error(f"Failed to update team ID {team_id}: {exc}")
        return False


@with_retry(max_retries=3, retry_delay=0.5)
def batch_update_teams_elo(teams: List[Dict[str, Any]]) -> List[bool]:
    """
    Batch update teams in the database.

    Parameters
    ----------
    teams : List[Dict[str, Any]]
        A list of dictionaries, where each dictionary represents a team
        and contains 'team_id' and other fields to update (e.g., 'global_elo', 'last_match_at').

    Returns
    -------
    List[bool]
        A list of booleans indicating the success of each individual team update.
    """
    results: List[bool] = []
    if not teams:
        return results

    try:
        with transaction() as db_client:
            for team_data in teams:
                team_id = team_data.get("team_id")
                if not team_id:
                    logger.warning(f"Skipping team update due to missing team_id in data: {team_data}")
                    results.append(False)
                    continue

                update_fields: Dict[str, Any] = {}
                if "global_elo" in team_data:
                    update_fields["global_elo"] = team_data["global_elo"]
                if "last_match_at" in team_data and team_data["last_match_at"] is not None:
                    last_match_at = team_data["last_match_at"]
                    update_fields["last_match_at"] = (
                        datetime.fromisoformat(last_match_at).isoformat()
                        if isinstance(last_match_at, str)
                        else last_match_at.isoformat() if isinstance(last_match_at, datetime) else None
                    )
                    if update_fields["last_match_at"] is None:
                        del update_fields["last_match_at"]

                if not update_fields:
                    logger.info(
                        f"No valid fields to update for team ID {team_id}. Assuming success as no change needed."
                    )
                    results.append(True)
                    continue

                current_team_success = False
                try:
                    response = db_client.table("teams").update(update_fields).eq("team_id", team_id).execute()
                    if (response.data and len(response.data) > 0) or getattr(response, "count", 0) > 0:
                        logger.info(f"Team ID {team_id} updated successfully in batch.")
                        current_team_success = True
                    else:
                        logger.warning(
                            f"Team ID {team_id} not found or no changes made in batch. Response: {response}"
                        )
                except Exception as single_update_exc:
                    logger.error(f"Failed to update team ID {team_id} in batch: {single_update_exc}")

                results.append(current_team_success)

        if all(results):
            logger.info("Batch update of teams completed, all successful.")
        else:
            logger.warning("Batch update of teams completed with one or more failures.")
        return results

    except Exception as outer_exc:
        logger.error(f"Outer error during batch update of teams: {outer_exc}")
        while len(results) < len(teams):
            results.append(False)
        return results


@with_retry(max_retries=3, retry_delay=0.5)
def delete_team_by_id(team_id: int) -> bool:
    """
    Delete a team from the database.

    Parameters
    ----------
    team_id : int
        ID of the team to delete.

    Returns
    -------
    bool
        True if the deletion was successful, False otherwise.
    """
    try:
        with transaction() as db_client:
            response = db_client.table("teams").delete().eq("team_id", team_id).execute()

        deleted_successfully = bool(response.data and len(response.data) > 0) or getattr(response, "count", 0) > 0

        if deleted_successfully:
            logger.info(f"Team ID {team_id} deleted successfully.")
            return True

        logger.warning(f"Team ID {team_id} not found for deletion. Response: {response}")
        return False
    except Exception as exc:
        logger.error(f"Failed to delete team ID {team_id}: {exc}")
        return False
