# PhotoHelper

## Установка

### Backend

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
