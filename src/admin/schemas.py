import uuid

from pydantic import BaseModel


class MainInfoOfTeamSchema(BaseModel):
    id: uuid.UUID | str
    owner: uuid.UUID | str
    title: str
    description: str
    team_city: str
    tag1: str
    tag2: str
    tag3: str
    tag4: str
    tag5: str
    tag6: str
    tag7: str


class MainInfoOfUserSchema(BaseModel):
    user_id: uuid.UUID | str
    profile_id: uuid.UUID | str
    username: str
    user_self_description: str | None
    link_user_email: str
    link_user_vk: str | None
    link_user_telegram: str | None
    link_user_discord: str | None
    link_user_other: str | None
