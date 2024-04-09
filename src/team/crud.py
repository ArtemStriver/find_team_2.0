import uuid

from fastapi import HTTPException, status
from sqlalchemy import and_, delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.crud import get_user_by_id
from src.auth.schemas import ResponseSchema, UserSchema
from src.find.crud import get_team_data
from src.team.models import Team, application_to_join_table, team_members_table, TeamTags
from src.team.schemas import ApplicationSchema, CreateTeamSchema, MemberSchema


async def create_team(
    team_data: CreateTeamSchema,
    session: AsyncSession,
    user: UserSchema,
) -> ResponseSchema:
    """Создание команды."""
    stmt_for_team = insert(Team).values({
        "owner": user.id,
        "title": team_data.title,
        "type_team": team_data.type_team,
        "number_of_members": team_data.number_of_members,
        "team_description": team_data.team_description,
        "team_deadline_at": team_data.team_deadline_at,
        "team_city": team_data.team_city,
    }).returning(Team.id)

    new_team_id = (await session.execute(stmt_for_team)).scalar_one_or_none()

    stmt_for_team_tags = insert(TeamTags).values({
        "team_id": new_team_id,
        "tag1": team_data.tags.tag1,
        "tag2": team_data.tags.tag2,
        "tag3": team_data.tags.tag3,
        "tag4": team_data.tags.tag4,
        "tag5": team_data.tags.tag5,
        "tag6": team_data.tags.tag6,
        "tag7": team_data.tags.tag7,
    })
    await session.execute(stmt_for_team_tags)

    await session.commit()
    return ResponseSchema(
        status_code=status.HTTP_201_CREATED,
        detail="team created",
    )


async def update_team(
    team_id: uuid.UUID,
    update_data: CreateTeamSchema,
    session: AsyncSession,
    user: UserSchema,
) -> ResponseSchema:
    """Обновление команды."""
    stmt_for_team = (
        update(Team)
        .values({
            "title": update_data.title,
            "number_of_members": update_data.number_of_members,
            "team_description": update_data.team_description,
            "team_deadline_at": update_data.team_deadline_at,
            "team_city": update_data.team_city,
        })
        .where(and_(
            Team.id == team_id,
            Team.owner == user.id,
        ))
        .returning(Team)
    )
    await session.execute(stmt_for_team)

    stmt_for_team_tags = (
        update(TeamTags)
        .values({
            "tag1": update_data.tags.tag1,
            "tag2": update_data.tags.tag2,
            "tag3": update_data.tags.tag3,
            "tag4": update_data.tags.tag4,
            "tag5": update_data.tags.tag5,
            "tag6": update_data.tags.tag6,
            "tag7": update_data.tags.tag7,
        })
        .where(and_(
            TeamTags.team_id == team_id,
        ))
    )
    await session.execute(stmt_for_team_tags)
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
    """Удаление команды."""
    if not (team := await get_team_data(team_id=team_id, session=session)):
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
            detail="no access",
        )
    return ResponseSchema(
        status_code=status.HTTP_200_OK,
        detail="team is deleted",
    )


async def get_members_list(
    team_id: uuid.UUID,
    user: UserSchema,
    session: AsyncSession,
) -> list[MemberSchema]:
    """Получение список участников команды."""
    query = select(Team).where(Team.id == team_id)
    result = await session.execute(query)
    team_data = result.scalar_one_or_none()
    query = select(team_members_table).where(team_members_table.c.team_id == team_id)
    result = await session.execute(query)
    members_without_name = result.all()
    if (team_data.owner != user.id and
            (user.id, uuid.UUID(team_id)) not in members_without_name):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="no access",
        ) from None
    members = []
    for member in members_without_name:
        username = (await get_user_by_id(member[0], session)).username
        member_data = MemberSchema(
            team_id=member[1],
            user_id=member[0],
            username=username,
        )
        members.append(member_data)
    return members


async def get_application_list(
    team_id: uuid.UUID,
    user: UserSchema,
    session: AsyncSession,
) -> list[ApplicationSchema]:
    """Получение заявок на вступление в команду."""
    query = select(Team).where(Team.id == team_id)
    result = await session.execute(query)
    if result.scalar_one_or_none().owner == user.id:
        query = select(application_to_join_table).where(application_to_join_table.c.team_id == team_id)
        result = await session.execute(query)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="no access",
        ) from None
    return result.all()


async def move_comrade_into_team(
    comrade_id: uuid.UUID,
    team_id: uuid.UUID,
    session: AsyncSession,
) -> ResponseSchema:
    """Принять заявку пользователя на вступление в команду."""
    try:
        stmt = insert(team_members_table).values(
            {"user_id": comrade_id, "team_id": team_id},
        )
        await session.execute(stmt)

        await _delete_application(comrade_id, team_id, session)

        await session.commit()
        return ResponseSchema(
            status_code=status.HTTP_200_OK,
            detail="comrade added into team",
        )
    except Exception:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid data",
        ) from None


async def remove_application_of_comrade(
    comrade_id: uuid.UUID | str,
    team_id: uuid.UUID | str,
    session: AsyncSession,
) -> ResponseSchema:
    """Отклонить заявку пользователя на вступление в команду."""
    try:
        await _delete_application(comrade_id, team_id, session)

        return ResponseSchema(
            status_code=status.HTTP_200_OK,
            detail="comrade's application rejected",
        )
    except Exception:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid data",
        ) from None


async def _delete_application(
    comrade_id: uuid.UUID | str,
    team_id: uuid.UUID | str,
    session: AsyncSession,
) -> None:
    """Удалить заявку из БД."""
    stmt = delete(application_to_join_table).where(
        and_(
            application_to_join_table.c.user_id == comrade_id,
            application_to_join_table.c.team_id == team_id,
        ),
    )
    await session.execute(stmt)
    await session.commit()


async def exclude_comrade_from_team(
    user_id: uuid.UUID,
    comrade_id: uuid.UUID,
    team_id: uuid.UUID,
    session: AsyncSession,
) -> ResponseSchema:
    """Исключить пользователя из команды."""
    query = select(Team).where(Team.id == team_id)
    result = await session.execute(query)
    if result.scalar_one_or_none().owner == user_id:
        stmt = delete(team_members_table).where(
            and_(
                team_members_table.c.user_id == comrade_id,
                team_members_table.c.team_id == team_id,
            ),
        )
        await session.execute(stmt)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="no access",
        ) from None
    await session.commit()
    return ResponseSchema(
        status_code=status.HTTP_200_OK,
        detail="comrade excluded",
    )
