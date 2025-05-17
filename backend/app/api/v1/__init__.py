"""
This module contains all v1 API endpoints.
"""

from fastapi import APIRouter
from .endpoints import health, matches, players, teams


api_router = APIRouter(prefix="/v1")
api_router.include_router(health.router)
api_router.include_router(players.router)
api_router.include_router(teams.router)
api_router.include_router(matches.router)
