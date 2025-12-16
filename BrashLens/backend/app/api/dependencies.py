"""Dependencies для FastAPI endpoints."""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.user_service import UserService


async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """Dependency для получения UserService."""
    return UserService(db)
