# -*- coding: utf-8 -*-
"""
This module defines custom exceptions that are specific to team-related operations.
These exceptions provide more specific error information than the built-in exceptions.
"""

from fastapi import status
from fastapi.exceptions import HTTPException


class TeamException(HTTPException):
    """
    Base exception for team-related errors.

    This serves as the base class for all team-related exceptions.
    """

    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class TeamNotFoundError(TeamException):
    """Raised when a team with the specified ID is not found."""

    def __init__(self, identifier: str):
        detail = f"Team not found: {identifier}"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class TeamAlreadyExistsError(TeamException):
    """Raised when attempting to create a team that already exists."""

    def __init__(self, detail: str = "A team with these players already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class InvalidTeamDataError(TeamException):
    """Raised when invalid team data is provided."""

    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)


class TeamOperationError(TeamException):
    """Raised when an operation on a team fails."""

    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Team operation failed: {detail}")
