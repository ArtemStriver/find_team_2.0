import uuid
from typing import Annotated

from annotated_types import MinLen, MaxLen
from pydantic import BaseModel, EmailStr


class UserSchema(BaseModel):
    id: uuid.UUID
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


class ResponseSchema(BaseModel):
    status_code: int
    detail: str


class TokenInfo(BaseModel):
    access_token: str
    token_type: str
