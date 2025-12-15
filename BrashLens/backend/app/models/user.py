"""Модель пользователя для системы BrashLens."""
import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserRole(str, enum.Enum):
    """Роли пользователей в системе."""

    PHOTOGRAPHER = "photographer"
    CLIENT = "client"
    ADMIN = "admin"


class User(Base):
    """Модель пользователя системы BrashLens.

    Хранит информацию о пользователях Telegram Mini App:
    - Фотографы (photographer)
    - Клиенты (client)
    - Администраторы (admin)
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False, index=True
    )
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", create_constraint=True),
        nullable=False,
        index=True,
    )
    language: Mapped[str] = mapped_column(String(5), nullable=False, default="ru")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    # Composite index для быстрых фильтраций по роли и активности
    __table_args__ = (
        Index("ix_users_role_is_active", "role", "is_active"),
    )

    def __repr__(self) -> str:
        return (
            f"<User(id={self.id}, telegram_id={self.telegram_id}, "
            f"username='{self.username}', role='{self.role.value}', "
            f"is_active={self.is_active})>"
        )

    def to_dict(self) -> dict:
        """Сериализация модели в словарь без конфиденциальных данных.

        Returns:
            dict: Словарь с данными пользователя
        """
        return {
            "id": self.id,
            "telegram_id": self.telegram_id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "role": self.role.value,
            "language": self.language,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
