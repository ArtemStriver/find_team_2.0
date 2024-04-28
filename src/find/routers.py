import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.auth_handler import current_user
from src.auth.schemas import ResponseSchema, UserSchema
from src.database import get_async_session
from src.find import crud
from src.find.schemas import JoinDataSchema, TeamPreviewSchema
from src.team.schemas import TeamSchema

find_router = APIRouter(
    prefix="/find",
    tags=["Find"],
)

"""
Логика для пользователей.

Этот модуль будет отвечать за поиск и подбор команд для пользователей,
a также взаимодействие пользователя c командой.
"""


@find_router.get(
    "/teams_list",
    status_code=status.HTTP_200_OK,
)
async def get_all_teams(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> list[TeamPreviewSchema]:
    """Получить список всех доступных команд."""
    return await crud.get_teams_list(session)


@find_router.get(
    "/team/{team_id}",
    status_code=status.HTTP_200_OK,
)
async def get_team(
    team_id: uuid.UUID,
    _: Annotated[UserSchema, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> TeamSchema:
    """Посмотреть данные o команде подробнее."""
    return await crud.get_team_data(team_id, session)


@find_router.post(
    "/join",
    response_model=ResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def join_team(
    join_data: JoinDataSchema,
    user: Annotated[UserSchema, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> ResponseSchema:
    """Присоединиться к команде."""
    return await crud.join_in_team(join_data, user, session)


@find_router.post(
    "/quit",
    response_model=ResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def quit_team(
    team_id: uuid.UUID,
    user: Annotated[UserSchema, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> ResponseSchema:
    """Покинуть команду."""
    return await crud.leave_team(team_id, user, session)
