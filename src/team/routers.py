from typing import Annotated

from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.team import crud
from src.auth.auth_handler import current_user
from src.auth.schemas import UserSchema, ResponseSchema
from src.team.schemas import CreateTeamSchema

team_router = APIRouter(
    prefix="/team",
    tags=["Team"],
)

"""
Логика для владельцев команды.

Этот модуль будет отвечать за создание и редактирование команды,
а также за управление командой.
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
    user: Annotated[UserSchema, Depends(current_user)],
):
    pass


@team_router.delete(
    "/delete",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_team(
    user: Annotated[UserSchema, Depends(current_user)],
):
    pass


@team_router.post(
    "/take_comrade",  # может сменить comrade на friend
    status_code=status.HTTP_204_NO_CONTENT,
)
async def take_comrade(
    user: Annotated[UserSchema, Depends(current_user)],
):
    """Принять запрос пользователя на вступление в команду."""
    pass


@team_router.post(
    "/reject_comrade",  # может сменить comrade на friend
    status_code=status.HTTP_204_NO_CONTENT,
)
async def reject_comrade(
    user: Annotated[UserSchema, Depends(current_user)],
):
    """Отклонить запрос пользователя на вступление в команду."""
    pass


@team_router.post(
    "/exclude_comrade",  # может сменить comrade на friend
    status_code=status.HTTP_204_NO_CONTENT,
)
async def exclude_comrade(
    user: Annotated[UserSchema, Depends(current_user)],
):
    """Исключить пользователя из команды."""
    pass
