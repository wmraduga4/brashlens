"""Сервис для работы с пользователями."""
from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    """Сервис для работы с пользователями."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_data: UserCreate) -> User:
        """Создать нового пользователя."""
        # Проверка существования по telegram_id
        existing = await self.get_by_telegram_id(user_data.telegram_id)
        if existing:
            raise ValueError(
                f"User with telegram_id {user_data.telegram_id} already exists"
            )

        # Создание пользователя
        user_dict = user_data.model_dump()
        # Конвертируем строку роли в enum
        if "role" in user_dict and isinstance(user_dict["role"], str):
            user_dict["role"] = UserRole(user_dict["role"])
        user = User(**user_dict)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Получить пользователя по Telegram ID."""
        result = await self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Получить пользователя по ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """Получить пользователя по username."""
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def update_user(
        self, user_id: int, user_data: UserUpdate
    ) -> Optional[User]:
        """Обновить данные пользователя."""
        user = await self.get_by_id(user_id)
        if not user:
            return None

        # Обновляем только переданные поля
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_users_by_role(
        self, role: str, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """Получить список пользователей по роли."""
        # Конвертируем строку в enum если нужно
        role_enum = UserRole(role) if isinstance(role, str) else role
        result = await self.db.execute(
            select(User)
            .where(and_(User.role == role_enum, User.is_active == True))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def deactivate_user(self, user_id: int) -> bool:
        """Деактивировать пользователя (soft delete)."""
        user = await self.get_by_id(user_id)
        if not user:
            return False

        user.is_active = False
        await self.db.commit()
        return True

    async def get_or_create_user(
        self, telegram_id: int, user_data: UserCreate
    ) -> tuple[User, bool]:
        """
        Получить существующего пользователя или создать нового.

        Returns:
            tuple[User, bool]: (user, created) где created=True если пользователь создан
        """
        existing = await self.get_by_telegram_id(telegram_id)
        if existing:
            return existing, False

        user = await self.create_user(user_data)
        return user, True
