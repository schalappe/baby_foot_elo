# -*- coding: utf-8 -*-
"""
This module defines application-specific exceptions that are raised by the matches service.
These exceptions are caught by FastAPI's exception handlers and converted to appropriate
HTTP responses.
"""

from fastapi import status
from fastapi.exceptions import HTTPException


class MatchException(HTTPException):
    """Base exception for match-related errors."""

    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class MatchNotFoundError(MatchException):
    """Raised when a match with the given ID is not found."""

    def __init__(self, identifier: str):
        detail = f"Match not found: {identifier}"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class InvalidMatchTeamsError(MatchException):
    """Raised when a match has invalid team configuration."""

    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class MatchCreationError(MatchException):
    """Raised when there's an error creating a match."""

    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


class MatchDeletionError(MatchException):
    """Raised when there's an error deleting a match."""

    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


class MatchUpdateError(MatchException):
    """Raised when there's an error updating a match."""

    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)
