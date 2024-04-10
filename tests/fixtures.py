import pytest
from httpx import AsyncClient
from sqlalchemy import insert, select

from src.auth import utils as auth_utils
from src.auth.models import AuthUser
from src.auth.schemas import UserSchema
from src.team.models import Team
from src.team.schemas import TeamSchema
from src.user_profile.crud import create_user_profile
from tests.conftest import async_session_maker

user_data_login = {
    "email": "test@example.com",
    "password": "string",
}
user_data = {
    "username": "user",
    "email": "user@example.com",
    "hashed_password": "string",
    "confirmed_password": "string",
}
test_user_data_1 = {
    "username": "test1",
    "email": "test1@example.com",
    "hashed_password": "string",
    "confirmed_password": "string",
}
test_user_data_2 = {
    "username": "test2",
    "email": "test2@example.com",
    "hashed_password": "string",
    "confirmed_password": "string",
}
team_data = {
    "title": "string",
    "type_team": "lifestyle",
    "number_of_members": 1,
    "team_description": "string",
    "team_deadline_at": "2024-04-05",
    "team_city": "Интернет",
    "tags": {
        "tag1": "string",
        "tag2": "string",
        "tag3": "string",
        "tag4": "string",
        "tag5": "string",
        "tag6": "string",
        "tag7": "string",
    },
}


@pytest.fixture(scope="session")
async def register_user_1(async_client: AsyncClient) -> None:
    """Авторизованный тестовый пользователь."""
    async with async_session_maker() as session:
        stmt = insert(AuthUser).values(
            {
                "username": test_user_data_1["username"],
                "email": test_user_data_1["email"],
                "hashed_password": auth_utils.hash_password(test_user_data_1["hashed_password"]),
                "verified": True,
            },
        ).returning(AuthUser.id, AuthUser.username, AuthUser.email, AuthUser.verified)
        data = (await session.execute(stmt)).all()
        new_user_data = UserSchema(
            id=data[0][0],
            username=data[0][1],
            email=data[0][2],
            verified=data[0][3],
        )
        await create_user_profile(new_user_data, session)
        await session.commit()
        return new_user_data


@pytest.fixture(scope="session")
async def register_user_2(async_client: AsyncClient) -> None:
    """Авторизованный тестовый пользователь."""
    async with async_session_maker() as session:
        stmt = insert(AuthUser).values(
            {
                "username": test_user_data_2["username"],
                "email": test_user_data_2["email"],
                "hashed_password": auth_utils.hash_password(test_user_data_2["hashed_password"]),
                "verified": True,
            },
        ).returning(AuthUser.id, AuthUser.username, AuthUser.email, AuthUser.verified)
        data = (await session.execute(stmt)).all()
        new_user_data = UserSchema(
            id=data[0][0],
            username=data[0][1],
            email=data[0][2],
            verified=data[0][3],
        )
        await create_user_profile(new_user_data, session)
        await session.commit()
        return new_user_data


@pytest.fixture(scope="session")
async def auth_user(async_client: AsyncClient) -> dict:
    """Авторизованный тестовый пользователь."""
    async with async_session_maker() as session:
        query = select(AuthUser).where(AuthUser.email == user_data["email"])
        result = await session.execute(query)
        return result.scalar_one_or_none()


@pytest.fixture(scope="session")
async def test_user_cookies(async_client: AsyncClient) -> dict:
    """Test user."""
    await async_client.post(
        "/auth/register",
        json=user_data,
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
