import uuid

from fastapi import HTTPException, status
from sqlalchemy import and_, delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.auth.models import AuthUser
from src.auth.schemas import ResponseSchema, UserSchema
from src.find.schemas import JoinDataSchema
from src.team.models import Team, application_to_join_table, team_members_table, TeamTags
from src.team.schemas import TeamSchema, TeamTagsSchema
from src.user_profile.models import UserContacts
from src.user_profile.schemas import UserContactsSchema


async def get_teams_list(
    session: AsyncSession,
) -> list[TeamSchema]:
    """Получение списка всех имеющихся команд."""
    query = (select(Team)
             .options(selectinload(Team.members)))
    result = await session.execute(query)
    teams = result.scalars().all()

    for team in teams:
        query_for_tags = (
            select(TeamTags)
            .where(TeamTags.team_id == team.id)
        )
        res = await session.execute(query_for_tags)
        team_tags = res.unique().scalar_one_or_none()
        team.tags = team_tags
    return teams


async def get_team_data(
    team_id: uuid.UUID,
    session: AsyncSession,
) -> TeamSchema | None:
    """Получение данных команды."""
    query_team = (
        select(Team)
        .options(selectinload(Team.members))
        .where(Team.id == team_id)
    )
    result_team_data = (await session.execute(query_team)).unique().scalar_one_or_none()
    if not result_team_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="there is no such team",
        ) from None
    query_tags = (select(TeamTags).where(TeamTags.team_id == team_id))
    result_tags = (await session.execute(query_tags)).unique().scalar_one_or_none()
    tags = TeamTagsSchema(
        tag1=result_tags.tag1,
        tag2=result_tags.tag2,
        tag3=result_tags.tag3,
        tag4=result_tags.tag4,
        tag5=result_tags.tag5,
        tag6=result_tags.tag6,
        tag7=result_tags.tag7,
    )
    query_owner_name = (select(AuthUser).where(AuthUser.id == result_team_data.owner))
    result_owner_name = (await session.execute(query_owner_name)).unique().scalar_one_or_none()
    members = []
    for user_auth_data in result_team_data.members:
        new_data = UserSchema(
            id=user_auth_data.id,
            username=user_auth_data.username,
            email=user_auth_data.email,
            verified=user_auth_data.verified,
        )
        members.append(new_data)
    team = TeamSchema(
        id=result_team_data.id,
        owner=result_team_data.owner,
        owner_name=result_owner_name.username,
        title=result_team_data.title,
        type_team=result_team_data.type_team,
        number_of_members=result_team_data.number_of_members,
        team_description=result_team_data.team_description,
        team_deadline_at=result_team_data.team_deadline_at,
        team_city=result_team_data.team_city,
        created_at=result_team_data.created_at,
        updated_at=result_team_data.updated_at,
        members=members,
        tags=tags,
    )
    return team


async def join_in_team(
    join_data: JoinDataSchema,
    user: UserSchema,
    session: AsyncSession,
) -> ResponseSchema:
    """Подать заявку на вступление в команду."""
    try:
        stmt = insert(application_to_join_table).values(
            {"user_id": user.id,
             "team_id": uuid.UUID(join_data.team_id),
             "cover_letter": join_data.cover_letter},
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

