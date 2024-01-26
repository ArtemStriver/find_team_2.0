import uuid
from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import text


class CreateTeamSchema(BaseModel):
    title: str
    type_team: str = "other"
    number_of_members: int
    contacts: str
    description: str
    tags: str
    deadline_at: datetime


class TeamSchema(BaseModel):
    id: uuid.UUID
    owner: str
    title: str
    type_team: str
    number_of_members: int
    contacts: str
    description: text
    tags: str
    deadline_at: datetime
    created_at: datetime
    updated_at: datetime

