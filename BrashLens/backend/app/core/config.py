from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения из переменных окружения."""

    DATABASE_URL: str
    REDIS_URL: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    TELEGRAM_BOT_TOKEN: str
    SECRET_KEY: str
    WEBHOOK_URL: str | None = None
    
    # CORS настройки
    ALLOWED_ORIGINS: list[str] = Field(
        default_factory=lambda: ["*"],
        description="Разрешенные origins для CORS. Для продакшна укажите конкретные домены."
    )
    ALLOWED_METHODS: list[str] = Field(
        default_factory=lambda: ["*"],
        description="Разрешенные HTTP методы"
    )
    ALLOWED_HEADERS: list[str] = Field(
        default_factory=lambda: ["*"],
        description="Разрешенные заголовки"
    )
    
    # Логирование
    LOG_LEVEL: str = Field(default="INFO", description="Уровень логирования")
    DEBUG: bool = Field(default=False, description="Режим отладки")
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="Включить rate limiting")
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, description="Лимит запросов в минуту")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Игнорируем дополнительные переменные из .env
    )


settings = Settings()
