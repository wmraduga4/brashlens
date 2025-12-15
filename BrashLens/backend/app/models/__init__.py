# Импорт всех моделей для Alembic autogenerate
# Добавляйте импорты новых моделей здесь

from app.models.test_model import TestConnection  # noqa: F401
from app.models.user import User, UserRole  # noqa: F401

__all__ = ["TestConnection", "User", "UserRole"]

