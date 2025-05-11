# -*- coding: utf-8 -*-
"""
Database module.

Re-exports core functionalities, CRUD operations, ELO functions, batch operations,
and query utilities from their respective submodules.
"""

from .builders import (
    DeleteQueryBuilder,
    InsertQueryBuilder,
    SelectQueryBuilder,
    UpdateQueryBuilder,
)
from .elo_history import (
    batch_record_elo_updates,
    record_elo_update,
)
from .matches import (
    create_match,
    get_all_matches_for_recalculation,
    get_match,
    get_matches_by_team,
)
from .players import (
    batch_insert_players,
    create_player,
    delete_player,
    get_all_players,
    get_player,
    search_players,
    update_player,
)
from .stats import get_leaderboard, get_player_elo_history, get_player_stats
from .teams import (
    batch_insert_teams,
    create_team,
    delete_team,
    get_all_teams,
    get_team,
)

__all__ = [
    # CRUD - Players
    "create_player",
    "get_player",
    "get_all_players",
    "update_player",
    "delete_player",
    "batch_insert_players",
    "search_players",
    # CRUD - Teams
    "create_team",
    "get_team",
    "get_all_teams",
    "delete_team",
    "batch_insert_teams",
    # CRUD - Matches
    "create_match",
    "get_match",
    "get_matches_by_team",
    "get_all_matches_for_recalculation",
    # ELO
    "record_elo_update",
    "batch_record_elo_updates",
    # Stats
    "get_player_stats",
    "get_leaderboard",
    "get_player_elo_history",
    # Query Builders
    "SelectQueryBuilder",
    "InsertQueryBuilder",
    "UpdateQueryBuilder",
    "DeleteQueryBuilder",
]
