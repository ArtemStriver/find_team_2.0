import pytest
from httpx import AsyncClient
from sqlalchemy import select

from src.auth.models import AuthUser
from src.auth.schemas import UserSchema
from src.team.models import Team
from src.team.schemas import TeamSchema
from tests.conftest import async_session_maker

test_user_data_login = {
    "email": "test@example.com",
    "password": "string",
}
test_user_data = {
  "username": "test",
  "email": "test@example.com",
  "hashed_password": "string",
  "confirmed_password": "string",
  "verified": True,
}

team_data = {
            "title": "test",
            "number_of_members": 1,
            "contacts": "@test_telegram",
            "description": "We need a cool team to test this program.",
            "tags": "test, ",
            "deadline_at": "2024-02-02T05:00:53",
        }


@pytest.fixture(scope="session")
async def auth_user(async_client: AsyncClient) -> dict:
    """Авторизованный тестовый пользователь."""
    async with async_session_maker() as session:
        query = select(AuthUser).where(AuthUser.email == test_user_data["email"])
        result = await session.execute(query)
        return result.scalar_one_or_none()


@pytest.fixture(scope="session")
async def test_user_cookies(async_client: AsyncClient) -> dict:
    """Test user."""
    await async_client.post(
        "/auth/register",
        json=test_user_data,
    )
    access_token = async_client.cookies.get("find-team")
    return {"find-team": access_token}


@pytest.fixture(scope="session")
async def user_team(auth_user: UserSchema, async_client: AsyncClient) -> TeamSchema | None:
    """Тестовая команда тестового пользователя."""
    async with async_session_maker() as session:
        query = select(Team).where(Team.owner == auth_user.id)
        result = await session.execute(query)
        return result.scalar_one_or_none()


@pytest.fixture(scope="session")
async def team(auth_user: UserSchema, test_user_cookies: dict, async_client: AsyncClient) -> None:
    """Тестовая команда тестового пользователя."""
    await async_client.post(
        "/team/create",
        json=team_data,
        cookies=test_user_cookies,
    )
