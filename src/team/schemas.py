import uuid
import datetime
from typing import Optional

from pydantic import BaseModel

from src.auth.schemas import UserSchema
from src.team.models import Tags
from src.user_profile.models import Contact


class TagSchema(BaseModel):
    tag_name: str

    class Config:
        orm_mode = True


class CreateTeamSchema(BaseModel):
    title: str
    type_team: str = "lifestyle"
    number_of_members: int = 1
    team_description: str
    team_deadline_at: datetime.date
    team_city: str = "Интернет"
    # tags: list[TagSchema]
    # contacts: Contact


class TeamSchema(BaseModel):
    id: uuid.UUID
    owner: uuid.UUID
    title: str
    type_team: str
    number_of_members: int
    team_description: str
    team_deadline_at: datetime.date
    team_city: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    members: Optional[list[UserSchema]]
    # tags: list[TagSchema]
    # contacts: Contact


class MemberSchema(BaseModel):
    team_id: str | uuid.UUID
    user_id: str | uuid.UUID


class ApplicationSchema(BaseModel):
    user_id: str | uuid.UUID
    team_id: str | uuid.UUID
    cover_letter: str | None
