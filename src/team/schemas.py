import uuid
import datetime
from typing import Optional

from pydantic import BaseModel

from src.auth.schemas import UserSchema
from src.user_profile.schemas import UserContactsSchema


class TeamTagsSchema(BaseModel):
    tag1: str | None
    tag2: str | None
    tag3: str | None
    tag4: str | None
    tag5: str | None
    tag6: str | None
    tag7: str | None


class CreateTeamSchema(BaseModel):
    title: str
    type_team: str = "lifestyle"
    number_of_members: int = 1
    team_description: str
    team_deadline_at: datetime.date
    team_city: str = "Интернет"
    tags: TeamTagsSchema


class TeamSchema(BaseModel):
    id: uuid.UUID
    owner: uuid.UUID
    owner_name: str
    title: str
    type_team: str
    number_of_members: int
    team_description: str
    team_deadline_at: datetime.date
    team_city: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    members: Optional[list[UserSchema]]
    tags: TeamTagsSchema


class MemberSchema(BaseModel):
    team_id: str | uuid.UUID
    user_id: str | uuid.UUID


class ApplicationSchema(BaseModel):
    user_id: str | uuid.UUID
    team_id: str | uuid.UUID
    cover_letter: str | None
