from fastapi import Form, Depends, HTTPException, status, Response
from fastapi.security import APIKeyCookie
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.crud import get_user
from src.auth import utils as auth_utils
from src.auth.schemas import UserSchema
from src.database import get_async_session
from src.config import settings

cookies_scheme = APIKeyCookie(name=settings.COOKIE_SESSION_ID_KEY)


async def validate_auth_user(
    email: str = Form(),
    password: str = Form(),
    session: AsyncSession = Depends(get_async_session),
):
    unauthenticated_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid username or password",
    )
    user = await get_user(email, session)
    if not user:
        raise unauthenticated_exception

    if not auth_utils.validate_password(
        password=password,
        hashed_password=user.hashed_password
    ):
        raise unauthenticated_exception

    if not user.verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user unverified",
        )
    return user


async def get_auth_user(
    token: str = Depends(cookies_scheme),
    session: AsyncSession = Depends(get_async_session),
) -> UserSchema:
    try:
        payload = auth_utils.decode_jwt(
            token=token,
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token error",
        )
    email: str = payload.get("email")
    if not (user := await get_user(email, session)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token invalid",
        )
    if not user.verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user unverified",
        )
    return user


def _create_token():
    pass  # TODO вынести логику создания токена сюда


def create_access_token(
    response: Response,
    user_data: UserSchema = Depends(validate_auth_user),
) -> dict:
    jwt_payload = {
        "sub": user_data.email,
        "email": user_data.email,
    }
    access_token = auth_utils.encode_jwt(jwt_payload, expire_minutes=settings.ACCESS_TOKEN_EXPIRES_IN)
    response.set_cookie(settings.COOKIE_SESSION_ID_KEY, access_token)
    return {"status": "success"}


# TODO Сделать логику рефреш токена.
def create_refresh_token(
    response: Response,
    user_data: UserSchema = Depends(validate_auth_user),
) -> dict:
    jwt_payload = {
        "sub": user_data.email,
        "email": user_data.email,
    }
    access_token = auth_utils.encode_jwt(jwt_payload, expire_minutes=settings.REFRESH_TOKEN_EXPIRES_IN)
    response.set_cookie(settings.COOKIE_SESSION_ID_KEY, access_token)
    return {"status": "success"}
