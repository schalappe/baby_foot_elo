# -*- coding: utf-8 -*-


from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from loguru import logger

from app.db.repositories.matches import get_matches_by_player_id, get_matches_by_team_id
from app.db.repositories.players_elo_history import get_player_elo_history_by_id
from app.db.repositories.teams_elo_history import get_team_elo_history_by_id
from app.exceptions.players import PlayerOperationError
from app.exceptions.teams import TeamNotFoundError, TeamOperationError
from app.models.match import MatchWithEloResponse
from app.models.player import PlayerResponse
from app.models.team import TeamResponse
from app.services.players import get_all_players_with_stats, get_player
from app.services.teams import get_all_teams_with_stats, get_team


def get_player_matches(player_id: int, limit: int = 10, offset: int = 0, **filters) -> List[MatchWithEloResponse]:
    """
    Retrieve a paginated list of matches for a specific player.

    Parameters
    ----------
    player_id : int
        The ID of the player.
    limit : int, optional
        Maximum number of matches to return (default: 10).
    offset : int, optional
        Number of matches to skip for pagination (default: 0).
    **filters
        Additional filters for the matches (e.g., start_date, end_date).

    Returns
    -------
    List[MatchWithEloResponse]
        A list of matches the player participated in.
    """
    try:
        matches = get_matches_by_player_id(player_id, limit, offset, **filters)
        response = [MatchWithEloResponse(**match) for match in matches]
        return response
    except Exception as e:
        logger.error(f"Error retrieving matches for player {player_id}: {e}")
        return []


def get_team_matches(team_id: int, limit: int = 100, offset: int = 0) -> List[MatchWithEloResponse]:
    """
    Retrieve a paginated list of matches for a specific team.

    Parameters
    ----------
    team_id : int
        The ID of the team.
    limit : int, optional
        Maximum number of matches to return (default: 100).
    offset : int, optional
        Number of matches to skip for pagination (default: 0).

    Returns
    -------
    List[MatchWithEloResponse]
        A list of matches the team participated in.
    """
    try:
        matches = get_matches_by_team_id(team_id, limit=limit, offset=offset)
        return [MatchWithEloResponse(**match) for match in matches]

    except Exception as exc:
        logger.error(f"Error retrieving matches for team {team_id}: {exc}")
        raise TeamOperationError(f"Failed to retrieve matches for team {team_id}") from exc


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
        player = get_player(player_id)

        # ##: Get ELO history for additional stats.
        elo_history = get_player_elo_history_by_id(player_id)

        # ##: Process ELO history if available.
        elo_changes = []
        elo_values = []

        if elo_history:
            elo_changes = [record["difference"] for record in elo_history if record["difference"] is not None]
            elo_values = [record["new_elo"] for record in elo_history if record["new_elo"] is not None]

        # ##: Calculate win rate.
        win_rate = player.wins / player.matches_played * 100 if player.matches_played > 0 else 0

        # ##: Process recent matches (last 30).
        recent_wins = 0
        recent_losses = 0
        recent_elo_changes = []

        if elo_history:
            for match in elo_history[:10]:
                if match["difference"] is not None:
                    recent_elo_changes.append(match["difference"])
                    if match["difference"] > 0:
                        recent_wins += 1
                    elif match["difference"] < 0:
                        recent_losses += 1

        # ##: Calculate average ELO change.
        avg_elo_change = sum(elo_changes) / len(elo_changes) if elo_changes else 0
        highest_elo = max(elo_values) if elo_values else player.global_elo
        lowest_elo = min(elo_values) if elo_values else player.global_elo

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
        team = get_team(team_id)

        elo_history = get_team_elo_history_by_id(team_id)

        # ##: Get ELO history.
        elo_changes = []
        elo_values = []

        if elo_history:
            elo_changes = [record["difference"] for record in elo_history if record["difference"] is not None]
            elo_values = [record["new_elo"] for record in elo_history if record["new_elo"] is not None]

        # ##: Get recent matches
        recent_wins = 0
        recent_losses = 0
        recent_elo_changes = []

        if elo_changes:
            for record in elo_changes[:10]:
                recent_elo_changes.append(record)
                if record > 0:
                    recent_wins += 1
                elif record < 0:
                    recent_losses += 1

        # ##: Calculate average ELO change.
        avg_elo_change = sum(elo_changes) / len(elo_changes) if elo_changes else 0
        highest_elo = max(elo_values) if elo_values else team.global_elo
        lowest_elo = min(elo_values) if elo_values else team.global_elo

        # ##: Calculate recent stats
        recent_matches_played = recent_wins + recent_losses
        recent_win_rate = (recent_wins / recent_matches_played * 100) if recent_matches_played > 0 else 0
        recent_avg_elo_change = sum(recent_elo_changes) / len(recent_elo_changes) if recent_elo_changes else 0

        return {
            "team_id": team_id,
            "global_elo": team.global_elo,
            "total_matches": team.matches_played,
            "wins": team.wins,
            "losses": team.losses,
            "win_rate": round(team.win_rate, 2),
            "elo_difference": elo_changes,
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
            # ##: Player information.
            "player1_id": team.player1_id,
            "player2_id": team.player2_id,
            "player1": team.player1,
            "player2": team.player2,
        }

    except TeamNotFoundError:
        raise
    except Exception as exc:
        logger.error(f"Error retrieving statistics for team {team_id}: {exc}")
        raise TeamOperationError(f"Failed to retrieve statistics for team {team_id}") from exc


def get_active_team_rankings(limit: int = 100, days_since_last_match: Optional[int] = None) -> List[TeamResponse]:
    """
    Retrieve team rankings based on ELO ratings.

    Parameters
    ----------
    limit : int, optional
        Maximum number of teams to return, by default 100.
    days_since_last_match : Optional[int], optional
        Only include teams whose last match was at least this many days ago, by default None.

    Returns
    -------
    List[TeamResponse]
        A list of teams sorted by ELO in descending order, with rank information.

    Raises
    ------
    TeamOperationError
        If there's an error retrieving the rankings.
    """
    try:
        # ##: Get team rankings from repository.
        teams = get_all_teams_with_stats(limit=limit)

        # ##: Apply additional filters.
        if days_since_last_match is not None:
            filtered_teams = []

            last_match_at_threshold = datetime.now(timezone.utc) - timedelta(days=days_since_last_match)
            for team in teams:
                if team.last_match_at is None:
                    continue

                if team.last_match_at <= last_match_at_threshold:
                    continue
                filtered_teams.append(team)

            # ##: Re-sort after filtering.
            teams = sorted(filtered_teams, key=lambda x: x.global_elo, reverse=True)

        return teams

    except Exception as exc:
        logger.error(f"Error retrieving team rankings: {exc}")
        raise TeamOperationError("Failed to retrieve team rankings") from exc


def get_active_players_rankings(limit: int = 100, days_since_last_match: Optional[int] = None) -> List[PlayerResponse]:
    """
    Retrieve active player rankings based on ELO ratings.

    Parameters
    ----------
    limit : int, optional
        Maximum number of players to return, by default 100.
    days_since_last_match : Optional[int], optional
        Only include players whose last match was at least this many days ago, by default None.

    Returns
    -------
    List[PlayerResponse]
        A list of players sorted by ELO in descending order, with rank information.

    Raises
    ------
    PlayerOperationError
        If there's an error retrieving the rankings.
    """
    try:
        # ##: Get all players with stats.
        players = get_all_players_with_stats()

        # ##: Apply additional filters.
        if days_since_last_match is not None:
            filtered_players = []

            last_match_at_threshold = datetime.now(timezone.utc) - timedelta(days=days_since_last_match)
            for player in players:
                if player.matches_played == 0 or player.last_match_at <= last_match_at_threshold:
                    continue
                filtered_players.append(player)

            players = sorted(filtered_players, key=lambda x: x.global_elo, reverse=True)

        # ##: Apply limit.
        return players[:limit]

    except Exception as exc:
        logger.error(f"Error retrieving player rankings: {exc}")
        raise PlayerOperationError("Failed to retrieve player rankings") from exc
