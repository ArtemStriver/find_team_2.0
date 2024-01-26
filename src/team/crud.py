import uuid

from fastapi import HTTPException, status
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import UserSchema, ResponseSchema
from src.team.models import Team
from src.team.schemas import CreateTeamSchema, TeamSchema


async def create_team(
    team_data: CreateTeamSchema,
    session: AsyncSession,
    user: UserSchema,
) -> ResponseSchema:
    if user_team := await get_user_team(user_id=user.id, session=session):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"user {user.username} already have one team {user_team.title}"
        )
    print(team_data)
    full_team_data = {"owner": user.id, **team_data.model_dump()}
    print(full_team_data)
    stmt = insert(Team).values(**full_team_data)
    await session.execute(stmt)
    await session.commit()
    return ResponseSchema(
        status_code=status.HTTP_201_CREATED,
        detail=f"team {full_team_data} is create"
    )


async def update_team():
    pass


async def delete_team():
    pass


async def get_user_team(
    user_id: uuid.UUID,
    session: AsyncSession,
) -> TeamSchema | None:
    query = select(Team).where(Team.owner == user_id)
    user_team = await session.execute(query)
    return user_team.scalar_one_or_none()
