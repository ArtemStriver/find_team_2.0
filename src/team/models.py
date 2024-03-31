import uuid
import datetime

from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

team_members_table = Table(
    "team_members",
    Base.metadata,
    Column("user_id", ForeignKey("auth_user.id", ondelete="CASCADE"), primary_key=True),
    Column("team_id", ForeignKey("team.id", ondelete="CASCADE"), primary_key=True),
)

application_to_join_table = Table(
    "application_to_join",
    Base.metadata,
    Column("user_id", ForeignKey("auth_user.id", ondelete="CASCADE"), primary_key=True),
    Column("team_id", ForeignKey("team.id", ondelete="CASCADE"), primary_key=True),
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
    title: Mapped[str] = mapped_column(
        String(length=50),
        nullable=False,
    )
    type_team: Mapped[str] = mapped_column(nullable=False, default="lifestyle")
    number_of_members: Mapped[int] = mapped_column(nullable=False)

    team_description: Mapped[str] = mapped_column(nullable=False)

    team_deadline_at: Mapped[datetime.date] = mapped_column(
        nullable=False,
        default=datetime.date.today
    )

    team_city: Mapped[str] = mapped_column(nullable=False, default="Интернет")

    created_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    )

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


class TeamTags(Base):
    __tablename__ = "team_tags"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    team_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("team.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    tag1: Mapped[str] = mapped_column(String(length=50), nullable=True, default=None)
    tag2: Mapped[str] = mapped_column(String(length=50), nullable=True, default=None)
    tag3: Mapped[str] = mapped_column(String(length=50), nullable=True, default=None)
    tag4: Mapped[str] = mapped_column(String(length=50), nullable=True, default=None)
    tag5: Mapped[str] = mapped_column(String(length=50), nullable=True, default=None)
    tag6: Mapped[str] = mapped_column(String(length=50), nullable=True, default=None)
    tag7: Mapped[str] = mapped_column(String(length=50), nullable=True, default=None)
