#!/bin/bash
# Скрипт для инициализации БД с правильным пользователем и паролем
# Использование: ./init_db.sh
# 
# ВАЖНО: Переменные POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB должны быть заданы
# через .env файл или переменные окружения (загружаются из infrastructure/.env)

set -e

# Загружаем переменные из .env если файл существует
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Проверяем обязательные переменные
if [ -z "$POSTGRES_USER" ]; then
    echo "Ошибка: POSTGRES_USER не задан!"
    echo "Создайте файл infrastructure/.env с переменными из infrastructure/.env.example"
    exit 1
fi

if [ -z "$POSTGRES_PASSWORD" ]; then
    echo "Ошибка: POSTGRES_PASSWORD не задан!"
    echo "Создайте файл infrastructure/.env с переменными из infrastructure/.env.example"
    exit 1
fi

POSTGRES_DB="${POSTGRES_DB:-brashlens_db}"

echo "Инициализация базы данных BrashLens..."

# Проверяем, запущен ли контейнер
if ! docker ps | grep -q brashlens_postgres; then
    echo "Ошибка: Контейнер brashlens_postgres не запущен!"
    echo "Запустите: cd infrastructure && docker compose up -d"
    exit 1
fi

# Определяем пользователя для подключения (используем POSTGRES_USER или postgres)
# Если POSTGRES_USER уже существует, используем его, иначе postgres
INIT_USER="postgres"
if docker exec brashlens_postgres psql -U postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='${POSTGRES_USER}'" 2>/dev/null | grep -q 1; then
    INIT_USER="${POSTGRES_USER}"
fi

# Подключаемся к PostgreSQL
docker exec -i brashlens_postgres psql -U ${INIT_USER} <<EOF
-- Удаляем старых пользователей (кроме postgres)
DO \$\$
DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT usename FROM pg_user WHERE usename NOT IN ('postgres', '${POSTGRES_USER}')) 
    LOOP
        EXECUTE 'DROP USER IF EXISTS ' || quote_ident(r.usename) || ' CASCADE';
    END LOOP;
END
\$\$;

-- Создаем или обновляем пользователя
DO \$\$
BEGIN
    IF EXISTS (SELECT FROM pg_user WHERE usename = '${POSTGRES_USER}') THEN
        ALTER USER ${POSTGRES_USER} WITH PASSWORD '${POSTGRES_PASSWORD}';
        RAISE NOTICE 'Пользователь ${POSTGRES_USER} обновлен';
    ELSE
        CREATE USER ${POSTGRES_USER} WITH PASSWORD '${POSTGRES_PASSWORD}';
        RAISE NOTICE 'Пользователь ${POSTGRES_USER} создан';
    END IF;
END
\$\$;

-- Даем права суперпользователя (для разработки)
ALTER USER ${POSTGRES_USER} WITH SUPERUSER CREATEDB CREATEROLE;

-- Создаем базу данных если не существует
SELECT 'CREATE DATABASE ${POSTGRES_DB} OWNER ${POSTGRES_USER}'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${POSTGRES_DB}')\gexec

-- Даем все права на базу данных
GRANT ALL PRIVILEGES ON DATABASE ${POSTGRES_DB} TO ${POSTGRES_USER};

-- Подключаемся к базе данных и даем права на схему public
\c ${POSTGRES_DB}
GRANT ALL ON SCHEMA public TO ${POSTGRES_USER};
ALTER SCHEMA public OWNER TO ${POSTGRES_USER};

\q
EOF

echo "База данных ${POSTGRES_DB} инициализирована успешно!"
echo "Пользователь: ${POSTGRES_USER}"
echo "База данных: ${POSTGRES_DB}"
