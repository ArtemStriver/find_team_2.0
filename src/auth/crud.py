import uuid

from fastapi import HTTPException, status
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import utils as auth_utils
from src.auth.models import AuthUser
from src.auth.schemas import CreateUserSchema, UserSchema


# TODO добавить это в кэш.
async def get_user(
    email: str,
    session: AsyncSession,
) -> UserSchema:
    """Получение данных o пользователе из БД по email."""
    query = select(AuthUser).where(AuthUser.email == email)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def create_user(
    user_data: CreateUserSchema,
    session: AsyncSession,
) -> UserSchema:
    """Создание пользователя в БД."""
    if await get_user(user_data.email, session):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="register user already exists",
        )
    if not user_data.hashed_password == user_data.confirmed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="passwords are different",
        )
    valid_user_data = UserSchema(
        id=uuid.uuid4(),
        username=user_data.username,
        email=user_data.email,
        hashed_password=auth_utils.hash_password(user_data.hashed_password),
        verified=user_data.verified,
    )
    stmt = insert(AuthUser).values(**valid_user_data.model_dump())
    await session.execute(stmt)
    await session.commit()
    return valid_user_data
