"""
API package for the Baby Foot Elo application.

This package contains all API-related code, including versioned API endpoints.
"""

from fastapi import APIRouter
from app.api.v1 import api_router as v1_router

# ##: Include v1 API routes.
api_router = APIRouter(prefix="/api")
api_router.include_router(v1_router)
