import uuid

from fastapi import HTTPException, status
from sqlalchemy import and_, delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.auth.schemas import ResponseSchema, UserSchema
from src.find.crud import get_team_data
from src.team.models import Team, application_to_join_table, team_members_table
from src.team.schemas import ApplicationSchema, CreateTeamSchema, TeamSchema, MemberSchema


async def create_team(
    team_data: CreateTeamSchema,
    session: AsyncSession,
    user: UserSchema,
) -> ResponseSchema:
    """Создание команды."""
    # if user_team := await get_user_team(user_id=user.id, session=session):
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail=f"user {user.username} already have one team {user_team.title}",
    #     )
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
    update_data: CreateTeamSchema,
    session: AsyncSession,
    user: UserSchema,
) -> ResponseSchema:
    """Обновление команды."""
    stmt = (
        update(Team)
        .values({
            "title": update_data.title,
            "number_of_members": update_data.number_of_members,
            "contacts": update_data.contacts,
            "description": update_data.description,
            "tags": update_data.tags,
            "deadline_at": update_data.deadline_at,
        })
        .where(and_(
            Team.id == team_id,
            Team.owner == user.id,
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
    if result.scalar_one_or_none().owner == user.id:
        query = select(team_members_table).where(team_members_table.c.team_id == team_id)
        result = await session.execute(query)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="no access",
        ) from None
    return result.all()
# TODO убрать дублирование кода и настроить релейшеншипс для отображения данных пользователя.


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
    comrade_id: uuid.UUID,
    team_id: uuid.UUID,
    session: AsyncSession,
) -> ResponseSchema:
    """Отклонить заявку пользователя на вступление в команду."""
    try:
        await _delete_application(comrade_id, team_id, session)

        await session.commit()
        return ResponseSchema(
            status_code=status.HTTP_200_OK,
            detail="comrade's application is rejected",
        )
    except Exception:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid data",
        ) from None


async def _delete_application(
    comrade_id: uuid.UUID,
    team_id: uuid.UUID,
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
        detail="comrade is excluded",
    )
