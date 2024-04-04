import uuid

from pydantic import BaseModel


class UserContactsSchema(BaseModel):
    email: str
    vk: str | None = None
    telegram: str | None = None
    discord: str | None = None
    other: str | None = None


class UserHobbiesSchema(BaseModel):
    lifestyle1: str | None = None
    lifestyle2: str | None = None
    lifestyle3: str | None = None
    sport1: str | None = None
    sport2: str | None = None
    sport3: str | None = None
    work1: str | None = None
    work2: str | None = None
    work3: str | None = None


class UserProfileSchema(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    username: str
    image_path: str
    contacts: UserContactsSchema
    description: str
    hobbies: UserHobbiesSchema


class UpdateProfileSchema(BaseModel):
    username: str
    image_path: str
    contacts: UserContactsSchema
    description: str
    hobbies: UserHobbiesSchema
