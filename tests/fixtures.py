import pytest
from httpx import AsyncClient
from sqlalchemy import select

from src.auth.models import AuthUser
from src.auth.schemas import UserSchema
from src.team.models import Team
from src.team.schemas import TeamSchema
from tests.conftest import async_session_maker

user_data = {
    "email": "user@example.com",
    "password": "string",
}
test_user_data = {
  "username": "test",
  "email": "test@example.com",
  "hashed_password": "string",
  "confirmed_password": "string",
  "verified": True,
}


@pytest.fixture(scope="module")
async def user(
    async_client: AsyncClient,
) -> UserSchema:
    """Данные тестового пользователя."""
    async with async_session_maker() as session:
        query = select(AuthUser).where(AuthUser.email == user_data["email"])
        result = await session.execute(query)
        return result.scalar_one_or_none()


@pytest.fixture(scope="session")
async def auth_user(async_client: AsyncClient) -> dict:
    """Авторизованный тестовый пользователь."""
    async with async_session_maker() as session:
        query = select(AuthUser).where(AuthUser.email == test_user_data["email"])
        result = await session.execute(query)
        return result.scalar_one_or_none()


@pytest.fixture(scope="session")
async def auth_user_cookies(async_client: AsyncClient) -> dict:
    """Авторизованный тестовый пользователь."""
    response = await async_client.post(
        "/auth/register",
        json=test_user_data,
    )
    access_token = response.cookies["find-team"]
    return {"find-team": access_token}


@pytest.fixture(scope="session")
async def test_team(auth_user: UserSchema, async_client: AsyncClient) -> TeamSchema:
    """Тестовая команда тестового пользователя."""
    async with async_session_maker() as session:
        query = select(Team).where(Team.owner == auth_user.id)
        result = await session.execute(query)
        return result.scalar_one_or_none()
