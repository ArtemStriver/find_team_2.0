from fastapi import Form, Depends, HTTPException, status, Response, Cookie
from fastapi.security import APIKeyCookie
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.crud import get_user
from src.auth import utils as auth_utils
from src.auth.schemas import UserSchema, ResponseSchema
from src.database import get_async_session
from src.config import settings

cookies_access_scheme = APIKeyCookie(name=settings.COOKIE_ACCESS_TOKEN_KEY)
cookies_refresh_scheme = APIKeyCookie(name=settings.COOKIE_REFRESH_TOKEN_KEY)


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
    access_token: str = Depends(cookies_access_scheme),
    session: AsyncSession = Depends(get_async_session),
) -> UserSchema:
    try:
        payload = auth_utils.decode_jwt(
            token=access_token,
        )
        user = await _check_token_data(payload, session)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"invalid token error",
        )
    return user


async def check_user_refresh_token(
    refresh_token: str = Depends(cookies_refresh_scheme),
    session: AsyncSession = Depends(get_async_session),
) -> UserSchema:
    try:
        payload = auth_utils.decode_jwt(
            token=refresh_token,
        )
        user = await _check_token_data(payload, session)
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"could not refresh access token: {e}"
        )
    return user


async def _check_token_data(
    payload: dict,
    session: AsyncSession,
) -> UserSchema:
    if not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="could not refresh access token",
        )
    email: str = payload.get("email")
    if not (user := await get_user(email, session)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="the user no longer exists",
        )
    if not user.verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user unverified",
        )
    return user


def _create_token(
    response: Response,
    type_token: str,
    expires_time: int,
    data: UserSchema,
) -> str:
    jwt_payload = {
        "sub": str(data.id),
        "email": data.email,
        "type": type_token,
    }
    token = auth_utils.encode_jwt(jwt_payload, expire_minutes=expires_time)
    response.set_cookie(type_token, token)
    return token


def create_access_token(
    response: Response,
    user_data: UserSchema = Depends(validate_auth_user),
) -> str:
    return _create_token(
        response=response,
        type_token=settings.COOKIE_ACCESS_TOKEN_KEY,
        expires_time=settings.ACCESS_TOKEN_EXPIRES_IN,
        data=user_data,
    )


def create_refresh_token(
    response: Response,
    user_data: UserSchema = Depends(validate_auth_user),
) -> dict:
    return _create_token(
        response=response,
        type_token=settings.COOKIE_REFRESH_TOKEN_KEY,
        expires_time=settings.REFRESH_TOKEN_EXPIRES_IN,
        data=user_data,
    )


def delete_all_tokens(
    response: Response,
) -> None:
    response.delete_cookie(settings.COOKIE_ACCESS_TOKEN_KEY)
    response.delete_cookie(settings.COOKIE_REFRESH_TOKEN_KEY)
