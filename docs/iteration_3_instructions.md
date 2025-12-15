# ТЗ-ИНСТРУКЦИЯ: ИТЕРАЦИЯ 3 - "Регистрация фотографа"
## BrashLens MVP - Для разработчика Mid+ на MacBook M1

**Цель итерации:** Расширенная регистрация фотографа с заполнением профиля, генерацией персональной ссылки и дефолтными настройками.

**Длительность:** 4-5 дней

**Критерий успеха:** Фотограф проходит регистрацию от начала до конца, получает персональную ссылку `t.me/brashlens_bot?start=username`, данные корректно сохраняются.

---

## 📋 ПРЕДВАРИТЕЛЬНЫЕ ТРЕБОВАНИЯ

### Проверка завершения итерации 2

```bash
# Проверь контейнеры
cd /root/wmraduga4/BrashLens
docker compose ps

# Проверь что User работает
curl "http://localhost:8044/api/v1/users/me?telegram_id=YOUR_ID"

# Проверь бота
# Отправь /start в Telegram - должны быть кнопки выбора роли
```

---

## 🔨 ЭТАП 1: МОДЕЛЬ PHOTOGRAPHER + МИГРАЦИЯ

### Задача
Создать модель `Photographer` со связью One-to-One с `User` и полями для профиля фотографа.

### Промт для Cursor

```
@BrashLens/backend/app/models Создай модель Photographer:

1. BrashLens/backend/app/models/photographer.py:
   - Класс Photographer(Base):
     * id: Integer, primary_key
     * user_id: Integer, ForeignKey('users.id'), unique, not null
     * display_name: String(100), not null (публичное имя для клиентов)
     * city: String(100), nullable
     * bio: Text, nullable (описание фотографа)
     * phone: String(20), nullable
     * email: String(255), nullable
     * instagram: String(100), nullable (@username формат)
     * currency: Enum('RUB', 'USD', 'EUR', 'THB'), default='RUB', not null
     * timezone: String(50), default='UTC', not null
     * avatar_url: String(500), nullable
     * public_link: String(100), unique, not null (username для ссылки)
     * is_profile_complete: Boolean, default=False
     * created_at: DateTime(timezone=True), server_default=func.now()
     * updated_at: DateTime(timezone=True), onupdate=func.now()
   
   - Relationships:
     * user: relationship('User', back_populates='photographer')
   
   - Методы:
     * __repr__
     * to_dict()
     * get_public_url() -> str  # возвращает t.me/brashlens_bot?start={public_link}

2. Обнови BrashLens/backend/app/models/user.py:
   - Добавь relationship: photographer: Mapped['Photographer'] = relationship(back_populates='user', uselist=False)

3. BrashLens/backend/app/models/photographer_settings.py:
   - Класс PhotographerSettings(Base) - дефолтные настройки:
     * photographer_id: Integer, ForeignKey, unique
     * working_days: JSON, default=[1,2,3,4,5] (пн-пт)
     * working_hours_start: Time, default='10:00'
     * working_hours_end: Time, default='20:00'
     * booking_buffer_minutes: Integer, default=30
     * advance_booking_days: Integer, default=90 (на сколько дней вперед можно бронировать)
     * created_at, updated_at

4. Создай миграцию: "create_photographer_tables"

Важно:
- public_link должен быть уникальным (используется в URL)
- currency определяет валюту для всех цен фотографа
- is_profile_complete=True когда заполнены обязательные поля
- Индексы на user_id, public_link
```

### ТРОЙНОЕ ТЕСТИРОВАНИЕ #1

#### ✅ Тест 1: Проверка модели
```bash
docker compose exec backend python

from app.models.photographer import Photographer, PhotographerSettings
from app.models.user import User
print(Photographer.__tablename__)
print(PhotographerSettings.__tablename__)
exit()
```

#### ✅ Тест 2: Применение миграции
```bash
docker compose exec backend alembic revision --autogenerate -m "create_photographer_tables"
docker compose exec backend alembic upgrade head

# Проверь таблицы
cd /root/wmraduga4/infrastructure
docker compose exec postgres psql -U govardvolov -d brashlens_db -c "\d photographers"
docker compose exec postgres psql -U govardvolov -d brashlens_db -c "\d photographer_settings"
```

#### ✅ Тест 3: Создание тестового фотографа
```bash
docker compose exec backend python

from app.core.database import engine, AsyncSession
from app.models.user import User
from app.models.photographer import Photographer, PhotographerSettings
from sqlalchemy.orm import sessionmaker
import asyncio

async def test():
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        # Найдём user с ролью photographer
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.role == 'photographer').limit(1))
        user = result.scalar_one_or_none()
        
        if user and not hasattr(user, 'photographer'):
            p = Photographer(
                user_id=user.id,
                display_name=user.first_name,
                public_link=user.username or f"user{user.id}",
                city="Test City",
                currency="RUB"
            )
            session.add(p)
            await session.commit()
            print(f"✅ Photographer created: {p.display_name}")
        else:
            print("No photographer user found or already has profile")

asyncio.run(test())
exit()
```

### Коммит
```bash
git checkout dev
git add .
git commit -m "feat: этап 1 итерации 3 - модель Photographer и PhotographerSettings"
git push origin dev && git checkout main && git merge dev && git push origin main && git checkout dev
```

---

## 🔨 ЭТАП 2: PYDANTIC СХЕМЫ + PHOTOGRAPHER SERVICE

### Задача
Создать схемы валидации и сервис для работы с фотографами.

### Промт для Cursor

```
@BrashLens/backend/app/schemas Создай схемы для Photographer:

1. BrashLens/backend/app/schemas/photographer.py:
   
   class PhotographerBase(BaseModel):
       display_name: str = Field(..., min_length=2, max_length=100)
       city: Optional[str] = Field(None, max_length=100)
       bio: Optional[str] = Field(None, max_length=1000)
       phone: Optional[str] = Field(None, pattern=r'^\+?[\d\s\-\(\)]+$')
       email: Optional[EmailStr] = None
       instagram: Optional[str] = Field(None, pattern=r'^@?[\w\.]+$')
       currency: Literal['RUB', 'USD', 'EUR', 'THB'] = 'RUB'
   
   class PhotographerCreate(PhotographerBase):
       public_link: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_]+$')
   
   class PhotographerUpdate(BaseModel):
       display_name: Optional[str] = Field(None, min_length=2, max_length=100)
       city: Optional[str] = None
       bio: Optional[str] = None
       phone: Optional[str] = None
       email: Optional[EmailStr] = None
       instagram: Optional[str] = None
   
   class PhotographerResponse(PhotographerBase):
       id: int
       user_id: int
       public_link: str
       avatar_url: Optional[str]
       is_profile_complete: bool
       created_at: datetime
       
       model_config = ConfigDict(from_attributes=True)
   
   class PhotographerPublic(BaseModel):
       """Публичная информация для клиентов"""
       display_name: str
       city: Optional[str]
       bio: Optional[str]
       avatar_url: Optional[str]
       instagram: Optional[str]
       
       model_config = ConfigDict(from_attributes=True)

2. Схемы для PhotographerSettings:
   
   class SettingsBase(BaseModel):
       working_days: List[int] = Field(default=[1,2,3,4,5], min_items=1, max_items=7)
       working_hours_start: time = Field(default=time(10, 0))
       working_hours_end: time = Field(default=time(20, 0))
       booking_buffer_minutes: int = Field(default=30, ge=0, le=120)
       advance_booking_days: int = Field(default=90, ge=1, le=365)
   
   class SettingsResponse(SettingsBase):
       id: int
       photographer_id: int
       model_config = ConfigDict(from_attributes=True)

@BrashLens/backend/app/services Создай PhotographerService:

class PhotographerService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_photographer(
        self, user_id: int, photographer_data: PhotographerCreate
    ) -> Photographer:
        """Создать профиль фотографа с дефолтными настройками"""
        # Проверка что user существует и photographer еще нет
        # Создание Photographer
        # Создание PhotographerSettings с дефолтами
        # Обновление is_profile_complete если все обязательные поля заполнены
        # Commit и return
    
    async def get_by_user_id(self, user_id: int) -> Optional[Photographer]:
        """Получить профиль фотографа по user_id"""
    
    async def get_by_public_link(self, public_link: str) -> Optional[Photographer]:
        """Получить фотографа по публичной ссылке"""
    
    async def update_photographer(
        self, photographer_id: int, update_data: PhotographerUpdate
    ) -> Optional[Photographer]:
        """Обновить профиль фотографа"""
    
    async def check_profile_completeness(self, photographer: Photographer) -> bool:
        """Проверить заполнены ли обязательные поля"""
        required = ['display_name', 'city', 'currency']
        return all(getattr(photographer, field) for field in required)
    
    async def generate_unique_public_link(self, base: str) -> str:
        """Генерация уникального public_link если base занят"""
        # Попробовать base, base2, base3 и т.д.

Добавь dependency в app/api/dependencies.py:
async def get_photographer_service(db: AsyncSession = Depends(get_db)) -> PhotographerService:
    return PhotographerService(db)
```

### ТРОЙНОЕ ТЕСТИРОВАНИЕ #2

#### ✅ Тест 1: Валидация схем
```bash
docker compose exec backend python

from app.schemas.photographer import PhotographerCreate, SettingsBase

# Валидный
pc = PhotographerCreate(
    display_name="Иван Фотограф",
    city="Москва",
    public_link="ivan_photo",
    currency="RUB"
)
print("✅ Valid:", pc.model_dump())

# Невалидный public_link (пробелы)
try:
    PhotographerCreate(
        display_name="Test",
        public_link="invalid link",
        currency="RUB"
    )
except Exception as e:
    print("✅ Validation rejected:", str(e)[:50])

exit()
```

#### ✅ Тест 2: Создание через сервис
```bash
docker compose exec backend python

from app.services.photographer_service import PhotographerService
from app.schemas.photographer import PhotographerCreate
from app.core.database import engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import asyncio

async def test():
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        service = PhotographerService(session)
        
        # Найди user photographer без профиля
        from app.services.user_service import UserService
        user_service = UserService(session)
        users = await user_service.get_users_by_role('photographer')
        
        for user in users:
            existing = await service.get_by_user_id(user.id)
            if not existing:
                data = PhotographerCreate(
                    display_name=user.first_name,
                    city="Test City",
                    public_link=user.username or f"user{user.id}",
                    currency="RUB"
                )
                p = await service.create_photographer(user.id, data)
                print(f"✅ Created: {p.display_name}, link: {p.public_link}")
                break

asyncio.run(test())
exit()
```

#### ✅ Тест 3: Получение по public_link
```bash
docker compose exec backend python

from app.services.photographer_service import PhotographerService
from app.core.database import engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import asyncio

async def test():
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        service = PhotographerService(session)
        
        # Замени на реальный public_link из БД
        p = await service.get_by_public_link("ivan_photo")
        if p:
            print(f"✅ Found: {p.display_name}")
            print(f"   Settings: {p.settings}")
        else:
            print("❌ Not found")

asyncio.run(test())
exit()
```

### Коммит
```bash
git checkout dev
git add .
git commit -m "feat: этап 2 итерации 3 - схемы и сервис для Photographer"
git push origin dev && git checkout main && git merge dev && git push origin main && git checkout dev
```

---

## 🔨 ЭТАП 3: API ENDPOINTS ДЛЯ PHOTOGRAPHER

### Задача
Создать REST API для работы с профилями фотографов.

### Промт для Cursor

```
@BrashLens/backend/app/api/v1 Создай API для photographers:

1. BrashLens/backend/app/api/v1/photographers.py:
   
   router = APIRouter(prefix="/photographers", tags=["photographers"])
   
   @router.post("", response_model=PhotographerResponse, status_code=201)
   async def create_photographer(
       photographer_data: PhotographerCreate,
       user_id: int = Query(...),  # временно через query, позже через JWT
       service: PhotographerService = Depends(get_photographer_service)
   ):
       """Создать профиль фотографа"""
       # Проверить что user существует и это photographer
       # Создать профиль
       # Вернуть
   
   @router.get("/me", response_model=PhotographerResponse)
   async def get_my_photographer_profile(
       user_id: int = Query(...),
       service: PhotographerService = Depends(get_photographer_service)
   ):
       """Получить свой профиль фотографа"""
   
   @router.get("/{public_link}", response_model=PhotographerPublic)
   async def get_photographer_by_link(
       public_link: str,
       service: PhotographerService = Depends(get_photographer_service)
   ):
       """Публичный endpoint - получить профиль по ссылке"""
   
   @router.patch("/{photographer_id}", response_model=PhotographerResponse)
   async def update_photographer(
       photographer_id: int,
       update_data: PhotographerUpdate,
       service: PhotographerService = Depends(get_photographer_service)
   ):
       """Обновить профиль"""
   
   @router.get("/{photographer_id}/settings", response_model=SettingsResponse)
   async def get_photographer_settings(
       photographer_id: int,
       service: PhotographerService = Depends(get_photographer_service)
   ):
       """Получить настройки фотографа"""

2. Подключи router в app/api/v1/__init__.py
```

### ТРОЙНОЕ ТЕСТИРОВАНИЕ #3

#### ✅ Тест 1: Создание через API
```bash
# Найди user_id фотографа без профиля
curl "http://localhost:8044/api/v1/users?role=photographer"

# Создай профиль
curl -X POST "http://localhost:8044/api/v1/photographers?user_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "display_name": "Анна Петрова",
    "city": "Москва",
    "public_link": "anna_photo",
    "currency": "RUB",
    "bio": "Профессиональный фотограф",
    "phone": "+7 999 123-45-67",
    "instagram": "@anna.photo"
  }'
```

#### ✅ Тест 2: Получение профиля
```bash
# По user_id
curl "http://localhost:8044/api/v1/photographers/me?user_id=1"

# По public_link (публичный endpoint)
curl "http://localhost:8044/api/v1/photographers/anna_photo"
```

#### ✅ Тест 3: Обновление
```bash
curl -X PATCH "http://localhost:8044/api/v1/photographers/1" \
  -H "Content-Type: application/json" \
  -d '{
    "bio": "Обновленное описание",
    "city": "Санкт-Петербург"
  }'
```

### Коммит
```bash
git checkout dev
git add .
git commit -m "feat: этап 3 итерации 3 - API endpoints для Photographer"
git push origin dev && git checkout main && git merge dev && git push origin main && git checkout dev
```

---

## 🔨 ЭТАП 4: TELEGRAM БОТ - ДИАЛОГОВЫЙ FLOW РЕГИСТРАЦИИ

### Задача
Реализовать пошаговую регистрацию фотографа через ConversationHandler с вводом данных и генерацией ссылки.

### Промт для Cursor

```
@BrashLens/backend/app/bot/handlers Создай регистрацию фотографа:

1. app/bot/handlers/photographer_registration.py:
   
   # States
   CHOOSING_LANGUAGE, ENTERING_NAME, ENTERING_CITY, CHOOSING_CURRENCY = range(4)
   
   async def start_photographer_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
       """Начало регистрации - выбор языка"""
       keyboard = [
           [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
           [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
       ]
       text = "Выберите язык интерфейса / Choose interface language:"
       await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
       return CHOOSING_LANGUAGE
   
   async def language_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
       """Язык выбран - запрос имени"""
       query = update.callback_query
       await query.answer()
       
       lang = query.data.replace("lang_", "")
       context.user_data['language'] = lang
       
       user = update.effective_user
       
       if lang == 'ru':
           text = (
               f"Отлично! Теперь давайте настроим ваш профиль.\n\n"
               f"**Шаг 1/3: Имя для клиентов**\n"
               f"Как вас будут видеть клиенты?\n\n"
               f"Предложение: {user.first_name}"
           )
           keyboard = [[InlineKeyboardButton(f"Использовать: {user.first_name}", callback_data=f"use_name_{user.first_name}")]]
       else:
           text = (
               f"Great! Let's set up your profile.\n\n"
               f"**Step 1/3: Display name**\n"
               f"How will clients see you?\n\n"
               f"Suggestion: {user.first_name}"
           )
           keyboard = [[InlineKeyboardButton(f"Use: {user.first_name}", callback_data=f"use_name_{user.first_name}")]]
       
       await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
       return ENTERING_NAME
   
   async def name_provided(update: Update, context: ContextTypes.DEFAULT_TYPE):
       """Имя получено - запрос города"""
       if update.callback_query:
           # Использовал предложенное имя
           query = update.callback_query
           await query.answer()
           name = query.data.replace("use_name_", "")
           message = query.message
       else:
           # Ввел свое имя
           name = update.message.text
           message = update.message
       
       # Валидация
       if len(name) < 2 or len(name) > 100:
           await message.reply_text("Имя должно быть от 2 до 100 символов. Попробуйте еще раз:")
           return ENTERING_NAME
       
       context.user_data['display_name'] = name
       
       lang = context.user_data.get('language', 'ru')
       text = (
           f"**Шаг 2/3: Город**\n"
           f"В каком городе вы работаете?\n"
           f"Например: Москва, Бангкок, Санкт-Петербург"
       ) if lang == 'ru' else (
           f"**Step 2/3: City**\n"
           f"Which city do you work in?\n"
           f"Example: Moscow, Bangkok, Saint Petersburg"
       )
       
       await message.reply_text(text, parse_mode='Markdown')
       return ENTERING_CITY
   
   async def city_provided(update: Update, context: ContextTypes.DEFAULT_TYPE):
       """Город получен - выбор валюты"""
       city = update.message.text.strip()
       
       if len(city) < 2:
           await update.message.reply_text("Укажите город:")
           return ENTERING_CITY
       
       context.user_data['city'] = city
       
       lang = context.user_data.get('language', 'ru')
       keyboard = [
           [InlineKeyboardButton("₽ RUB", callback_data="currency_RUB")],
           [InlineKeyboardButton("$ USD", callback_data="currency_USD")],
           [InlineKeyboardButton("€ EUR", callback_data="currency_EUR")],
           [InlineKeyboardButton("฿ THB", callback_data="currency_THB")]
       ]
       
       text = (
           f"**Шаг 3/3: Валюта**\n"
           f"В какой валюте вы указываете цены?"
       ) if lang == 'ru' else (
           f"**Step 3/3: Currency**\n"
           f"Which currency do you use for pricing?"
       )
       
       await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
       return CHOOSING_CURRENCY
   
   async def currency_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
       """Валюта выбрана - создание профиля"""
       query = update.callback_query
       await query.answer()
       
       currency = query.data.replace("currency_", "")
       context.user_data['currency'] = currency
       
       # Собираем все данные
       user = update.effective_user
       display_name = context.user_data['display_name']
       city = context.user_data['city']
       language = context.user_data['language']
       
       # Генерируем public_link из username или telegram_id
       public_link = user.username or f"user{user.id}"
       
       # Создаем профиль через API/сервис
       try:
           from app.core.database import get_db
           from app.services.photographer_service import PhotographerService
           from app.services.user_service import UserService
           from app.schemas.photographer import PhotographerCreate
           
           async with get_db() as db:
               # Обновляем язык в User
               user_service = UserService(db)
               await user_service.update_user(user.id, {'language': language})
               
               # Создаем профиль фотографа
               photographer_service = PhotographerService(db)
               
               # Проверяем уникальность public_link
               unique_link = await photographer_service.generate_unique_public_link(public_link)
               
               photographer_data = PhotographerCreate(
                   display_name=display_name,
                   city=city,
                   currency=currency,
                   public_link=unique_link
               )
               
               photographer = await photographer_service.create_photographer(user.id, photographer_data)
               
               # Генерируем ссылку
               bot_username = context.bot.username
               share_link = f"https://t.me/{bot_username}?start={unique_link}"
               
               lang = context.user_data.get('language', 'ru')
               if lang == 'ru':
                   text = (
                       f"✅ **Профиль создан!**\n\n"
                       f"👤 {display_name}\n"
                       f"📍 {city}\n"
                       f"💰 {currency}\n\n"
                       f"🔗 **Ваша персональная ссылка:**\n"
                       f"`{share_link}`\n\n"
                       f"Делитесь этой ссылкой с клиентами!\n"
                       f"Когда они перейдут по ней, автоматически создастся связь.\n\n"
                       f"**Следующие шаги:**\n"
                       f"1. Загрузите портфолио\n"
                       f"2. Настройте календарь\n"
                       f"3. Создайте пакеты услуг\n\n"
                       f"Используйте /help для списка команд"
                   )
                   keyboard = [[InlineKeyboardButton("📋 Скопировать ссылку", url=share_link)]]
               else:
                   text = (
                       f"✅ **Profile created!**\n\n"
                       f"👤 {display_name}\n"
                       f"📍 {city}\n"
                       f"💰 {currency}\n\n"
                       f"🔗 **Your personal link:**\n"
                       f"`{share_link}`\n\n"
                       f"Share this link with clients!\n\n"
                       f"**Next steps:**\n"
                       f"1. Upload portfolio\n"
                       f"2. Setup calendar\n"
                       f"3. Create packages\n\n"
                       f"Use /help for commands"
                   )
                   keyboard = [[InlineKeyboardButton("📋 Copy link", url=share_link)]]
               
               await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
               return ConversationHandler.END
               
       except Exception as e:
           print(f"Error creating photographer: {e}")
           await query.edit_message_text(
               "Произошла ошибка при создании профиля. Попробуйте /start снова."
           )
           return ConversationHandler.END

2. Обнови app/bot/handlers/start.py:
   - После выбора роли "photographer" запускай start_photographer_registration
   - Для "client" оставь простое сохранение как было

3. Обнови app/bot/main.py:
   - Добавь ConversationHandler для регистрации фотографа
   - States: CHOOSING_LANGUAGE, ENTERING_NAME, ENTERING_CITY, CHOOSING_CURRENCY
```

### ТРОЙНОЕ ТЕСТИРОВАНИЕ #4

#### ✅ Тест 1: Flow регистрации в Telegram

**В Telegram:**
1. Удали предыдущего тестового пользователя из БД (если есть)
2. Отправь `/start` боту
3. Выбери "Я фотограф 📸"
4. Пройди весь flow:
   - Выбери язык (🇷🇺 или 🇬🇧)
   - Введи/подтверди имя
   - Введи город
   - Выбери валюту
5. Получи персональную ссылку

#### ✅ Тест 2: Проверка в БД
```bash
cd /root/wmraduga4/infrastructure
docker compose exec postgres psql -U govardvolov -d brashlens_db -c \
  "SELECT u.telegram_id, u.username, p.display_name, p.city, p.currency, p.public_link 
   FROM users u 
   JOIN photographers p ON u.id = p.user_id 
   ORDER BY p.created_at DESC 
   LIMIT 3;"
```

#### ✅ Тест 3: Проверка ссылки через API
```bash
# Замени public_link на реальный из БД
curl "http://localhost:8044/api/v1/photographers/your_public_link"
```

### Коммит
```bash
git checkout dev
git add .
git commit -m "feat: этап 4 итерации 3 - диалоговый flow регистрации фотографа"
git push origin dev && git checkout main && git merge dev && git push origin main && git checkout dev
```

---

## 📊 ФИНАЛЬНАЯ ПРОВЕРКА ИТЕРАЦИИ 3

### Чеклист завершения

- [ ] **Модель Photographer:**
  - [ ] Таблица photographers создана
  - [ ] Связь с User работает (One-to-One)
  - [ ] PhotographerSettings создаются с дефолтами
  - [ ] public_link уникальный

- [ ] **API Endpoints:**
  - [ ] POST /api/v1/photographers создает профили
  - [ ] GET /api/v1/photographers/me работает
  - [ ] GET /api/v1/photographers/{public_link} публичный endpoint
  - [ ] PATCH обновляет профили

- [ ] **Telegram Bot:**
  - [ ] Выбор языка работает
  - [ ] Пошаговый ввод данных работает
  - [ ] Валидация работает
  - [ ] Профиль создается в БД
  - [ ] Генерируется уникальная ссылка
  - [ ] Ссылка отображается правильно

### Итоговое тестирование

```bash
# 1. Проверь контейнеры
docker compose ps

# 2. Полный flow через бота:
# - Новый пользователь → /start → "Я фотограф" → регистрация → получение ссылки

# 3. Проверь через API
curl "http://localhost:8044/api/v1/photographers/me?user_id=YOUR_USER_ID"

# 4. Проверь публичный endpoint
curl "http://localhost:8044/api/v1/photographers/YOUR_PUBLIC_LINK"

# 5. Статистика в БД
cd /root/wmraduga4/infrastructure
docker compose exec postgres psql -U govardvolov -d brashlens_db -c \
  "SELECT 
    (SELECT COUNT(*) FROM users WHERE role='photographer') as total_photographers,
    (SELECT COUNT(*) FROM photographers) as profiles_created,
    (SELECT COUNT(*) FROM photographer_settings) as settings_created;"
```

**Критерии успеха:**
- ✅ Фотограф проходит регистрацию полностью
- ✅ Все данные сохраняются корректно
- ✅ Персональная ссылка генерируется
- ✅ Дефолтные настройки создаются
- ✅ API endpoints работают
- ✅ Публичная ссылка доступна

---

## 📝 ФИНАЛЬНЫЙ КОММИТ

```bash
git checkout dev
git add .
git commit -m "feat: iteration 3 complete - photographer registration

- Created Photographer model with profile fields
- Created PhotographerSettings with defaults
- Implemented registration flow in bot (language, name, city, currency)
- Generated unique public links
- Added API endpoints for photographer management
- All features tested and working

Photographer can now complete registration and get personal link for clients."

git push origin dev
git checkout main
git merge dev
git push origin main
git checkout dev
```

---

## 🎯 ИТОГО

**Что получилось в итерации 3:**
- ✅ Модель Photographer с расширенным профилем
- ✅ Дефолтные настройки календаря
- ✅ Диалоговый flow регистрации в боте
- ✅ Выбор языка, имени, города, валюты
- ✅ Генерация персональной ссылки
- ✅ API для работы с профилями
- ✅ Публичный endpoint для клиентов

**Время выполнения:** 4-5 дней

**Готовность к итерации 4:** ✅

**Следующая итерация:** Mini App - основа (React + Telegram WebApp SDK)
