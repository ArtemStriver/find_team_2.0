import uuid
from datetime import datetime

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.team.models import team_members_table, application_to_join_table


class AuthUser(Base):
    """Базовая модель пользователя."""
    __tablename__ = "auth_user"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(nullable=True)
    email: Mapped[str] = mapped_column(
        String(length=50),
        unique=True,
        index=True,
        nullable=False,
    )
    hashed_password: Mapped[bytes] = mapped_column(nullable=False)
    verified: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    teams = relationship(
        "Team",
        back_populates="members",
        secondary=team_members_table,
    )

    applications_in = relationship(
        "Team",
        back_populates="applications_from",
        secondary=application_to_join_table,
    )

    # TODO нужны ли настройки для юзера?
    # TODO settings = relationship("UserSettings", back_populates="user")
