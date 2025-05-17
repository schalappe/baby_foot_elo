# -*- coding: utf-8 -*-
"""
This module defines custom exceptions that are specific to player-related operations.
These exceptions provide more specific error information than the built-in exceptions.
"""

from fastapi import status
from fastapi.exceptions import HTTPException


class PlayerException(HTTPException):
    """
    Base exception for player-related errors.
    
    This serves as the base class for all player-related exceptions.
    """
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class PlayerNotFoundError(PlayerException):
    """Raised when a player with the specified ID or name is not found."""
    def __init__(self, identifier: str):
        detail = f"Player not found: {identifier}"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class PlayerAlreadyExistsError(PlayerException):
    """Raised when attempting to create a player that already exists."""
    def __init__(self, name: str):
        detail = f"A player with the name '{name}' already exists"
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class InvalidPlayerDataError(PlayerException):
    """Raised when invalid player data is provided."""
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)


class PlayerOperationError(PlayerException):
    """Raised when an operation on a player fails."""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Player operation failed: {detail}"
        )
