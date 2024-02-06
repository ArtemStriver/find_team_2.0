import uuid
from typing import Annotated

from annotated_types import MaxLen, MinLen
from pydantic import BaseModel, EmailStr


# TODO необходимо убрать пароль из схемы пользователя, сделать как в проекте мир.
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
