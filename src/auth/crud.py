import uuid

from fastapi import HTTPException, status
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import utils as auth_utils
from src.auth.models import AuthUser
from src.auth.schemas import CreateUserSchema, UserSchema, PasswordChangeSchema
from src.user_profile.crud import create_profile


async def get_user(
    email: str,
    session: AsyncSession,
) -> AuthUser:
    """Получение данных o пользователе из БД по email."""
    query = select(AuthUser).where(AuthUser.email == email)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_user_by_id(
    user_id: uuid.UUID,
    session: AsyncSession,
) -> AuthUser | None:
    """Получение данных o пользователе из БД по id."""
    query = select(AuthUser).where(AuthUser.id == user_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def create_user(
    user_data: CreateUserSchema,
    session: AsyncSession,
) -> AuthUser:
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
    stmt = insert(AuthUser).values(
        {
            "username": user_data.username,
            "email": user_data.email,
            "hashed_password": auth_utils.hash_password(user_data.hashed_password),
            # TODO СДЕЛАНО ТОЛЬКО ДЛЯ ОТЛАДКИ !!! НА ПРОДАКШЕНЕ УБРАТЬ !!!
            "verified": True,
        },
    )
    await session.execute(stmt)
    user = await get_user(user_data.email, session)
    await session.commit()
    # TODO СДЕЛАНО ТОЛЬКО ДЛЯ ОТЛАДКИ !!! НА ПРОДАКШЕНЕ УБРАТЬ !!!
    await create_profile(user, session)
    # TODO СДЕЛАНО ТОЛЬКО ДЛЯ ОТЛАДКИ !!! НА ПРОДАКШЕНЕ УБРАТЬ !!!
    return UserSchema(
        id=user.id,
        username=user.username,
        email=user.email,
        verified=user.verified,
    )


async def verify_user_data(
    user_id: uuid.UUID,
    session: AsyncSession,
):
    stmt = update(AuthUser).values({"verified": True}).where(AuthUser.id == user_id)
    await session.execute(stmt)
    await session.commit()


async def change_password(
    user_id: uuid.UUID | str,
    password_data: PasswordChangeSchema,
    session: AsyncSession,
) -> None:
    if not password_data.hashed_password == password_data.confirmed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="passwords are different",
        )
    stmt = update(AuthUser).values({
        "hashed_password": auth_utils.hash_password(password_data.hashed_password),
    }).where(AuthUser.id == user_id)
    await session.execute(stmt)
    await session.commit()
