from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select

from app.core.database import get_db
from app.models.test_model import TestConnection

app = FastAPI(title="BrashLens API")

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
    return {"message": "BrashLens API v1.0"}


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


class TestConnectionRequest(BaseModel):
    """Запрос для создания тестовой записи."""
    message: str


@app.post("/test-db")
async def test_db(
    request: TestConnectionRequest,
    db: AsyncSession = Depends(get_db)
) -> dict[str, str]:
    """Тестовый endpoint для создания записи в test_connections."""
    try:
        test_record = TestConnection(message=request.message)
        db.add(test_record)
        await db.commit()
        await db.refresh(test_record)
        return {
            "status": "ok",
            "message": "Record created successfully",
            "id": str(test_record.id),
            "created_at": test_record.created_at.isoformat(),
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating record: {str(e)}")


@app.get("/test-db")
async def get_test_records(db: AsyncSession = Depends(get_db)) -> dict:
    """Получить все тестовые записи."""
    try:
        result = await db.execute(select(TestConnection).order_by(TestConnection.created_at.desc()))
        records = result.scalars().all()
        return {
            "status": "ok",
            "count": len(records),
            "records": [
                {
                    "id": str(record.id),
                    "message": record.message,
                    "created_at": record.created_at.isoformat(),
                }
                for record in records
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching records: {str(e)}")
