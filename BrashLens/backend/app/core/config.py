from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import logging

logger = logging.getLogger(__name__)


def _auto_detect_test_bot(token: str) -> bool:
    """
    Автоматически определяет тестовый бот по username через Telegram API.
    
    Логика:
    - Если username содержит "test" (case-insensitive) - тестовый бот
    - Иначе - продакшн бот
    
    Args:
        token: Telegram bot token
        
    Returns:
        bool: True если тестовый бот, False если продакшн
    """
    try:
        import httpx
        import sys
        
        # Получаем информацию о боте через getMe API
        response = httpx.get(
            f"https://api.telegram.org/bot{token}/getMe",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok") and "result" in data:
                username = data["result"].get("username", "").lower()
                is_test = "test" in username
                bot_username = data["result"].get("username", "unknown")
                
                # Логируем в stderr для гарантированного вывода
                print(
                    f"[AUTO-DETECT] Bot username: {bot_username}, IS_TEST_BOT={is_test}",
                    file=sys.stderr
                )
                logger.info(
                    f"Auto-detected bot mode: username={bot_username}, IS_TEST_BOT={is_test}"
                )
                return is_test
            else:
                print("[AUTO-DETECT] Failed to get bot info from Telegram API, using default IS_TEST_BOT=False", file=sys.stderr)
                logger.warning("Failed to get bot info from Telegram API, using default IS_TEST_BOT=False")
                return False
        else:
            print(f"[AUTO-DETECT] Telegram API returned {response.status_code}, using default IS_TEST_BOT=False", file=sys.stderr)
            logger.warning(f"Telegram API returned {response.status_code}, using default IS_TEST_BOT=False")
            return False
            
    except Exception as e:
        print(f"[AUTO-DETECT] Failed to auto-detect bot mode: {e}, using default IS_TEST_BOT=False", file=sys.stderr)
        logger.warning(f"Failed to auto-detect bot mode: {e}, using default IS_TEST_BOT=False")
        return False


class Settings(BaseSettings):
    """Настройки приложения из переменных окружения."""

    DATABASE_URL: str
    REDIS_URL: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    TELEGRAM_BOT_TOKEN: str
    SECRET_KEY: str
    WEBHOOK_URL: str | None = Field(default=None, description="Webhook URL для Telegram бота (опционально, для production)")
    
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
    
    # Test bot access control
    # Если IS_TEST_BOT не указан в .env, автоматически определяется по username бота
    IS_TEST_BOT: bool | None = Field(
        default=None,
        description="Флаг тестового бота. Если None - определяется автоматически по username. Если True - проверяется доступ через TEST_BOT_ALLOWED_USER_ID"
    )
    TEST_BOT_ALLOWED_USER_ID: int | None = Field(
        default=None,
        description="Telegram ID пользователя, которому разрешено использовать тестового бота (только если IS_TEST_BOT=True)"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Игнорируем дополнительные переменные из .env
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Автоматически определяем IS_TEST_BOT если не указан явно
        if self.IS_TEST_BOT is None:
            import sys
            print("[AUTO-DETECT] IS_TEST_BOT not set, auto-detecting from bot username...", file=sys.stderr)
            self.IS_TEST_BOT = _auto_detect_test_bot(self.TELEGRAM_BOT_TOKEN)
            print(f"[AUTO-DETECT] Final IS_TEST_BOT={self.IS_TEST_BOT}", file=sys.stderr)
            logger.info(f"Auto-detected IS_TEST_BOT={self.IS_TEST_BOT} from bot username")


settings = Settings()
