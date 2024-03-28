import uuid
import datetime
from typing import Optional

from pydantic import BaseModel

from src.team.models import Tags


class TeamPreviewSchema(BaseModel):
    id: uuid.UUID
    title: str
    type_team: str
    number_of_members: int
    # tags: Optional[list["Tags"]]
    team_deadline_at: datetime.date
