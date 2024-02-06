import uuid
from datetime import datetime

from pydantic import BaseModel


class TeamPreviewSchema(BaseModel):
    title: str
    # type_team: str = "other"
    number_of_members: int = 1
    tags: str
    deadline_at: datetime


class JoinInTeamSchema(BaseModel):
    team_id: uuid.UUID
    cover_letter: str
