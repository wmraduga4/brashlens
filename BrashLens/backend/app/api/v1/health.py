"""Health check endpoints."""
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db
from app.schemas.responses import HealthResponse, HealthDbResponse

router = APIRouter()


@router.get(
    "",
    response_model=HealthResponse,
    summary="Health check",
    description="Проверка работоспособности приложения. Возвращает статус и временную метку.",
    responses={
        200: {
            "description": "Приложение работает нормально",
            "content": {
                "application/json": {
                    "example": {
                        "status": "ok",
                        "timestamp": "2024-01-01T12:00:00Z"
                    }
                }
            }
        }
    }
)
async def health_check() -> HealthResponse:
    """
    Проверка здоровья приложения.
    
    Returns:
        HealthResponse: Статус приложения и временная метка
    """
    return HealthResponse(
        status="ok",
        timestamp=datetime.utcnow().isoformat() + "Z",
    )


@router.get(
    "/db",
    response_model=HealthDbResponse,
    summary="Database health check",
    description="Проверка подключения к базе данных PostgreSQL. Возвращает статус подключения и версию БД.",
    responses={
        200: {
            "description": "Результат проверки подключения",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "Успешное подключение",
                            "value": {
                                "status": "ok",
                                "database": "connected",
                                "version": "PostgreSQL 16.0",
                                "error": None
                            }
                        },
                        "error": {
                            "summary": "Ошибка подключения",
                            "value": {
                                "status": "error",
                                "database": "disconnected",
                                "version": None,
                                "error": "Connection refused"
                            }
                        }
                    }
                }
            }
        }
    }
)
async def health_check_db(db: AsyncSession = Depends(get_db)) -> HealthDbResponse:
    """
    Проверка подключения к базе данных.
    
    Returns:
        HealthDbResponse: Статус подключения к БД и версия PostgreSQL
    """
    try:
        result = await db.execute(text("SELECT version()"))
        version = result.scalar()
        return HealthDbResponse(
            status="ok",
            database="connected",
            version=str(version),
            error=None,
        )
    except Exception as e:
        return HealthDbResponse(
            status="error",
            database="disconnected",
            version=None,
            error=str(e),
        )
