import uuid
from typing import Optional, Annotated

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, UUIDIDMixin

from src.auth.models import AuthUser
from src.auth.utils import get_user_db
from src.config import settings
from src.database import Base


class UserManager(UUIDIDMixin, BaseUserManager[AuthUser, uuid.UUID]):
    reset_password_token_secret = settings.SECRET_KEY
    verification_token_secret = settings.SECRET_KEY

    # TODO переделать данные функции для профиля пользователя и установить логирование
    async def on_after_register(self, user: AuthUser, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: AuthUser, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: AuthUser, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db: Annotated[Base, Depends(get_user_db)]):
    yield UserManager(user_db)