# -*- coding: utf-8 -*-
"""
This module provides a collection of repositories for database operations.
"""

from app.db.repositories.elo_history import (
    batch_record_elo_updates,
    get_player_elo_history,
    record_elo_update,
)
from app.db.repositories.matches import (
    create_match,
    get_all_matches_for_recalculation,
    get_match,
    get_matches_by_team,
    get_fanny_matches,
    get_matches_by_player
)
from app.db.repositories.players import (
    batch_insert_players,
    create_player,
    delete_player,
    get_all_players,
    get_player,
    get_player_stats,
    search_players,
    update_player,
)
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
    "get_player_stats",
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
    "get_all_matches_for_recalculation",
    "get_fanny_matches",
    "get_matches_by_player",
    # ##: ELO.
    "record_elo_update",
    "batch_record_elo_updates",
    "get_player_elo_history",
]
