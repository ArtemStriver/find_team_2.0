import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, Response, status
from sqlalchemy import and_, delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import crud as auth_crud
from src.auth.models import AuthUser
from src.auth.schemas import ResponseSchema, UserSchema
from src.team.models import Team, TeamTags, team_members_table
from src.team.schemas import TeamSchema
from src.user_profile.models import UserContacts, UserHobbies, UserProfile
from src.user_profile.schemas import UpdateProfileSchema, UserContactsSchema, UserHobbiesSchema, UserProfileSchema


async def get_user_profile(
    user_id: uuid.UUID,
    session: AsyncSession,
) -> UserProfileSchema | None:
    try:
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
        query_for_hobbies = select(UserHobbies).where(UserHobbies.user_id == user_id)
        result_hobbies = (await session.execute(query_for_hobbies)).scalar_one_or_none()
        user_hobbies = UserHobbiesSchema(
            lifestyle1=result_hobbies.lifestyle1,
            lifestyle2=result_hobbies.lifestyle2,
            lifestyle3=result_hobbies.lifestyle3,
            sport1=result_hobbies.sport1,
            sport2=result_hobbies.sport2,
            sport3=result_hobbies.sport3,
            work1=result_hobbies.work1,
            work2=result_hobbies.work2,
            work3=result_hobbies.work3,
        )
        username = (await auth_crud.get_user_by_id(user_id, session)).username
        return UserProfileSchema(
            id=user_profile.id,
            user_id=user_profile.user_id,
            username=username,
            image_path=user_profile.image_path,
            contacts=user_contacts,
            description=user_profile.description,
            hobbies=user_hobbies,
        )
    except Exception:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="cannot get profile data",
        ) from None


async def create_user_profile(
    user: UserSchema,
    session: AsyncSession,
) -> None:
    if await get_user_profile(user.id, session) is None:
        stmt = insert(UserProfile).values(
            {
                "user_id": user.id,
                "image_path": "images/default.jpg",
                "description": "Your description",
            },
        )
        await session.execute(stmt)
        stmt = insert(UserContacts).values(
            {
                "user_id": user.id,
                "email": user.email,
            },
        )
        await session.execute(stmt)
        stmt = insert(UserHobbies).values(
            {
                "user_id": user.id,
            },
        )
        await session.execute(stmt)
        await session.commit()


async def change_user_profile(
    updated_data: UpdateProfileSchema,
    user: UserSchema,
    session: AsyncSession,
) -> ResponseSchema:
    from src.auth.crud import get_user

    user_data = await get_user(updated_data.username, session)
    if user_data and user_data.id != user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user with that name already exists",
        )
    stmt_user = update(AuthUser).values({
        "username": updated_data.username,
        "updated_at": datetime.now(timezone.utc).replace(tzinfo=None),
    }).where(
        AuthUser.id == user.id,
    )
    stmt_profile = update(UserProfile).values({
        "image_path": updated_data.image_path,
        "description": updated_data.description,
    }).where(and_(
        UserProfile.user_id == user.id,
    ))
    stmt_contacts = update(UserContacts).values({
        "vk": updated_data.contacts.vk,
        "telegram": updated_data.contacts.telegram,
        "discord": updated_data.contacts.discord,
        "other": updated_data.contacts.other,
    }).where(and_(
        UserContacts.user_id == user.id,
    ))
    stmt_hobbies = update(UserHobbies).values({
        "lifestyle1": updated_data.hobbies.lifestyle1,
        "lifestyle2": updated_data.hobbies.lifestyle2,
        "lifestyle3": updated_data.hobbies.lifestyle3,
        "sport1": updated_data.hobbies.sport1,
        "sport2": updated_data.hobbies.sport2,
        "sport3": updated_data.hobbies.sport3,
        "work1": updated_data.hobbies.work1,
        "work2": updated_data.hobbies.work2,
        "work3": updated_data.hobbies.work3,
    }).where(and_(
        UserHobbies.user_id == user.id,
    ))
    await session.execute(stmt_user)
    await session.execute(stmt_profile)
    await session.execute(stmt_contacts)
    await session.execute(stmt_hobbies)
    await session.commit()
    return ResponseSchema(
        status_code=status.HTTP_200_OK,
        detail="profile is updated",
    )


async def delete_user_profile(
    user: UserSchema,
    session: AsyncSession,
    response: Response,
) -> ResponseSchema:
    user_profile = await get_user_profile(user.id, session)
    if user_profile is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="there is no such user or profile",
        )
    stmt_profile = delete(UserProfile).where(
        and_(UserProfile.id == user_profile.id, UserProfile.user_id == user.id),
    )
    stmt_user = delete(AuthUser).where(AuthUser.id == user.id)
    stmt_contacts = delete(UserContacts).where(UserContacts.user_id == user.id)
    stmt_hobbies = delete(UserHobbies).where(UserHobbies.user_id == user.id)
    await session.execute(stmt_contacts)
    await session.execute(stmt_hobbies)
    await session.execute(stmt_profile)
    await session.execute(stmt_user)
    await session.commit()

    from src.auth.auth_handler import AuthHandler
    AuthHandler.delete_all_tokens(response)

    return ResponseSchema(
        status_code=status.HTTP_200_OK,
        detail="user and his profile deleted",
    )


async def get_teams_where_user_is_on(
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
    for team in teams:
        query_for_tags = (
            select(TeamTags)
            .where(TeamTags.team_id == team.id)
        )
        res = await session.execute(query_for_tags)
        team_tags = res.unique().scalar_one_or_none()
        team.tags = team_tags
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
    teams = (await session.execute(query)).scalars().all()
    for team in teams:
        query_for_tags = (
            select(TeamTags)
            .where(TeamTags.team_id == team.id)
        )
        res = await session.execute(query_for_tags)
        team_tags = res.unique().scalar_one_or_none()
        team.tags = team_tags
    return teams
