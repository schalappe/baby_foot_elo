# -*- coding: utf-8 -*-
"""
Pydantic models for the Baby Foot Elo backend.
"""

from .elo_history import (
    EloHistoryBase,
    EloHistoryCreate,
    EloHistoryResponse,
    EloHistoryUpdate,
)
from .match import MatchBase, MatchCreate, MatchResponse, MatchUpdate
from .periodic_ranking import (
    PeriodicRankingBase,
    PeriodicRankingCreate,
    PeriodicRankingResponse,
    PeriodicRankingUpdate,
)
from .player import PlayerBase, PlayerCreate, PlayerResponse, PlayerUpdate
from .team import TeamBase, TeamCreate, TeamResponse, TeamUpdate
from .team_periodic_ranking import (
    TeamPeriodicRankingBase,
    TeamPeriodicRankingCreate,
    TeamPeriodicRankingResponse,
    TeamPeriodicRankingUpdate,
)

__all__ = [
    # Player Models
    "PlayerBase",
    "PlayerCreate",
    "PlayerUpdate",
    "PlayerResponse",
    # Team Models
    "TeamBase",
    "TeamCreate",
    "TeamUpdate",
    "TeamResponse",
    # Match Models
    "MatchBase",
    "MatchCreate",
    "MatchUpdate",
    "MatchResponse",
    # ELO History Models
    "EloHistoryBase",
    "EloHistoryCreate",
    "EloHistoryUpdate",
    "EloHistoryResponse",
    # Periodic Ranking Models (Player)
    "PeriodicRankingBase",
    "PeriodicRankingCreate",
    "PeriodicRankingUpdate",
    "PeriodicRankingResponse",
    # Periodic Ranking Models (Team)
    "TeamPeriodicRankingBase",
    "TeamPeriodicRankingCreate",
    "TeamPeriodicRankingUpdate",
    "TeamPeriodicRankingResponse",
]
