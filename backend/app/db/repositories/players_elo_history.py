# -*- coding: utf-8 -*-
"""
Operations related to ELO history.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from loguru import logger

from app.db.session import transaction, with_retry


@with_retry(max_retries=3, retry_delay=0.5)
def record_player_elo_update(
    player_id: int,
    match_id: int,
    old_elo: int,
    new_elo: int,
    date: Optional[datetime] = None,
) -> Optional[int]:
    """
    Record an ELO score update after a match.

    Parameters
    ----------
    player_id : int
        ID of the player
    match_id : int
        ID of the match
    old_elo : int
        Previous ELO score before the match
    new_elo : int
        New ELO score after the match
    date : Optional[datetime], optional
        Date of the update, by default current time

    Returns
    -------
    Optional[int]
        ID of the newly created ELO history record, or None on failure
    """
    try:
        if date is None:
            date = datetime.now()

        difference = new_elo - old_elo
        elo_data = {
            "player_id": player_id,
            "match_id": match_id,
            "old_elo": old_elo,
            "new_elo": new_elo,
            "difference": difference,
            "date": date.isoformat() if isinstance(date, datetime) else date,
        }
        with transaction() as db_client:
            response = db_client.table("players_elo_history").insert(elo_data).execute()
            if response.data and len(response.data) > 0:
                history_id = response.data[0].get("history_id")
                if history_id is not None:
                    logger.info(f"ELO update for player {player_id} recorded with ID: {history_id}")
                    return history_id
        logger.warning(f"ELO update recording for player {player_id} did not return an ID or failed.")
        return None
    except Exception as exc:
        logger.error(f"Failed to record ELO update: {exc}")
        return None


@with_retry(max_retries=3, retry_delay=0.5)
def batch_record_player_elo_updates(elo_updates: List[Dict[str, Any]]) -> List[Optional[int]]:
    """
    Record multiple ELO updates in a single transaction.

    Parameters
    ----------
    elo_updates : List[Dict[str, Any]]
        List of ELO update dictionaries, each with required keys:
        - 'player_id': int - ID of the player
        - 'match_id': int - ID of the match
        - 'old_elo': int - Previous ELO score
        - 'new_elo': int - New ELO score
        Optional keys:
        - 'date': datetime - Date of the update

    Returns
    -------
    List[Optional[int]]
        List of IDs for the newly created ELO history records, or None for failures
    """
    if not elo_updates:
        return []

    updates_to_insert = []
    for update in elo_updates:
        date = update.get("date", datetime.now())
        difference = update["new_elo"] - update["old_elo"]
        updates_to_insert.append(
            {
                "player_id": update["player_id"],
                "match_id": update["match_id"],
                "old_elo": update["old_elo"],
                "new_elo": update["new_elo"],
                "difference": difference,
                "date": date.isoformat() if isinstance(date, datetime) else date,
            }
        )

    if not updates_to_insert:
        return []

    try:
        with transaction() as db_client:
            response = db_client.table("players_elo_history").insert(updates_to_insert).execute()
            if response.data and len(response.data) > 0:
                history_ids = [item.get("history_id") for item in response.data if item.get("history_id") is not None]
                logger.info(f"Batch ELO updates recorded. IDs: {history_ids}")
                return history_ids
            logger.warning("Batch ELO update recording did not return IDs or failed.")
            return []
    except Exception as exc:
        logger.error(f"Failed to batch record ELO updates: {exc}")
        return []


@with_retry(max_retries=3, retry_delay=0.5)
def get_player_elo_history_by_id(
    player_id: int,
    limit: int = 100,
    offset: int = 0,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> List[Dict[str, Any]]:
    """
    Get the ELO history for a player with optional filtering.

    Parameters
    ----------
    player_id : int
        ID of the player
    limit : int, optional
        Maximum number of records to return, by default 100
    offset : int, optional
        Number of records to skip, by default 0
    start_date : Optional[datetime], optional
        Filter by start date, by default None
    end_date : Optional[datetime], optional
        Filter by end date, by default None

    Returns
    -------
    List[Dict[str, Any]]
        List of ELO history records
    """
    try:
        with transaction() as db_client:
            query = db_client.table("players_elo_history").select("*").eq("player_id", player_id)

            if start_date:
                query = query.gte("date", start_date.isoformat() if isinstance(start_date, datetime) else start_date)
            if end_date:
                query = query.lte("date", end_date.isoformat() if isinstance(end_date, datetime) else end_date)

            response = query.order("date", desc=True).limit(limit).offset(offset).execute()

            history_records = []
            if response.data:
                for record_data in response.data:
                    if record_data.get("date") and isinstance(record_data["date"], str):
                        record_data["date"] = datetime.fromisoformat(record_data["date"])
                    history_records.append(record_data)
            return history_records
    except Exception as exc:
        logger.error(f"Failed to get ELO history for player ID {player_id}: {exc}")
        return []


@with_retry(max_retries=3, retry_delay=0.5)
def get_player_elo_history_by_match_id(player_id: int, match_id: int) -> Optional[Dict[str, Any]]:
    """
    Get the ELO history for a specific player and match.

    Parameters
    ----------
    player_id : int
        ID of the player
    match_id : int
        ID of the match

    Returns
    -------
    Optional[Dict[str, Any]]
        ELO history record for the player and match, or None if not found
    """
    try:
        with transaction() as db_client:
            response = (
                db_client.table("players_elo_history")
                .select("*")
                .eq("player_id", player_id)
                .eq("match_id", match_id)
                .maybe_single()
                .execute()
            )
            if response and response.data:
                if response.data.get("date") and isinstance(response.data["date"], str):
                    response.data["date"] = datetime.fromisoformat(response.data["date"])
                return response.data
        return None
    except Exception as exc:
        logger.error(f"Failed to get ELO history for player {player_id} and match {match_id}: {exc}")
        return None


@with_retry(max_retries=3, retry_delay=0.5)
def get_players_elo_history_by_match_id(match_id: int) -> List[Dict[str, Any]]:
    """
    Get all ELO history records for a specific match.

    Parameters
    ----------
    match_id : int
        ID of the match

    Returns
    -------
    List[Dict[str, Any]]
        List of ELO history records for the match
    """
    try:
        with transaction() as db_client:
            response = (
                db_client.table("players_elo_history")
                .select("*")
                .eq("match_id", match_id)
                .order("date", desc=True)
                .execute()
            )
            history_records = []
            if response.data:
                for record_data in response.data:
                    if record_data.get("date") and isinstance(record_data["date"], str):
                        record_data["date"] = datetime.fromisoformat(record_data["date"])
                    history_records.append(record_data)
            return history_records
    except Exception as exc:
        logger.error(f"Failed to get ELO history for match {match_id}: {exc}")
        return []
