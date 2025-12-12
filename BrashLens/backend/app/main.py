"""FastAPI application main entry point."""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.exceptions import global_exception_handler, validation_exception_handler
from app.core.limiter import limiter
from app.api.v1 import api_router

# Настройка логирования
setup_logging()
logger = get_logger(__name__)

# Создание приложения
app = FastAPI(
    title="BrashLens API",
    description="Telegram Mini App для управления фотобизнесом",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Подключение rate limiter
app.state.limiter = limiter
if settings.RATE_LIMIT_ENABLED:
    app.add_middleware(SlowAPIMiddleware)
    # Обработчик превышения rate limit
    app.add_exception_handler(
        RateLimitExceeded,
        lambda request, exc: JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": f"Rate limit exceeded: {exc.detail}",
            },
            headers={"Retry-After": str(exc.retry_after)} if exc.retry_after else {},
        ),
    )

# CORS middleware с настройками из config
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)

# Глобальные обработчики исключений
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Подключение роутеров API v1
app.include_router(api_router, prefix="/api")


@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    """
    Корневой эндпоинт API.
    
    Returns:
        dict: Информация о версии API
    """
    return {"message": "BrashLens API v1.0", "docs": "/docs"}


@app.on_event("startup")
async def startup_event() -> None:
    """Событие запуска приложения."""
    logger.info("BrashLens API starting up...")
    logger.info(f"CORS allowed origins: {settings.ALLOWED_ORIGINS}")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Событие остановки приложения."""
    logger.info("BrashLens API shutting down...")
