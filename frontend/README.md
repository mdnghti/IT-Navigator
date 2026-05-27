# IT Navigator - Frontend

Фронтенд профориентационной платформы на Next.js 14 с TypeScript.

## Технологии

- **Next.js 14** - React фреймворк с App Router
- **TypeScript** - типизация
- **Framer Motion** - анимации
- **TanStack Query** - управление серверным состоянием
- **Zustand** - управление клиентским состоянием
- **Axios** - HTTP клиент

## Установка

```bash
npm install
```

## Запуск

### Development режим

```bash
npm run dev
```

Приложение будет доступно на http://localhost:3000

### Production сборка

```bash
npm run build
npm start
```

## Переменные окружения

Создайте файл `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Структура проекта

```
src/
├── app/                    # Next.js App Router страницы
│   ├── (auth)/            # Группа авторизации
│   │   ├── login/
│   │   └── register/
│   ├── test/              # Страницы тестирования
│   │   ├── general/
│   │   └── specialized/[code]/
│   ├── results/[id]/      # Результаты теста
│   ├── dashboard/         # Дашборд пользователя
│   ├── layout.tsx         # Корневой layout
│   ├── page.tsx           # Главная страница
│   ├── providers.tsx      # React Query провайдер
│   └── globals.css        # Глобальные стили
├── components/            # React компоненты
│   ├── test/             # Компоненты тестирования
│   ├── results/          # Компоненты результатов
│   └── ui/               # UI компоненты
├── lib/                  # Утилиты
│   └── api.ts           # API клиент
├── store/               # Zustand stores
│   └── testStore.ts    # Состояние теста
└── types/              # TypeScript типы
    └── index.ts
```

## Основные страницы

- `/` - Главная страница
- `/register` - Регистрация
- `/login` - Вход
- `/dashboard` - Дашборд пользователя
- `/test/general` - Общий тест
- `/test/specialized/[code]` - Специализированный тест
- `/results/[id]` - Результаты теста

## Docker

```bash
docker build -t career-platform-frontend .
docker run -p 3000:3000 career-platform-frontend
```

## Дизайн

Фронтенд использует уникальный дизайн с:
- Темной цветовой схемой с градиентами
- Анимациями на Framer Motion
- Glass morphism эффектами
- Плавными переходами
- Адаптивной версткой
