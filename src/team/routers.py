import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.auth_handler import current_user
from src.auth.schemas import ResponseSchema, UserSchema
from src.database import get_async_session
from src.team import crud
from src.team.schemas import CreateTeamSchema, TeamSchema

team_router = APIRouter(
    prefix="/team",
    tags=["Team"],
)

"""
Логика для владельцев команды.

Этот модуль будет отвечать за создание и редактирование команды,
a также за управление командой.
"""


@team_router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
)
async def create_team(
    team_data: CreateTeamSchema,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[UserSchema, Depends(current_user)],
) -> ResponseSchema:
    return await crud.create_team(team_data, session, user)


@team_router.patch(
    "/change",
    status_code=status.HTTP_200_OK,
)
async def update_team(
    team_id: uuid.UUID,
    update_data: TeamSchema,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[UserSchema, Depends(current_user)],
) -> ResponseSchema:
    return await crud.update_team(team_id, update_data, session, user)


@team_router.delete(
    "/delete",
)
async def delete_team(
    team_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[UserSchema, Depends(current_user)],
) -> ResponseSchema:
    return await crud.delete_team(team_id, session, user)


@team_router.get(
    "/my_team",
    status_code=status.HTTP_200_OK,
)
async def get_my_team(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[UserSchema, Depends(current_user)],
) -> TeamSchema | None:
    if not (team := await crud.get_user_team(user.id, session)):
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail="user has not any team"
        )
    return team


@team_router.post(
    "/take_comrade",  # может сменить comrade на friend
    status_code=status.HTTP_204_NO_CONTENT,
)
async def take_comrade(
    user: Annotated[UserSchema, Depends(current_user)],
):
    """Принять запрос пользователя на вступление в команду."""


@team_router.post(
    "/reject_comrade",  # может сменить comrade на friend
    status_code=status.HTTP_204_NO_CONTENT,
)
async def reject_comrade(
    user: Annotated[UserSchema, Depends(current_user)],
):
    """Отклонить запрос пользователя на вступление в команду."""


@team_router.post(
    "/exclude_comrade",  # может сменить comrade на friend
    status_code=status.HTTP_204_NO_CONTENT,
)
async def exclude_comrade(
    user: Annotated[UserSchema, Depends(current_user)],
):
    """Исключить пользователя из команды."""
