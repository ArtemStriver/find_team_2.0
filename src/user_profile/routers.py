import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.auth_handler import current_user
from src.auth.schemas import UserSchema, ResponseSchema
from src.database import get_async_session
from src.find.schemas import TeamPreviewSchema
from src.team.schemas import TeamSchema
from src.user_profile import crud
from src.user_profile.schemas import UserProfileSchema, UpdateProfileSchema

profile_router = APIRouter(
    prefix="/profile",
    tags=["Profile"],
)

"""Логика профиля пользователя."""


@profile_router.get(
    "/profile/{user_id}",
    response_model=UserProfileSchema,
    status_code=status.HTTP_200_OK,
)
async def profile(
    user_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    _: Annotated[UserSchema, Depends(current_user)],
) -> UserProfileSchema:
    """Получение данных профиля пользователя."""
    if (user_profile := await crud.get_profile(user_id, session)) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="there is no such profile",
        )
    return user_profile


@profile_router.patch(
    "/change_profile",
    response_model=ResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def change_profile(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[UserSchema, Depends(current_user)],
    updated_data: UpdateProfileSchema,
) -> ResponseSchema:
    """Изменение профиля пользователя."""
    return await crud.change_profile(updated_data, user, session)


@profile_router.delete(
    "/delete_profile",
    response_model=ResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def delete_profile(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[UserSchema, Depends(current_user)],
    response: Response,
) -> ResponseSchema:
    """Удалить профиля пользователя и его данные."""
    return await crud.delete_profile(user, session, response)


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
