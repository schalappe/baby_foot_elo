# -*- coding: utf-8 -*-
"""
Pydantic models for player-related operations in the Baby Foot Elo backend.

This module defines data models for creating, updating, and returning player information.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PlayerBase(BaseModel):
    """
    Base model for player properties.

    Attributes
    ----------
    name : str
        The name of the player.
    global_elo : int
        The global ELO rating of the player.
    """

    name: str = Field(..., min_length=1, max_length=100, description="Player's name")
    global_elo: int = Field(default=1000, ge=0, description="Initial global ELO rating for the player")


class PlayerCreate(PlayerBase):
    """
    Data model for creating a new player.

    Attributes
    ----------
    name : str
        The name of the player (inherited from PlayerBase).
    global_elo : int, optional
        The initial global ELO rating for the player (default is 1000).
    """


class PlayerUpdate(BaseModel):
    """
    Data model for updating an existing player's information.

    Attributes
    ----------
    name : str, optional
        The updated name of the player.
    global_elo : int, optional
        The updated global ELO rating for the player.
    """

    name: Optional[str] = Field(default=None, min_length=1, max_length=100, description="Player's updated name")
    global_elo: Optional[int] = Field(default=None, ge=0, description="Updated global ELO rating for the player")


class PlayerResponse(PlayerBase):
    """
    Data model for returning player information in API responses.

    Attributes
    ----------
    player_id : int
        Unique identifier for the player.
    name : str
        The name of the player (inherited from PlayerBase).
    global_elo : int
        The current global ELO rating of the player.
    creation_date : datetime
        The date and time when the player was created.
    last_match_at : Optional[datetime]
        The date and time of the player's last match.
    matches_played : int, optional
        The number of matches the player has played (default is 0).
    wins : int, optional
        The number of matches the player has won (default is 0).
    losses : int, optional
        The number of matches the player has lost (default is 0).
    """

    player_id: int = Field(..., gt=0, description="Unique identifier for the player")
    created_at: datetime = Field(..., description="Timestamp of player creation")
    last_match_at: Optional[datetime] = Field(default=None, description="Timestamp of the player's last match")
    matches_played: int = Field(default=0, ge=0, description="Total matches played by the player")
    wins: int = Field(default=0, ge=0, description="Total matches won by the player")
    losses: int = Field(default=0, ge=0, description="Total matches lost by the player")
    win_rate: float = Field(default=0.0, description="Win rate of the player")

    class Config:
        from_attributes = True
