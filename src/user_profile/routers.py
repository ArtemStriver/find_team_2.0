import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.auth_handler import current_user
from src.auth.schemas import UserSchema
from src.database import get_async_session
from src.find.schemas import TeamPreviewSchema
from src.team.schemas import TeamSchema
from src.user_profile import crud

profile_router = APIRouter(
    prefix="/profile",
    tags=["Profile"],
)

"""Логика профиля пользователя."""


@profile_router.patch(
    "/photo",
    status_code=status.HTTP_200_OK,
)
async def change_photo(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[UserSchema, Depends(current_user)],
):
    """Обновление фото пользователя
    (вместо дефолтного установить загруженное пользователем,
    при изменении - новое установить, старо удалить)."""


@profile_router.patch(
    "/change_password",
    status_code=status.HTTP_200_OK,
)
async def change_password(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[UserSchema, Depends(current_user)],
):
    """Изменение пароля пользователя"""


@profile_router.post(
    "/password_recovery",
    status_code=status.HTTP_200_OK,
)
async def recover_password(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[UserSchema, Depends(current_user)],
) -> list[TeamPreviewSchema]:
    """Восстановление пароля пользователя"""
# TODO сделать ручку для получения данных пользователя по его id

# TODO подумать над названиями функций!!!
@profile_router.get(
    "/teams",
    response_model=list[TeamPreviewSchema],
    status_code=status.HTTP_200_OK,
)
async def get_teams(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[UserSchema, Depends(current_user)],
) -> list[TeamPreviewSchema]:
    """Получение списка команд, в которых состоит пользователь."""
    return await crud.get_teams(user.id, session)


@profile_router.get(
    "/my_teams",
    response_model=list[TeamPreviewSchema],
    status_code=status.HTTP_200_OK,
)
async def get_my_teams(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[UserSchema, Depends(current_user)],
) -> list[TeamPreviewSchema]:
    """Получение команд пользователя."""
    return await crud.get_user_teams(user.id, session)

# TODO убрать и использовать find/team/id ??? Отличие только в проверке на причастность команды пользователю
@profile_router.get(
    "/my_team/{team_id}",
    response_model=TeamSchema,
    status_code=status.HTTP_200_OK,
)
async def get_my_team(
    team_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[UserSchema, Depends(current_user)],
) -> TeamSchema | None:
    """Получение данных o команде пользователя."""
    if not (team := await crud.get_user_team(team_id, user.id, session)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user does not have access to this team",
        )
    return team
