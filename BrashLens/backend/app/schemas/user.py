"""Pydantic schemas for User model."""
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    """Базовая схема с общими полями пользователя."""

    telegram_id: int = Field(..., description="Telegram user ID", gt=0)
    username: Optional[str] = Field(None, max_length=255, description="Telegram username")
    first_name: str = Field(..., min_length=1, max_length=255)
    last_name: Optional[str] = Field(None, max_length=255)
    language: str = Field(default="ru", pattern="^(ru|en)$", description="Interface language")


class UserCreate(UserBase):
    """Схема для создания пользователя."""

    role: Literal["photographer", "client"] = Field(..., description="User role")
    # Примечание: admin не доступен при регистрации

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "telegram_id": 123456789,
                    "username": "photographer_user",
                    "first_name": "Иван",
                    "last_name": "Петров",
                    "language": "ru",
                    "role": "photographer",
                },
                {
                    "telegram_id": 987654321,
                    "username": "client_user",
                    "first_name": "Мария",
                    "last_name": "Сидорова",
                    "language": "en",
                    "role": "client",
                },
            ]
        }
    )


class UserUpdate(BaseModel):
    """Схема для обновления пользователя."""

    first_name: Optional[str] = Field(None, min_length=1, max_length=255)
    last_name: Optional[str] = Field(None, max_length=255)
    language: Optional[str] = Field(None, pattern="^(ru|en)$")
    # Примечание: role и telegram_id нельзя менять


class UserResponse(UserBase):
    """Схема для ответа API (публичная)."""

    id: int
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserResponse):
    """Схема для внутреннего использования (полная)."""

    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
