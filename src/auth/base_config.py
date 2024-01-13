import uuid

from fastapi_users import FastAPIUsers
from fastapi_users.authentication import CookieTransport, JWTStrategy, AuthenticationBackend

from src.auth.manager import get_user_manager
from src.auth.models import AuthUser
from src.config import settings

cookies_transport = CookieTransport(cookie_name="find-team", cookie_max_age=3600)


def get_jwt_strategy() -> JWTStrategy:
    """Получение JWT токена по секретному ключу"""
    return JWTStrategy(secret=settings.SECRET_KEY, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookies_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users_auth = FastAPIUsers[AuthUser, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

current_user = fastapi_users_auth.current_user()
