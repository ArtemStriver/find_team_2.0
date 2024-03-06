import uuid
from typing import Annotated

from annotated_types import MaxLen, MinLen
from pydantic import BaseModel, EmailStr


class UserSchema(BaseModel):
    id: uuid.UUID
    username: str | None = None
    email: EmailStr
    verified: bool


class CreateUserSchema(BaseModel):
    username: str | None = None
    email: EmailStr
    hashed_password: Annotated[str, MinLen(6), MaxLen(24)]
    confirmed_password: str


class LoginUserSchema(BaseModel):
    email: EmailStr
    password: str


class ResponseSchema(BaseModel):
    status_code: int
    detail: str
