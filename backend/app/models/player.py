# -*- coding: utf-8 -*-
"""
Pydantic models for player-related operations in the Baby Foot Elo backend.

This module defines data models for creating, updating, and returning player information.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PlayerCreate(BaseModel):
    """
    Data model for creating a new player.

    Attributes
    ----------
    name : str
        The name of the player.
    initial_elo : int, optional
        The initial ELO rating for the player (default is 1000).
    """

    name: str
    initial_elo: int = 1000


class PlayerUpdate(BaseModel):
    """
    Data model for updating an existing player's information.

    Attributes
    ----------
    name : str, optional
        The updated name of the player.
    initial_elo : int, optional
        The updated initial ELO rating for the player.
    """

    name: Optional[str] = None
    initial_elo: Optional[int] = None


class PlayerResponse(BaseModel):
    """
    Data model for returning player information in API responses.

    Attributes
    ----------
    id : int
        Unique identifier for the player.
    name : str
        The name of the player.
    elo : int
        The current ELO rating of the player.
    creation_date : datetime
        The date and time when the player was created.
    matches_played : int, optional
        The number of matches the player has played (default is 0).
    wins : int, optional
        The number of matches the player has won (default is 0).
    losses : int, optional
        The number of matches the player has lost (default is 0).
    """

    id: int
    name: str
    elo: int
    creation_date: datetime
    matches_played: int = 0
    wins: int = 0
    losses: int = 0

    class Config:
        from_attributes = True
