# Настройка проверки доступа для тестового бота

## Проблема
Тестовый бот @test_BrashLens_bot отвечает на команды от всех пользователей, хотя должен принимать только от вас (telegram_id: 5796545346).

## Решение

### Шаг 1: Добавьте переменные в `backend/.env`

Откройте файл `BrashLens/backend/.env` и добавьте следующие строки:

```env
# Режим тестового бота (проверка доступа включена)
IS_TEST_BOT=true

# Только этот пользователь может использовать тестового бота
TEST_BOT_ALLOWED_USER_ID=5796545346
```

### Шаг 2: Перезапустите контейнер бота

```bash
cd /Users/aleksey/git_projects/BrashLens/BrashLens
docker compose restart chat-bot
```

### Шаг 3: Проверьте настройки

```bash
docker compose exec chat-bot python -c "from app.core.config import settings; print(f'IS_TEST_BOT: {settings.IS_TEST_BOT}'); print(f'TEST_BOT_ALLOWED_USER_ID: {settings.TEST_BOT_ALLOWED_USER_ID}')"
```

Должно вывести:
```
IS_TEST_BOT: True
TEST_BOT_ALLOWED_USER_ID: 5796545346
```

### Шаг 4: Протестируйте

1. Отправьте `/start` с вашего аккаунта (telegram_id: 5796545346) - должно работать ✅
2. Отправьте `/start` с другого аккаунта - должно показать "Доступ запрещен" ❌

---

## Для продакшн бота (@brashlens_bot)

Для продакшн бота **НЕ добавляйте** эти переменные в `.env`, или установите:

```env
IS_TEST_BOT=false
```

Продакшн бот будет принимать команды от всех пользователей.

---

## Текущий статус

После добавления переменных и перезапуска:
- ✅ Тестовый бот будет принимать команды только от вас
- ✅ Продакшн бот будет принимать команды от всех
