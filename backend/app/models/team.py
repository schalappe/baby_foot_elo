# -*- coding: utf-8 -*-
"""
Pydantic models for teams.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator

from .player import PlayerResponse


class TeamBase(BaseModel):
    """
    Base model for team properties.

    Attributes
    ----------
    player1_id : int
        The ID of the first player in the team.
    player2_id : int
        The ID of the second player in the team.
    """

    player1_id: int = Field(..., gt=0, description="ID of the first player")
    player2_id: int = Field(..., gt=0, description="ID of the second player")


class TeamCreate(TeamBase):
    """
    Data model for creating a new team.

    Attributes
    ----------
    player1_id : int
        The ID of the first player.
    player2_id : int
        The ID of the second player.
    global_elo : float, optional
        The initial global ELO rating for the team (default is 1000.0).
    current_month_elo : float, optional
        The initial ELO rating for the current month for the team (default is 1000.0).
    """

    global_elo: float = Field(default=1000.0, ge=0, description="Initial global ELO rating for the team")
    current_month_elo: float = Field(default=1000.0, ge=0, description="Initial ELO rating for the current month")

    @model_validator(mode="after")
    def validate_players(cls, values: Any) -> Any:
        """
        Validate that player1_id and player2_id are different and enforce canonical order.
        Canonical order: player1_id < player2_id.
        """
        p1_id = values.player1_id
        p2_id = values.player2_id

        if p1_id is None or p2_id is None:
            raise ValueError("player1_id and player2_id must be provided")

        if p1_id == p2_id:
            raise ValueError("player1_id and player2_id cannot be the same")

        if p1_id > p2_id:
            values.player1_id, values.player2_id = p2_id, p1_id
        return values


class TeamUpdate(BaseModel):
    """
    Data model for updating an existing team's information.
    Currently, teams are immutable in terms of players; ELO and last_match_at
    are updated via match results.
    This model is a placeholder for potential future updatable fields.
    """

    pass


class TeamResponse(TeamBase):
    """
    Data model for returning team information in API responses.

    Attributes
    ----------
    team_id : int
        Unique identifier for the team.
    player1_id : int
        ID of the first player.
    player2_id : int
        ID of the second player.
    global_elo : float
        The current global ELO rating of the team.
    current_month_elo : float
        The current ELO rating of the team for the month.
    created_at : datetime
        The date and time when the team was created.
    last_match_at : Optional[datetime]
        The date and time of the team's last match.
    player1 : Optional[PlayerResponse]
        Detailed information for player 1 (populated by service layer).
    player2 : Optional[PlayerResponse]
        Detailed information for player 2 (populated by service layer).
    rank : Optional[int]
        Ranking position based on ELO (populated for ranking endpoints).
    """

    team_id: int = Field(..., gt=0, description="Unique identifier for the team")
    global_elo: float = Field(..., ge=0, description="Current global ELO rating of the team")
    current_month_elo: float = Field(..., ge=0, description="Current ELO rating for the team for the month")
    created_at: datetime = Field(..., description="Timestamp of team creation")
    last_match_at: Optional[datetime] = Field(default=None, description="Timestamp of the team's last match")

    player1: Optional[PlayerResponse] = Field(default=None, description="Details for player 1")
    player2: Optional[PlayerResponse] = Field(default=None, description="Details for player 2")
    rank: Optional[int] = Field(default=None, description="Ranking position based on ELO")

    model_config = {"from_attributes": True}
