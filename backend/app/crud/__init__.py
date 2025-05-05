# -*- coding: utf-8 -*-
"""
Database module.

Re-exports core functionalities, CRUD operations, ELO functions, batch operations,
and query utilities from their respective submodules.
"""

from .batch_operations import (
    batch_insert_players,
    batch_insert_teams,
    batch_record_elo_updates,
)
from .builders import QueryBuilder
from .elo_history import get_current_elo, get_player_elo_history, record_elo_update
from .matches import create_match, get_match, get_matches_by_team
from .players import (
    create_player,
    delete_player,
    get_all_players,
    get_player,
    update_player,
)
from .queries import get_leaderboard, get_player_stats, search_players
from .teams import create_team, delete_team, get_all_teams, get_team

__all__ = [
    # CRUD - Players
    "create_player",
    "get_player",
    "get_all_players",
    "update_player",
    "delete_player",
    # CRUD - Teams
    "create_team",
    "get_team",
    "get_all_teams",
    "delete_team",
    # CRUD - Matches
    "create_match",
    "get_match",
    "get_matches_by_team",
    # ELO
    "record_elo_update",
    "get_player_elo_history",
    "get_current_elo",
    # Batch
    "batch_insert_players",
    "batch_insert_teams",
    "batch_record_elo_updates",
    # Query
    "QueryBuilder",
    "search_players",
    "get_player_stats",
    "get_leaderboard",
]
