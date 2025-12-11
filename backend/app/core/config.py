from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения из переменных окружения."""

    DATABASE_URL: str
    REDIS_URL: str
    TELEGRAM_BOT_TOKEN: str
    SECRET_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Игнорируем дополнительные переменные из .env
    )


settings = Settings()
