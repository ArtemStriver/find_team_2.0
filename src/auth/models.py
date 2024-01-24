import uuid
from datetime import datetime
from uuid import UUID

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class AuthUser(Base):
    """Базовая модель пользователя."""
    __tablename__ = "auth_user"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
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

    # TODO нужны ли настройки для юзера?
    # settings = relationship("UserSettings", back_populates="user")
