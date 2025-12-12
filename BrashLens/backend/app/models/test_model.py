"""Тестовая модель для проверки подключения к БД."""
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class TestConnection(Base):
    """Тестовая модель для проверки работы БД."""

    __tablename__ = "test_connections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<TestConnection(id={self.id}, message='{self.message}', created_at={self.created_at})>"
