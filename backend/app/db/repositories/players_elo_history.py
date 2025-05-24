# -*- coding: utf-8 -*-
"""
Operations related to ELO history.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from loguru import logger

from app.db.builders import InsertQueryBuilder, SelectQueryBuilder
from app.db.session import transaction, with_retry


@with_retry(max_retries=3, retry_delay=0.5)
def record_elo_update(
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
        with transaction() as db:
            query, params = (
                InsertQueryBuilder("Players_ELO_History")
                .set(
                    player_id=player_id,
                    match_id=match_id,
                    old_elo=old_elo,
                    new_elo=new_elo,
                    difference=difference,
                    date=date,
                )
                .build()
            )

            result = db.fetchone(f"{query} RETURNING history_id", params)

            if result and result[0]:
                return result[0]
            return None
    except Exception as exc:
        logger.error(f"Failed to record ELO update: {exc}")
        return None


@with_retry(max_retries=3, retry_delay=0.5)
def batch_record_elo_updates(elo_updates: List[Dict[str, Any]]) -> List[Optional[int]]:
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

    history_ids = []
    try:
        with transaction() as db:
            for update in elo_updates:
                # ##: Get date from update or use current time.
                date = update.get("date", datetime.now())
                difference = update["new_elo"] - update["old_elo"]

                query, params = (
                    InsertQueryBuilder("Players_ELO_History")
                    .set(
                        player_id=update["player_id"],
                        match_id=update["match_id"],
                        old_elo=update["old_elo"],
                        new_elo=update["new_elo"],
                        difference=difference,
                        date=date,
                    )
                    .build()
                )

                result = db.fetchone(f"{query} RETURNING history_id", params)
                if result and result[0] is not None:
                    history_ids.append(result[0])

        return history_ids
    except Exception as exc:
        logger.error(f"Failed to batch record ELO updates: {exc}")
        return []


@with_retry(max_retries=3, retry_delay=0.5)
def get_player_elo_history(
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
        builder = SelectQueryBuilder("Players_ELO_History").select("*").where("player_id = ?", player_id)

        if start_date:
            builder = builder.where("date >= ?", start_date)

        if end_date:
            builder = builder.where("date <= ?", end_date)

        results = builder.order_by_clause("date DESC").limit(limit).offset(offset).execute(fetch_all=True)

        if not results:
            return []

        history_records = []
        for record in results:
            history_records.append(
                {
                    "history_id": record[0],
                    "player_id": record[1],
                    "match_id": record[2],
                    "old_elo": record[3],
                    "new_elo": record[4],
                    "difference": record[5],
                    "date": record[6],
                }
            )

        return history_records
    except Exception as exc:
        logger.error(f"Failed to get ELO history for player ID {player_id}: {exc}")
        return []


@with_retry(max_retries=3, retry_delay=0.5)
def get_elo_history_by_match(match_id: int) -> List[Dict[str, Any]]:
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
        results = (
            SelectQueryBuilder("Players_ELO_History")
            .select("*")
            .where("match_id = ?", match_id)
            .execute(fetch_all=True)
        )

        if not results:
            return []

        history_records = []
        for record in results:
            history_records.append(
                {
                    "history_id": record[0],
                    "player_id": record[1],
                    "match_id": record[2],
                    "old_elo": record[3],
                    "new_elo": record[4],
                    "difference": record[5],
                    "date": record[6],
                }
            )
        return history_records
    except Exception as exc:
        logger.error(f"Failed to get ELO history for match {match_id}: {exc}")
        return []


@with_retry(max_retries=3, retry_delay=0.5)
def get_elo_history_by_player_match(player_id: int, match_id: int) -> Optional[Dict[str, Any]]:

    try:
        builder = (
            SelectQueryBuilder("Players_ELO_History")
            .select("*")
            .where("player_id = ?", player_id)
            .where("match_id = ?", match_id)
        )
        results = builder.execute(fetch_all=True)

        if not results:
            return None

        history_record = {
            "history_id": results[0][0],
            "player_id": results[0][1],
            "match_id": results[0][2],
            "old_elo": results[0][3],
            "new_elo": results[0][4],
            "difference": results[0][5],
            "date": results[0][6],
        }
        return history_record
    except Exception as exc:
        logger.error(f"Failed to get ELO history for player {player_id} and match {match_id}: {exc}")
        return None
