# Настройка Production окружения

## Общие принципы

1. **Все секреты в .env файлах** - никогда не коммитьте .env в Git
2. **Сильные пароли** - минимум 32 символа, используйте генераторы паролей
3. **Ограничение доступа** - не публикуйте порты БД наружу
4. **Бэкапы** - настройте автоматические бэкапы БД
5. **Мониторинг** - настройте логирование и мониторинг

## Первоначальная настройка

### 1. Настройка инфраструктуры

```bash
cd infrastructure

# Скопируй шаблон
cp .env.example .env

# Отредактируй .env с production значениями
nano .env
```

**Пример .env для продакшна:**
```bash
POSTGRES_USER=brashlens_prod_user
POSTGRES_PASSWORD=<сильный_пароль_32+_символов>
POSTGRES_DB=brashlens_db
```

### 2. Запуск инфраструктуры

```bash
# Запусти инфраструктуру
docker compose up -d

# Дождись готовности
docker compose ps

# Инициализируй БД (создаст пользователя и базу)
./init_db.sh
```

### 3. Настройка приложения

```bash
cd ../BrashLens

# Скопируй шаблоны
cp .env.example .env
cp backend/.env.example backend/.env

# Отредактируй с production значениями
nano .env
nano backend/.env
```

**Важно:** DATABASE_URL должен использовать те же значения что в infrastructure/.env

### 4. Безопасность портов

В продакшне не публикуйте порты БД наружу. Обновите `infrastructure/docker-compose.yml`:

```yaml
postgres:
  # Убери строку с ports для продакшна:
  # ports:
  #   - "5432:5432"
  
redis:
  # Убери строку с ports для продакшна:
  # ports:
  #   - "6379:6379"
```

Или создайте `infrastructure/docker-compose.prod.yml`:

```yaml
services:
  postgres:
    # Не публикуем порты наружу в продакшне
    # ports: [] 
    
  redis:
    # Не публикуем порты наружу в продакшне
    # ports: []
```

## Генерация секретов

### Генерация SECRET_KEY

```bash
# Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# OpenSSL
openssl rand -hex 32

# Bash
cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1
```

### Генерация паролей БД

```bash
# Генерация сильного пароля
openssl rand -base64 32

# Или используй менеджер паролей (1Password, Bitwarden и т.д.)
```

## Настройка бэкапов

### Автоматический бэкап PostgreSQL

Создай `infrastructure/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
CONTAINER="brashlens_postgres"

# Загрузи переменные из .env
source .env

mkdir -p $BACKUP_DIR

docker exec $CONTAINER pg_dump -U $POSTGRES_USER $POSTGRES_DB > $BACKUP_DIR/backup_$DATE.sql

# Удаляй бэкапы старше 30 дней
find $BACKUP_DIR -name "backup_*.sql" -mtime +30 -delete
```

Добавь в crontab:
```bash
# Бэкап каждый день в 2:00
0 2 * * * /path/to/infrastructure/backup.sh
```

## Мониторинг

### Проверка здоровья сервисов

```bash
# Статус контейнеров
docker compose ps

# Логи
docker compose logs -f

# Использование ресурсов
docker stats
```

### Настройка алертов

Рекомендуется использовать:
- Prometheus + Grafana для метрик
- Sentry для ошибок
- Log aggregation (ELK, Loki)

## Обновление

### Безопасное обновление

1. **Создай бэкап:**
```bash
cd infrastructure
./backup.sh
```

2. **Обнови код:**
```bash
# На сервере обычно работаем с main веткой
git checkout main
git pull origin main
```

3. **Пересобери и перезапусти:**
```bash
cd BrashLens
docker compose build
docker compose up -d
```

4. **Проверь работоспособность:**
```bash
curl http://localhost:8001/health
```

## Чеклист безопасности

- [ ] Все .env файлы в .gitignore
- [ ] Сильные пароли (32+ символов)
- [ ] Порты БД не опубликованы наружу
- [ ] Настроены бэкапы
- [ ] SSL сертификаты для HTTPS
- [ ] Firewall настроен
- [ ] Регулярные обновления безопасности
- [ ] Мониторинг и алерты настроены
- [ ] Логирование настроено
- [ ] Ограничение прав пользователей БД (не SUPERUSER в продакшне)

## Troubleshooting

### Проблема: Контейнер не запускается

```bash
# Проверь логи
docker compose logs <service_name>

# Проверь переменные окружения
docker compose config
```

### Проблема: Не могу подключиться к БД

```bash
# Проверь что контейнер запущен
docker compose ps

# Проверь подключение изнутри контейнера
docker compose exec postgres psql -U $POSTGRES_USER -d $POSTGRES_DB
```

### Проблема: Забыл пароль

Если забыли пароль БД:
1. Останови контейнер
2. Подключись к volume напрямую (требует root доступ)
3. Или пересоздай volume (потеря данных!)

**Лучше:** Храни пароли в безопасном менеджере паролей.
