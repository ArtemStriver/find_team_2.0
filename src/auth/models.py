import uuid
from datetime import datetime
from uuid import UUID

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class AuthUser(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "auth_user"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(length=50), nullable=False)
    email: Mapped[str] = mapped_column(
        String(length=50),
        unique=True,
        index=True,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    is_verified: Mapped[bool] = mapped_column(default=False)
    is_delete: Mapped[bool] = mapped_column(default=False)

    # TODO нужны ли настройки для юзера?
    # settings = relationship("UserSettings", back_populates="user")
