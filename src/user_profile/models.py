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
    contacts: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    # TODO увлечения будут выбираться из фиксированного списка, храниться через пробел, плюс переименовать на hobbies.
    hobby: Mapped[str] = mapped_column(String(length=50), nullable=False)


    # TODO удалить город из профиля, изменить username на уникальные ники и добавить возможность логиниться по нику.
    # TODO плюс прибрать код и провести ручное тестирование.
    city: Mapped[str] = mapped_column(nullable=True)
