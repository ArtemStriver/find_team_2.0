import datetime
import uuid

from pydantic import BaseModel

from src.team.schemas import TeamTagsSchema


class TeamPreviewSchema(BaseModel):
    id: uuid.UUID
    title: str
    type_team: str
    number_of_members: int
    team_deadline_at: datetime.date
    tags: TeamTagsSchema


class JoinDataSchema(BaseModel):
    team_id: str | uuid.UUID
    cover_letter: str | None
