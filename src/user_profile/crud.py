import uuid
from datetime import datetime, timezone

from fastapi import status, HTTPException, Response
from sqlalchemy import and_, select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import AuthUser
from src.auth.schemas import UserSchema, ResponseSchema
from src.team.models import Team, team_members_table
from src.team.schemas import TeamSchema
from src.user_profile.models import UserProfile, UserContacts, UserHobbies
from src.user_profile.schemas import UserProfileSchema, UpdateProfileSchema


async def get_user_profile(
    user_id: uuid.UUID,
    session: AsyncSession,
) -> UserProfileSchema | None:
    query = select(UserProfile).where(UserProfile.user_id == user_id)
    user_profile = await session.execute(query)
    return user_profile.scalar_one_or_none()


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
            }
        )
        await session.execute(stmt)
        stmt = insert(UserContacts).values(
            {
                "user_id": user.id,
                "email": user.email,
            }
        )
        await session.execute(stmt)
        stmt = insert(UserHobbies).values(
            {
                "user_id": user.id,
            }
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
        and_(UserProfile.id == user_profile.id, UserProfile.user_id == user.id)
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
