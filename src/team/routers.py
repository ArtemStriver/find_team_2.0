import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.auth_handler import current_user
from src.auth.schemas import ResponseSchema, UserSchema
from src.database import get_async_session
from src.team import crud
from src.team.schemas import ApplicationSchema, CreateTeamSchema, MemberSchema

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
    response_model=ResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_team(
    team_data: CreateTeamSchema,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[UserSchema, Depends(current_user)],
) -> ResponseSchema:
    return await crud.create_team(team_data, session, user)


@team_router.patch(
    "/change/{team_id}",
    response_model=ResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def update_team(
    team_id: uuid.UUID,
    update_data: CreateTeamSchema,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[UserSchema, Depends(current_user)],
) -> ResponseSchema:
    return await crud.update_team(team_id, update_data, session, user)


@team_router.delete(
    "/delete/{team_id}",
    response_model=ResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def delete_team(
    team_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[UserSchema, Depends(current_user)],
) -> ResponseSchema:
    return await crud.delete_team(team_id, session, user)


@team_router.get(
    "/members_list",
    response_model=list[MemberSchema],
    status_code=status.HTTP_200_OK,
)
async def get_members(
    team_id: str,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[UserSchema, Depends(current_user)],
) -> list[MemberSchema]:
    """Получение списка всех заявок на вступление в команду пользователя."""
    return await crud.get_members_list(team_id, user, session)


@team_router.get(
    "/applications_list",
    response_model=list[ApplicationSchema],
    status_code=status.HTTP_200_OK,
)
async def get_applications(
    team_id: str,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[UserSchema, Depends(current_user)],
) -> list[ApplicationSchema]:
    """Получение списка всех заявок на вступление в команду пользователя."""
    return await crud.get_application_list(team_id, user, session)


@team_router.post(
    "/take_comrade",
    response_model=ResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def take_comrade(
    comrade_id: str,
    team_id: str,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    _: Annotated[UserSchema, Depends(current_user)],
) -> ResponseSchema:
    """Принять запрос пользователя на вступление в команду."""
    return await crud.move_comrade_into_team(comrade_id, team_id, session)


@team_router.post(
    "/reject_comrade",
    response_model=ResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def reject_comrade(
    comrade_id: str | uuid.UUID,
    team_id: str | uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    _: Annotated[UserSchema, Depends(current_user)],
) -> ResponseSchema:
    """Отклонить запрос пользователя на вступление в команду."""
    return await crud.remove_application_of_comrade(comrade_id, team_id, session)


@team_router.post(
    "/exclude_comrade",
    response_model=ResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def exclude_comrade(
    comrade_id: str,
    team_id: str,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    user: Annotated[UserSchema, Depends(current_user)],
) -> ResponseSchema:
    """Исключить пользователя из команды."""
    return await crud.exclude_comrade_from_team(user.id, comrade_id, team_id, session)
