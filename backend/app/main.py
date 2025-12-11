from datetime import datetime
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db

app = FastAPI(title="PhotoHelper API")

# CORS middleware - разрешаем все origins для разработки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict[str, str]:
    """Корневой эндпоинт API."""
    return {"message": "PhotoHelper API v1.0"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Проверка здоровья приложения."""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@app.get("/health/db")
async def health_check_db(db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    """Временный endpoint для проверки подключения к БД."""
    try:
        result = await db.execute(text("SELECT version()"))
        version = result.scalar()
        return {
            "status": "ok",
            "database": "connected",
            "version": str(version),
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "disconnected",
            "error": str(e),
        }
