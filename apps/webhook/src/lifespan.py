from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from src.models.database.config import create_engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    app.state.engine = create_engine()

    yield

    await app.state.engine.dispose()
