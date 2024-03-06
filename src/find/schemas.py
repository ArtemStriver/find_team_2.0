import uuid
from datetime import datetime

from pydantic import BaseModel


class TeamPreviewSchema(BaseModel):
    id: uuid.UUID
    title: str
    type_team: str
    number_of_members: int
    tags: str
    deadline_at: datetime
