# ТЗ-ИНСТРУКЦИЯ: ИТЕРАЦИЯ 4 - "Mini App - основа"
## BrashLens MVP - Для разработчика Mid+ на MacBook M1

**Цель итерации:** Создать React Mini App с базовой структурой, интеграцией Telegram WebApp SDK, роутингом, навигацией и заглушками всех страниц.

**Длительность:** 4-5 дней

**Критерий успеха:** Mini App открывается из бота, корректно отображается на мобильном, навигация работает, смена языка работает, API запросы проходят с аутентификацией.

---

## 📋 ПРЕДВАРИТЕЛЬНЫЕ ТРЕБОВАНИЯ

### Проверка завершения итерации 3

```bash
cd /root/wmraduga4/BrashLens
docker compose ps

# Проверь API photographers
curl "http://localhost:8044/api/v1/photographers/me?user_id=YOUR_USER_ID"

# Проверь бота - должен выдавать персональную ссылку после регистрации
```

---

## 🔨 ЭТАП 1: ИНИЦИАЛИЗАЦИЯ REACT ПРОЕКТА

### Задача
Создать React проект с Vite, TypeScript, Tailwind CSS и базовой структурой файлов.

### Промт для Cursor

```
@BrashLens Создай React Mini App проект:

1. Структура:
BrashLens/frontend/
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
├── index.html
└── src/
    ├── main.tsx
    ├── App.tsx
    ├── vite-env.d.ts
    ├── components/
    │   ├── Layout/
    │   │   ├── Layout.tsx
    │   │   └── Navigation.tsx
    │   └── common/
    │       ├── Button.tsx
    │       ├── Card.tsx
    │       └── Loader.tsx
    ├── pages/
    │   ├── Dashboard.tsx
    │   ├── Profile.tsx
    │   ├── Portfolio.tsx
    │   ├── Calendar.tsx
    │   └── Clients.tsx
    ├── hooks/
    │   ├── useTelegram.ts
    │   └── useApi.ts
    ├── services/
    │   └── api.ts
    ├── store/
    │   └── index.ts
    ├── types/
    │   └── index.ts
    ├── utils/
    │   └── helpers.ts
    └── styles/
        └── globals.css

2. package.json:
{
  "name": "brashlens-miniapp",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "@tanstack/react-query": "^5.12.0",
    "zustand": "^4.4.7",
    "axios": "^1.6.2",
    "i18next": "^23.7.6",
    "react-i18next": "^13.5.0",
    "@twa-dev/sdk": "^7.0.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.3.3",
    "vite": "^5.0.8",
    "tailwindcss": "^3.3.6",
    "postcss": "^8.4.32",
    "autoprefixer": "^10.4.16"
  }
}

3. vite.config.ts:
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    host: true
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    minify: 'terser'
  }
})

4. tailwind.config.js - стандартная конфигурация для Telegram Mini App:
- Используй цветовую схему из Telegram WebApp
- Темная/светлая тема через CSS переменные
- Responsive breakpoints

5. tsconfig.json - strict mode, path aliases

Используй современный TypeScript, functional components, hooks.
```

### Реализация

```bash
# Создай frontend директорию
cd /root/wmraduga4/BrashLens
mkdir -p frontend
cd frontend

# Cursor создаст структуру
# Затем установи зависимости
npm install
```

### ТРОЙНОЕ ТЕСТИРОВАНИЕ #1

#### ✅ Тест 1: Проверка структуры
```bash
cd /root/wmraduga4/BrashLens/frontend
tree -L 3 -I node_modules
cat package.json | grep "name\|version"
```

#### ✅ Тест 2: Dev сервер запускается
```bash
npm run dev

# Должен запуститься на http://localhost:5173
# Открой в браузере или curl
curl http://localhost:5173
```

#### ✅ Тест 3: Build работает
```bash
npm run build

# Должна создаться папка dist/
ls -la dist/
```

### Коммит
```bash
git checkout dev
git add .
git commit -m "feat: этап 1 итерации 4 - инициализация React проекта"
git push origin dev && git checkout main && git merge dev && git push origin main && git checkout dev
```

---

## 🔨 ЭТАП 2: ИНТЕГРАЦИЯ TELEGRAM WEBAPP SDK

### Задача
Интегрировать Telegram WebApp SDK, создать хук для работы с ним, настроить тему и получение данных пользователя.

### Промт для Cursor

```
@BrashLens/frontend/src Интегрируй Telegram WebApp SDK:

1. src/hooks/useTelegram.ts:
import { useEffect, useState } from 'react'

interface TelegramUser {
  id: number
  first_name: string
  last_name?: string
  username?: string
  language_code?: string
}

interface TelegramWebApp {
  initData: string
  initDataUnsafe: {
    user?: TelegramUser
    query_id?: string
    auth_date: number
    hash: string
  }
  version: string
  platform: string
  colorScheme: 'light' | 'dark'
  themeParams: {
    bg_color: string
    text_color: string
    hint_color: string
    link_color: string
    button_color: string
    button_text_color: string
  }
  isExpanded: boolean
  viewportHeight: number
  viewportStableHeight: number
  headerColor: string
  backgroundColor: string
  BackButton: {
    isVisible: boolean
    onClick(callback: () => void): void
    offClick(callback: () => void): void
    show(): void
    hide(): void
  }
  MainButton: {
    text: string
    color: string
    textColor: string
    isVisible: boolean
    isActive: boolean
    isProgressVisible: boolean
    setText(text: string): void
    onClick(callback: () => void): void
    offClick(callback: () => void): void
    show(): void
    hide(): void
    enable(): void
    disable(): void
    showProgress(leaveActive?: boolean): void
    hideProgress(): void
  }
  ready(): void
  expand(): void
  close(): void
  sendData(data: string): void
}

declare global {
  interface Window {
    Telegram?: {
      WebApp: TelegramWebApp
    }
  }
}

export const useTelegram = () => {
  const [tg] = useState(() => window.Telegram?.WebApp)
  
  useEffect(() => {
    if (tg) {
      tg.ready()
      tg.expand()
    }
  }, [tg])
  
  const user = tg?.initDataUnsafe?.user
  const queryId = tg?.initDataUnsafe?.query_id
  
  return {
    tg,
    user,
    queryId,
    initData: tg?.initData,
    colorScheme: tg?.colorScheme,
    themeParams: tg?.themeParams,
    onClose: () => tg?.close(),
    onToggleButton: () => {
      if (tg?.MainButton.isVisible) {
        tg.MainButton.hide()
      } else {
        tg.MainButton.show()
      }
    }
  }
}

2. src/App.tsx:
import { useEffect } from 'react'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useTelegram } from './hooks/useTelegram'
import AppRouter from './AppRouter'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1
    }
  }
})

function App() {
  const { tg, colorScheme, themeParams } = useTelegram()
  
  useEffect(() => {
    // Применяем тему Telegram
    if (themeParams) {
      document.documentElement.style.setProperty('--tg-theme-bg-color', themeParams.bg_color)
      document.documentElement.style.setProperty('--tg-theme-text-color', themeParams.text_color)
      document.documentElement.style.setProperty('--tg-theme-hint-color', themeParams.hint_color)
      document.documentElement.style.setProperty('--tg-theme-link-color', themeParams.link_color)
      document.documentElement.style.setProperty('--tg-theme-button-color', themeParams.button_color)
      document.documentElement.style.setProperty('--tg-theme-button-text-color', themeParams.button_text_color)
    }
  }, [themeParams])
  
  useEffect(() => {
    // Устанавливаем класс для темы
    document.body.className = colorScheme === 'dark' ? 'dark' : 'light'
  }, [colorScheme])
  
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppRouter />
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App

3. src/AppRouter.tsx:
import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout/Layout'
import Dashboard from './pages/Dashboard'
import Profile from './pages/Profile'
import Portfolio from './pages/Portfolio'
import Calendar from './pages/Calendar'
import Clients from './pages/Clients'

const AppRouter = () => {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="profile" element={<Profile />} />
        <Route path="portfolio" element={<Portfolio />} />
        <Route path="calendar" element={<Calendar />} />
        <Route path="clients" element={<Clients />} />
      </Route>
    </Routes>
  )
}

export default AppRouter

4. src/styles/globals.css:
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --tg-theme-bg-color: #ffffff;
  --tg-theme-text-color: #000000;
  --tg-theme-hint-color: #999999;
  --tg-theme-link-color: #2481cc;
  --tg-theme-button-color: #2481cc;
  --tg-theme-button-text-color: #ffffff;
}

body {
  margin: 0;
  padding: 0;
  background-color: var(--tg-theme-bg-color);
  color: var(--tg-theme-text-color);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

body.dark {
  --tg-theme-bg-color: #1c1c1d;
  --tg-theme-text-color: #ffffff;
  --tg-theme-hint-color: #7d7d7d;
}

5. index.html - добавь скрипт Telegram WebApp:
<script src="https://telegram.org/js/telegram-web-app.js"></script>
```

### ТРОЙНОЕ ТЕСТИРОВАНИЕ #2

#### ✅ Тест 1: Проверка импортов
```bash
cd /root/wmraduga4/BrashLens/frontend
npm run build

# Не должно быть ошибок TypeScript
```

#### ✅ Тест 2: Dev mode
```bash
npm run dev

# Открой в браузере http://localhost:5173
# Должна быть заглушка, но без ошибок в консоли
```

#### ✅ Тест 3: Mock Telegram объект (для разработки)
```bash
# Создай файл public/mock-telegram.js для тестирования вне Telegram
cat > public/mock-telegram.js << 'EOF'
window.Telegram = {
  WebApp: {
    initData: '',
    initDataUnsafe: {
      user: {
        id: 123456789,
        first_name: 'Test',
        username: 'testuser',
        language_code: 'ru'
      }
    },
    version: '6.0',
    platform: 'web',
    colorScheme: 'light',
    themeParams: {
      bg_color: '#ffffff',
      text_color: '#000000',
      hint_color: '#999999',
      link_color: '#2481cc',
      button_color: '#2481cc',
      button_text_color: '#ffffff'
    },
    isExpanded: true,
    viewportHeight: 600,
    viewportStableHeight: 600,
    BackButton: { isVisible: false, show() {}, hide() {} },
    MainButton: { isVisible: false, show() {}, hide() {} },
    ready() {},
    expand() {},
    close() {}
  }
}
EOF

# Подключи в index.html для dev режима (условно)
```

### Коммит
```bash
git checkout dev
git add .
git commit -m "feat: этап 2 итерации 4 - интеграция Telegram WebApp SDK"
git push origin dev && git checkout main && git merge dev && git push origin main && git checkout dev
```

---

## 🔨 ЭТАП 3: LAYOUT, NAVIGATION И СТРАНИЦЫ-ЗАГЛУШКИ

### Задача
Создать Layout с навигацией, все страницы-заглушки с роутингом.

### Промт для Cursor

```
@BrashLens/frontend/src Создай Layout и страницы:

1. src/components/Layout/Layout.tsx:
import { Outlet } from 'react-router-dom'
import Navigation from './Navigation'

const Layout = () => {
  return (
    <div className="min-h-screen flex flex-col">
      <main className="flex-1 pb-16">
        <Outlet />
      </main>
      <Navigation />
    </div>
  )
}

export default Layout

2. src/components/Layout/Navigation.tsx:
import { NavLink } from 'react-router-dom'
import { Home, User, Image, Calendar, Users } from 'lucide-react'

const Navigation = () => {
  const links = [
    { to: '/dashboard', icon: Home, label: 'Главная' },
    { to: '/portfolio', icon: Image, label: 'Портфолио' },
    { to: '/calendar', icon: Calendar, label: 'Календарь' },
    { to: '/clients', icon: Users, label: 'Клиенты' },
    { to: '/profile', icon: User, label: 'Профиль' }
  ]
  
  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800">
      <div className="flex justify-around items-center h-16">
        {links.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex flex-col items-center justify-center flex-1 h-full transition-colors ${
                isActive
                  ? 'text-blue-600 dark:text-blue-400'
                  : 'text-gray-600 dark:text-gray-400'
              }`
            }
          >
            <Icon size={24} />
            <span className="text-xs mt-1">{label}</span>
          </NavLink>
        ))}
      </div>
    </nav>
  )
}

export default Navigation

3. src/pages/Dashboard.tsx:
import { useTelegram } from '@/hooks/useTelegram'

const Dashboard = () => {
  const { user } = useTelegram()
  
  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">
        Привет, {user?.first_name || 'Фотограф'}! 👋
      </h1>
      
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <div className="text-3xl font-bold mb-2">0</div>
          <div className="text-gray-600 dark:text-gray-400">Броней сегодня</div>
        </div>
        
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <div className="text-3xl font-bold mb-2">0</div>
          <div className="text-gray-600 dark:text-gray-400">Новых клиентов</div>
        </div>
        
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <div className="text-3xl font-bold mb-2">0</div>
          <div className="text-gray-600 dark:text-gray-400">Фото в портфолио</div>
        </div>
        
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <div className="text-3xl font-bold mb-2">₽0</div>
          <div className="text-gray-600 dark:text-gray-400">Выручка за месяц</div>
        </div>
      </div>
      
      <div className="mt-6 bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
        <h2 className="font-semibold mb-2">🚀 Быстрый старт</h2>
        <ul className="space-y-2 text-sm">
          <li>1. Загрузите фото в портфолио</li>
          <li>2. Настройте календарь доступности</li>
          <li>3. Создайте пакеты услуг</li>
          <li>4. Поделитесь ссылкой с клиентами</li>
        </ul>
      </div>
    </div>
  )
}

export default Dashboard

4. src/pages/Profile.tsx:
const Profile = () => {
  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Профиль</h1>
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg">
        <p className="text-gray-600 dark:text-gray-400">
          Здесь будут настройки профиля фотографа
        </p>
      </div>
    </div>
  )
}

export default Profile

5. src/pages/Portfolio.tsx:
const Portfolio = () => {
  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Портфолио</h1>
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg text-center">
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          Портфолио пока пусто
        </p>
        <button className="bg-blue-600 text-white px-6 py-2 rounded-lg">
          Добавить фото
        </button>
      </div>
    </div>
  )
}

export default Portfolio

6. src/pages/Calendar.tsx:
const Calendar = () => {
  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Календарь</h1>
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg">
        <p className="text-gray-600 dark:text-gray-400">
          Здесь будет календарь доступности
        </p>
      </div>
    </div>
  )
}

export default Calendar

7. src/pages/Clients.tsx:
const Clients = () => {
  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Клиенты</h1>
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg">
        <p className="text-gray-600 dark:text-gray-400">
          Список клиентов появится здесь
        </p>
      </div>
    </div>
  )
}

export default Clients

8. Установи lucide-react для иконок:
npm install lucide-react
```

### ТРОЙНОЕ ТЕСТИРОВАНИЕ #3

#### ✅ Тест 1: Проверка роутинга
```bash
npm run dev

# Открой http://localhost:5173
# Кликай по навигации - страницы должны переключаться
```

#### ✅ Тест 2: Проверка темной темы
```bash
# В браузере открой DevTools
# В консоли выполни:
document.body.className = 'dark'

# Тема должна переключиться
```

#### ✅ Тест 3: Build
```bash
npm run build
ls -lh dist/

# Должен быть bundle с оптимизацией
```

### Коммит
```bash
git checkout dev
git add .
git commit -m "feat: этап 3 итерации 4 - Layout, навигация и страницы-заглушки"
git push origin dev && git checkout main && git merge dev && git push origin main && git checkout dev
```

---

## 🔨 ЭТАП 4: API КЛИЕНТ + REACT QUERY + I18N

### Задача
Настроить API клиент с axios, React Query для запросов, i18next для мультиязычности.

### Промт для Cursor

```
@BrashLens/frontend/src Настрой API и i18n:

1. src/services/api.ts:
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8044/api/v1'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Интерсептор для добавления Telegram данных
api.interceptors.request.use((config) => {
  const tg = window.Telegram?.WebApp
  if (tg?.initData) {
    config.headers['X-Telegram-Init-Data'] = tg.initData
  }
  return config
})

// Интерсептор для обработки ошибок
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export default api

2. src/hooks/useApi.ts:
import { useQuery, useMutation, UseQueryOptions, UseMutationOptions } from '@tanstack/react-query'
import api from '@/services/api'
import { AxiosError } from 'axios'

export const useGetPhotographer = (userId?: number) => {
  return useQuery({
    queryKey: ['photographer', userId],
    queryFn: async () => {
      const { data } = await api.get(`/photographers/me?user_id=${userId}`)
      return data
    },
    enabled: !!userId
  })
}

export const useGetUser = (telegramId?: number) => {
  return useQuery({
    queryKey: ['user', telegramId],
    queryFn: async () => {
      const { data } = await api.get(`/users/me?telegram_id=${telegramId}`)
      return data
    },
    enabled: !!telegramId
  })
}

3. src/i18n/index.ts:
import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'

const resources = {
  ru: {
    translation: {
      nav: {
        dashboard: 'Главная',
        portfolio: 'Портфолио',
        calendar: 'Календарь',
        clients: 'Клиенты',
        profile: 'Профиль'
      },
      dashboard: {
        greeting: 'Привет, {{name}}!',
        bookings_today: 'Броней сегодня',
        new_clients: 'Новых клиентов',
        photos: 'Фото в портфолио',
        revenue: 'Выручка за месяц',
        quick_start: 'Быстрый старт'
      },
      profile: {
        title: 'Профиль',
        settings: 'Настройки'
      }
    }
  },
  en: {
    translation: {
      nav: {
        dashboard: 'Home',
        portfolio: 'Portfolio',
        calendar: 'Calendar',
        clients: 'Clients',
        profile: 'Profile'
      },
      dashboard: {
        greeting: 'Hello, {{name}}!',
        bookings_today: 'Bookings today',
        new_clients: 'New clients',
        photos: 'Photos in portfolio',
        revenue: 'Revenue this month',
        quick_start: 'Quick start'
      },
      profile: {
        title: 'Profile',
        settings: 'Settings'
      }
    }
  }
}

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: 'ru',
    fallbackLng: 'ru',
    interpolation: {
      escapeValue: false
    }
  })

export default i18n

4. Обнови src/main.tsx:
import './i18n'  // Импортируй i18n
import './styles/globals.css'

5. Обнови Dashboard.tsx чтобы использовать i18n и API:
import { useTranslation } from 'react-i18next'
import { useTelegram } from '@/hooks/useTelegram'
import { useGetUser } from '@/hooks/useApi'

const Dashboard = () => {
  const { t } = useTranslation()
  const { user } = useTelegram()
  const { data: userData, isLoading } = useGetUser(user?.id)
  
  if (isLoading) return <div className="p-4">Loading...</div>
  
  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">
        {t('dashboard.greeting', { name: userData?.first_name || user?.first_name || 'User' })}
      </h1>
      {/* Остальной код */}
    </div>
  )
}

6. Создай .env для frontend:
VITE_API_URL=http://localhost:8044/api/v1
```

### ТРОЙНОЕ ТЕСТИРОВАНИЕ #4

#### ✅ Тест 1: API запрос работает
```bash
npm run dev

# В браузере DevTools -> Network
# Должен быть запрос к /api/v1/users/me
```

#### ✅ Тест 2: i18n работает
```bash
# В консоли браузера:
import i18n from './src/i18n'
i18n.changeLanguage('en')

# Тексты должны переключиться
```

#### ✅ Тест 3: Build с env
```bash
echo "VITE_API_URL=http://localhost:8044/api/v1" > .env
npm run build
grep -r "localhost:8044" dist/
```

### Коммит
```bash
git checkout dev
git add .
git commit -m "feat: этап 4 итерации 4 - API клиент, React Query, i18n"
git push origin dev && git checkout main && git merge dev && git push origin main && git checkout dev
```

---

## 🔨 ЭТАП 5: ДЕПЛОЙ MINI APP + ИНТЕГРАЦИЯ С БОТОМ

### Задача
Собрать production build, настроить Nginx для статики, добавить кнопку в боте для открытия Mini App.

### Промт для Cursor

```
@BrashLens Настрой деплой Mini App:

1. Создай BrashLens/frontend/.env.production:
VITE_API_URL=https://your-domain.com/api/v1

2. Build скрипт для деплоя:
#!/bin/bash
cd /root/wmraduga4/BrashLens/frontend
npm install
npm run build
sudo rm -rf /var/www/brashlens/miniapp
sudo mkdir -p /var/www/brashlens/miniapp
sudo cp -r dist/* /var/www/brashlens/miniapp/
sudo chown -R www-data:www-data /var/www/brashlens/miniapp
echo "✅ Mini App deployed"

3. Nginx конфигурация - добавь location в существующий server block:
location /app {
    alias /var/www/brashlens/miniapp;
    try_files $uri $uri/ /index.html;
    
    # CORS для API
    add_header 'Access-Control-Allow-Origin' '*' always;
    add_header 'Access-Control-Allow-Methods' 'GET, POST, PATCH, DELETE, OPTIONS' always;
    add_header 'Access-Control-Allow-Headers' 'Content-Type, X-Telegram-Init-Data' always;
}

4. Обнови бота - добавь кнопку "Открыть приложение":
# В app/bot/handlers/start.py после успешной регистрации:

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

# Для фотографа после регистрации
keyboard = [
    [InlineKeyboardButton(
        "🚀 Открыть приложение",
        web_app=WebAppInfo(url="https://your-domain.com/app")
    )],
    [InlineKeyboardButton("📋 Скопировать ссылку", url=share_link)]
]

await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

5. docker-compose.yml - добавь volume для frontend build:
services:
  backend:
    volumes:
      - ./frontend/dist:/app/frontend/dist:ro
```

### ТРОЙНОЕ ТЕСТИРОВАНИЕ #5

#### ✅ Тест 1: Production build
```bash
cd /root/wmraduga4/BrashLens/frontend
npm run build
ls -lh dist/

# Должны быть минифицированные файлы
cat dist/index.html | grep -o "assets/index-.*\.js"
```

#### ✅ Тест 2: Nginx конфигурация
```bash
# Добавь location в Nginx
sudo nano /etc/nginx/sites-available/brashlens
# Вставь location /app { ... }

sudo nginx -t
sudo systemctl reload nginx

# Проверь доступность
curl -I https://your-domain.com/app/
```

#### ✅ Тест 3: Открытие из бота
```bash
# В Telegram:
# 1. Отправь /start боту
# 2. После регистрации появится кнопка "🚀 Открыть приложение"
# 3. Нажми - должен открыться Mini App
# 4. Проверь что навигация работает на мобильном
```

### Коммит
```bash
git checkout dev
git add .
git commit -m "feat: этап 5 итерации 4 - деплой Mini App и интеграция с ботом"
git push origin dev && git checkout main && git merge dev && git push origin main && git checkout dev
```

---

## 📊 ФИНАЛЬНАЯ ПРОВЕРКА ИТЕРАЦИИ 4

### Чеклист завершения

- [ ] **React проект:**
  - [ ] Vite + TypeScript работает
  - [ ] Tailwind CSS настроен
  - [ ] Build создается без ошибок

- [ ] **Telegram WebApp SDK:**
  - [ ] useTelegram хук работает
  - [ ] Тема Telegram применяется
  - [ ] Данные пользователя получаются

- [ ] **Навигация:**
  - [ ] Layout с Navigation работает
  - [ ] Все 5 страниц доступны
  - [ ] Роутинг работает корректно

- [ ] **API интеграция:**
  - [ ] axios клиент настроен
  - [ ] React Query работает
  - [ ] Запросы к API проходят

- [ ] **Мультиязычность:**
  - [ ] i18next настроен
  - [ ] RU/EN переключаются
  - [ ] Тексты переводятся

- [ ] **Деплой:**
  - [ ] Production build собирается
  - [ ] Nginx отдает статику
  - [ ] Mini App открывается из бота
  - [ ] На мобильном отображается корректно

### Итоговое тестирование

```bash
# 1. Build
cd /root/wmraduga4/BrashLens/frontend
npm run build

# 2. Деплой
bash deploy-frontend.sh

# 3. Проверь в браузере
curl https://your-domain.com/app/

# 4. В Telegram:
# - Отправь /start боту
# - Нажми "Открыть приложение"
# - Проверь навигацию
# - Проверь темную/светлую тему
# - Проверь что API запросы проходят
```

**Критерии успеха:**
- ✅ Mini App открывается из бота
- ✅ Корректно отображается на мобильном
- ✅ Навигация между страницами работает
- ✅ Тема Telegram применяется
- ✅ API запросы проходят с аутентификацией
- ✅ Смена языка работает

---

## 📝 ФИНАЛЬНЫЙ КОММИТ

```bash
git checkout dev
git add .
git commit -m "feat: iteration 4 complete - Mini App foundation

- Created React project with Vite + TypeScript + Tailwind
- Integrated Telegram WebApp SDK
- Implemented Layout with bottom navigation
- Created 5 page stubs (Dashboard, Profile, Portfolio, Calendar, Clients)
- Setup API client with axios and React Query
- Configured i18next for RU/EN
- Deployed to production with Nginx
- Added 'Open App' button in bot

Mini App now opens from Telegram and displays correctly on mobile."

git push origin dev
git checkout main
git merge dev
git push origin main
git checkout dev
```

---

## 🎯 ИТОГО

**Что получилось в итерации 4:**
- ✅ React Mini App с современным стеком
- ✅ Интеграция с Telegram WebApp SDK
- ✅ Роутинг и навигация между страницами
- ✅ 5 страниц-заглушек готовы к наполнению
- ✅ API клиент с React Query
- ✅ Мультиязычность (RU/EN)
- ✅ Деплой на сервере
- ✅ Кнопка в боте открывает приложение

**Время выполнения:** 4-5 дней

**Готовность к итерации 5:** ✅

**Следующая итерация:** Профиль фотографа + загрузка аватара (File Storage HDD/R2)
