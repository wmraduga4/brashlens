# ТЗ-ИНСТРУКЦИЯ: ИТЕРАЦИЯ 1 - "Скелет инфраструктуры"
## BrashLens MVP - Для разработчика Mid+ на MacBook M1

**Цель итерации:** Создать рабочий фундамент системы с базовой инфраструктурой, деплоем и простым Telegram ботом.

**Длительность:** 3-5 дней

**Критерий успеха:** Бот отвечает на `/start`, все сервисы работают, деплой настроен.

---

## 📋 ПРЕДВАРИТЕЛЬНАЯ ПОДГОТОВКА

### 1. Создание структуры проекта

```bash
# Создаём корневую директорию
mkdir brashlens && cd brashlens
git init

# Создаём начальный коммит и ветку dev
git checkout -b dev

# Создаём структуру
mkdir -p backend/app/{models,schemas,services,api,core,utils}
mkdir -p backend/app/api/v1
mkdir -p backend/alembic/versions
mkdir -p frontend/src/{components,pages,hooks,services,utils,types}
mkdir -p docs
mkdir -p nginx

# Создаём базовые файлы
touch backend/requirements.txt
touch backend/.env.example
touch backend/Dockerfile
touch frontend/package.json
touch docker-compose.yml
touch .gitignore
touch README.md
touch .cursorrules

# Открываем в Cursor
cursor .
```

### 2. Копирование .cursorrules

Скопируй содержимое файла `.cursorrules` в корень проекта.

---

## 🔄 GIT WORKFLOW

### Правила работы с Git

**⚠️ ВАЖНО:** Следуй этим правилам на протяжении всей разработки:

1. **Работаем в ветке `dev`** - основная ветка разработки
2. **Коммить после каждого завершенного этапа** - не накапливай изменения
3. **Используй conventional commits** - `feat:`, `fix:`, `docs:`, `refactor:`
4. **По окончанию этапа:**
   - Коммитим изменения в `dev` с описанием что изменилось
   - Пушим `dev` в удаленный репозиторий
   - Мержим `dev` в `main`
   - Пушим `main` в удаленный репозиторий
   - Возвращаемся в ветку `dev`
5. **Никогда не коммитьте секреты** - `.env`, токены, ключи, пароли

### Workflow по окончанию этапа

```bash
# 1. Убедись что находишься в ветке dev
git checkout dev

# 2. Добавь изменения
git add .

# 3. Закоммить с описанием изменений
git commit -m "feat: этап X - описание что сделано"

# 4. Запушить dev
git push origin dev

# 5. Переключись на main
git checkout main

# 6. Смержи dev в main
git merge dev

# 7. Запуши main
git push origin main

# 8. Вернись в dev для дальнейшей работы
git checkout dev
```

**Кратко:** "Запушить dev, смержить в main, вернуться в dev"

### ⚠️ Безопасность

**КРИТИЧЕСКИ ВАЖНО:**
- ✅ Файл `.env` должен быть в `.gitignore`
- ✅ Используй только `.env.example` для шаблона
- ✅ Никогда не коммитьте реальные токены, пароли, API ключи
- ✅ Проверяй `git status` перед каждым коммитом
- ✅ Используй переменные окружения для всех секретов

### Формат коммитов

```bash
# Примеры хороших коммитов:
git commit -m "feat: этап 1 - Docker Compose инфраструктура"
git commit -m "feat: этап 2 - FastAPI базовое приложение"
git commit -m "fix: исправление подключения к Redis"
git commit -m "docs: обновление инструкций деплоя"
```

---

## 🔨 ЭТАП 1: DOCKER COMPOSE + POSTGRESQL + REDIS

### Задача
Настроить базовую инфраструктуру в Docker: PostgreSQL и Redis в отдельной директории `infrastructure/`, подготовить контейнеры для FastAPI, Celery и Telegram бота.

### Промт для Cursor

```
@Codebase Создай структуру Docker Compose для проекта BrashLens:

1. infrastructure/docker-compose.yml:
   Сервисы:
   - postgres: PostgreSQL 16 с pgvector
     * Имя контейнера: brashlens_postgres
     * Порт: 5432
     * База: brashlens_db
     * Пользователь и пароль из .env
     * Volume: postgres_data
     * Healthcheck: pg_isready
     * Network: shared-network (создаёт сеть)
   
   - redis: Redis 7 Alpine
     * Имя контейнера: brashlens_redis
     * Порт: 6379
     * Volume: redis_data
     * Healthcheck: redis-cli ping
     * Network: shared-network

2. BrashLens/docker-compose.yml:
   Сервисы (пока без Dockerfile, добавим позже):
   - backend: FastAPI приложение
     * Порт: 8001:8000
     * Volume для hot reload
     * Environment из .env
     * Network: shared-network (external: true)
     * Подключение к brashlens_postgres:5432 и brashlens_redis:6379
   
   - chat-bot: Telegram бот (отдельный сервис)
     * Environment из .env
     * Network: shared-network (external: true)
   
   - celery-worker: Celery worker
     * Environment из .env
     * Network: shared-network (external: true)
   
   - celery-beat: Celery beat scheduler
     * Environment из .env
     * Network: shared-network (external: true)

Используй restart: unless-stopped для всех сервисов.
Создай network shared-network в infrastructure, используй external в приложении.

Также создай:
- infrastructure/.env.example с переменными для postgres и redis
- BrashLens/backend/.env.example с необходимыми переменными
- .gitignore с типичными исключениями для Python/Node.js/Docker
```

### Реализация

1. **Создай файлы через Cursor** (используй промт выше)
2. **Скопируй .env.example → .env** в обеих директориях и заполни реальные значения
3. **Проверь структуру файлов**

### ТРОЙНОЕ ТЕСТИРОВАНИЕ #1

#### ✅ Тест 1: Проверка конфигурации Docker Compose
```bash
# Валидация infrastructure/docker-compose.yml
cd infrastructure
docker compose config

# Валидация BrashLens/docker-compose.yml
cd ../BrashLens
docker compose config

# Ожидаемый результат: YAML валиден, нет ошибок
```

#### ✅ Тест 2: Запуск инфраструктуры
```bash
# Запускаем инфраструктуру (postgres и redis)
cd infrastructure
docker compose up -d

# Проверяем статус
docker compose ps

# Проверяем логи
docker compose logs postgres
docker compose logs redis

# Проверяем сеть
docker network ls | grep shared-network

# Ожидаемый результат: оба сервиса healthy, сеть создана
```

#### ✅ Тест 3: Подключение к БД и Redis
```bash
# Подключение к PostgreSQL
docker compose exec postgres psql -U ${POSTGRES_USER:-postgres} -d ${POSTGRES_DB:-brashlens_db} -c "SELECT version();"

# Подключение к Redis
docker compose exec redis redis-cli ping

# Ожидаемый результат:
# PostgreSQL: выводит версию
# Redis: PONG
```

**Критерии прохождения:**
- ✅ docker compose config без ошибок в обеих директориях
- ✅ Контейнеры brashlens_postgres и brashlens_redis запущены и healthy
- ✅ Сеть shared-network создана
- ✅ Успешное подключение к обеим БД

**Если тесты не прошли:** исправь ошибки, повтори все 3 теста заново.

### Коммит изменений

```bash
# Убедись что в ветке dev
git checkout dev

# Добавь изменения
git add .

# Закоммить
git commit -m "feat: этап 1 - Docker Compose инфраструктура с PostgreSQL и Redis"

# Запушить dev, смержить в main, вернуться в dev
git push origin dev
git checkout main
git merge dev
git push origin main
git checkout dev
```

---

## 🔨 ЭТАП 2: FASTAPI БАЗОВОЕ ПРИЛОЖЕНИЕ

### Задача
Создать минимальное FastAPI приложение с эндпоинтами `/health` и автогенерируемой документацией `/docs`.

### Промт для Cursor

```
@backend/app Создай структуру FastAPI приложения для BrashLens:

1. backend/app/main.py:
   - FastAPI приложение с title="BrashLens API"
   - Подключение CORS middleware (разрешить все origins для разработки)
   - Роут GET /health -> {"status": "ok", "timestamp": "..."}
   - Роут GET / -> {"message": "BrashLens API v1.0"}

2. backend/app/core/config.py:
   - Класс Settings на основе pydantic BaseSettings
   - Загрузка переменных окружения:
     * DATABASE_URL
     * REDIS_URL
     * TELEGRAM_BOT_TOKEN
     * SECRET_KEY
   - Валидация обязательных полей

3. backend/app/core/database.py:
   - Async SQLAlchemy 2.0 engine
   - Async session factory
   - Dependency для получения session
   - Base для моделей

4. backend/requirements.txt:
   - fastapi[all]
   - sqlalchemy[asyncio]
   - asyncpg
   - alembic
   - python-dotenv
   - pydantic[email]
   - pydantic-settings
   - redis[hiredis]
   - celery
   - python-telegram-bot==20.7
   - pillow
   - httpx

5. backend/Dockerfile:
   - Multi-stage build
   - Python 3.11-slim
   - Оптимизация для ARM64 (M1)
   - User non-root
   - Health check на /health

Следуй .cursorrules, используй async/await, type hints везде.
```

### Реализация

1. **Генерируй код через Cursor** (используй промт выше)
2. **Обнови docker-compose.yml** чтобы использовать Dockerfile для backend
3. **Пересобери контейнеры**

```bash
cd BrashLens
docker compose build backend
docker compose up -d backend
```

### ТРОЙНОЕ ТЕСТИРОВАНИЕ #2

#### ✅ Тест 1: Проверка работы FastAPI
```bash
# Проверка health endpoint
curl http://localhost:8000/health

# Ожидаемый результат: {"status":"ok","timestamp":"..."}

# Проверка корневого endpoint
curl http://localhost:8000/

# Ожидаемый результат: {"message":"BrashLens API v1.0"}
```

#### ✅ Тест 2: Проверка документации
```bash
# Открой в браузере
open http://localhost:8000/docs

# Ожидаемый результат: Swagger UI с документацией
# Проверь, что есть эндпоинты: GET /, GET /health
```

#### ✅ Тест 3: Проверка подключения к БД
```bash
# Смотрим логи backend
docker compose logs backend

# Ожидаемый результат: нет ошибок подключения к PostgreSQL
# Можно добавить временный endpoint для проверки коннекта

# Проверка через psql что база создана
cd ../infrastructure
docker compose exec postgres psql -U ${POSTGRES_USER:-postgres} -d ${POSTGRES_DB:-brashlens_db} -c "\dt"
```

**Критерии прохождения:**
- ✅ Эндпоинты /health и / отвечают корректно
- ✅ Swagger UI доступен и отображает API
- ✅ Backend успешно стартует без ошибок

**Если тесты не прошли:** проверь логи, исправь, повтори тесты.

### Коммит изменений

```bash
# Убедись что в ветке dev
git checkout dev

# Добавь изменения
git add .

# Закоммить
git commit -m "feat: этап 2 - FastAPI базовое приложение с health check и документацией"

# Запушить dev, смержить в main, вернуться в dev
git push origin dev
git checkout main
git merge dev
git push origin main
git checkout dev
```

---

## 🔨 ЭТАП 3: POSTGRESQL ПОДКЛЮЧЕНИЕ + ТЕСТОВАЯ ТАБЛИЦА

### Задача
Настроить Alembic, создать первую миграцию с тестовой таблицей, проверить работу БД.

### ⚠️ Важно: Backup перед миграциями

**Перед применением миграций в production:**
```bash
# Создай backup базы данных
cd infrastructure
docker compose exec postgres pg_dump -U ${POSTGRES_USER:-postgres} ${POSTGRES_DB:-brashlens_db} > backup_$(date +%Y%m%d_%H%M%S).sql
```

**Восстановление из backup:**
```bash
cd infrastructure
docker compose exec -T postgres psql -U ${POSTGRES_USER:-postgres} ${POSTGRES_DB:-brashlens_db} < backup_YYYYMMDD_HHMMSS.sql
```

### Промт для Cursor

```
@backend/app/models @backend/alembic Настрой Alembic и создай первую модель:

1. backend/alembic.ini:
   - Инициализация Alembic
   - sqlalchemy.url берётся из env

2. backend/alembic/env.py:
   - Async конфигурация
   - Импорт Base из app.core.database
   - Импорт всех моделей
   - target_metadata = Base.metadata

3. backend/app/models/__init__.py:
   - Импорт всех моделей

4. backend/app/models/test_model.py:
   - Модель TestConnection(Base)
   - Поля: id (UUID, primary_key), message (String), created_at (DateTime)
   - __tablename__ = "test_connections"

5. Скрипт backend/scripts/init_db.sh:
   - alembic revision --autogenerate -m "Initial test table"
   - alembic upgrade head

Используй SQLAlchemy 2.0 async стиль, type hints, UUID для id.
```

### Реализация

1. **Генерируй код через Cursor**
2. **Инициализируй Alembic внутри контейнера:**

```bash
# Зайди в контейнер backend
docker compose exec backend bash

# Инициализируй Alembic
alembic init alembic

# Выйди из контейнера
exit
```

3. **Примени промт Cursor для настройки конфигурации**
4. **Создай и примени миграцию:**

```bash
docker compose exec backend alembic revision --autogenerate -m "Initial test table"
docker compose exec backend alembic upgrade head
```

### ТРОЙНОЕ ТЕСТИРОВАНИЕ #3

#### ✅ Тест 1: Проверка создания миграции
```bash
# Проверь что миграция создалась
ls backend/alembic/versions/

# Ожидаемый результат: файл миграции с timestamp

# Проверь содержимое миграции
cat backend/alembic/versions/*_initial_test_table.py

# Ожидаемый результат: код создания таблицы test_connections
```

#### ✅ Тест 2: Проверка применения миграции
```bash
# Проверь таблицы в БД
docker compose exec postgres psql -U brashlens_user -d brashlens_db -c "\dt"

# Ожидаемый результат: таблицы test_connections и alembic_version

# Проверь структуру таблицы
docker compose exec postgres psql -U brashlens_user -d brashlens_db -c "\d test_connections"

# Ожидаемый результат: колонки id, message, created_at
```

#### ✅ Тест 3: Создание тестовой записи через API
```bash
# Добавь временный endpoint в backend/app/main.py:
# POST /test-db -> создаёт запись в test_connections

# После добавления endpoint:
curl -X POST http://localhost:8000/test-db \
  -H "Content-Type: application/json" \
  -d '{"message":"Test connection works!"}'

# Проверь что запись создалась
docker compose exec postgres psql -U brashlens_user -d brashlens_db \
  -c "SELECT * FROM test_connections;"

# Ожидаемый результат: одна запись с сообщением
```

**Критерии прохождения:**
- ✅ Миграция создана и применена
- ✅ Таблица test_connections существует в БД
- ✅ Можно создавать записи через API (если добавил endpoint)

**Если тесты не прошли:** проверь настройки Alembic, повтори миграцию.

### Коммит изменений

```bash
# Убедись что в ветке dev
git checkout dev

# Добавь изменения
git add .

# Закоммить
git commit -m "feat: этап 3 - PostgreSQL подключение, Alembic миграции и тестовая таблица"

# Запушить dev, смержить в main, вернуться в dev
git push origin dev
git checkout main
git merge dev
git push origin main
git checkout dev
```

---

## 🔨 ЭТАП 4: REDIS ПОДКЛЮЧЕНИЕ + ТЕСТОВЫЙ КЛЮЧ

### Задача
Подключить Redis, создать сервис для работы с кешем, протестировать запись/чтение.

### Промт для Cursor

```
@backend/app/core Создай Redis сервис для BrashLens:

1. backend/app/core/redis.py:
   - Async Redis client
   - Функция get_redis_client() -> Redis
   - Dependency для FastAPI

2. backend/app/services/cache_service.py:
   - Класс CacheService
   - Методы:
     * async set(key: str, value: str, expire: int = 3600)
     * async get(key: str) -> str | None
     * async delete(key: str)
     * async ping() -> bool

3. Обнови backend/app/main.py:
   - Добавь эндпоинт GET /test-redis
   - Использует CacheService.ping()
   - Возвращает {"redis": "ok"} или {"redis": "error"}

4. Добавь эндпоинт POST /cache:
   - Принимает {"key": "...", "value": "..."}
   - Сохраняет в Redis
   - Возвращает {"status": "saved"}

5. Добавь эндпоинт GET /cache/{key}:
   - Возвращает значение из Redis
   - Или 404 если ключ не найден

Используй redis.asyncio, type hints, обработку ошибок.
```

### Реализация

1. **Генерируй код через Cursor**
2. **Перезапусти backend:**

```bash
cd BrashLens
docker compose restart backend
```

### ТРОЙНОЕ ТЕСТИРОВАНИЕ #4

#### ✅ Тест 1: Проверка подключения к Redis
```bash
# Тест ping
curl http://localhost:8000/test-redis

# Ожидаемый результат: {"redis":"ok"}
```

#### ✅ Тест 2: Запись в Redis через API
```bash
# Сохрани значение
curl -X POST http://localhost:8000/cache \
  -H "Content-Type: application/json" \
  -d '{"key":"test_key","value":"Hello Redis!"}'

# Ожидаемый результат: {"status":"saved"}

# Проверь через Redis CLI
cd ../infrastructure
docker compose exec redis redis-cli GET test_key

# Ожидаемый результат: "Hello Redis!"
```

#### ✅ Тест 3: Чтение из Redis через API
```bash
# Получи значение
curl http://localhost:8000/cache/test_key

# Ожидаемый результат: {"key":"test_key","value":"Hello Redis!"}

# Попробуй несуществующий ключ
curl http://localhost:8000/cache/nonexistent

# Ожидаемый результат: 404 Not Found
```

**Критерии прохождения:**
- ✅ Redis ping успешен
- ✅ Запись в Redis работает
- ✅ Чтение из Redis работает

**Если тесты не прошли:** проверь REDIS_URL, настройки клиента.

### Коммит изменений

```bash
# Убедись что в ветке dev
git checkout dev

# Добавь изменения
git add .

# Закоммить
git commit -m "feat: этап 4 - Redis подключение и cache service"

# Запушить dev, смержить в main, вернуться в dev
git push origin dev
git checkout main
git merge dev
git push origin main
git checkout dev
```

---

## 🔨 ЭТАП 5: CELERY WORKER + ТЕСТОВАЯ ЗАДАЧА

### Задача
Настроить Celery worker, создать тестовую задачу, проверить асинхронное выполнение.

### Промт для Cursor

```
@backend/app/core @backend/app/services Настрой Celery для BrashLens:

1. backend/app/core/celery_app.py:
   - Создание Celery app
   - Broker: Redis
   - Backend: Redis
   - Автообнаружение задач из app.services.tasks
   - Конфигурация:
     * task_serializer = 'json'
     * result_serializer = 'json'
     * accept_content = ['json']
     * timezone = 'UTC'
     * enable_utc = True

2. backend/app/services/tasks.py:
   - Декоратор @celery_app.task
   - Задача test_task(message: str):
     * Логирует сообщение
     * Спит 5 секунд (имитация работы)
     * Возвращает {"status": "completed", "message": message}
   - Задача add_numbers(a: int, b: int):
     * Возвращает сумму

3. backend/app/celery_worker.py (точка входа):
   - Импорт celery_app
   - __name__ == "__main__" -> celery_app.start()

4. Обнови docker compose.yml:
   - Для celery_worker укажи command: celery -A app.core.celery_app worker --loglevel=info

5. Добавь в backend/app/main.py эндпоинт POST /test-celery:
   - Принимает {"message": "..."}
   - Запускает test_task.delay(message)
   - Возвращает {"task_id": "..."}

6. Добавь эндпоинт GET /task-status/{task_id}:
   - Проверяет статус задачи
   - Возвращает {"status": "...", "result": "..."}

Используй type hints, логирование, обработку ошибок.
```

### Реализация

1. **Генерируй код через Cursor**
2. **Обнови docker-compose.yml**
3. **Пересобери и перезапусти:**

```bash
cd BrashLens
docker compose down
docker compose build
docker compose up -d
```

### ТРОЙНОЕ ТЕСТИРОВАНИЕ #5

#### ✅ Тест 1: Проверка запуска Celery Worker
```bash
# Проверь логи worker
cd BrashLens
docker compose logs celery-worker

# Ожидаемый результат:
# - Celery worker запущен
# - Подключение к Redis успешно
# - Задачи зарегистрированы (test_task, add_numbers)

# Проверь статус
docker compose ps celery-worker

# Ожидаемый результат: Up
```

#### ✅ Тест 2: Запуск задачи через API
```bash
# Запусти тестовую задачу
curl -X POST http://localhost:8000/test-celery \
  -H "Content-Type: application/json" \
  -d '{"message":"Testing Celery!"}'

# Ожидаемый результат: {"task_id":"..."}
# Сохрани task_id

# Сразу проверь статус
curl http://localhost:8000/task-status/{task_id}

# Ожидаемый результат: {"status":"PENDING",...} или {"status":"STARTED",...}

# Подожди 6 секунд и проверь снова
sleep 6
curl http://localhost:8000/task-status/{task_id}

# Ожидаемый результат: {"status":"SUCCESS","result":{...}}
```

#### ✅ Тест 3: Проверка логов задачи
```bash
# Смотри логи worker во время выполнения задачи
cd BrashLens
docker compose logs -f celery-worker

# Ожидаемый результат в логах:
# - Получена задача test_task
# - Лог сообщения "Testing Celery!"
# - Задача завершена успешно
```

**Критерии прохождения:**
- ✅ Celery worker запущен и подключен к Redis
- ✅ Задачи регистрируются и выполняются
- ✅ Статус задачи отслеживается через API

**Если тесты не прошли:** проверь конфигурацию Celery, Redis URL.

### Коммит изменений

```bash
# Убедись что в ветке dev
git checkout dev

# Добавь изменения
git add .

# Закоммить
git commit -m "feat: этап 5 - Celery worker с тестовыми задачами"

# Запушить dev, смержить в main, вернуться в dev
git push origin dev
git checkout main
git merge dev
git push origin main
git checkout dev
```

---

## 🔨 ЭТАП 6: TELEGRAM БОТ - БАЗОВАЯ НАСТРОЙКА

### Задача
Зарегистрировать бота через BotFather, создать отдельный сервис для чат-бота в Docker, настроить обработчик команды `/start`.

### Предварительные действия

1. **Регистрация бота:**
   - Открой Telegram, найди @BotFather
   - Отправь `/newbot`
   - Укажи имя: `BrashLens Bot`
   - Укажи username: `brashlens_yourname_bot`
   - Скопируй токен: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

2. **Добавь токен в .env:**
```bash
# В BrashLens/backend/.env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
WEBHOOK_URL=https://yourdomain.com/webhook  # Опционально для production
```

### Промт для Cursor

```
@backend/app Создай Telegram бота для BrashLens как отдельный сервис:

1. backend/app/bot/__init__.py - пустой файл

2. backend/app/bot/handlers.py:
   - Обработчик команды /start:
     * Отправляет "👋 Привет! Я BrashLens бот."
     * Добавляет кнопки Inline:
       - "📸 Я фотограф"
       - "👤 Я клиент"

3. backend/app/bot/bot.py:
   - Инициализация бота (Application.builder())
   - Регистрация handlers
   - Функция setup_webhook(webhook_url: str)
   - Функция start_polling() для локальной разработки
   - Функция main() для запуска бота

4. backend/app/bot/main.py:
   - Точка входа для запуска бота как отдельного процесса
   - Загружает конфигурацию
   - Запускает polling или webhook в зависимости от настроек

5. backend/app/api/v1/webhook.py (для webhook режима):
   - Router для webhook
   - POST /webhook:
     * Принимает Update от Telegram
     * Обрабатывает через бота
     * Возвращает 200 OK

6. Обнови backend/app/core/config.py:
   - Добавь TELEGRAM_BOT_TOKEN: str
   - Добавь WEBHOOK_URL: str | None = None

7. Создай backend/Dockerfile.bot для чат-бота:
   - Базовый образ python:3.11-slim
   - Копирует код бота
   - CMD запускает bot/main.py

8. Обнови BrashLens/docker-compose.yml:
   - Добавь сервис chat-bot:
     * build: context: ./backend, dockerfile: Dockerfile.bot
     * container_name: brashlens_chat_bot
     * environment: TELEGRAM_BOT_TOKEN, WEBHOOK_URL
     * env_file: ./backend/.env
     * networks: shared-network
     * restart: unless-stopped
     * depends_on: backend (для webhook режима)

Используй python-telegram-bot 20.7, async/await, type hints.
```

### Реализация

1. **Генерируй код через Cursor**
2. **Для локальной разработки используй polling** (закомментируй WEBHOOK_URL в .env)
3. **Запусти чат-бот:**

```bash
cd BrashLens
docker compose up -d chat-bot
```

### ТРОЙНОЕ ТЕСТИРОВАНИЕ #6

#### ✅ Тест 1: Проверка запуска бота
```bash
# Проверь логи chat-bot
cd BrashLens
docker compose logs chat-bot | grep -i telegram

# Ожидаемый результат:
# - "Bot started in polling mode" или "Webhook set to ..."
# - Нет ошибок авторизации
# - Контейнер chat-bot запущен и работает
```

#### ✅ Тест 2: Отправка /start в Telegram
```bash
# Ручной тест в Telegram:
1. Открой чат с ботом
2. Отправь /start
3. Ожидаемый результат:
   - Бот отвечает "👋 Привет! Я BrashLens бот."
   - Видны кнопки "📸 Я фотограф" и "👤 Я клиент"

# Проверь логи обработки команды
docker compose logs chat-bot | tail -20
```

#### ✅ Тест 3: Проверка callback кнопок
```bash
# Ручной тест в Telegram:
1. Нажми кнопку "📸 Я фотограф"
2. Ожидаемый результат:
   - Бот реагирует (пока может быть заглушка)
   - Нет ошибок в логах

# Проверь логи callback
docker compose logs backend | grep -i callback
```

**Критерии прохождения:**
- ✅ Бот запущен и отвечает на сообщения
- ✅ Команда /start работает корректно
- ✅ Кнопки отображаются (обработка - позже)

**Если тесты не прошли:** проверь токен, права бота, логи ошибок.

### Коммит изменений

```bash
# Убедись что в ветке dev
git checkout dev

# Добавь изменения
git add .

# Закоммить
git commit -m "feat: этап 6 - Telegram бот с базовой настройкой и командой /start"

# Запушить dev, смержить в main, вернуться в dev
git push origin dev
git checkout main
git merge dev
git push origin main
git checkout dev
```

---

## 🔨 ЭТАП 7: ДЕПЛОЙ НА VPS

### Задача
Настроить VPS, задеплоить приложение, настроить Nginx, SSL, автозапуск.

### Предварительные требования

- VPS с Ubuntu 22.04+
- Доменное имя (brashlens.example.com)
- SSH доступ

### Промт для Cursor

```
@docs Создай документацию по деплою BrashLens:

1. docs/deployment.md:
   
   Секция "VPS Setup":
   - Установка Docker & Docker Compose
   - Настройка firewall (ufw)
   - Создание пользователя deploy
   
   Секция "Application Deploy":
   - Клонирование репозитория
   - Копирование .env.production
   - docker compose -f docker-compose.prod.yml up -d
   
   Секция "Nginx Configuration":
   - Установка Nginx
   - Конфигурация reverse proxy
   - Настройка для FastAPI (/api, /docs)
   - Настройка для React SPA (/, /assets)
   
   Секция "SSL Certificates":
   - Установка Certbot
   - Получение Let's Encrypt сертификата
   - Auto-renewal настройка
   
   Секция "Systemd Service":
   - Создание brashlens.service
   - Автозапуск при перезагрузке
   
   Секция "CI/CD":
   - Базовый deploy.sh скрипт:
     * git checkout main (на сервере работаем с main)
     * git pull origin main
     * docker compose build
     * docker compose up -d
     * docker compose exec backend alembic upgrade head

2. docker-compose.prod.yml:
   - Отличия от dev версии:
     * Без volume для hot reload
     * Restart: always
     * Healthchecks
     * Логирование в файлы

3. nginx/brashlens.conf:
   - Конфигурация Nginx
   - Proxy pass для backend
   - Static файлы для frontend
   - WebSocket support для Telegram

Включи команды для Ubuntu 22.04, безопасные настройки.
```

### Реализация

**Важно для MacBook M1:** Docker образы должны быть multi-platform или собраны для linux/amd64.

1. **Генерируй документацию через Cursor**
2. **Следуй инструкциям в docs/deployment.md**

### Пошаговый деплой

```bash
# На VPS
ssh deploy@brashlens.example.com

# Клонируй репозиторий
git clone https://github.com/yourusername/brashlens.git
cd brashlens

# Для разработки переключись на dev ветку
git checkout dev

# Настрой .env
cp backend/.env.example backend/.env
nano backend/.env  # Заполни production значения

# Запусти
docker compose -f docker-compose.prod.yml up -d

# Проверь статус
docker compose -f docker-compose.prod.yml ps

# Проверь логи
docker compose -f docker-compose.prod.yml logs
```

### Настройка Nginx

```bash
# Установи Nginx
sudo apt update
sudo apt install nginx

# Скопируй конфигурацию
sudo cp nginx/brashlens.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/brashlens.conf /etc/nginx/sites-enabled/

# Проверь конфигурацию
sudo nginx -t

# Перезапусти
sudo systemctl restart nginx
```

### Настройка SSL

```bash
# Установи Certbot
sudo apt install certbot python3-certbot-nginx

# Получи сертификат
sudo certbot --nginx -d brashlens.example.com

# Auto-renewal уже настроен через systemd timer
```

### Настройка webhook для бота

```bash
# Обнови .env на сервере
WEBHOOK_URL=https://brashlens.example.com/webhook

# Перезапусти backend
docker compose -f docker-compose.prod.yml restart backend
```

### ТРОЙНОЕ ТЕСТИРОВАНИЕ #7

#### ✅ Тест 1: Проверка доступности сервисов
```bash
# На VPS проверь статус контейнеров
docker compose -f docker-compose.prod.yml ps

# Ожидаемый результат: все контейнеры Up и Healthy

# Проверь доступность API
curl https://brashlens.example.com/health

# Ожидаемый результат: {"status":"ok",...}
```

#### ✅ Тест 2: Проверка Nginx и SSL
```bash
# Проверь SSL сертификат
curl -I https://brashlens.example.com

# Ожидаемый результат: HTTP/2 200, сертификат валиден

# Проверь редирект с HTTP на HTTPS
curl -I http://brashlens.example.com

# Ожидаемый результат: 301 или 302 редирект на HTTPS

# Проверь документацию API
open https://brashlens.example.com/docs
```

#### ✅ Тест 3: Проверка webhook бота
```bash
# Отправь /start боту в Telegram
# Ожидаемый результат: бот отвечает через webhook

# Проверь логи webhook
docker compose -f docker-compose.prod.yml logs backend | grep webhook

# Ожидаемый результат: POST /webhook 200 OK

# Проверь что webhook установлен
# В логах должно быть: "Webhook set to https://brashlens.example.com/webhook"
```

**Критерии прохождения:**
- ✅ Все сервисы запущены на VPS
- ✅ API доступен через HTTPS
- ✅ SSL сертификат валиден
- ✅ Nginx корректно проксирует запросы
- ✅ Telegram webhook работает

**Если тесты не прошли:** проверь логи, firewall, DNS настройки.

### Коммит изменений

```bash
# Убедись что в ветке dev
git checkout dev

# Добавь изменения
git add .

# Закоммить
git commit -m "feat: этап 7 - Деплой на VPS с Nginx, SSL и webhook"

# Запушить dev, смержить в main, вернуться в dev
git push origin dev
git checkout main
git merge dev
git push origin main
git checkout dev
```

---

## 🔨 ЭТАП 8: SYSTEMD + АВТОЗАПУСК

### Задача
Настроить автоматический запуск приложения при перезагрузке сервера.

### Реализация

Создай systemd service на VPS:

```bash
# На VPS
sudo nano /etc/systemd/system/brashlens.service
```

Содержимое файла:

```ini
[Unit]
Description=BrashLens Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/deploy/brashlens
ExecStart=/usr/local/bin/docker compose -f docker-compose.prod.yml up -d
ExecStop=/usr/local/bin/docker compose -f docker-compose.prod.yml down
User=deploy
Group=deploy

[Install]
WantedBy=multi-user.target
```

Активируй сервис:

```bash
sudo systemctl daemon-reload
sudo systemctl enable brashlens.service
sudo systemctl start brashlens.service
```

### ТРОЙНОЕ ТЕСТИРОВАНИЕ #8

#### ✅ Тест 1: Проверка статуса systemd service
```bash
# Проверь статус сервиса
sudo systemctl status brashlens.service

# Ожидаемый результат:
# - Active: active (running)
# - Enabled: enabled
```

#### ✅ Тест 2: Тест автозапуска при перезагрузке
```bash
# Перезагрузи сервер
sudo reboot

# Подожди 2-3 минуты, затем подключись снова
ssh deploy@brashlens.example.com

# Проверь что все контейнеры запустились автоматически
docker ps

# Ожидаемый результат: все контейнеры Running

# Проверь доступность API
curl https://brashlens.example.com/health
```

#### ✅ Тест 3: Проверка логов автозапуска
```bash
# Проверь логи systemd
sudo journalctl -u brashlens.service -n 50

# Ожидаемый результат: успешный запуск без ошибок

# Проверь что бот работает
# Отправь /start боту в Telegram
```

**Критерии прохождения:**
- ✅ Systemd service запущен и enabled
- ✅ После перезагрузки все контейнеры стартуют автоматически
- ✅ Приложение доступно после перезагрузки

**Если тесты не прошли:** проверь права пользователя deploy, пути в service файле.

### Коммит изменений

```bash
# Убедись что в ветке dev
git checkout dev

# Добавь изменения
git add .

# Закоммить
git commit -m "feat: этап 8 - Systemd service для автозапуска приложения"

# Запушить dev, смержить в main, вернуться в dev
git push origin dev
git checkout main
git merge dev
git push origin main
git checkout dev
```

---

## 🔨 ЭТАП 9: CI/CD СКРИПТ ДЕПЛОЯ

### Задача
Создать простой скрипт для обновления приложения на сервере.

### Промт для Cursor

```
@docs Создай скрипт автоматического деплоя:

1. scripts/deploy.sh:
   - Цветной вывод (green, red, yellow)
   - Шаги:
     * Проверка что запущено на VPS (не локально)
     * git pull origin main
     * Проверка изменений в requirements.txt
     * Если есть изменения -> docker compose build
     * docker compose -f docker-compose.prod.yml up -d
     * Применение миграций: docker compose exec backend alembic upgrade head
     * Restart сервисов
     * Healthcheck: curl /health
     * Вывод статуса всех контейнеров
   - Обработка ошибок на каждом шаге
   - Rollback если что-то пошло не так

2. scripts/rollback.sh:
   - git checkout HEAD~1
   - docker compose down
   - docker compose up -d
   - Восстановление миграций БД

3. .github/workflows/deploy.yml (если используешь GitHub):
   - Триггер: push в main
   - Job: Deploy to VPS
   - SSH в VPS
   - Запуск deploy.sh

Скрипты для bash, безопасные, с логированием.
```

### Реализация

1. **Генерируй скрипты через Cursor**
2. **Сделай их исполняемыми:**

```bash
chmod +x scripts/deploy.sh
chmod +x scripts/rollback.sh
```

### ТРОЙНОЕ ТЕСТИРОВАНИЕ #9

#### ✅ Тест 1: Локальная проверка скрипта
```bash
# Проверь синтаксис
bash -n scripts/deploy.sh

# Ожидаемый результат: нет ошибок синтаксиса
```

#### ✅ Тест 2: Тестовый деплой на VPS
```bash
# На VPS
cd /home/deploy/brashlens

# Сделай небольшое изменение (например, в README)
echo "# Test deploy" >> README.md
git add README.md
git commit -m "Test deploy script"

# Запушить dev, смержить в main, вернуться в dev
git push origin dev
git checkout main
git merge dev
git push origin main
git checkout dev

# Запусти deploy скрипт
./scripts/deploy.sh

# Ожидаемый результат:
# - Успешный git pull
# - Контейнеры перезапущены
# - Healthcheck passed
# - Статус контейнеров: все Running
```

#### ✅ Тест 3: Проверка rollback
```bash
# Сделай ещё один коммит
echo "# Another change" >> README.md
git add README.md
git commit -m "Test rollback"

# Запушить dev, смержить в main, вернуться в dev
git push origin dev
git checkout main
git merge dev
git push origin main
git checkout dev

./scripts/deploy.sh

# Откатись назад
./scripts/rollback.sh

# Проверь что изменения отменены
cat README.md

# Ожидаемый результат: последняя строка не должна быть видна

# Проверь что приложение работает
curl https://brashlens.example.com/health
```

**Критерии прохождения:**
- ✅ Скрипт deploy.sh успешно обновляет приложение
- ✅ Все этапы деплоя выполняются без ошибок
- ✅ Скрипт rollback.sh откатывает изменения

**Если тесты не прошли:** добавь больше логирования, проверь пути и права.

### Коммит изменений

```bash
# Убедись что в ветке dev
git checkout dev

# Добавь изменения
git add .

# Закоммить
git commit -m "feat: этап 9 - CI/CD скрипты деплоя и rollback"

# Запушить dev, смержить в main, вернуться в dev
git push origin dev
git checkout main
git merge dev
git push origin main
git checkout dev
```

---

## 📊 ФИНАЛЬНАЯ ПРОВЕРКА ИТЕРАЦИИ 1

### Чеклист завершения

Пройдись по всем критериям:

- [ ] **Docker Compose:**
  - [ ] PostgreSQL работает и доступен (infrastructure/)
  - [ ] Redis работает и доступен (infrastructure/)
  - [ ] Backend запускается без ошибок
  - [ ] Chat-bot запущен и работает
  - [ ] Celery worker обрабатывает задачи
  - [ ] Celery beat запущен (если настроен)

- [ ] **FastAPI:**
  - [ ] Эндпоинты /health и / работают
  - [ ] Swagger UI доступен на /docs
  - [ ] Подключение к PostgreSQL успешно
  - [ ] Подключение к Redis успешно

- [ ] **База данных:**
  - [ ] Alembic настроен корректно
  - [ ] Миграции применяются
  - [ ] Тестовая таблица создана
  - [ ] Можно создавать записи

- [ ] **Celery:**
  - [ ] Worker запущен
  - [ ] Тестовая задача выполняется
  - [ ] Статус задачи отслеживается

- [ ] **Telegram Bot:**
  - [ ] Бот зарегистрирован в BotFather
  - [ ] Команда /start работает
  - [ ] Кнопки отображаются
  - [ ] Webhook настроен (production) или polling работает (dev)

- [ ] **Деплой:**
  - [ ] VPS настроен
  - [ ] Nginx проксирует запросы
  - [ ] SSL сертификат валиден
  - [ ] Systemd service запускает приложение
  - [ ] Автозапуск при перезагрузке работает
  - [ ] Скрипт deploy.sh обновляет приложение

### Итоговое тестирование системы

```bash
# 1. Проверь все контейнеры
docker compose ps

# 2. Проверь API
curl https://brashlens.example.com/health
curl https://brashlens.example.com/docs

# 3. Проверь БД
cd infrastructure
docker compose exec postgres psql -U ${POSTGRES_USER:-postgres} -d ${POSTGRES_DB:-brashlens_db} -c "SELECT COUNT(*) FROM test_connections;"

# 4. Проверь Redis
docker compose exec redis redis-cli PING

# 5. Запусти тестовую Celery задачу
curl -X POST https://brashlens.example.com/test-celery \
  -H "Content-Type: application/json" \
  -d '{"message":"Final test"}'

# 6. Проверь бота в Telegram
# Отправь /start
```

**Критерии успеха итерации:**
- ✅ Все контейнеры работают стабильно
- ✅ API доступен и отвечает
- ✅ База данных принимает запросы
- ✅ Redis кеширует данные
- ✅ Celery выполняет задачи
- ✅ Telegram бот отвечает на команды
- ✅ Деплой на VPS успешен
- ✅ Автозапуск работает
- ✅ Логи пишутся корректно

---

## 📝 КОММИТ И ПОДГОТОВКА К ИТЕРАЦИИ 2

### Финальный коммит

```bash
# Убедись что в ветке dev
git checkout dev

# Добавь изменения
git add .

# Закоммить
git commit -m "feat: iteration 1 - infrastructure skeleton

- Setup Docker Compose with PostgreSQL, Redis, FastAPI, Celery
- Configure FastAPI with health check and docs endpoints
- Setup Alembic migrations
- Connect PostgreSQL with test table
- Connect Redis with cache service
- Setup Celery worker with test tasks
- Create Telegram bot with /start command
- Deploy to VPS with Nginx and SSL
- Configure systemd auto-start
- Create deploy and rollback scripts

All services tested and working in production."

# Запушить dev, смержить в main, вернуться в dev
git push origin dev
git checkout main
git merge dev
git push origin main
git checkout dev
```

### Документация

Создай краткий отчёт:

```markdown
# Итерация 1 - Завершена ✅

## Реализовано
- ✅ Docker Compose инфраструктура
- ✅ FastAPI базовое приложение
- ✅ PostgreSQL + Alembic
- ✅ Redis кеширование
- ✅ Celery worker
- ✅ Telegram бот (базовый)
- ✅ Деплой на VPS
- ✅ Nginx + SSL
- ✅ Systemd автозапуск
- ✅ CI/CD скрипты

## Технические метрики
- Контейнеров: 6 (brashlens_postgres, brashlens_redis, backend, chat-bot, celery-worker, celery-beat)
- API endpoints: 8
- Моделей БД: 1 (test_connections)
- Celery задач: 2
- Время деплоя: ~3 минуты

## Следующая итерация
Итерация 2: Регистрация пользователей
- Модель User
- Выбор роли (фотограф/клиент)
- Сохранение в БД
- API для работы с пользователями
```

---

## 🎯 ИТОГО

**Что получилось в итерации 1:**
- ✅ Рабочая инфраструктура на Docker
- ✅ FastAPI с документацией
- ✅ PostgreSQL с миграциями
- ✅ Redis для кеша и очередей
- ✅ Celery для фоновых задач
- ✅ Telegram бот отвечает на /start
- ✅ Приложение задеплоено на VPS
- ✅ Автоматический деплой настроен

**Время выполнения:** 3-5 дней

**Готовность к итерации 2:** ✅

---

## 📚 ПОЛЕЗНЫЕ КОМАНДЫ

### Docker
```bash
# Пересобрать все контейнеры приложения
cd BrashLens
docker compose build --no-cache

# Перезапустить конкретный сервис
docker compose restart backend

# Посмотреть логи
docker compose logs -f backend

# Зайти в контейнер
docker compose exec backend bash

# Остановить приложение (не удаляет инфраструктуру)
docker compose down

# Остановить инфраструктуру (осторожно - удалит данные если не сохранены)
cd ../infrastructure
docker compose down -v
```

### База данных
```bash
# Создать миграцию
cd BrashLens
docker compose exec backend alembic revision --autogenerate -m "Description"

# Применить миграции
docker compose exec backend alembic upgrade head

# Откатить миграцию
docker compose exec backend alembic downgrade -1

# Посмотреть историю миграций
docker compose exec backend alembic history
```

### Celery
```bash
# Посмотреть активные задачи
cd BrashLens
docker compose exec celery-worker celery -A app.core.celery_app inspect active

# Очистить очередь
cd ../infrastructure
docker compose exec redis redis-cli FLUSHALL
```

### Nginx
```bash
# Проверить конфигурацию
sudo nginx -t

# Перезапустить
sudo systemctl restart nginx

# Посмотреть логи ошибок
sudo tail -f /var/log/nginx/error.log
```

---

**Успехов в разработке! 🚀**

При проблемах:
1. Проверь логи контейнеров
2. Проверь .env файл
3. Проверь доступность портов
4. Проверь права доступа
5. Прогони тесты заново

**Следующая итерация:** Регистрация пользователей (User модель + роли)
