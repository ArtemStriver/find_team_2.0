import uuid
from typing import Annotated

from sqlalchemy import select, and_, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import status, HTTPException, Form

from src.auth.schemas import UserSchema, ResponseSchema
from src.team.models import Team, application_to_join_table, team_members_table
from src.team.schemas import TeamSchema


async def get_teams_list(
    user: UserSchema,
    session: AsyncSession,
) -> list[TeamSchema]:
    query = (select(Team)
             .options(selectinload(Team.members))
             .where(Team.owner != user.id))
    result = await session.execute(query)
    return result.scalars().all()


async def get_team_data(
    team_id: uuid.UUID,
    session: AsyncSession,
) -> TeamSchema | None:
    """Получение данных команды."""
    # TODO нужно будет добавить проверку доступа пользователя к данной команде - задел на приватизацию проекта.
    query = (
        select(Team)
        .options(selectinload(Team.members))
        .where(Team.id == team_id)
    )
    team = await session.execute(query)
    return team.unique().scalar_one_or_none()


async def join_in_team(
    team_id: uuid.UUID,
    cover_letter: str | None,
    user: UserSchema,
    session: AsyncSession,
) -> ResponseSchema:
    """Подать заявку на вступление в команду."""
    try:
        stmt = insert(application_to_join_table).values(
            {"user_id": user.id,
             "team_id": team_id,
             "cover_letter": cover_letter},
        )
        await session.execute(stmt)
        await session.commit()
        return ResponseSchema(
            status_code=status.HTTP_200_OK,
            detail="your application has been submitted",
        )
    except Exception:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid data",
        ) from None


async def leave_team(
    team_id: uuid.UUID,
    user: UserSchema,
    session: AsyncSession,
) -> ResponseSchema:
    """Покинуть команду."""
    stmt = delete(team_members_table).where(
        and_(
            team_members_table.c.user_id == user.id,
            team_members_table.c.team_id == team_id,
        ),
    )
    await session.execute(stmt)
    await session.commit()
    return ResponseSchema(
        status_code=status.HTTP_200_OK,
        detail="you leaved the team",
    )

