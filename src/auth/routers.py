import smtplib
import uuid
from email.message import EmailMessage
from redis.asyncio import Redis as AsyncRedis
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import crud
from src.auth.auth_handler import AuthHandler, current_user
from src.auth.crud import create_user, get_user
from src.auth.models import AuthUser
from src.auth.schemas import (
    CreateUserSchema,
    LoginUserSchema,
    ResponseSchema,
    UserSchema,
)
from src.config import settings
from src.database import get_async_session

auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

redis_client = AsyncRedis.from_url(
            url=settings.db_url_redis,
            db=0,
            decode_responses=True,
        )


def get_email(user_email: str, token: str):
    email = EmailMessage()
    email['Subject'] = "Подтверждение регистрации"
    email['From'] = "artemstriver@gmail.com"
    email['To'] = user_email

    email.set_content(
        # TODO исправить текст сообщения + ссылка не работает!!!!
        f"Для подтверждения email, перейдите по ссылке: http://127.0.0.1:8000/auth/verify/{token}",
    )
    return email


def send_email(user_email: str, token: str):
    email = get_email(user_email, token)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login("artemstriver@gmail.com", "pttv foby vrfs puiz")
        server.send_message(email)


@auth_router.post(
    "/register",
    response_model=ResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_data: CreateUserSchema,
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    """Регистрация нового пользователя c отправкой ему сообщению для подтверждения почты."""
    if user := await get_user(user_data.email, session):
        if not user.verified:
            token = uuid.uuid4().hex
            redis_key = str(token)
            await redis_client.set(redis_key, str(user.id), ex=600)
            send_email(user.email, token)
            return ResponseSchema(
                status_code=status.HTTP_200_OK,
                detail="message was sent again",
            )
    if not (user := await create_user(user_data, session)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid user data",
        )
    token = uuid.uuid4().hex
    redis_key = str(token)
    await redis_client.set(redis_key, str(user.id), ex=600)
    send_email(user.email, token)
    return ResponseSchema(
        status_code=status.HTTP_201_CREATED,
        detail="to complete the registration, confirm your emai",
    )


@auth_router.post(
    "/login",
    response_model=ResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def login(
    response: Response,
    user: Annotated[LoginUserSchema, Depends(AuthHandler.validate_auth_user)],
) -> ResponseSchema:
    """Проверка и вход пользователя c выдачей ему access и refresh token."""
    AuthHandler.create_all_tokens(response, user)
    return ResponseSchema(
        status_code=status.HTTP_200_OK,
        detail=user.username,
    )


@auth_router.get(
    "/refresh",
    response_model=ResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def refresh_token(
    response: Response,
    user: Annotated[UserSchema, Depends(AuthHandler.check_user_refresh_token)],
) -> ResponseSchema:
    """Обновление access_token при наличии действующего refresh_token."""
    AuthHandler.create_all_tokens(response, user)
    return ResponseSchema(
        status_code=status.HTTP_200_OK,
        detail=user.username,
    )


@auth_router.get(
    "/logout",
    response_model=ResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def logout(
    response: Response,
    user: Annotated[UserSchema, Depends(current_user)],
) -> ResponseSchema:
    """Выход пользователя c удалением файлов куки из браузера."""
    AuthHandler.delete_all_tokens(response)
    username = user.username
    return ResponseSchema(
        status_code=status.HTTP_200_OK,
        detail=f"Bye, {username}!",
    )


@auth_router.patch(
    "/verify/{token}",
    response_model=ResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def verify(
    token: str,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> ResponseSchema:
    """Проверка подлинности email адреса пользователя."""
    if not (user_id := await redis_client.get(token)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid data",
        )
    user = await crud.get_user_by_id(user_id, session) # TODO зачем нужно получать юзера?
    stmt = update(AuthUser).values({"verified": True}).where(AuthUser.id == user_id)
    await session.execute(stmt)
    await session.commit()

    await redis_client.delete(token)

    AuthHandler.create_all_tokens(response, user)
    return ResponseSchema(
        status_code=status.HTTP_200_OK,
        detail=user.username,
    )
