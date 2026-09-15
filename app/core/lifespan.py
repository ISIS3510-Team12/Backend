from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.dependencies import initialize_firebase_app

@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_firebase_app()
    yield