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
from .player import PlayerBase, PlayerCreate, PlayerResponse, PlayerUpdate
from .team import TeamBase, TeamCreate, TeamResponse, TeamUpdate

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
]
