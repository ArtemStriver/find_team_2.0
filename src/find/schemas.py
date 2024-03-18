import uuid
from datetime import datetime

from pydantic import BaseModel


class TeamPreviewSchema(BaseModel):
    id: uuid.UUID
    title: str
    type_team: str
    number_of_members: int
    team_tags: str
    team_deadline_at: datetime
