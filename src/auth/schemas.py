import uuid
from typing import Annotated

from annotated_types import MaxLen, MinLen
from pydantic import BaseModel, EmailStr


class UserSchema(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    verified: bool


class CreateUserSchema(BaseModel):
    username: str
    email: EmailStr
    hashed_password: Annotated[str, MinLen(6), MaxLen(24)]
    confirmed_password: str


class LoginUserSchema(BaseModel):
    email: EmailStr | str
    password: str


class ResponseSchema(BaseModel):
    status_code: int
    detail: str


class PasswordChangeSchema(BaseModel):
    hashed_password: Annotated[str, MinLen(6), MaxLen(24)]
    confirmed_password: str
