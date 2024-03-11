import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.auth.schemas import UserSchema


class CreateTeamSchema(BaseModel):
    title: str
    type_team: str = "lifestyle"
    number_of_members: int = 1
    contacts: str
    description: str
    tags: str
    deadline_at: datetime
    city: str = "Интернет"


class TeamSchema(BaseModel):
    id: uuid.UUID
    owner: uuid.UUID
    title: str
    type_team: str
    number_of_members: int
    contacts: str
    description: str
    tags: str
    deadline_at: datetime
    city: str
    created_at: datetime
    updated_at: datetime
    members: Optional[list[UserSchema]]


class MemberSchema(BaseModel):
    team_id: str | uuid.UUID
    user_id: str | uuid.UUID


class ApplicationSchema(BaseModel):
    user_id: str | uuid.UUID
    team_id: str | uuid.UUID
    cover_letter: str | None
