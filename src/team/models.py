import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import text, String, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

team_members_table = Table(
    "team_members",
    Base.metadata,
    Column("user_id", ForeignKey("auth_user.id"), primary_key=True),
    Column("team_id", ForeignKey("team.id"), primary_key=True),
    Column("cover_letter", String, nullable=True),
)


# TODO продумать какие типы команд (для каких целей) будут необходимы
class TypeTeam(Enum):
    sport = "sport"
    study = "study"
    fun = "fun"
    other = "other"


class Team(Base):
    """Модель команды"""
    __tablename__ = "team"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    owner: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("auth_user.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(length=50),
        unique=True,
        nullable=False,
    )
    type_team: Mapped[TypeTeam]
    number_of_members: Mapped[int] = mapped_column(nullable=False)  # количество необходимого числа участников команды
    # TODO продумать тип данных для контактов и какие данные будут там находиться, м/б настроить relationship
    contacts: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    tags: Mapped[Optional[str]] = mapped_column(nullable=True)
    deadline_at: Mapped[datetime] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    members = relationship(
        "AuthUser",
        back_populates="teams",
        secondary=team_members_table,
    )


# class TeamMembers(Base):
#     __tablename__ = "team_members"
#
#     user_id: Mapped[uuid.UUID] = mapped_column(
#         ForeignKey("auth_user.id", ondelete="CASCADE"),
#         primary_key=True,
#     )
#     team_id: Mapped[uuid.UUID] = mapped_column(
#         ForeignKey("team.id", ondelete="CASCADE"),
#         primary_key=True,
#     )
#     cover_letter: Mapped[Optional[str]]
