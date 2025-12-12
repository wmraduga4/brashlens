"""Test endpoints for database operations."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.test_model import TestConnection
from app.schemas.requests import TestConnectionRequest
from app.schemas.responses import TestConnectionResponse, TestConnectionsListResponse, TestConnectionRecord

router = APIRouter()


@router.post(
    "/db",
    response_model=TestConnectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create test record",
    description="Создать тестовую запись в таблице test_connections. Используется для проверки работы БД.",
    responses={
        201: {
            "description": "Запись успешно создана",
            "content": {
                "application/json": {
                    "example": {
                        "status": "ok",
                        "message": "Record created successfully",
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "created_at": "2024-01-01T12:00:00"
                    }
                }
            }
        },
        500: {
            "description": "Ошибка при создании записи",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Error creating record: ..."
                    }
                }
            }
        }
    }
)
async def test_db(
    request: TestConnectionRequest,
    db: AsyncSession = Depends(get_db)
) -> TestConnectionResponse:
    """
    Создать тестовую запись в таблице test_connections.
    
    Args:
        request: Данные для создания записи
        db: Сессия базы данных
        
    Returns:
        TestConnectionResponse: Информация о созданной записи
        
    Raises:
        HTTPException: При ошибке создания записи
    """
    try:
        test_record = TestConnection(message=request.message)
        db.add(test_record)
        await db.commit()
        await db.refresh(test_record)
        return TestConnectionResponse(
            status="ok",
            message="Record created successfully",
            id=str(test_record.id),
            created_at=test_record.created_at.isoformat(),
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating record: {str(e)}"
        )


@router.get(
    "/db",
    response_model=TestConnectionsListResponse,
    summary="Get test records",
    description="Получить все тестовые записи из таблицы test_connections, отсортированные по дате создания (новые первыми).",
    responses={
        200: {
            "description": "Список тестовых записей",
            "content": {
                "application/json": {
                    "example": {
                        "status": "ok",
                        "count": 2,
                        "records": [
                            {
                                "id": "123e4567-e89b-12d3-a456-426614174000",
                                "message": "Test message 1",
                                "created_at": "2024-01-01T12:00:00"
                            },
                            {
                                "id": "223e4567-e89b-12d3-a456-426614174001",
                                "message": "Test message 2",
                                "created_at": "2024-01-01T11:00:00"
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def get_test_records(db: AsyncSession = Depends(get_db)) -> TestConnectionsListResponse:
    """
    Получить все тестовые записи из таблицы test_connections.
    
    Args:
        db: Сессия базы данных
        
    Returns:
        TestConnectionsListResponse: Список всех тестовых записей
        
    Raises:
        HTTPException: При ошибке получения записей
    """
    try:
        result = await db.execute(select(TestConnection).order_by(TestConnection.created_at.desc()))
        records = result.scalars().all()
        return TestConnectionsListResponse(
            status="ok",
            count=len(records),
            records=[
                TestConnectionRecord(
                    id=str(record.id),
                    message=record.message,
                    created_at=record.created_at.isoformat(),
                )
                for record in records
            ],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching records: {str(e)}"
        )
