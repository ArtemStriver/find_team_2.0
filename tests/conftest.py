import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from fastapi.testclient import TestClient

from src.config import settings

if settings.TEST_DB_NAME:
    settings.DB_NAME = settings.TEST_DB_NAME

engine = create_async_engine(settings.test_db_url_postgresql, poolclass=NullPool)
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

pytest_plugins = [
    "tests.fixtures"
]


@pytest.fixture(autouse=True, scope="module")
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    from src.database import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session_maker() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
async def event_loop() -> Generator[asyncio.AbstractEventLoop, Any, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def async_client() -> AsyncGenerator[TestClient]:
    from src.main import app

    async with TestClient(app) as client:
        yield client
