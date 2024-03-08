import uuid

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.team.models import Team, team_members_table
from src.team.schemas import TeamSchema


async def get_teams(
    user_id: uuid.UUID,
    session: AsyncSession,
) -> list[TeamSchema]:
    """Получение команд, в которых состоит пользователь."""
    query = select(team_members_table).where(team_members_table.c.user_id == user_id)
    team_list = (await session.execute(query)).all()
    teams = []
    for _, team_id in team_list:
        query = (
            select(Team)
            .where(Team.id == team_id)
        )
        team = (await session.execute(query)).scalar_one_or_none()
        teams.append(team)
    # TODO переделать, и придумать что-нибудь лучше, чем этот костыль.
    return teams


async def get_user_teams(
    user_id: uuid.UUID,
    session: AsyncSession,
) -> list[TeamSchema]:
    """Получение команд пользователя."""
    query = (
        select(Team)
        .where(Team.owner == user_id)
    )
    user_teams = await session.execute(query)
    return user_teams.scalars().all()


async def get_user_team(
    team_id: uuid.UUID,
    user_id: uuid.UUID,
    session: AsyncSession,
) -> TeamSchema | None:
    """Получение команды пользователя."""
    query = (
        select(Team)
        .options(selectinload(Team.members))
        .where(
            and_(
                Team.id == team_id,
                Team.owner == user_id,
            ),
        )
    )
    user_team = await session.execute(query)
    return user_team.unique().scalar_one_or_none()

