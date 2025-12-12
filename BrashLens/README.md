# BrashLens Application

Telegram Mini App для управления фотобизнесом.

## Структура

- `backend/` - FastAPI приложение
- `frontend/` - React приложение

## Запуск

### Предварительные требования

1. Убедись, что инфраструктура запущена:
```bash
cd ../infrastructure
docker compose up -d
```

2. Настрой переменные окружения:
```bash
cp .env.example .env
# Отредактируй .env и заполни значения из infrastructure/.env
cp backend/.env.example backend/.env
# Отредактируй backend/.env
```

### Запуск приложения

```bash
docker compose up -d
```

### Проверка статуса

```bash
docker compose ps
```

### Логи

```bash
docker compose logs -f backend
docker compose logs -f chat-bot
docker compose logs -f celery-worker
docker compose logs -f celery-beat
```

## Разработка

### Backend (локально)

1. Создать виртуальное окружение:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # на macOS/Linux
```

2. Установить зависимости:
```bash
pip install -r requirements.txt
```

3. Настроить переменные окружения:
```bash
cp .env.example .env
# Отредактировать .env файл
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Остановка

```bash
docker compose down
```

**Важно:** Остановка приложения не останавливает инфраструктуру (brashlens_postgres, brashlens_redis).

## Сервисы

- **backend** - FastAPI приложение (порт 8001)
- **chat-bot** - Telegram бот (отдельный сервис)
- **celery-worker** - Celery worker для фоновых задач
- **celery-beat** - Celery beat для периодических задач
