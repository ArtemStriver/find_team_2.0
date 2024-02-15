import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class UserProfile(Base):
    """Модель профиля"""
    __tablename__ = "user_profile"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("auth_user.id", ondelete="CASCADE"), nullable=False)
    image_path: Mapped[str] = mapped_column(default="")
    # TODO написать путь до дефолтной фотографии
