from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import (
    APIRouter,
    Depends,
    status,
    Response,
    HTTPException,
)

from src.auth.crud import create_user
from src.auth.auth_handler import (
    validate_auth_user,
    get_auth_user,
    create_access_token,
)
from src.auth.schemas import (
    UserSchema,
    LoginUserSchema,
    CreateUserSchema,
)

from src.database import get_async_session
from src.config import settings

auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@auth_router.post("/register")
async def register(
    response: Response,
    user_data: CreateUserSchema,
    session: AsyncSession = Depends(get_async_session),
):
    if await create_user(user_data, session) != {"status": 201}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid user data",
        )
    create_access_token(response, user_data)
    return {
        "status_code": status.HTTP_201_CREATED,
        "username": user_data.username
    }


@auth_router.post("/login")
def login(
    response: Response,
    user: LoginUserSchema = Depends(validate_auth_user),
):
    create_access_token(response, user)
    return {
        "status_code": status.HTTP_200_OK,
        "username": user.username
    }


@auth_router.get("/logout")
def logout(
    response: Response,
    user: UserSchema = Depends(get_auth_user),
):
    response.delete_cookie(settings.COOKIE_SESSION_ID_KEY)
    username = user.username
    return {
        "message": f"Bye, {username}!",
    }


@auth_router.get("/check-cookie/")
def check_cookie(
    user: UserSchema = Depends(get_auth_user),
):
    username = user.username
    return {
        "message": f"Hello, {username}!",
    }
