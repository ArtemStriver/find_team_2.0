import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class UserProfile(Base):
    """Модель профиля"""
    __tablename__ = "user_profile"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("auth_user.id", ondelete="CASCADE"), nullable=False)
    image_path: Mapped[str] = mapped_column(nullable=True)
    description: Mapped[str] = mapped_column(nullable=False)


class UserContacts(Base):
    __tablename__ = "user_contact"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("auth_user.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    email: Mapped[str] = mapped_column(String(length=200), nullable=False)
    vk: Mapped[str] = mapped_column(String(length=200), nullable=True, default=None)
    telegram: Mapped[str] = mapped_column(String(length=200), nullable=True, default=None)
    discord: Mapped[str] = mapped_column(String(length=200), nullable=True, default=None)
    other: Mapped[str] = mapped_column(String(length=200), nullable=True, default=None)


class UserHobbies(Base):
    __tablename__ = "user_hobbies"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("auth_user.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    lifestyle1: Mapped[str] = mapped_column(String(length=60), nullable=True, default=None)
    lifestyle2: Mapped[str] = mapped_column(String(length=60), nullable=True, default=None)
    lifestyle3: Mapped[str] = mapped_column(String(length=60), nullable=True, default=None)
    sport1: Mapped[str] = mapped_column(String(length=60), nullable=True, default=None)
    sport2: Mapped[str] = mapped_column(String(length=60), nullable=True, default=None)
    sport3: Mapped[str] = mapped_column(String(length=60), nullable=True, default=None)
    work1: Mapped[str] = mapped_column(String(length=60), nullable=True, default=None)
    work2: Mapped[str] = mapped_column(String(length=60), nullable=True, default=None)
    work3: Mapped[str] = mapped_column(String(length=60), nullable=True, default=None)
