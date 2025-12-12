# BrashLens

Telegram Mini App для управления фотобизнесом.

## Структура проекта

```
BrashLens/
├── infrastructure/          # Общая инфраструктура (PostgreSQL, Redis)
│   ├── docker-compose.yml
│   └── .env.example
├── BrashLens/              # Основное приложение
│   ├── backend/            # FastAPI приложение
│   ├── frontend/           # React приложение
│   ├── docker-compose.yml
│   └── .env.example
└── README.md
```

## Быстрый старт

### 0. Настройка секретов

**Важно:** Все чувствительные данные (пароли, токены, API ключи) хранятся в файле `.secret` в корне проекта.

```bash
# Файл .secret уже создан и содержит:
# - Учетные данные для PostgreSQL (пользователь: govardvolov)
# - Шаблоны для других секретов
# Используйте его как справочник для заполнения .env файлов
```

### 1. Запуск инфраструктуры

```bash
cd infrastructure
cp .env.example .env
# Отредактируй .env - скопируй значения из ../.secret (для разработки)
# Или используй production значения (для продакшна)
nano .env
docker compose up -d

# После первого запуска выполни инициализацию БД:
./init_db.sh
```

**ВАЖНО:** 
- Файл `.env` обязателен и НЕ коммитится в Git
- Для продакшна используйте сильные пароли (см. `docs/PRODUCTION_SETUP.md`)

**Скрипт `init_db.sh` создаст:**
- Базу данных `brashlens_db`
- Пользователя `govardvolov` с паролем из `.secret`
- Удалит лишних пользователей
- Настроит все права доступа

### 2. Запуск приложения

```bash
cd ../BrashLens
cp .env.example .env
# Отредактируй .env - скопируй значения из ../.secret
cp backend/.env.example backend/.env
# Отредактируй backend/.env - используй данные из ../.secret
docker compose up -d
```

### 3. Проверка

```bash
# Проверь инфраструктуру
cd infrastructure && docker compose ps

# Проверь приложение
cd ../BrashLens && docker compose ps

# Проверь API
curl http://localhost:8001/health
```

## Разработка

### Backend (локально)

1. Создать виртуальное окружение:
```bash
cd BrashLens/backend
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
cd BrashLens/frontend
npm install
npm run dev
```

## Очистка глобальных пакетов Python

Для очистки глобальных установок Python (оставляет только pip, setuptools, wheel):

```bash
./cleanup_global_python.sh
```

## Обновление pip во всех версиях Python

Для обновления pip во всех глобально установленных версиях Python:

```bash
./update_all_pip.sh
```

**Важно:** Все зависимости проектов должны быть в виртуальных окружениях!

## Остановка

```bash
# Остановить приложение
cd BrashLens && docker compose down

# Остановить инфраструктуру (осторожно - удалит данные если не сохранены)
cd infrastructure && docker compose down
```

## Сервисы

### Инфраструктура (infrastructure/)
- **brashlens_postgres** - PostgreSQL 16 с pgvector
- **brashlens_redis** - Redis 7 для кеша и очередей

### Приложение (BrashLens/)
- **backend** - FastAPI приложение (порт 8001)
- **chat-bot** - Telegram бот (отдельный сервис)
- **celery-worker** - Celery worker для фоновых задач
- **celery-beat** - Celery beat для периодических задач

## Секретные данные

**Файл `.secret`:**
- Справочник всех чувствительных данных проекта
- Расположен в корне проекта
- НЕ коммитится в Git
- Используйте его для заполнения `.env` файлов

**База данных:**
- Имя БД: `brashlens_db`
- Пользователь: `govardvolov`
- Пароль и другие данные: см. `.secret`
- Инициализация: `infrastructure/init_db.sh`

## Добавление нового приложения

1. Создай директорию для нового приложения
2. Создай `docker-compose.yml` с подключением к `shared-network`
3. Используй имена контейнеров из infrastructure: `brashlens_postgres`, `brashlens_redis`
4. Используй данные из `.secret` для настройки подключений
