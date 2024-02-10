import uuid

from fastapi import HTTPException, status
from sqlalchemy import and_, delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.auth.schemas import ResponseSchema, UserSchema
from src.team.models import Team, application_to_join_table, team_members_table
from src.team.schemas import TeamSchema


async def get_teams_list(
    session: AsyncSession,
) -> list[TeamSchema]:
    """Получение списка всех имеющихся команд."""
    query = (select(Team)
             .options(selectinload(Team.members)))
    result = await session.execute(query)
    return result.scalars().all()


async def get_team_data(
    team_id: uuid.UUID,
    session: AsyncSession,
) -> TeamSchema | None:
    """Получение данных команды."""
    query = (
        select(Team)
        .options(selectinload(Team.members))
        .where(Team.id == team_id)
    )
    result = await session.execute(query)
    team = result.unique().scalar_one_or_none()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="there is no such team",
        ) from None
    return team


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
    query = select(team_members_table).where(
        and_(
            team_members_table.c.user_id == user.id,
            team_members_table.c.team_id == team_id,
        ),
    )
    check = await session.execute(query)
    if not check.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="there is no such user in the team",
        ) from None

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

