from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.auth_handler import AuthHandler, current_user
from src.auth.schemas import (
    CreateUserSchema,
    LoginUserSchema,
    ResponseSchema,
    UserSchema,
)
from src.database import get_async_session

auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


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
    if await AuthHandler.check_register_user(user_data, session):
        return ResponseSchema(
            status_code=status.HTTP_200_OK,
            detail="message was sent again",
        )
    else:
        await AuthHandler.register_user(user_data, session)
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
    user = await AuthHandler.verify_user_data(token, session)
    AuthHandler.create_all_tokens(response, user)
    return ResponseSchema(
        status_code=status.HTTP_200_OK,
        detail=user.username,
    )
