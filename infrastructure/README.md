# Infrastructure

Общая инфраструктура для проекта BrashLens: PostgreSQL и Redis.

## Сервисы

- **postgres** (`brashlens_postgres`) - PostgreSQL 16 с расширением pgvector
- **redis** (`brashlens_redis`) - Redis 7 для кеша, очередей Celery и сессий

## Запуск инфраструктуры

### Разработка

```bash
cd infrastructure
cp .env.example .env
# Отредактируйте .env и заполните реальные значения из ../.secret
nano .env
docker compose up -d
```

### Продакшн

```bash
cd infrastructure
cp .env.example .env
# Отредактируйте .env с production значениями (сильные пароли!)
nano .env
docker compose up -d
```

**ВАЖНО:** 
- Файл `.env` НЕ коммитится в Git (добавлен в .gitignore)
- Для продакшна используйте сильные пароли (минимум 32 символа)
- Все значения должны быть заданы в `.env` файле

**Важно:** После первого запуска выполните инициализацию БД (см. ниже).

## Инициализация базы данных

После первого запуска инфраструктуры выполните инициализацию БД:

```bash
# Убедитесь, что контейнер запущен
docker compose ps

# Запустите скрипт инициализации
./init_db.sh
```

Скрипт создаст:
- Базу данных `brashlens_db`
- Пользователя `govardvolov` с указанным паролем
- Удалит лишних пользователей (кроме postgres и govardvolov)
- Настроит все необходимые права доступа

**Важно:** 
- Данные для подключения задаются в файле `infrastructure/.env`
- Для разработки используйте значения из `.secret` в корне проекта
- Для продакшна используйте сильные пароли и безопасные настройки
- Скрипт автоматически определяет существующего пользователя и обновляет его права

## Проверка статуса

```bash
docker compose ps
```

## Проверка подключения

```bash
# PostgreSQL (используйте пользователя из .secret)
docker exec -it brashlens_postgres psql -U govardvolov -d brashlens_db

# Redis
docker exec -it brashlens_redis redis-cli ping
```

## Остановка

```bash
docker compose down
```

**Внимание:** Остановка удалит контейнеры, но данные сохранятся в volumes (`postgres_data`, `redis_data`).

## Удаление данных

Если нужно полностью удалить данные:

```bash
docker compose down -v
```

## Важно

- Инфраструктура должна быть запущена **до** запуска приложений BrashLens
- Используется Docker network `shared-network` для связи между сервисами
- Volumes сохраняют данные между перезапусками
- Контейнеры доступны по именам: `brashlens_postgres`, `brashlens_redis`
- Все чувствительные данные (пароли, токены) хранятся в файле `.env` (не коммитится в Git)
- Для разработки используйте `.secret` как справочник
- Для продакшна см. `docs/PRODUCTION_SETUP.md`
