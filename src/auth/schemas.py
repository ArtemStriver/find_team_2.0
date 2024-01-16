import uuid

from fastapi_users import schemas
from fastapi_users.schemas import CreateUpdateDictModel
from pydantic import EmailStr


class UserCreateOutput(schemas.BaseUser[uuid.UUID]):
    id: uuid.UUID
    email: str
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    class Config:
        from_attributes = True


class UserCreateInput(CreateUpdateDictModel):
    email: EmailStr
    password: str
