import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

team_members_table = Table(
    "team_members",
    Base.metadata,
    Column("user_id", ForeignKey("auth_user.id"), primary_key=True),
    Column("team_id", ForeignKey("team.id"), primary_key=True),
)

application_to_join_table = Table(
    "application_to_join",
    Base.metadata,
    Column("user_id", ForeignKey("auth_user.id"), primary_key=True),
    Column("team_id", ForeignKey("team.id"), primary_key=True),
    Column("cover_letter", String, nullable=True),
)


class Team(Base):
    """Модель команды"""
    __tablename__ = "team"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    owner: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("auth_user.id", ondelete="CASCADE"),
        nullable=False,
    )
    # TODO имена команд сделать не уникальные!
    title: Mapped[str] = mapped_column(
        String(length=50),
        unique=True,
        nullable=False,
    )
    type_team: Mapped[str] = mapped_column(nullable=False)
    number_of_members: Mapped[int] = mapped_column(nullable=False)  # количество необходимого числа участников команды
    # TODO продумать тип данных для контактов и какие данные будут там находиться, мб настроить relationship
    contacts: Mapped[str] = mapped_column(nullable=False)
    # TODO подумать, может добавить мини описание или сделать как отрывок из главного описания.
    description: Mapped[str] = mapped_column(nullable=False)
    # TODO сделать фиксированное количество тегов и чтобы они заполнялись как как в словарь - одинаково.
    tags: Mapped[Optional[str]] = mapped_column(nullable=True)
    # TODO сделать дефолтное значение дедлайна now + 1 день (хотя можно еще обсудить какое значение ставить)
    deadline_at: Mapped[datetime] = mapped_column(nullable=False)
    # TODO может изменить на просто дату?
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    members = relationship(
        "AuthUser",
        back_populates="teams",
        secondary=team_members_table,
    )

    applications_from = relationship(
        "AuthUser",
        back_populates="applications_in",
        secondary=application_to_join_table,
    )
