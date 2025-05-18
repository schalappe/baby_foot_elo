# -*- coding: utf-8 -*-
"""
This module provides a collection of repositories for database operations.
"""

from app.db.repositories.elo_history import (
    batch_record_elo_updates,
    get_elo_history_by_match,
    get_elo_history_by_player_match,
    get_player_elo_history,
    record_elo_update,
)
from app.db.repositories.matches import (
    create_match,
    get_fanny_matches,
    get_match,
    get_matches_by_player,
    get_matches_by_team,
)
from app.db.repositories.players import (
    batch_insert_players,
    create_player,
    delete_player,
    get_all_players,
    get_player,
    search_players,
    update_player,
)
from app.db.repositories.stats import get_player_stats, get_team_stats
from app.db.repositories.teams import (
    batch_insert_teams,
    create_team,
    delete_team,
    get_all_teams,
    get_team,
    get_teams_by_player,
)

__all__ = [
    # ##: Players.
    "create_player",
    "get_player",
    "get_all_players",
    "update_player",
    "delete_player",
    "batch_insert_players",
    "search_players",
    # ##: Teams.
    "create_team",
    "get_team",
    "get_all_teams",
    "delete_team",
    "batch_insert_teams",
    "get_teams_by_player",
    # ##: Matches.
    "create_match",
    "get_match",
    "get_matches_by_team",
    "get_fanny_matches",
    "get_matches_by_player",
    # ##: ELO.
    "record_elo_update",
    "batch_record_elo_updates",
    "get_player_elo_history",
    "get_elo_history_by_match",
    "get_elo_history_by_player_match",
    # ##: Stats.
    "get_player_stats",
    "get_team_stats",
]
