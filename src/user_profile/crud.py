import uuid

from fastapi import status, HTTPException, Response
from sqlalchemy import and_, select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.auth.models import AuthUser
from src.auth.schemas import UserSchema, ResponseSchema
from src.team.models import Team, team_members_table
from src.team.schemas import TeamSchema
from src.user_profile.models import UserProfile
from src.user_profile.schemas import UserProfileSchema, UpdateProfileSchema


async def get_profile(
    user_id: uuid.UUID,
    session: AsyncSession,
) -> UserProfileSchema | None:
    query = select(UserProfile).where(UserProfile.user_id == user_id)
    user_profile = await session.execute(query)
    return user_profile.scalar_one_or_none()


async def create_profile(
    user: UserSchema,
    session: AsyncSession,
) -> None:
    if await get_profile(user.id, session) is None:
        stmt = insert(UserProfile).values(
            {
                "user_id": user.id,
                "image_path": "images/default.jpg",
                "contacts": user.email,
                "description": "Your description",
                "hobby": "Sport, Lifestyle, Work",
            }
        )
        await session.execute(stmt)
        await session.commit()


async def change_profile(
    updated_data: UpdateProfileSchema,
    user: UserSchema,
    session: AsyncSession,
) -> ResponseSchema:
    stmt_profile = update(UserProfile).values({
        "image_path": updated_data.image_path,
        "contacts": updated_data.contacts,
        "description": updated_data.contacts,
        "hobby": updated_data.hobby,
        "city": updated_data.city,
    }).where(and_(
        UserProfile.user_id == user.id,
    ))
    stmt_user = update(AuthUser).values({
        "username": updated_data.username,
    }).where(
        AuthUser.id == user.id,
    )
    await session.execute(stmt_profile)
    await session.execute(stmt_user)
    await session.commit()
    return ResponseSchema(
        status_code=status.HTTP_200_OK,
        detail="profile is updated",
    )


async def delete_profile(
    user: UserSchema,
    session: AsyncSession,
    response: Response,
) -> ResponseSchema:
    user_profile = await get_profile(user.id, session)
    if user_profile is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="there is no such user or profile",
        )
    stmt_profile = delete(UserProfile).where(
        and_(UserProfile.id == user_profile.id, UserProfile.user_id == user.id)
    )
    stmt_user = delete(AuthUser).where(AuthUser.id == user.id)
    await session.execute(stmt_profile)
    await session.execute(stmt_user)
    await session.commit()

    from src.auth.auth_handler import AuthHandler
    AuthHandler.delete_all_tokens(response)

    return ResponseSchema(
        status_code=status.HTTP_200_OK,
        detail="user and his profile deleted",
    )


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

