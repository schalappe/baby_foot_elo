# -*- coding: utf-8 -*-
"""

"""

from app.routers import health
from fastapi import FastAPI

app = FastAPI()

app.include_router(health.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}
