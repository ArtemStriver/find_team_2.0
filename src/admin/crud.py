import uuid

from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.admin.schemas import MainInfoOfTeamSchema, MainInfoOfUserSchema
from src.auth import crud as auth_crud
from src.auth.models import AuthUser
from src.auth.schemas import ResponseSchema, UserSchema
from src.find.crud import get_team_data
from src.team.models import Team, TeamTags
from src.team.schemas import TeamSchema, TeamTagsSchema
from src.user_profile.crud import get_user_profile
from src.user_profile.models import UserContacts, UserProfile
from src.user_profile.schemas import UserContactsSchema


async def get_all_users(
    session: AsyncSession,
) -> list[UserSchema]:
    query = select(AuthUser)
    result = await session.execute(query)
    return result.scalars().all()


async def get_all_teams(
    session: AsyncSession,
) -> list[MainInfoOfTeamSchema]:
    query = select(
        Team.id,
        Team.owner,
        Team.title,
        Team.team_description,
        Team.team_city,
        TeamTags.tag1, TeamTags.tag2, TeamTags.tag3, TeamTags.tag4, TeamTags.tag5, TeamTags.tag6, TeamTags.tag7,
    ).join(TeamTags, TeamTags.team_id == Team.id)
    result = (await session.execute(query)).all()
    teams = []
    for team_data in result:
        teams.append(MainInfoOfTeamSchema(
            id=str(team_data[0]),
            owner=str(team_data[1]),
            title=team_data[2],
            description=team_data[3],
            team_city=team_data[4],
            tag1=team_data[5],
            tag2=team_data[6],
            tag3=team_data[7],
            tag4=team_data[8],
            tag5=team_data[9],
            tag6=team_data[10],
            tag7=team_data[11],
        ))
    return teams


async def search_user_data(
    user_id: str | None,
    session: AsyncSession,
) -> MainInfoOfUserSchema | None:
    query_for_profile = select(UserProfile).where(UserProfile.user_id == user_id)
    result_profile = await session.execute(query_for_profile)
    user_profile = result_profile.scalar_one_or_none()
    if user_profile is None:
        return None

    query_for_contacts = select(UserContacts).where(UserContacts.user_id == user_id)
    result_contacts = (await session.execute(query_for_contacts)).scalar_one_or_none()
    user_contacts = UserContactsSchema(
        email=result_contacts.email,
        vk=result_contacts.vk,
        telegram=result_contacts.telegram,
        discord=result_contacts.discord,
        other=result_contacts.other,
    )
    username = (await auth_crud.get_user_by_id(user_id, session)).username
    return MainInfoOfUserSchema(
        user_id=user_id,
        profile_id=user_profile.id,
        username=username,
        user_self_description=user_profile.description,
        link_user_email=user_contacts.email,
        link_user_vk=user_contacts.vk,
        link_user_telegram=user_contacts.telegram,
        link_user_discord=user_contacts.discord,
        link_user_other=user_contacts.other,
    )


async def search_team_data(
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
    return TeamSchema(
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
        members=None,
        tags=tags,
    )


async def delete_user(
    user_id: str | uuid.UUID,
    session: AsyncSession,
) -> ResponseSchema:
    user_profile = await get_user_profile(user_id, session)
    if user_profile is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="there is no such user or profile",
        )
    if user_id == user_profile.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="you cannot delete your profile",
        )
    stmt_user = delete(AuthUser).where(AuthUser.id == user_id)
    await session.execute(stmt_user)
    await session.commit()

    return ResponseSchema(
        status_code=status.HTTP_200_OK,
        detail="user and his profile deleted",
    )


async def delete_team(
    team_id: str | uuid.UUID,
    session: AsyncSession,
) -> ResponseSchema:
    if not (await get_team_data(team_id=team_id, session=session)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="there is no such team",
        )
    stmt = delete(Team).where(Team.id == team_id)
    await session.execute(stmt)
    await session.commit()
    return ResponseSchema(
        status_code=status.HTTP_200_OK,
        detail="team deleted",
    )
