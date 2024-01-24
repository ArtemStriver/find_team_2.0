import asyncio
from collections.abc import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from src.config import settings
from src.database import Base, get_async_session
from src.main import app

if settings.TEST_DB_NAME:
    settings.DB_NAME = settings.TEST_DB_NAME

engine_test = create_async_engine(settings.test_db_url_postgresql, poolclass=NullPool)
async_session_maker = sessionmaker(
    engine_test,
    class_=AsyncSession,
    expire_on_commit=False,
)
Base.metadata.bind = engine_test


pytest_plugins = [
    "tests.fixtures"
]


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

app.dependency_overrides[get_async_session] = override_get_async_session


@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


client = TestClient(app)


@pytest.fixture(scope="session")
async def async_client() -> AsyncGenerator[AsyncClient]:
    async with AsyncClient(app=app, base_url="http://test") as aclient:
        yield aclient
