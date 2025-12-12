"""Global exception handlers."""
import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

logger = logging.getLogger(__name__)


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Глобальный обработчик исключений.
    
    Args:
        request: HTTP запрос
        exc: Исключение
        
    Returns:
        JSONResponse: JSON ответ с описанием ошибки
    """
    logger.error(
        f"Unhandled exception: {exc.__class__.__name__} - {str(exc)}",
        exc_info=True,
        extra={"path": request.url.path, "method": request.method},
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "type": exc.__class__.__name__,
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Обработчик ошибок валидации Pydantic.
    
    Args:
        request: HTTP запрос
        exc: Исключение валидации
        
    Returns:
        JSONResponse: JSON ответ с описанием ошибок валидации
    """
    logger.warning(
        f"Validation error: {exc.errors()}",
        extra={"path": request.url.path, "method": request.method},
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "body": exc.body,
        },
    )
