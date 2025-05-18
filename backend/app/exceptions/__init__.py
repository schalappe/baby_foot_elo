# -*- coding: utf-8 -*-
"""
This module serves as the central place to import all custom exceptions used throughout the application.
"""

from app.exceptions.matches import (
    InvalidMatchTeamsError,
    MatchCreationError,
    MatchDeletionError,
    MatchException,
    MatchNotFoundError,
    MatchUpdateError,
)
from app.exceptions.players import (
    InvalidPlayerDataError,
    PlayerAlreadyExistsError,
    PlayerException,
    PlayerNotFoundError,
    PlayerOperationError,
)
from app.exceptions.teams import (
    InvalidTeamDataError,
    TeamAlreadyExistsError,
    TeamException,
    TeamNotFoundError,
    TeamOperationError,
)

__all__ = [
    # Player exceptions
    "PlayerException",
    "PlayerNotFoundError",
    "PlayerAlreadyExistsError",
    "InvalidPlayerDataError",
    "PlayerOperationError",
    # Team exceptions
    "TeamException",
    "TeamNotFoundError",
    "TeamAlreadyExistsError",
    "InvalidTeamDataError",
    "TeamOperationError",
    # Match exceptions
    "MatchException",
    "MatchNotFoundError",
    "InvalidMatchTeamsError",
    "MatchCreationError",
    "MatchDeletionError",
    "MatchUpdateError",
]
