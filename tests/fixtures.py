import pytest
from httpx import AsyncClient
from sqlalchemy import select

from src.auth.models import AuthUser
from src.auth.schemas import UserSchema
from tests.conftest import async_session_maker

user_data = {
    "email": "user@example.com",
    "password": "string",
}


@pytest.fixture(scope="module")
async def user(
    async_client: AsyncClient,
) -> UserSchema:
    async with async_session_maker() as session:
        query = select(AuthUser).where(AuthUser.email == user_data["email"])
        result = await session.execute(query)
        return result.scalar_one_or_none()
