import uuid
from datetime import timedelta
from typing import Annotated

from annotated_types import MinLen, MaxLen
from pydantic import BaseModel, EmailStr, ConfigDict


class UserSchema(BaseModel):
    model_config = ConfigDict(strict=True)

    username: str | None = None
    email: EmailStr
    hashed_password: bytes | str
    verified: bool = True


class CreateUserSchema(BaseModel):
    username: str | None = None
    email: EmailStr
    hashed_password: Annotated[str, MinLen(6), MaxLen(24)]
    confirmed_password: str
    verified: bool = True


class LoginUserSchema(BaseModel):
    email: EmailStr
    password: str


class TokenInfo(BaseModel):
    access_token: str
    token_type: str
