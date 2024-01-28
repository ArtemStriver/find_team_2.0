from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.auth.auth_handler import current_user
from src.auth.schemas import UserSchema

find_router = APIRouter(
    prefix="/fins",
    tags=["Find"],
)

"""
Логика для пользователей.

Этот модуль будет отвечать за поиск и подбор команд для пользователей,
a также взаимодействие пользователя c командой.
"""


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
