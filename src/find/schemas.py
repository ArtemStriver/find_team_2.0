import uuid
from datetime import datetime

from pydantic import BaseModel


class TeamPreviewSchema(BaseModel):
    id: uuid.UUID
    title: str
    # type_team: str = "other"
    number_of_members: int = 1
    tags: str
    deadline_at: datetime
