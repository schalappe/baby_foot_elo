# -*- coding: utf-8 -*-
"""
Pydantic models for player-related operations in the Baby Foot Elo backend.

This module defines data models for creating, updating, and returning player information.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# Shared properties
class PlayerBase(BaseModel):
    """
    Base model for player properties.

    Attributes
    ----------
    name : str
        The name of the player.
    """

    name: str = Field(..., min_length=1, max_length=100, description="Player's name")


class PlayerCreate(PlayerBase):
    """
    Data model for creating a new player.

    Attributes
    ----------
    name : str
        The name of the player (inherited from PlayerBase).
    global_elo : int, optional
        The initial global ELO rating for the player (default is 1000).
    current_month_elo : int, optional
        The initial ELO rating for the current month (default is 1000).
    """

    global_elo: int = Field(default=1000, ge=0, description="Initial global ELO rating for the player")
    current_month_elo: int = Field(default=1000, ge=0, description="Initial ELO rating for the current month")


class PlayerUpdate(BaseModel):
    """
    Data model for updating an existing player's information.

    Attributes
    ----------
    name : str, optional
        The updated name of the player.
    """

    name: Optional[str] = Field(default=None, min_length=1, max_length=100, description="Player's updated name")


class PlayerResponse(PlayerBase):
    """
    Data model for returning player information in API responses.

    Attributes
    ----------
    id : int
        Unique identifier for the player.
    name : str
        The name of the player (inherited from PlayerBase).
    global_elo : int
        The current global ELO rating of the player.
    current_month_elo : int
        The current ELO rating of the player for the month.
    creation_date : datetime
        The date and time when the player was created.
    matches_played : int, optional
        The number of matches the player has played (default is 0).
    wins : int, optional
        The number of matches the player has won (default is 0).
    losses : int, optional
        The number of matches the player has lost (default is 0).
    """

    id: int = Field(..., gt=0, description="Unique identifier for the player")
    global_elo: int = Field(..., ge=0, description="Current global ELO rating of the player")
    current_month_elo: int = Field(..., ge=0, description="Current ELO rating of the player for the month")
    creation_date: datetime = Field(..., description="Timestamp of player creation")
    matches_played: int = Field(default=0, ge=0, description="Total matches played by the player")
    wins: int = Field(default=0, ge=0, description="Total matches won by the player")
    losses: int = Field(default=0, ge=0, description="Total matches lost by the player")

    model_config = {"from_attributes": True}
