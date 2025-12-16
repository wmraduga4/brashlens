# Автоматическое определение режима бота

## Как это работает

Система автоматически определяет, является ли бот тестовым или продакшн, по **username бота** через Telegram API.

### Логика определения

1. При старте бота система вызывает Telegram API `getMe` для получения информации о боте
2. Проверяет username бота:
   - Если username содержит `"test"` (без учета регистра) → **тестовый бот** (`IS_TEST_BOT=True`)
   - Иначе → **продакшн бот** (`IS_TEST_BOT=False`)

### Примеры

- `@test_BrashLens_bot` → `IS_TEST_BOT=True` ✅
- `@brashlens_bot` → `IS_TEST_BOT=False` ✅
- `@testbot` → `IS_TEST_BOT=True` ✅
- `@my_test_bot` → `IS_TEST_BOT=True` ✅

## Настройка

### Автоматический режим (рекомендуется)

**Не указывайте** `IS_TEST_BOT` в `.env` файле - система определит автоматически:

```env
# backend/.env
TELEGRAM_BOT_TOKEN=your_bot_token
TEST_BOT_ALLOWED_USER_ID=5796545346  # Только для тестового бота
```

### Ручная настройка (если нужно переопределить)

Если нужно явно указать режим (например, для тестирования):

```env
# Для тестового бота
IS_TEST_BOT=true
TEST_BOT_ALLOWED_USER_ID=5796545346

# Для продакшн бота
IS_TEST_BOT=false
```

## Для разных окружений

### Локальная разработка (тестовый бот)

```env
# backend/.env (локально)
TELEGRAM_BOT_TOKEN=8386947371:AAEOCQHkxmST5i7qvmMVKsHHyn8k4fyZVBE  # @test_BrashLens_bot
TEST_BOT_ALLOWED_USER_ID=5796545346
# IS_TEST_BOT не указываем - определится автоматически как True
```

### Продакшн (продакшн бот)

```env
# backend/.env (на сервере)
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz  # @brashlens_bot
# IS_TEST_BOT не указываем - определится автоматически как False
# TEST_BOT_ALLOWED_USER_ID не нужен для продакшн
```

## CI/CD и автоматический деплой

При автоматическом деплое через push в `main`:

1. **На сервере** используется продакшн токен (`@brashlens_bot`)
2. Система автоматически определяет `IS_TEST_BOT=False`
3. Бот принимает запросы от всех пользователей ✅

**Никаких дополнительных настроек не требуется!**

## Проверка работы

После деплоя проверьте настройки:

```bash
docker exec brashlens_chat_bot python -c "from app.core.config import settings; print(f'IS_TEST_BOT: {settings.IS_TEST_BOT}')"
```

Должно вывести:
- Для тестового бота: `IS_TEST_BOT: True`
- Для продакшн бота: `IS_TEST_BOT: False`

## Логирование

При автоматическом определении в логах будет:

```
Auto-detected bot mode: username=test_BrashLens_bot, IS_TEST_BOT=True
Auto-detected IS_TEST_BOT=True from bot username
```

## Преимущества

✅ **Не нужно менять настройки** при деплое  
✅ **Автоматически работает** для разных окружений  
✅ **Меньше ошибок** - не забудете переключить режим  
✅ **Работает с CI/CD** без дополнительной настройки  

## Откат к ручной настройке

Если нужно отключить автоматическое определение, просто укажите `IS_TEST_BOT` явно в `.env`:

```env
IS_TEST_BOT=true  # или false
```

Явное значение имеет приоритет над автоматическим определением.
