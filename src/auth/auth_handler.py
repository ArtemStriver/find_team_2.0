from typing import Annotated

from fastapi import Depends, Form, HTTPException, Response, status
from fastapi.security import APIKeyCookie
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import utils as auth_utils
from src.auth.crud import get_user
from src.auth.models import AuthUser
from src.auth.schemas import UserSchema
from src.config import settings
from src.database import get_async_session


class AuthHandler:
    cookies_access_scheme = APIKeyCookie(name=settings.COOKIE_ACCESS_TOKEN_KEY)
    cookies_refresh_scheme = APIKeyCookie(name=settings.COOKIE_REFRESH_TOKEN_KEY)

    @classmethod
    async def validate_auth_user(
        cls,
        session: Annotated[AsyncSession, Depends(get_async_session)],
        email: str = Form(),
        password: str = Form(),
    ) -> AuthUser:
        """Идентификация данных пользователя."""
        unauthenticated_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid username or password",
        )
        user = await get_user(email, session)
        cls._verify_user(
            user=user,
            user_password=password,
            custom_exception=unauthenticated_exception,
        )
        return user

    @staticmethod
    def _verify_user(
        user: AuthUser,
        user_password: str | bytes,
        custom_exception: HTTPException,
    ) -> None:
        if not user:
            raise custom_exception
        if not auth_utils.validate_password(
            password=user_password,
            hashed_password=user.hashed_password,
        ):
            raise custom_exception
        if not user.verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="user unverified",
            )

    @classmethod
    async def get_auth_user(
        cls,
        session: Annotated[AsyncSession, Depends(get_async_session)],
        access_token: str = Depends(cookies_access_scheme),
    ) -> UserSchema:
        """
        Получение данных аутентифицированного пользователя.
        Функция проверяет подлинность пользователя и дает
        доступ к использованию закрытых эндпоинтов.
        """
        try:
            payload = auth_utils.decode_jwt(
                token=access_token,
            )
            return await cls._check_token_data(payload, session)
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid token error",
            ) from None

    @classmethod
    async def check_user_refresh_token(
        cls,
        refresh_token: Annotated[str, Depends(cookies_refresh_scheme)],
        session: Annotated[AsyncSession, Depends(get_async_session)],
    ) -> AuthUser:
        """Проверка refresh token на подлинность."""
        try:
            payload = auth_utils.decode_jwt(
                token=refresh_token,
            )
            user = await cls._check_token_data(payload, session)
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="could not refresh access token",
            ) from None
        return user

    @staticmethod
    async def _check_token_data(
        payload: dict,
        session: AsyncSession,
    ) -> AuthUser:
        """Функция проверки данных токена."""
        if not payload.get("sub"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="could not refresh access token",
            ) from None
        email: str = payload.get("email")
        if not (user := await get_user(email, session)):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="the user no longer exists",
            ) from None
        if not user.verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="user unverified",
            ) from None
        return user

    @staticmethod
    def _create_token(
        response: Response,
        type_token: str,
        expires_time: int,
        data: UserSchema,
    ) -> str:
        """Функция создания токена по заданным параметрам."""
        jwt_payload = {
            "sub": str(data.id),
            "email": data.email,
            "type": type_token,
        }
        token = auth_utils.encode_jwt(jwt_payload, expire_minutes=expires_time)
        response.set_cookie(type_token, token, httponly=True, secure=False)
        return token

    @classmethod
    def create_access_token(
        cls,
        response: Response,
        user_data: Annotated[UserSchema, Depends(validate_auth_user)],
    ) -> str:
        """Создание access_token."""
        return cls._create_token(
            response=response,
            type_token=settings.COOKIE_ACCESS_TOKEN_KEY,
            expires_time=settings.ACCESS_TOKEN_EXPIRES_IN,
            data=user_data,
        )

    @classmethod
    def create_refresh_token(
        cls,
        response: Response,
        user_data: Annotated[UserSchema, Depends(validate_auth_user)],
    ) -> dict:
        """Создание refresh_token."""
        return cls._create_token(
            response=response,
            type_token=settings.COOKIE_REFRESH_TOKEN_KEY,
            expires_time=settings.REFRESH_TOKEN_EXPIRES_IN,
            data=user_data,
        )

    @classmethod
    def create_all_tokens(
        cls,
        response: Response,
        user: AuthUser,
    ) -> None:
        """Создание всех токенов пользователя."""
        cls.create_access_token(response, user)
        cls.create_refresh_token(response, user)

    @staticmethod
    def delete_all_tokens(
        response: Response,
    ) -> None:
        """Удаление всех токенов из браузера пользователя."""
        response.delete_cookie(settings.COOKIE_ACCESS_TOKEN_KEY)
        response.delete_cookie(settings.COOKIE_REFRESH_TOKEN_KEY)


current_user = AuthHandler.get_auth_user
