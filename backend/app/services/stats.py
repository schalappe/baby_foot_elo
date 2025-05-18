# -*- coding: utf-8 -*-


from typing import Any, Dict, List

from loguru import logger

from app.db.repositories.elo_history import get_player_elo_history
from app.db.repositories.matches import get_matches_by_team
from app.exceptions.teams import TeamNotFoundError, TeamOperationError
from app.models.elo_history import EloHistoryResponse
from app.services.players import get_player_by_id
from app.services.teams import get_team_by_id, get_team_elo_history


def get_elo_history_by_id(player_id: int, limit: int = 20, offset: int = 0, **filters) -> List[EloHistoryResponse]:
    """
    Retrieve ELO history for a specific player.

    Parameters
    ----------
    player_id : int
        The ID of the player.
    limit : int, optional
        Maximum number of history records to return (default: 20).
    offset : int, optional
        Number of records to skip for pagination (default: 0).
    **filters
        Additional filters for the history (e.g., start_date, end_date, elo_type).

    Returns
    -------
    List[EloHistoryResponse]
        A list of ELO history records for the player.
    """
    try:
        history = get_player_elo_history(player_id, limit, offset, **filters)
        return [EloHistoryResponse(**record) for record in history] if history else []
    except Exception as e:
        logger.error(f"Error retrieving ELO history for player {player_id}: {e}")
        return []


def get_player_statistics(player_id: int) -> Dict[str, Any]:
    """
    Retrieve statistics for a specific player.

    Parameters
    ----------
    player_id : int
        The ID of the player.


    Returns
    -------
    Dict[str, Any]
        A dictionary containing the player's statistics.
    """
    try:
        player = get_player_by_id(player_id)

        # ##: Get ELO history for additional stats.
        elo_history: List[EloHistoryResponse] = get_elo_history_by_id(
            player_id, 1000, 0, start_date=None, end_date=None
        )

        # ##: Process ELO history if available.
        elo_changes = []
        elo_values = []

        if elo_history:
            elo_changes = [record.difference for record in elo_history if record.difference is not None]
            elo_values = [record.new_elo for record in elo_history if record.new_elo is not None]

        # ##: Calculate win rate.
        win_rate = player.wins / player.matches_played if player.matches_played > 0 else 0

        # ##: Process recent matches (last 30).
        recent_wins = 0
        recent_losses = 0
        recent_elo_changes = []

        if elo_history:
            for match in elo_history[:10]:
                if match.difference is not None:
                    recent_elo_changes.append(match.difference)
                    if match.difference > 0:
                        recent_wins += 1
                    elif match.difference < 0:
                        recent_losses += 1

        # ##: Calculate average ELO change.
        avg_elo_change = sum(elo_changes) / len(elo_changes) if elo_changes else 0
        highest_elo = max(elo_values) if elo_values else stats.get("global_elo", 1000)
        lowest_elo = min(elo_values) if elo_values else stats.get("global_elo", 1000)

        # ##: Calculate recent stats
        recent_matches_played = recent_wins + recent_losses
        recent_win_rate = (recent_wins / recent_matches_played * 100) if recent_matches_played > 0 else 0
        recent_avg_elo_change = sum(recent_elo_changes) / len(recent_elo_changes) if recent_elo_changes else 0

        # ##: Return comprehensive statistics.
        return {
            "player_id": player_id,
            "name": player.name,
            "global_elo": player.global_elo,
            "matches_played": player.matches_played,
            "wins": player.wins,
            "losses": player.losses,
            "win_rate": round(win_rate, 2),
            "elo_difference": elo_changes,
            "elo_values": elo_values,
            "average_elo_change": round(avg_elo_change, 2),
            "highest_elo": int(highest_elo),
            "lowest_elo": int(lowest_elo),
            "creation_date": player.created_at,
            # ##: Recent performance (last 10 matches).
            "recent": {
                "matches_played": recent_matches_played,
                "wins": recent_wins,
                "losses": recent_losses,
                "win_rate": round(recent_win_rate, 2),
                "average_elo_change": round(recent_avg_elo_change, 2),
                "elo_changes": recent_elo_changes,
            },
        }
    except Exception as e:
        logger.error(f"Error retrieving statistics for player {player_id}: {e}")
        raise


def get_team_statistics(team_id: int) -> Dict[str, Any]:
    """
    Retrieve statistics for a specific team.

    Parameters
    ----------
    team_id : int
        The ID of the team.


    Returns
    -------
    Dict[str, Any]
        A dictionary containing the team's statistics.
    """
    try:
        # ##: Get team details.
        team = get_team_by_id(team_id)

        # ##: Get team matches.
        matches = get_matches_by_team(team_id)

        # ##: Calculate statistics.
        total_matches = len(matches)
        wins = sum(1 for match in matches if match["winner_team_id"] == team_id)
        losses = total_matches - wins
        win_rate = (wins / total_matches * 100) if total_matches > 0 else 0

        # ##: Get ELO history.
        elo_differences = []
        elo_values = []

        for match in matches:
            elo_changes = get_team_elo_history(team, match["match_id"])
            if elo_changes:
                elo_differences.append(elo_changes["difference"])
                elo_values.append(elo_changes["new_elo"])

        # ##: Get recent matches
        recent_wins = 0
        recent_losses = 0
        recent_elo_changes = []

        if elo_differences:
            for record in elo_differences[:10]:
                recent_elo_changes.append(record)
                if record > 0:
                    recent_wins += 1
                elif record < 0:
                    recent_losses += 1

        # ##: Calculate average ELO change.
        avg_elo_change = sum(elo_differences) / len(elo_differences) if elo_differences else 0
        highest_elo = max(elo_values) if elo_values else team.global_elo
        lowest_elo = min(elo_values) if elo_values else team.global_elo

        # ##: Calculate recent stats
        recent_matches_played = recent_wins + recent_losses
        recent_win_rate = (recent_wins / recent_matches_played * 100) if recent_matches_played > 0 else 0
        recent_avg_elo_change = sum(recent_elo_changes) / len(recent_elo_changes) if recent_elo_changes else 0

        return {
            "team_id": team_id,
            "global_elo": team.global_elo,
            "total_matches": total_matches,
            "wins": wins,
            "losses": losses,
            "win_rate": round(win_rate, 2),
            "elo_difference": elo_differences,
            "elo_values": elo_values,
            "average_elo_change": round(avg_elo_change, 2),
            "highest_elo": highest_elo,
            "lowest_elo": lowest_elo,
            "created_at": team.created_at,
            "last_match_at": team.last_match_at,
            # ##: Recent performance (last 10 matches).
            "recent": {
                "matches_played": recent_matches_played,
                "wins": recent_wins,
                "losses": recent_losses,
                "win_rate": round(recent_win_rate, 2),
                "average_elo_change": round(recent_avg_elo_change, 2),
                "elo_changes": recent_elo_changes,
            },
        }

    except TeamNotFoundError:
        raise
    except Exception as exc:
        logger.error(f"Error retrieving statistics for team {team_id}: {exc}")
        raise TeamOperationError(f"Failed to retrieve statistics for team {team_id}") from exc
