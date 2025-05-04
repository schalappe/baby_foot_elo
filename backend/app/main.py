# -*- coding: utf-8 -*-
""" """

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import DatabaseManager
from app.routers import health, test_info


@asynccontextmanager
async def lifespan(app):
    db = DatabaseManager()
    db.initialize_database()
    yield


app = FastAPI(lifespan=lifespan)

# ##: Allow CORS from frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(test_info.router)


@app.get("/")
def read_root():
    return {"Hello": "World"}
