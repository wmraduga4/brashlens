# ТЗ-ИНСТРУКЦИЯ: ИТЕРАЦИЯ 2 - "Регистрация пользователей"
## BrashLens MVP - Для разработчика Mid+ на MacBook M1

**Цель итерации:** Реализовать полноценную систему регистрации пользователей с выбором роли через Telegram бота и API для управления пользователями.

**Длительность:** 3-4 дня

**Критерий успеха:** Новый пользователь может выбрать роль (фотограф/клиент), данные сохраняются в БД, повторный `/start` не создает дубликаты, API возвращает данные пользователя.

---

## 📋 ПРЕДВАРИТЕЛЬНЫЕ ТРЕБОВАНИЯ

### Проверка завершения итерации 1

Убедись, что итерация 1 завершена:

```bash
# Проверь что все контейнеры запущены
cd /root/wmraduga4/BrashLens
docker compose ps

# Проверь что API работает
curl http://localhost:8044/api/v1/health

# Проверь что бот отвечает
# Отправь /start боту в Telegram
```

**Ожидаемый результат:**
- ✅ Все контейнеры Running
- ✅ API отвечает {"status": "ok"}
- ✅ Бот отвечает на /start

---

## 🔄 GIT WORKFLOW

**⚠️ НАПОМИНАНИЕ:** Следуй правилам из итерации 1:

1. **Работаем в ветке `dev`**
2. **Коммитим после каждого завершенного этапа**
3. **Используем conventional commits**
4. **По окончанию этапа:** коммит → push dev → merge в main → push main → возврат в dev

### Быстрый workflow

```bash
# После завершения этапа
git add .
git commit -m "feat: описание изменений"
git push origin dev
git checkout main
git merge dev
git push origin main
git checkout dev
```

---

## 🔨 ЭТАП 1: МОДЕЛЬ USER + ALEMBIC МИГРАЦИЯ

### Задача
Создать модель `User` в SQLAlchemy с необходимыми полями и настроить Alembic для управления миграциями БД.

### Теоретическая база

**Модель User - центральная сущность системы:**
- Каждый пользователь идентифицируется через `telegram_id` (уникальный)
- `username` может быть None (не все пользователи Telegram имеют username)
- `role` определяет доступные функции (photographer/client/admin)
- `language` автоматически определяется из настроек Telegram
- Используем UTC для всех временных меток

**Best practices для моделей:**
- Используй `mapped_column` из SQLAlchemy 2.0
- Добавь `__repr__` для удобства отладки
- Используй `Enum` для ограничения значений role
- Индексируй поля для поиска (telegram_id, username, role)
- Добавь created_at и updated_at для аудита

**Alembic:**
- Инициализация создает папку `alembic/` с конфигурацией
- Каждая миграция имеет уникальный ID и описание
- `upgrade` применяет изменения, `downgrade` откатывает
- Миграции версионируются в git

### Промт для Cursor

```
@BrashLens/backend/app/models Создай модель User для системы BrashLens:

1. BrashLens/backend/app/models/user.py:
   - Импорты: SQLAlchemy 2.0 (mapped_column, Mapped), datetime, enum
   - Класс User(Base):
     * id: Integer, primary_key, autoincrement
     * telegram_id: BigInteger, unique, not null, indexed
       (BigInteger т.к. Telegram ID могут быть очень большими)
     * username: String(255), nullable (не у всех есть username), indexed
     * first_name: String(255), not null
     * last_name: String(255), nullable
     * role: Enum('photographer', 'client', 'admin'), not null, indexed
     * language: String(5), not null, default='ru' (ISO 639-1: ru/en)
     * is_active: Boolean, default=True
     * created_at: DateTime(timezone=True), server_default=func.now()
     * updated_at: DateTime(timezone=True), onupdate=func.now()
   - Методы:
     * __repr__ для удобного вывода
     * to_dict() для сериализации (без конфиденциальных данных)
   - Добавь docstring с описанием модели

2. BrashLens/backend/app/models/__init__.py:
   - Импортируй User
   - Экспортируй в __all__

3. Настрой Alembic:
   - Инициализация (если еще не сделано): создай alembic.ini и alembic/env.py
   - В alembic/env.py:
     * Импортируй Base из app.core.database
     * Импортируй все модели (from app.models import *)
     * Настрой target_metadata = Base.metadata
     * Используй async engine для миграций
   - Создай первую миграцию: "create_users_table"
   - В миграции:
     * upgrade(): создание таблицы users со всеми полями и индексами
     * downgrade(): drop table users

Важные детали:
- Используй SQLAlchemy 2.0 синтаксис (Mapped, mapped_column)
- Все datetime поля с timezone=True
- Создай composite index на (role, is_active) для быстрых фильтраций
- В alembic/env.py правильно настрой async подключение к БД
- Не забудь про Enum type в PostgreSQL
```

### Реализация

1. **Создай модель через Cursor** (используй промт выше)
2. **Проверь структуру файлов**:
   ```bash
   tree BrashLens/backend/app/models/
   tree BrashLens/backend/alembic/
   ```

### ТРОЙНОЕ ТЕСТИРОВАНИЕ #1

#### ✅ Тест 1: Проверка модели User

```bash
# Запусти Python shell в контейнере
docker compose exec backend python

# В Python:
from app.models.user import User
from app.core.database import engine, Base
import asyncio

# Проверь что модель импортируется без ошибок
print(User.__tablename__)
print(User.__table__.columns.keys())

# Проверь что Base.metadata содержит таблицу
print('users' in Base.metadata.tables)

exit()
```

**Ожидаемый результат:**
- ✅ Модель импортируется без ошибок
- ✅ Выводит 'users'
- ✅ Показывает все колонки
- ✅ users найдена в metadata

#### ✅ Тест 2: Проверка конфигурации Alembic

```bash
# Проверь alembic.ini
cat BrashLens/backend/alembic.ini

# Проверь что env.py правильно настроен
cat BrashLens/backend/alembic/env.py | grep "target_metadata"

# Проверь текущую версию БД
docker compose exec backend alembic current

# Покажи историю миграций
docker compose exec backend alembic history
```

**Ожидаемый результат:**
- ✅ alembic.ini существует и правильно настроен
- ✅ target_metadata = Base.metadata
- ✅ Команда alembic current выполняется (может показать empty)
- ✅ История миграций показывает создание users

#### ✅ Тест 3: Применение миграции

```bash
# Создай миграцию (если еще не создана через Cursor)
docker compose exec backend alembic revision --autogenerate -m "create_users_table"

# Примени миграцию
docker compose exec backend alembic upgrade head

# Проверь что таблица создана
cd /root/wmraduga4/infrastructure
docker compose exec postgres psql -U govardvolov -d brashlens_db -c "\d users"

# Проверь индексы
docker compose exec postgres psql -U govardvolov -d brashlens_db -c "\di"

# Проверь текущую версию
cd /root/wmraduga4/BrashLens
docker compose exec backend alembic current
```

**Ожидаемый результат:**
- ✅ Миграция создана в alembic/versions/
- ✅ Миграция применена без ошибок
- ✅ Таблица users существует со всеми колонками
- ✅ Индексы созданы (telegram_id, username, role, composite)
- ✅ alembic current показывает актуальную версию

**Критерии прохождения:**
- ✅ Модель User определена корректно
- ✅ Alembic настроен и работает
- ✅ Миграция применена, таблица создана
- ✅ Все индексы на месте

**Если тесты не прошли:** проверь:
- DATABASE_URL в .env корректен
- Alembic env.py использует правильный Base
- Миграция не имеет синтаксических ошибок
- PostgreSQL доступен

### Коммит изменений

```bash
git checkout dev
git add .
git commit -m "feat: этап 1 итерации 2 - модель User и Alembic миграция"
git push origin dev
git checkout main
git merge dev
git push origin main
git checkout dev
```

---

## 🔨 ЭТАП 2: PYDANTIC СХЕМЫ ДЛЯ USER

### Задача
Создать Pydantic схемы для валидации данных User и использования в API endpoints.

### Теоретическая база

**Зачем нужны схемы:**
- **Валидация входных данных** от клиентов
- **Сериализация** моделей БД в JSON
- **Документация API** (автоматическая через FastAPI)
- **Разделение слоев** (БД модели ≠ API схемы)

**Типы схем:**
- **Base** - общие поля для всех схем
- **Create** - данные для создания (без id, timestamps)
- **Update** - данные для обновления (все поля optional)
- **InDB** - полное представление из БД (с id, timestamps)
- **Public** - для отдачи клиенту (без конфиденциальных данных)

**Best practices:**
- Наследование от базовой схемы
- ConfigDict для настройки поведения
- Field для валидации и описания
- Примеры в schema_extra для документации

### Промт для Cursor

```
@BrashLens/backend/app/schemas Создай Pydantic схемы для User:

1. BrashLens/backend/app/schemas/user.py:
   
   # Базовая схема с общими полями
   class UserBase(BaseModel):
       telegram_id: int = Field(..., description="Telegram user ID", gt=0)
       username: Optional[str] = Field(None, max_length=255, description="Telegram username")
       first_name: str = Field(..., min_length=1, max_length=255)
       last_name: Optional[str] = Field(None, max_length=255)
       language: str = Field(default="ru", pattern="^(ru|en)$", description="Interface language")
   
   # Схема для создания пользователя
   class UserCreate(UserBase):
       role: Literal['photographer', 'client'] = Field(..., description="User role")
       # Примечание: admin не доступен при регистрации
   
   # Схема для обновления пользователя
   class UserUpdate(BaseModel):
       first_name: Optional[str] = Field(None, min_length=1, max_length=255)
       last_name: Optional[str] = Field(None, max_length=255)
       language: Optional[str] = Field(None, pattern="^(ru|en)$")
       # Примечание: role и telegram_id нельзя менять
   
   # Схема для ответа API (публичная)
   class UserResponse(UserBase):
       id: int
       role: str
       is_active: bool
       created_at: datetime
       
       model_config = ConfigDict(from_attributes=True)
   
   # Схема для внутреннего использования (полная)
   class UserInDB(UserResponse):
       updated_at: Optional[datetime] = None
       
       model_config = ConfigDict(from_attributes=True)

2. BrashLens/backend/app/schemas/__init__.py:
   - Импортируй все схемы User
   - Экспортируй в __all__

3. Добавь примеры в schema_extra:
   - В UserCreate добавь Config с json_schema_extra для документации
   - Примеры для photographer и client

Важно:
- Используй Pydantic v2 синтаксис (model_config вместо Config)
- Field для валидации и описания
- from_attributes=True для работы с ORM моделями
- Правильные типы (int для telegram_id, datetime с timezone)
```

### Реализация

1. **Создай схемы через Cursor** (используй промт выше)
2. **Проверь структуру**:
   ```bash
   cat BrashLens/backend/app/schemas/user.py
   cat BrashLens/backend/app/schemas/__init__.py
   ```

### ТРОЙНОЕ ТЕСТИРОВАНИЕ #2

#### ✅ Тест 1: Валидация схем

```bash
# Запусти Python в контейнере
docker compose exec backend python

# В Python:
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from datetime import datetime

# Тест 1: Валидная схема создания
try:
    user_create = UserCreate(
        telegram_id=123456789,
        username="test_user",
        first_name="Иван",
        role="photographer",
        language="ru"
    )
    print("✅ UserCreate валидация прошла")
    print(user_create.model_dump())
except Exception as e:
    print(f"❌ Ошибка UserCreate: {e}")

# Тест 2: Невалидные данные
try:
    UserCreate(
        telegram_id=-1,  # Должно упасть
        first_name="Test",
        role="photographer"
    )
    print("❌ Валидация пропустила негативный ID")
except Exception as e:
    print(f"✅ Валидация корректно отклонила: {e}")

# Тест 3: Невалидный language
try:
    UserCreate(
        telegram_id=123,
        first_name="Test",
        role="client",
        language="fr"  # Должно упасть
    )
    print("❌ Валидация пропустила неверный язык")
except Exception as e:
    print(f"✅ Валидация корректно отклонила язык: {e}")

# Тест 4: UserUpdate (все поля optional)
try:
    update = UserUpdate(first_name="Новое имя")
    print("✅ UserUpdate с частичными данными работает")
    print(update.model_dump(exclude_unset=True))
except Exception as e:
    print(f"❌ Ошибка UserUpdate: {e}")

exit()
```

**Ожидаемый результат:**
- ✅ Валидные данные проходят
- ✅ Невалидные данные отклоняются
- ✅ Частичное обновление работает

#### ✅ Тест 2: Сериализация из ORM

```bash
docker compose exec backend python

# В Python:
from app.models.user import User
from app.schemas.user import UserResponse, UserInDB
from datetime import datetime, timezone

# Создаем mock объект ORM (имитация из БД)
mock_user = type('MockUser', (), {
    'id': 1,
    'telegram_id': 987654321,
    'username': 'test_photographer',
    'first_name': 'Анна',
    'last_name': 'Иванова',
    'role': 'photographer',
    'language': 'ru',
    'is_active': True,
    'created_at': datetime.now(timezone.utc),
    'updated_at': datetime.now(timezone.utc)
})()

# Тест сериализации
try:
    user_response = UserResponse.model_validate(mock_user)
    print("✅ Сериализация в UserResponse работает")
    print(user_response.model_dump_json(indent=2))
    
    user_in_db = UserInDB.model_validate(mock_user)
    print("✅ Сериализация в UserInDB работает")
except Exception as e:
    print(f"❌ Ошибка сериализации: {e}")

exit()
```

**Ожидаемый результат:**
- ✅ ORM объекты сериализуются в схемы
- ✅ JSON выглядит корректно
- ✅ Все поля присутствуют

#### ✅ Тест 3: Документация API

```bash
# Проверим что схемы появятся в OpenAPI документации
# После запуска FastAPI проверим в браузере
curl http://localhost:8044/docs

# Или проверим JSON schema
curl http://localhost:8044/openapi.json | grep -A 20 "UserCreate"
```

**Ожидаемый результат:**
- ✅ Схемы видны в /docs (проверим позже)
- ✅ openapi.json содержит определения схем

**Критерии прохождения:**
- ✅ Все схемы корректно валидируют данные
- ✅ Сериализация из ORM работает
- ✅ Валидация отклоняет невалидные данные

**Если тесты не прошли:** проверь:
- Pydantic v2 синтаксис используется
- Field constraints корректны
- model_config настроен правильно

### Коммит изменений

```bash
git checkout dev
git add .
git commit -m "feat: этап 2 итерации 2 - Pydantic схемы для User"
git push origin dev
git checkout main
git merge dev
git push origin main
git checkout dev
```

---

## 🔨 ЭТАП 3: CRUD СЕРВИС ДЛЯ USER

### Задача
Создать сервисный слой для работы с пользователями (CRUD операции) с использованием Repository паттерна.

### Теоретическая база

**Зачем нужен сервисный слой:**
- **Отделение бизнес-логики** от API endpoints
- **Переиспользование** кода (бот и API используют один сервис)
- **Тестируемость** (легко mock'ать)
- **Единая точка** для работы с моделью User

**Repository паттерн:**
- Абстрагирует работу с БД
- Предоставляет CRUD методы
- Скрывает детали SQLAlchemy
- Упрощает смену БД в будущем

**Async/await:**
- Все операции БД асинхронные
- Используем AsyncSession из SQLAlchemy
- Обязательно закрываем сессии (context manager)

### Промт для Cursor

```
@BrashLens/backend/app/services Создай сервис для работы с User:

1. BrashLens/backend/app/services/user_service.py:
   
   # Импорты
   from sqlalchemy.ext.asyncio import AsyncSession
   from sqlalchemy import select, and_
   from app.models.user import User
   from app.schemas.user import UserCreate, UserUpdate
   from typing import Optional, List
   
   # Класс UserService
   class UserService:
       """Сервис для работы с пользователями"""
       
       def __init__(self, db: AsyncSession):
           self.db = db
       
       async def create_user(self, user_data: UserCreate) -> User:
           """Создать нового пользователя"""
           # Проверка существования по telegram_id
           existing = await self.get_by_telegram_id(user_data.telegram_id)
           if existing:
               raise ValueError(f"User with telegram_id {user_data.telegram_id} already exists")
           
           # Создание пользователя
           user = User(**user_data.model_dump())
           self.db.add(user)
           await self.db.commit()
           await self.db.refresh(user)
           return user
       
       async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
           """Получить пользователя по Telegram ID"""
           result = await self.db.execute(
               select(User).where(User.telegram_id == telegram_id)
           )
           return result.scalar_one_or_none()
       
       async def get_by_id(self, user_id: int) -> Optional[User]:
           """Получить пользователя по ID"""
           result = await self.db.execute(
               select(User).where(User.id == user_id)
           )
           return result.scalar_one_or_none()
       
       async def get_by_username(self, username: str) -> Optional[User]:
           """Получить пользователя по username"""
           result = await self.db.execute(
               select(User).where(User.username == username)
           )
           return result.scalar_one_or_none()
       
       async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
           """Обновить данные пользователя"""
           user = await self.get_by_id(user_id)
           if not user:
               return None
           
           # Обновляем только переданные поля
           update_data = user_data.model_dump(exclude_unset=True)
           for field, value in update_data.items():
               setattr(user, field, value)
           
           await self.db.commit()
           await self.db.refresh(user)
           return user
       
       async def get_users_by_role(self, role: str, skip: int = 0, limit: int = 100) -> List[User]:
           """Получить список пользователей по роли"""
           result = await self.db.execute(
               select(User)
               .where(and_(User.role == role, User.is_active == True))
               .offset(skip)
               .limit(limit)
           )
           return list(result.scalars().all())
       
       async def deactivate_user(self, user_id: int) -> bool:
           """Деактивировать пользователя (soft delete)"""
           user = await self.get_by_id(user_id)
           if not user:
               return False
           
           user.is_active = False
           await self.db.commit()
           return True
       
       async def get_or_create_user(
           self, telegram_id: int, user_data: UserCreate
       ) -> tuple[User, bool]:
           """
           Получить существующего пользователя или создать нового
           Returns: (user, created) где created=True если пользователь создан
           """
           existing = await self.get_by_telegram_id(telegram_id)
           if existing:
               return existing, False
           
           user = await self.create_user(user_data)
           return user, True

2. BrashLens/backend/app/services/__init__.py:
   - Импортируй UserService
   - Экспортируй в __all__

3. Добавь dependency для получения сервиса в app/api/dependencies.py:
   
   from app.core.database import get_db
   from app.services.user_service import UserService
   from sqlalchemy.ext.asyncio import AsyncSession
   
   async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
       return UserService(db)

Важно:
- Все методы async
- Используй AsyncSession
- Обрабатывай None результаты
- commit() и refresh() после изменений
- get_or_create полезен для бота
```

### Реализация

1. **Создай сервис через Cursor** (используй промт выше)
2. **Проверь файлы**:
   ```bash
   cat BrashLens/backend/app/services/user_service.py
   cat BrashLens/backend/app/api/dependencies.py
   ```

### ТРОЙНОЕ ТЕСТИРОВАНИЕ #3

#### ✅ Тест 1: Создание пользователя

```bash
# Создай тестовый скрипт
cat > /root/wmraduga4/BrashLens/test_user_service.py << 'EOF'
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.services.user_service import UserService
from app.schemas.user import UserCreate

async def test_create_user():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        service = UserService(session)
        
        # Создаем тестового пользователя
        user_data = UserCreate(
            telegram_id=111222333,
            username="test_user_service",
            first_name="Тест",
            last_name="Тестов",
            role="photographer",
            language="ru"
        )
        
        try:
            user = await service.create_user(user_data)
            print(f"✅ Пользователь создан: {user.id}, {user.first_name}")
            
            # Проверяем что можем получить его обратно
            found = await service.get_by_telegram_id(111222333)
            if found:
                print(f"✅ Пользователь найден: {found.username}")
            else:
                print("❌ Пользователь не найден после создания")
                
        except ValueError as e:
            print(f"⚠️ Пользователь уже существует (это ок для повторного запуска)")
        except Exception as e:
            print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(test_create_user())
EOF

# Запусти тест
docker compose exec backend python test_user_service.py
```

**Ожидаемый результат:**
- ✅ Пользователь создается
- ✅ Находится по telegram_id
- ✅ При повторном запуске выдает ошибку о существовании

#### ✅ Тест 2: CRUD операции

```bash
cat > /root/wmraduga4/BrashLens/test_user_crud.py << 'EOF'
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserUpdate

async def test_crud():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        service = UserService(session)
        
        # 1. Создание
        print("1. Тестируем создание...")
        user_data = UserCreate(
            telegram_id=999888777,
            username="crud_test",
            first_name="CRUD",
            role="client",
            language="en"
        )
        
        user, created = await service.get_or_create_user(999888777, user_data)
        if created:
            print(f"✅ Создан: {user.id}")
        else:
            print(f"✅ Уже существует: {user.id}")
        
        # 2. Чтение
        print("2. Тестируем чтение...")
        found = await service.get_by_telegram_id(999888777)
        if found and found.username == "crud_test":
            print(f"✅ Найден: {found.username}")
        else:
            print("❌ Не найден или данные неверны")
        
        # 3. Обновление
        print("3. Тестируем обновление...")
        update_data = UserUpdate(first_name="CRUD Updated")
        updated = await service.update_user(user.id, update_data)
        if updated and updated.first_name == "CRUD Updated":
            print(f"✅ Обновлен: {updated.first_name}")
        else:
            print("❌ Обновление не сработало")
        
        # 4. Деактивация
        print("4. Тестируем деактивацию...")
        deactivated = await service.deactivate_user(user.id)
        if deactivated:
            check = await service.get_by_id(user.id)
            if not check.is_active:
                print(f"✅ Деактивирован: is_active={check.is_active}")
            else:
                print("❌ Деактивация не сработала")
        else:
            print("❌ Ошибка деактивации")

if __name__ == "__main__":
    asyncio.run(test_crud())
EOF

docker compose exec backend python test_user_crud.py
```

**Ожидаемый результат:**
- ✅ Все CRUD операции работают
- ✅ Данные корректно обновляются
- ✅ Деактивация работает

#### ✅ Тест 3: Получение по роли

```bash
cat > /root/wmraduga4/BrashLens/test_user_role.py << 'EOF'
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.services.user_service import UserService

async def test_get_by_role():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        service = UserService(session)
        
        # Получаем всех фотографов
        photographers = await service.get_users_by_role("photographer")
        print(f"✅ Найдено фотографов: {len(photographers)}")
        for p in photographers:
            print(f"  - {p.first_name} (@{p.username})")
        
        # Получаем всех клиентов
        clients = await service.get_users_by_role("client")
        print(f"✅ Найдено клиентов: {len(clients)}")
        for c in clients:
            print(f"  - {c.first_name} (@{c.username})")

if __name__ == "__main__":
    asyncio.run(test_get_by_role())
EOF

docker compose exec backend python test_user_role.py
```

**Ожидаемый результат:**
- ✅ Возвращает список пользователей по роли
- ✅ Только активные пользователи

**Критерии прохождения:**
- ✅ Все CRUD операции работают
- ✅ Транзакции корректны (commit/rollback)
- ✅ get_or_create работает правильно
- ✅ Фильтрация по роли работает

**Если тесты не прошли:** проверь:
- AsyncSession используется правильно
- commit() вызывается после изменений
- refresh() для обновления объектов
- Обработка None результатов

### Коммит изменений

```bash
git checkout dev
git add .
git commit -m "feat: этап 3 итерации 2 - CRUD сервис для User"
git push origin dev
git checkout main
git merge dev
git push origin main
git checkout dev
```

---

## 🔨 ЭТАП 4: API ENDPOINTS ДЛЯ USER

### Задача
Создать RESTful API endpoints для работы с пользователями.

### Теоретическая база

**API Design Best Practices:**
- Версионирование: `/api/v1/users`
- HTTP методы: GET (чтение), POST (создание), PATCH (обновление)
- Статус коды: 200 (OK), 201 (Created), 404 (Not Found), 409 (Conflict)
- Dependency Injection для сервисов и авторизации
- Единый формат ответов

**Endpoints для итерации 2:**
- `GET /api/v1/users/me` - текущий пользователь (будет использоваться ботом)
- `POST /api/v1/users` - создание пользователя (внутренний, для бота)
- `GET /api/v1/users/{user_id}` - получение по ID (для тестов)

**Авторизация:**
- Пока простая (telegram_id в query параметре)
- В следующих итерациях: JWT tokens

### Промт для Cursor

```
@BrashLens/backend/app/api/v1 Создай API endpoints для User:

1. BrashLens/backend/app/api/v1/users.py:
   
   from fastapi import APIRouter, Depends, HTTPException, status, Query
   from app.services.user_service import UserService
   from app.api.dependencies import get_user_service
   from app.schemas.user import UserResponse, UserCreate, UserUpdate
   from typing import List
   
   router = APIRouter(prefix="/users", tags=["users"])
   
   @router.get("/me", response_model=UserResponse)
   async def get_current_user(
       telegram_id: int = Query(..., description="Telegram user ID"),
       service: UserService = Depends(get_user_service)
   ):
       """
       Получить данные текущего пользователя по Telegram ID
       
       Используется ботом и Mini App для получения информации о пользователе
       """
       user = await service.get_by_telegram_id(telegram_id)
       if not user:
           raise HTTPException(
               status_code=status.HTTP_404_NOT_FOUND,
               detail=f"User with telegram_id {telegram_id} not found"
           )
       return user
   
   @router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
   async def create_user(
       user_data: UserCreate,
       service: UserService = Depends(get_user_service)
   ):
       """
       Создать нового пользователя
       
       Используется ботом при первом взаимодействии пользователя
       """
       try:
           user = await service.create_user(user_data)
           return user
       except ValueError as e:
           raise HTTPException(
               status_code=status.HTTP_409_CONFLICT,
               detail=str(e)
           )
   
   @router.get("/{user_id}", response_model=UserResponse)
   async def get_user(
       user_id: int,
       service: UserService = Depends(get_user_service)
   ):
       """Получить пользователя по ID"""
       user = await service.get_by_id(user_id)
       if not user:
           raise HTTPException(
               status_code=status.HTTP_404_NOT_FOUND,
               detail=f"User with id {user_id} not found"
           )
       return user
   
   @router.patch("/{user_id}", response_model=UserResponse)
   async def update_user(
       user_id: int,
       user_data: UserUpdate,
       service: UserService = Depends(get_user_service)
   ):
       """Обновить данные пользователя"""
       user = await service.update_user(user_id, user_data)
       if not user:
           raise HTTPException(
               status_code=status.HTTP_404_NOT_FOUND,
               detail=f"User with id {user_id} not found"
           )
       return user
   
   @router.get("", response_model=List[UserResponse])
   async def get_users(
       role: str = Query(None, description="Filter by role"),
       skip: int = Query(0, ge=0),
       limit: int = Query(100, ge=1, le=1000),
       service: UserService = Depends(get_user_service)
   ):
       """Получить список пользователей с фильтрацией"""
       if role:
           users = await service.get_users_by_role(role, skip, limit)
       else:
           # TODO: добавить метод get_all в следующей итерации
           users = []
       return users

2. Подключи роутер в app/api/v1/__init__.py:
   - Импортируй users router
   - Добавь в api_router.include_router()

3. Обнови app/main.py если нужно:
   - Убедись что v1 router подключен

Важно:
- Правильные HTTP статус коды
- Подробные docstrings
- Используй Query для параметров запроса
- HTTPException с детальными сообщениями
- Response models для автодокументации
```

### Реализация

1. **Создай endpoints через Cursor** (используй промт выше)
2. **Проверь структуру**:
   ```bash
   cat BrashLens/backend/app/api/v1/users.py
   cat BrashLens/backend/app/api/v1/__init__.py
   ```
3. **Перезапусти backend**:
   ```bash
   docker compose restart backend
   ```

### ТРОЙНОЕ ТЕСТИРОВАНИЕ #4

#### ✅ Тест 1: Проверка документации API

```bash
# Открой Swagger UI в браузере или через curl
curl http://localhost:8044/docs | grep -i "users"

# Проверь OpenAPI schema
curl http://localhost:8044/openapi.json | jq '.paths' | grep "/users"

# Должны быть endpoints:
# - POST /api/v1/users
# - GET /api/v1/users/me
# - GET /api/v1/users/{user_id}
# - PATCH /api/v1/users/{user_id}
# - GET /api/v1/users
```

**Ожидаемый результат:**
- ✅ Swagger UI доступен
- ✅ Все endpoints видны
- ✅ Документация сгенерирована автоматически

#### ✅ Тест 2: Создание пользователя через API

```bash
# Создай пользователя photographer
curl -X POST http://localhost:8044/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_id": 555666777,
    "username": "api_photographer",
    "first_name": "API",
    "last_name": "Photographer",
    "role": "photographer",
    "language": "ru"
  }'

# Должно вернуть 201 Created с данными пользователя

# Создай пользователя client
curl -X POST http://localhost:8044/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_id": 777888999,
    "username": "api_client",
    "first_name": "API",
    "last_name": "Client",
    "role": "client",
    "language": "en"
  }'

# Попробуй создать дубликат (должно вернуть 409 Conflict)
curl -X POST http://localhost:8044/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_id": 555666777,
    "username": "duplicate",
    "first_name": "Duplicate",
    "role": "client",
    "language": "ru"
  }'
```

**Ожидаемый результат:**
- ✅ Первый запрос возвращает 201 и данные пользователя
- ✅ Второй запрос тоже работает
- ✅ Дубликат возвращает 409 Conflict

#### ✅ Тест 3: Получение пользователя

```bash
# Получи по telegram_id (endpoint /me)
curl "http://localhost:8044/api/v1/users/me?telegram_id=555666777"

# Должно вернуть данные photographer

# Получи несуществующего (должен вернуть 404)
curl "http://localhost:8044/api/v1/users/me?telegram_id=123456789"

# Получи по user_id (из результата создания возьми id)
curl "http://localhost:8044/api/v1/users/1"

# Обнови пользователя
curl -X PATCH "http://localhost:8044/api/v1/users/1" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "API Updated"
  }'

# Получи список фотографов
curl "http://localhost:8044/api/v1/users?role=photographer"

# Получи список клиентов
curl "http://localhost:8044/api/v1/users?role=client"
```

**Ожидаемый результат:**
- ✅ /me возвращает пользователя
- ✅ Несуществующий возвращает 404
- ✅ GET по ID работает
- ✅ PATCH обновляет данные
- ✅ Фильтрация по роли работает

**Критерии прохождения:**
- ✅ Все endpoints работают
- ✅ Правильные HTTP статусы
- ✅ Валидация работает
- ✅ Документация сгенерирована

**Если тесты не прошли:** проверь:
- Router подключен в main.py
- Dependencies работают
- Сервис доступен
- База данных доступна

### Коммит изменений

```bash
git checkout dev
git add .
git commit -m "feat: этап 4 итерации 2 - API endpoints для User"
git push origin dev
git checkout main
git merge dev
git push origin main
git checkout dev
```

---

## 🔨 ЭТАП 5: TELEGRAM БОТ - РЕГИСТРАЦИЯ ПОЛЬЗОВАТЕЛЕЙ

### Задача
Реализовать в боте обработку `/start` с проверкой существования пользователя, выбором роли и сохранением в БД.

### Теоретическая база

**Архитектура бота:**
- Отдельный контейнер `chat-bot` 
- Использует python-telegram-bot library
- Работает в режиме webhook (production) или polling (development)
- Взаимодействует с БД через тот же UserService

**Конечные автоматы (FSM):**
- Для диалоговых flow используем ConversationHandler
- States (состояния): CHOOSING_ROLE, REGISTERING
- Transitions (переходы) по кнопкам/сообщениям
- Fallback handlers для выхода

**Best practices:**
- Используй InlineKeyboardMarkup для кнопок выбора
- Ответы в соответствии с языком пользователя
- Graceful error handling
- Логирование всех действий

### Промт для Cursor

```
@BrashLens/backend/app Создай Telegram бота для регистрации:

1. BrashLens/backend/app/bot/__init__.py:
   - Структура для бота

2. BrashLens/backend/app/bot/config.py:
   - Загрузка TELEGRAM_BOT_TOKEN из settings
   - Webhook URL (если нужен)

3. BrashLens/backend/app/bot/handlers/start.py:
   
   from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
   from telegram.ext import ContextTypes, ConversationHandler
   from app.services.user_service import UserService
   from app.schemas.user import UserCreate
   from app.core.database import get_db
   
   # States
   CHOOSING_ROLE = 0
   
   async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
       """
       Обработка команды /start
       
       1. Проверяет существование пользователя по telegram_id
       2. Если существует - показывает приветствие по роли
       3. Если новый - предлагает выбрать роль
       """
       user = update.effective_user
       
       # Получаем сервис для работы с БД
       async with get_db() as db:
           service = UserService(db)
           existing_user = await service.get_by_telegram_id(user.id)
       
       if existing_user:
           # Пользователь уже зарегистрирован
           if existing_user.role == "photographer":
               text = (
                   f"С возвращением, {existing_user.first_name}! 📸\n\n"
                   "Вы можете:\n"
                   "• Управлять портфолио\n"
                   "• Настроить календарь\n"
                   "• Посмотреть брони\n"
                   "• Управлять клиентами"
               )
           else:  # client
               text = (
                   f"Привет, {existing_user.first_name}! 👋\n\n"
                   "Вы можете:\n"
                   "• Посмотреть портфолио фотографов\n"
                   "• Записаться на съемку\n"
                   "• Посмотреть свои брони"
               )
           
           await update.message.reply_text(text)
           return ConversationHandler.END
       
       # Новый пользователь - предлагаем выбрать роль
       keyboard = [
           [InlineKeyboardButton("Я фотограф 📸", callback_data="role_photographer")],
           [InlineKeyboardButton("Я клиент 🙂", callback_data="role_client")]
       ]
       reply_markup = InlineKeyboardMarkup(keyboard)
       
       text = (
           f"Привет, {user.first_name}! 👋\n\n"
           "Добро пожаловать в BrashLens - ваш помощник в организации фотосъемок.\n\n"
           "Для начала, выберите вашу роль:"
       )
       
       await update.message.reply_text(text, reply_markup=reply_markup)
       return CHOOSING_ROLE
   
   async def role_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
       """Обработка выбора роли"""
       query = update.callback_query
       await query.answer()
       
       user = update.effective_user
       role = query.data.replace("role_", "")  # photographer или client
       
       # Определяем язык из настроек Telegram
       language = user.language_code if user.language_code in ["ru", "en"] else "ru"
       
       # Создаем пользователя
       user_data = UserCreate(
           telegram_id=user.id,
           username=user.username,
           first_name=user.first_name,
           last_name=user.last_name,
           role=role,
           language=language
       )
       
       try:
           async with get_db() as db:
               service = UserService(db)
               created_user = await service.create_user(user_data)
           
           if role == "photographer":
               text = (
                   "Отлично! Вы зарегистрированы как фотограф 📸\n\n"
                   "Следующие шаги:\n"
                   "1. Заполните профиль (имя, город, валюта)\n"
                   "2. Загрузите портфолио\n"
                   "3. Настройте календарь\n"
                   "4. Создайте пакеты услуг\n\n"
                   "Используйте /help для списка команд"
               )
           else:  # client
               text = (
                   "Отлично! Вы зарегистрированы как клиент 🙂\n\n"
                   "Теперь вы можете:\n"
                   "• Просматривать портфолио фотографов\n"
                   "• Записываться на съемки\n"
                   "• Получать уведомления\n\n"
                   "Используйте /help для списка команд"
               )
           
           await query.edit_message_text(text)
           return ConversationHandler.END
           
       except Exception as e:
           await query.edit_message_text(
               "Произошла ошибка при регистрации. Попробуйте позже или обратитесь в поддержку."
           )
           # Логируем ошибку
           print(f"Error creating user: {e}")
           return ConversationHandler.END
   
   async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
       """Отмена регистрации"""
       await update.message.reply_text(
           "Регистрация отменена. Используйте /start для повторной попытки."
       )
       return ConversationHandler.END

4. BrashLens/backend/app/bot/main.py:
   
   import logging
   from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler
   from app.bot.config import TELEGRAM_BOT_TOKEN
   from app.bot.handlers.start import start_command, role_chosen, cancel, CHOOSING_ROLE
   
   logging.basicConfig(
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
       level=logging.INFO
   )
   
   def main():
       """Запуск бота"""
       # Создаем приложение
       application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
       
       # Conversation handler для регистрации
       registration_handler = ConversationHandler(
           entry_points=[CommandHandler("start", start_command)],
           states={
               CHOOSING_ROLE: [
                   CallbackQueryHandler(role_chosen, pattern="^role_")
               ],
           },
           fallbacks=[CommandHandler("cancel", cancel)]
       )
       
       # Добавляем handlers
       application.add_handler(registration_handler)
       
       # Запускаем polling (для разработки)
       # В продакшене использовать webhook
       application.run_polling()
   
   if __name__ == "__main__":
       main()

5. Обнови Dockerfile для chat-bot (если нужно):
   - Убедись что все зависимости установлены
   - CMD запускает app/bot/main.py

6. Обнови docker-compose.yml:
   - Убедись что chat-bot имеет доступ к БД
   - Проброшены правильные переменные окружения

Важно:
- Используй async/await везде
- ConversationHandler для управления состояниями
- InlineKeyboardMarkup для кнопок (не ReplyKeyboard)
- Определяй язык автоматически из user.language_code
- Логируй все важные действия
- Обрабатывай ошибки gracefully
```

### Реализация

1. **Создай бота через Cursor** (используй промт выше)
2. **Проверь структуру**:
   ```bash
   tree BrashLens/backend/app/bot/
   cat BrashLens/backend/app/bot/main.py
   ```
3. **Перезапусти chat-bot**:
   ```bash
   docker compose restart chat-bot
   docker compose logs -f chat-bot
   ```

### ТРОЙНОЕ ТЕСТИРОВАНИЕ #5

#### ✅ Тест 1: Проверка запуска бота

```bash
# Проверь что контейнер запущен
docker compose ps chat-bot

# Проверь логи
docker compose logs chat-bot | tail -20

# Должны увидеть:
# - "Bot started"
# - "Polling started"
# - Никаких ошибок
```

**Ожидаемый результат:**
- ✅ Контейнер Running
- ✅ В логах нет ошибок
- ✅ Бот начал polling

#### ✅ Тест 2: Регистрация нового пользователя

**Важно:** Используй НОВЫЙ Telegram аккаунт (или удали пользователя из БД перед тестом)

```bash
# Удали тестового пользователя если есть (подставь свой telegram_id)
cd /root/wmraduga4/infrastructure
docker compose exec postgres psql -U govardvolov -d brashlens_db -c \
  "DELETE FROM users WHERE telegram_id = YOUR_TELEGRAM_ID;"
```

**В Telegram:**
1. Найди своего бота: `@your_bot_username`
2. Отправь `/start`
3. Должны появиться 2 кнопки:
   - "Я фотограф 📸"
   - "Я клиент 🙂"
4. Нажми "Я фотограф 📸"
5. Должно появиться сообщение с подтверждением регистрации

**Проверь в БД:**
```bash
cd /root/wmraduga4/infrastructure
docker compose exec postgres psql -U govardvolov -d brashlens_db -c \
  "SELECT telegram_id, username, first_name, role, language FROM users ORDER BY id DESC LIMIT 3;"
```

**Ожидаемый результат:**
- ✅ Бот показывает кнопки выбора роли
- ✅ После выбора - подтверждение регистрации
- ✅ Пользователь создан в БД с правильной ролью
- ✅ Язык определен автоматически

#### ✅ Тест 3: Повторный /start существующего пользователя

**В Telegram:**
1. Отправь `/start` еще раз
2. Должно появиться приветственное сообщение (БЕЗ кнопок выбора роли)
3. Сообщение должно соответствовать твоей роли (photographer/client)

```bash
# Проверь что дубликат НЕ создан
cd /root/wmraduga4/infrastructure
docker compose exec postgres psql -U govardvolov -d brashlens_db -c \
  "SELECT COUNT(*) FROM users WHERE telegram_id = YOUR_TELEGRAM_ID;"
```

**Ожидаемый результат:**
- ✅ Показывает приветствие без кнопок
- ✅ Дубликат НЕ создан (COUNT = 1)
- ✅ Текст соответствует роли

**Критерии прохождения:**
- ✅ Бот запускается и работает
- ✅ Регистрация новых пользователей работает
- ✅ Выбор роли сохраняется в БД
- ✅ Повторный /start не создает дубликаты
- ✅ Язык определяется автоматически

**Если тесты не прошли:** проверь:
- TELEGRAM_BOT_TOKEN в .env правильный
- DATABASE_URL доступен из контейнера chat-bot
- Сеть shared-network настроена
- Логи chat-bot на наличие ошибок

### Коммит изменений

```bash
git checkout dev
git add .
git commit -m "feat: этап 5 итерации 2 - Telegram бот регистрация пользователей"
git push origin dev
git checkout main
git merge dev
git push origin main
git checkout dev
```

---

## 📊 ФИНАЛЬНАЯ ПРОВЕРКА ИТЕРАЦИИ 2

### Чеклист завершения

Пройдись по всем критериям:

- [ ] **Модель User:**
  - [ ] Таблица users создана в БД
  - [ ] Все поля корректны (telegram_id, username, role, etc.)
  - [ ] Индексы созданы
  - [ ] Alembic миграция работает

- [ ] **Pydantic Схемы:**
  - [ ] Все схемы созданы (Create, Update, Response, InDB)
  - [ ] Валидация работает
  - [ ] Сериализация из ORM работает

- [ ] **UserService:**
  - [ ] CRUD операции работают
  - [ ] get_or_create работает
  - [ ] Фильтрация по роли работает
  - [ ] Soft delete работает

- [ ] **API Endpoints:**
  - [ ] POST /api/v1/users создает пользователей
  - [ ] GET /api/v1/users/me возвращает данные
  - [ ] PATCH обновляет пользователей
  - [ ] Правильные HTTP статусы
  - [ ] Swagger UI показывает документацию

- [ ] **Telegram Bot:**
  - [ ] Бот запускается без ошибок
  - [ ] Команда /start работает
  - [ ] Выбор роли работает
  - [ ] Данные сохраняются в БД
  - [ ] Повторный /start не создает дубликаты
  - [ ] Язык определяется автоматически

### Итоговое интеграционное тестирование

```bash
# 1. Проверь все контейнеры
docker compose ps

# 2. Создай пользователя через API
curl -X POST http://localhost:8044/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_id": 111222333444,
    "username": "final_test",
    "first_name": "Final",
    "role": "photographer",
    "language": "ru"
  }'

# 3. Получи через API
curl "http://localhost:8044/api/v1/users/me?telegram_id=111222333444"

# 4. Проверь в БД
cd /root/wmraduga4/infrastructure
docker compose exec postgres psql -U govardvolov -d brashlens_db -c \
  "SELECT * FROM users WHERE username = 'final_test';"

# 5. Проверь количество пользователей
docker compose exec postgres psql -U govardvolov -d brashlens_db -c \
  "SELECT role, COUNT(*) FROM users GROUP BY role;"

# 6. Тестируй бота в Telegram:
# - Новый пользователь: /start → выбор роли → регистрация
# - Существующий: /start → приветствие без регистрации
```

**Критерии успеха итерации:**
- ✅ Модель User работает корректно
- ✅ API endpoints отвечают правильно
- ✅ Бот регистрирует новых пользователей
- ✅ Повторный /start не создает дубликаты
- ✅ Данные корректно сохраняются и читаются
- ✅ Язык определяется автоматически
- ✅ Все компоненты интегрированы

---

## 📝 ФИНАЛЬНЫЙ КОММИТ И ДОКУМЕНТАЦИЯ

### Финальный коммит

```bash
git checkout dev
git add .
git commit -m "feat: iteration 2 complete - user registration system

- Created User model with all necessary fields
- Setup Alembic migrations
- Implemented Pydantic schemas for validation
- Created UserService with CRUD operations
- Added API endpoints for user management
- Implemented Telegram bot registration flow
- Added role selection (photographer/client)
- Automatic language detection from Telegram
- Prevent duplicate registrations

All features tested and working in production."

git push origin dev
git checkout main
git merge dev
git push origin main
git checkout dev
```

### Создание отчета

```bash
cat > /root/wmraduga4/ITERATION_2_REPORT.md << 'EOF'
# Итерация 2 - Завершена ✅

## Реализовано
- ✅ Модель User в SQLAlchemy
- ✅ Alembic миграции
- ✅ Pydantic схемы валидации
- ✅ UserService (CRUD операции)
- ✅ API endpoints (/api/v1/users)
- ✅ Telegram бот регистрация
- ✅ Выбор роли (photographer/client)
- ✅ Автоопределение языка
- ✅ Защита от дубликатов

## Технические метрики
- Моделей БД: 1 (User)
- API endpoints: 5 (POST, GET /me, GET /{id}, PATCH, GET list)
- Telegram handlers: 3 (start, role_chosen, cancel)
- Индексов БД: 4 (telegram_id, username, role, composite)
- Поддерживаемых языков: 2 (ru, en)

## База данных
- Таблица: users
- Поля: id, telegram_id, username, first_name, last_name, role, language, is_active, created_at, updated_at
- Индексы: telegram_id (unique), username, role, (role + is_active)

## API Endpoints
```
POST   /api/v1/users          - Создание пользователя
GET    /api/v1/users/me       - Текущий пользователь по telegram_id
GET    /api/v1/users/{id}     - Пользователь по ID
PATCH  /api/v1/users/{id}     - Обновление пользователя
GET    /api/v1/users          - Список пользователей с фильтрацией
```

## Telegram Bot Flow
1. Пользователь: /start
2. Система: проверка существования по telegram_id
3. Если новый:
   - Показ кнопок: "Я фотограф" / "Я клиент"
   - Создание записи в БД
   - Подтверждение регистрации
4. Если существует:
   - Приветствие по роли
   - Список доступных действий

## Следующая итерация
Итерация 3: Регистрация фотографа (расширенный профиль)
- Модель Photographer
- Диалоговый flow (имя, город, валюта)
- Генерация персональной ссылки
- Настройки календаря по умолчанию
EOF
```

---

## 🎯 ИТОГО

**Что получилось в итерации 2:**
- ✅ Полноценная модель User в БД
- ✅ API для управления пользователями
- ✅ Telegram бот с регистрацией
- ✅ Выбор роли (photographer/client)
- ✅ Автоматическое определение языка
- ✅ Защита от дубликатов
- ✅ Все компоненты протестированы и работают

**Время выполнения:** 3-4 дня

**Готовность к итерации 3:** ✅

---

## 📚 ПОЛЕЗНЫЕ КОМАНДЫ

### База данных
```bash
# Подключиться к БД
cd /root/wmraduga4/infrastructure
docker compose exec postgres psql -U govardvolov -d brashlens_db

# Посмотреть всех пользователей
SELECT * FROM users;

# Посмотреть статистику по ролям
SELECT role, COUNT(*) FROM users GROUP BY role;

# Удалить тестового пользователя
DELETE FROM users WHERE telegram_id = 123456789;

# Посмотреть историю миграций
cd /root/wmraduga4/BrashLens
docker compose exec backend alembic history

# Откатить последнюю миграцию
docker compose exec backend alembic downgrade -1

# Применить все миграции
docker compose exec backend alembic upgrade head
```

### API
```bash
# Создать пользователя
curl -X POST http://localhost:8044/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{"telegram_id": 123, "first_name": "Test", "role": "client"}'

# Получить пользователя
curl "http://localhost:8044/api/v1/users/me?telegram_id=123"

# Обновить пользователя
curl -X PATCH "http://localhost:8044/api/v1/users/1" \
  -H "Content-Type: application/json" \
  -d '{"first_name": "Updated Name"}'

# Список пользователей
curl "http://localhost:8044/api/v1/users?role=photographer"
```

### Telegram Bot
```bash
# Посмотреть логи бота
docker compose logs -f chat-bot

# Перезапустить бота
docker compose restart chat-bot

# Проверить статус
docker compose ps chat-bot
```

### Отладка
```bash
# Python shell в backend
docker compose exec backend python

# В Python:
from app.models.user import User
from app.services.user_service import UserService
from app.core.database import get_db

# Импортировать и тестировать компоненты
```

---

**Успехов в разработке! 🚀**

При проблемах:
1. Проверь логи контейнеров
2. Проверь .env файлы (backend и chat-bot)
3. Проверь что все миграции применены
4. Проверь что бот имеет доступ к БД
5. Прогони тесты заново

**Следующая итерация:** Регистрация фотографа (расширенный профиль + настройки)
