import uuid

from pydantic import BaseModel


class UserProfileSchema(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    image_path: str
    contacts: str
    description: str
    hobbies: str


class UpdateProfileSchema(BaseModel):
    username: str
    image_path: str
    contacts: str
    description: str
    hobbies: str
