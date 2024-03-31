import uuid
from typing import Annotated

from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.auth_handler import current_user
from src.auth.schemas import UserSchema
from src.config import settings
from src.database import get_async_session

"""
Админ-панель будет организована через swagger - интерактивную документацию.
Доступ к ней будет у нескольких, заранее прописанных аккаунтов,
ссылка, по которой она будет доступна, будет сложной, чтобы к ней нельзя было просто так подключится,
данные ссылки будут в env файле.
Модуль будет содержать:
- получение списка всех пользователей;
- получение списка всех команд;
- поиск пользователя по id, username или email;
- поиск команды по ее id;
- ручку удаления команды и ручку удаления пользователя,
  доступ к которой будет для определенного числа пользователей - админов.
"""


admin_router = APIRouter(
    prefix=f"/admin/{settings.SECRET_PATH}/",
    tags=["Admin"],
)


@admin_router.get(
    "/all_users",
    status_code=status.HTTP_200_OK,
)
async def get_all_users(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[UserSchema, Depends(current_user)],
) -> None:
    """Получение списка всех пользователей с подробной информацией о них."""


@admin_router.get(
    "/all_teams",
    status_code=status.HTTP_200_OK,
)
async def get_all_teams(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[UserSchema, Depends(current_user)],
) -> None:
    """Получение списка всех команд с краткой информацией о них."""


@admin_router.get(
    "/search_user",
    status_code=status.HTTP_200_OK,
)
async def search_user(
    user_info: str,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[UserSchema, Depends(current_user)],
) -> None:
    """Поиск и получение данных о пользователе по его email/username/id."""


@admin_router.get(
    "/search_team",
    status_code=status.HTTP_200_OK,
)
async def search_team(
    team_id: str | uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[UserSchema, Depends(current_user)],
) -> None:
    """Поиск и получение данных о команде по ее id."""


@admin_router.delete(
    "/delete_user",
    status_code=status.HTTP_200_OK,
)
async def delete_user(
    user_info: str,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[UserSchema, Depends(current_user)],
) -> None:
    """Удаление пользователя по его email/username/id."""


@admin_router.delete(
    "/delete_team",
    status_code=status.HTTP_200_OK,
)
async def delete_team(
    team_id: str | uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[UserSchema, Depends(current_user)],
) -> None:
    """Удаление команды по ее id."""
