import uuid
from datetime import datetime

from pydantic import BaseModel


class CreateTeamSchema(BaseModel):
    title: str
    # type_team: str = "other"
    number_of_members: int
    contacts: str
    description: str
    tags: str
    deadline_at: datetime


class TeamSchema(BaseModel):
    id: uuid.UUID
    owner: uuid.UUID
    title: str
    # type_team: str
    number_of_members: int
    contacts: str
    description: str
    tags: str
    deadline_at: datetime
    created_at: datetime
    updated_at: datetime

