import uuid

from fastapi import HTTPException, status
from sqlalchemy import insert, select, update, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import ResponseSchema, UserSchema
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
            detail=f"user {user.username} already have one team {user_team.title}",
        )
    full_team_data = {"owner": user.id, **team_data.model_dump()}
    stmt = insert(Team).values(**full_team_data)
    await session.execute(stmt)
    await session.commit()
    return ResponseSchema(
        status_code=status.HTTP_201_CREATED,
        detail="team is created",
    )


async def update_team(
    team_id: uuid.UUID,
    update_data: TeamSchema,
    session: AsyncSession,
    user: UserSchema,
) -> ResponseSchema:
    new_team_data = {**update_data.model_dump()}
    stmt = (
        update(Team)
        .values(new_team_data)
        .where(and_(
            Team.id == team_id,
            Team.owner == user.id
        ))
        .returning(Team)
    )
    await session.execute(stmt)
    await session.commit()
    return ResponseSchema(
        status_code=status.HTTP_200_OK,
        detail="team is updated",
    )


async def delete_team(
    team_id: uuid.UUID,
    session: AsyncSession,
    user: UserSchema,
) -> ResponseSchema:
    if not (team := await get_user_team(user_id=user.id, session=session)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="there is no such team",
        )
    if user.id == team.owner:
        stmt = delete(Team).where(Team.id == team_id)
        await session.execute(stmt)
        await session.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="no access"
        )
    return ResponseSchema(
        status_code=status.HTTP_204_NO_CONTENT,
    )


async def get_user_team(
    user_id: uuid.UUID,
    session: AsyncSession,
) -> TeamSchema | None:
    query = select(Team).where(Team.owner == user_id)
    user_team = await session.execute(query)
    return user_team.scalar_one_or_none()
