from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.auth.auth_handler import current_user
from src.auth.schemas import UserSchema

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
    user: Annotated[UserSchema, Depends(current_user)],
):
    """Получить список всех доступных команд."""


@find_router.get(
    "/find_team",
    status_code=status.HTTP_200_OK,
)
async def get_team(
    user: Annotated[UserSchema, Depends(current_user)],
):
    """Поиск команды."""


@find_router.post(
    "/join",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def join_team(
    user: Annotated[UserSchema, Depends(current_user)],
):
    """Присоединиться к команде."""


@find_router.post(
    "/quit",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def quit_team(
    user: Annotated[UserSchema, Depends(current_user)],
):
    """Покинуть команду."""
