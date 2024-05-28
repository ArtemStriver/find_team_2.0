import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, Response, status
from fastapi.security import APIKeyCookie
from jwt import InvalidTokenError
from redis.asyncio import Redis as AsyncRedis
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import utils as auth_utils
from src.auth.crud import change_password, create_user, get_user, get_user_by_id, verify_user_data
from src.auth.models import AuthUser
from src.auth.schemas import CreateUserSchema, LoginUserSchema, PasswordChangeSchema, ResponseSchema, UserSchema
from src.config import settings
from src.database import get_async_session
from src.email_settings import send_email


class AuthHandler:
    cookies_access_scheme = APIKeyCookie(name=settings.COOKIE_ACCESS_TOKEN_KEY)
    cookies_refresh_scheme = APIKeyCookie(name=settings.COOKIE_REFRESH_TOKEN_KEY)

    @classmethod
    async def validate_auth_user(
        cls,
        session: Annotated[AsyncSession, Depends(get_async_session)],
        user_data: LoginUserSchema,
    ) -> AuthUser:
        """Идентификация данных пользователя."""
        unauthenticated_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid username or password",
        )
        user = await get_user(user_data.email, session)
        cls._check_user_data(
            user=user,
            user_password=user_data.password,
            custom_exception=unauthenticated_exception,
        )
        return user

    @staticmethod
    def _check_user_data(
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
        user_id: str = payload.get("sub")
        if not (user := await get_user_by_id(user_id, session)):
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
        access_token = cls.create_access_token(response, user)
        refresh_token = cls.create_refresh_token(response, user)
        return {"access_token": access_token, "refresh_token": refresh_token, "user": UserSchema(**user.__dict__)}

    @staticmethod
    def delete_all_tokens(
        response: Response,
    ) -> None:
        """Удаление всех токенов из браузера пользователя."""
        response.delete_cookie(settings.COOKIE_ACCESS_TOKEN_KEY)
        response.delete_cookie(settings.COOKIE_REFRESH_TOKEN_KEY)

    @classmethod
    async def check_register_user(
        cls,
        user_data: CreateUserSchema,
        session: AsyncSession,
    ) -> bool:
        if not (user := await get_user(user_data.email, session)):
            return False
        if not user.verified:
            token = await cls.generate_email_token(user.id)
            send_email(
                user_email=user.email,
                subject="Подтверждение регистрации",
                content_with_token=f"Для подтверждения email, перейдите по ссылке: "
                                   f"{settings.SERVER_HOST}/auth/verify/{token}",
            )
            return True
        return False

    @classmethod
    async def register_user(
        cls,
        user_data: CreateUserSchema,
        session: AsyncSession,
    ) -> None:
        if not (user := await create_user(user_data, session)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="invalid user data",
            )
        token = await cls.generate_email_token(user.id)
        send_email(
            user_email=user.email,
            subject="Подтверждение регистрации",
            content_with_token=f"Для подтверждения email, перейдите по ссылке: "
                               f"{settings.SERVER_HOST}/auth/verify/{token}",
        )

    @staticmethod
    async def generate_email_token(user_id: str | uuid.UUID):
        token = uuid.uuid4().hex
        redis_key = str(token)
        await redis_client.set(redis_key, str(user_id), ex=900)
        return redis_key

    @staticmethod
    async def verify_user_data(
        token: str,
        session: AsyncSession,
    ) -> AuthUser:
        if not (user_id := await redis_client.get(token)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="invalid data",
            )

        user = await get_user_by_id(user_id, session)
        await verify_user_data(user_id, session)
        await redis_client.delete(token)
        return user

    @classmethod
    async def recover_password(
        cls,
        email: str,
        session: AsyncSession,
    ) -> ResponseSchema:
        if not (user := await get_user(email, session)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="there is no user with this email",
            )
        token = await cls.generate_email_token(user.id)
        send_email(
            user_email=user.email,
            subject="Сброс пароля",
            content_with_token=f"Если вы не хотели менять пароль - проигнорируйте это сообщение!!!\n\n"
                               f"Для сброса пароля, перейдите по ссылке: "
                               f"{settings.CLIENT_HOST}/profile/change_password/{token}",
        )
        return ResponseSchema(
            status_code=status.HTTP_201_CREATED,
            detail="the link for password recovery has been sent to the specified email",
        )

    @staticmethod
    async def change_user_password(
        token: str,
        password_data: PasswordChangeSchema,
        session: AsyncSession,
    ) -> None:
        if not (user_id := await redis_client.get(token)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="invalid data",
            )
        await change_password(user_id, password_data, session)
        await redis_client.delete(token)


current_user = AuthHandler.get_auth_user

redis_client = AsyncRedis.from_url(
    url=settings.db_url_redis,
    db=0,
    decode_responses=True,
)
