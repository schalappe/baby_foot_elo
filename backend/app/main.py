# -*- coding: utf-8 -*-
"""
Main application module for the Baby Foot Elo API.

This module initializes the FastAPI application, sets up middleware,
routers, error handling, rate limiting, and API documentation.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from app.api import api_router
from app.core import config
from app.db import DatabaseManager, initialize_database
from app.utils.error_handlers import setup_error_handlers
from app.utils.rate_limiter import setup_rate_limiting
from app.utils.validation import (
    ValidationErrorResponse,
    validation_error_response_handler,
    validation_exception_handler,
)


@asynccontextmanager
async def lifespan(app):
    db = DatabaseManager(db_path=config.get_db_url())
    initialize_database(db)
    yield


app = FastAPI(
    title="Baby Foot Elo API",
    description="API for managing baby foot (foosball) players, teams, matches, and ELO ratings",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None,
    redoc_url="/api/docs",
)

# ##: Set up error handlers.
setup_error_handlers(app)

# ##: Set up custom validation error handlers.
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValidationErrorResponse, validation_error_response_handler)

# ##: Set up rate limiting.
endpoint_limits = {
    "/api/v1/players/": (20, 60),  # 20 requests per minute for player creation
    "/api/v1/players/{player_id}": (30, 60),  # 30 requests per minute for player updates
}
setup_rate_limiting(app, default_limit=100, default_window=60, endpoint_limits=endpoint_limits)

# ##: Allow CORS from frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ##: Include routers.
app.include_router(api_router)


@app.get("/", tags=["root"])
def read_root():
    """
    Root endpoint that returns a welcome message.

    Returns
    -------
    dict
        A simple welcome message.
    """
    return {"message": "Welcome to the Baby Foot Elo API"}


@app.get("/api/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """
    Custom Swagger UI endpoint.

    Returns
    -------
    HTMLResponse
        The Swagger UI HTML.
    """
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - API Documentation",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )


def custom_openapi():
    """
    Generate a custom OpenAPI schema with additional information.

    Returns
    -------
    dict
        The OpenAPI schema.
    """
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # ##: Add global security scheme for rate limiting.
    openapi_schema["components"] = openapi_schema.get("components", {})
    openapi_schema["components"]["securitySchemes"] = {
        "RateLimit": {
            "type": "apiKey",
            "name": "X-API-Key",
            "in": "header",
            "description": "API rate limiting is enforced. See response headers for limits.",
        }
    }

    # ##: Add global tags metadata.
    openapi_schema["tags"] = [
        {
            "name": "players",
            "description": "Operations related to player management",
        },
        {
            "name": "teams",
            "description": "Operations related to team management",
        },
        {
            "name": "matches",
            "description": "Operations related to match recording and history",
        },
        {
            "name": "health",
            "description": "API health check endpoints",
        },
        {
            "name": "root",
            "description": "Root level API endpoints",
        },
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
