"""Celery tasks endpoints."""
from fastapi import APIRouter, HTTPException, status

from app.core.celery_app import celery_app
from app.schemas.requests import CeleryTaskRequest
from app.schemas.responses import CeleryTaskResponse, TaskStatusResponse

router = APIRouter()


@router.post(
    "/test",
    response_model=CeleryTaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start test task",
    description="Запустить тестовую Celery задачу. Задача выполняется асинхронно и занимает ~5 секунд.",
    responses={
        202: {
            "description": "Задача принята в обработку",
            "content": {
                "application/json": {
                    "example": {
                        "task_id": "123e4567-e89b-12d3-a456-426614174000"
                    }
                }
            }
        }
    }
)
async def test_celery(request: CeleryTaskRequest) -> CeleryTaskResponse:
    """
    Запустить тестовую Celery задачу.
    
    Args:
        request: Данные для задачи
        
    Returns:
        CeleryTaskResponse: ID запущенной задачи
    """
    from app.services.tasks import test_task
    
    task = test_task.delay(request.message)
    return CeleryTaskResponse(task_id=task.id)


@router.get(
    "/status/{task_id}",
    response_model=TaskStatusResponse,
    summary="Get task status",
    description="Получить статус выполнения Celery задачи по её ID. Возможные статусы: PENDING, SUCCESS, FAILURE.",
    responses={
        200: {
            "description": "Статус задачи",
            "content": {
                "application/json": {
                    "examples": {
                        "pending": {
                            "summary": "Задача в очереди",
                            "value": {
                                "status": "PENDING",
                                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                                "result": None,
                                "error": None
                            }
                        },
                        "success": {
                            "summary": "Задача выполнена",
                            "value": {
                                "status": "SUCCESS",
                                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                                "result": {"status": "completed", "message": "test"},
                                "error": None
                            }
                        },
                        "failure": {
                            "summary": "Задача завершилась ошибкой",
                            "value": {
                                "status": "FAILURE",
                                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                                "result": None,
                                "error": "Task failed"
                            }
                        }
                    }
                }
            }
        }
    }
)
async def get_task_status(task_id: str) -> TaskStatusResponse:
    """
    Получить статус выполнения Celery задачи.
    
    Args:
        task_id: ID задачи
        
    Returns:
        TaskStatusResponse: Статус и результат задачи
    """
    task_result = celery_app.AsyncResult(task_id)
    
    if task_result.state == "PENDING":
        return TaskStatusResponse(
            status=task_result.state,
            task_id=task_id,
            result=None,
            error=None,
        )
    elif task_result.state == "FAILURE":
        return TaskStatusResponse(
            status=task_result.state,
            task_id=task_id,
            result=None,
            error=str(task_result.info),
        )
    else:
        return TaskStatusResponse(
            status=task_result.state,
            task_id=task_id,
            result=task_result.result,
            error=None,
        )
